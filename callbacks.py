import base64
import copy
import datetime as dt
import functools
import gettext
import hashlib
import io
import math

from dash import exceptions
from dash.dependencies import Input, Output, State
import dash_html_components as html
import geopy.distance
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from app import app
import drones

# datetime of the beginning of the emergency call
col_time_em_call = 'time_call'
# in seconds, BLS team delay
col_BLS_time = 'BLS_time'
# indicator: 1 if the incident is during the day, 0 during the night
col_indic_day = 'day'
# indicator : 1 if the incident is at home, 0 otherwise
col_indic_home = 'home'
# Latitude WGS84
col_lat_inter = 'latitude'
# Longitude WGS84
col_lon_inter = 'longitude'

# indicator: 1 if wind is low enough to fly (less than 50 km/h)
col_indic_wind = 'low_wind'
# indicator: 1 if sight is clear enough to fly
col_indic_sight = 'clear_sight'

col_drone_delay = 'col_res'


@functools.lru_cache(3)
def _load_incidents(contents):
    if contents:
        content_ = contents.split(',')
        content_string = content_[1]
        decoded = base64.b64decode(content_string)
        incidents_csv = io.StringIO(decoded.decode('utf-8'))
    else:
        incidents_csv = 'data/dataACRtime_GPSCSPCpostime_v7.csv'
    incidents = pd.read_csv(incidents_csv, encoding='latin-1', index_col=0)
    print(incidents)
    incidents[col_time_em_call] = pd.to_datetime(incidents[col_time_em_call])
    incidents = incidents.loc[incidents[col_BLS_time] >= 0]
    incidents = incidents.loc[incidents[col_BLS_time] <= 25 * 60]
    return incidents


_CUSTOM_DRONE_INPUT = 'custom'


def update_avail(time_dec, avail, unavail):
    """
    Update of the available fleet of drones after each launch.

    :param time_dec: (dt.datetime) Datetime when the incident started.
    :param avail: (np.array) List of available drones (name, GPS location)
    :param unavail: (np.array) List of unavailable drones (name, GPS location and datetime until
        when they are unavailable)

    :return: (np.array, np.array) Updated list of available and unavailable drones.
    """
    drop_drone = []
    for i in range(0, unavail.shape[0]):
        if unavail[i][3] < time_dec:
            avail = np.append(avail, [[unavail[i][0], unavail[i][1], unavail[i][2]]], axis=0)
            drop_drone.append(i)

    res_unavail = np.delete(unavail, drop_drone, axis=0)
    return avail, res_unavail


def drone_unavail(df, duree, avail_ini):
    """
    For all incident selects the closest available drone to send.
    :param df:
    :param duree:
    :param avail_ini:
    :return:
    """

    avail = copy.deepcopy(avail_ini)
    # init
    unavail = np.array([['NULL', 0.0, 0.0, dt.datetime(2017, 1, 1, 0, 0, 0)]])
    list_dist = []

    for unused_index, row in df.iterrows():
        time_dec = row[col_time_em_call]
        avail, unavail = update_avail(time_dec, avail, unavail)
        lat_a = row[col_lat_inter]
        lon_a = row[col_lon_inter]
        coord_a = (lat_a, lon_a)

        dist_tot = []
        for drone in avail:
            coord_drone = (drone[1], drone[2])
            try:
                dist = geopy.distance.geodesic(coord_drone, coord_a).km
            except ValueError:
                dist = np.nan
            dist_tot.append(dist)

        try:
            min_dist = np.nanmin(dist_tot)
            min_ind = dist_tot.index(min_dist)
            cs_rm = avail[min_ind]
            avail = np.delete(avail, min_ind, axis=0)
            time_unavail = time_dec + dt.timedelta(hours=duree)
            new_unavail = np.array([cs_rm[0], cs_rm[1], cs_rm[2], time_unavail])
            unavail = np.vstack([unavail, new_unavail])
            list_dist.append(min_dist)
        except ValueError:
            list_dist.append(np.nan)

    return list_dist


def select_interv(all_incidents, condition, column, rate):
    """Select randomly some incidents.

    :param all_incidents: a DataFrame containing incidents. This will be modified.
    :param condition: a boolean array, the same size of df to restrict the rows that can be
        affected: True for those that can be selected, False if not.
    :param column: (str) The name of the column of df to null if not selected.
    :param rate (float) The rate (between 0 and 1) of rows that should be kept.
    """
    selected = np.random.rand(len(all_incidents)) > rate
    selected_final = condition & selected
    all_incidents.loc[selected_final, column] = 0
    return all_incidents, selected_final


def _read_uploaded_data(contents):
    """Extract the content of a file uploaded with the dcc.Upload component.

    The input format is like "data:text/csv;base64,Q09ACzer324..."
    """
    return io.BytesIO(base64.b64decode(contents.split(',')[1]))


def _compute_drone_time(
        drone_input, custom_drone_input, custom_incidents_dataset,
        input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
        input_jour_, detec_rate_home, no_witness_rate, detec_rate_vp, unavail_delta, lang):
    """
    Computes drone simulated flights.

    :param custom_incidents_dataset: (str) incidents data as CSV
    :param drone_input: (str) drones initial locations as index for STARTING_POINTS
    :param custom_drone_input: (str) drones initial locations as CSV data
    :param input_speed: (str) drone horizontal speed in km/h
    :param input_acc: (str) drone horizontal acceleration in m/s^2
    :param vert_acc: (str) drone vertical speed in m/s
    :param alt: (str) flight altitude in meters
    :param dep_delay: (str) departure delay in seconds
    :param arr_delay: (str) arrival delay in seconds
    :param detec_delay: (str) delay between detection of unconsciousness and OHCA detection
        by 18/112 operators in seconds
    :param input_jour: (str) whether drone flights are unauthorized at night (yes/no)
    :param detec_rate_home: (str) rate of OHCA detection by 18/112 operators ([0,1])
    :param no_witness_rate: (str) rate of OHCA at home, which only have one witness alone ([0,1])
    :param detec_rate_vp: (str) odd ratio of OHCA in the streets vs OHCA at home or in a public
        place detection by 18/112 operators ([0,1])
    :param unavail_delta: (str) delay during which a drone is unavailable after being sent to an
        OHCA in hours
    :param lang: (str) the language code used by the interface.

    :return: graphs for Dash visualisation
    """
    # drone_input = 'Postes de commandement'
    # input_wind = 'Non'
    # input_speed = '80'
    # input_acc = '9'
    # vert_acc = '9'
    # alt = '100'
    # dep_delay = '15'
    # arr_delay = '15'
    # detec_delay = '104'
    # input_jour_ = 'Non'
    # detec_rate_home = '1'
    # no_witness_rate = '0.56'
    # detec_rate_vp = '0.15'
    # unavail_delta = '6'
    # lang = 'fr'

    np.random.seed(123)

    if lang:
        t11n = gettext.translation('messages', localedir='locales', languages=[lang], fallback=True)
        t11n.install()

    dep_delay = np.float(dep_delay) + np.float(detec_delay) + (np.float(alt) / np.float(vert_acc))
    arr_delay = np.float(arr_delay) + (np.float(alt) / np.float(vert_acc))
    input_acc = np.float(input_acc)
    detec_rate_home = np.float(detec_rate_home)
    no_witness_rate = np.float(no_witness_rate)
    detec_rate_vp = np.float(detec_rate_vp)
    unavail_delta = np.float(unavail_delta)

    input_jour = input_jour_ == 'Oui' or input_jour_ == 'Yes'
    input_speed = np.float(input_speed)

    if drone_input == _CUSTOM_DRONE_INPUT:
        avail_ini_ = np.genfromtxt(
            _read_uploaded_data(custom_drone_input), delimiter=',', dtype=str)
    else:
        avail_ini_ = drones.STARTING_POINTS[drone_input]

    res_col_a = 'col_res'
    res_col_b = 'apport_drone'
    df_res = copy.deepcopy(_load_incidents(custom_incidents_dataset))

    # Apport drone: si négatif, temps gagné grâce au drone. Sinon, temps gagné grâce au VSAV.

    no_drone = dict()
    no_drone['night'] = np.full((len(df_res),), False)

    df_res[col_drone_delay] = np.nan
    if not input_jour:
        index_nuit = df_res[col_indic_day] == 0
        no_drone['night'] = index_nuit
        df_res.loc[index_nuit, col_drone_delay] = 0

    df_res.loc[df_res[col_indic_wind] == 0, col_drone_delay] = 0
    df_res.loc[df_res[col_indic_sight] == 0, col_drone_delay] = 0

    in_a_public_place = df_res[col_indic_home] == 0
    # detection rate of OHCA in a public place
    df_res, index_detec_rate_vp = \
        select_interv(df_res, in_a_public_place, col_drone_delay, detec_rate_vp)
    # detection rate of OHCA in a private place (at home)
    df_res, index_detec_home = select_interv(df_res, ~in_a_public_place, col_drone_delay,
                                             detec_rate_home)
    # update no drone reasons : lack of detection
    no_drone['no detection'] = np.logical_or(index_detec_rate_vp, index_detec_home)

    # rate of OHCA witnesses home alone
    df_res, index_witness = select_interv(df_res, ~in_a_public_place, col_drone_delay,
                                          1 - no_witness_rate)
    # update no drone reasons : not enough witnesses
    no_drone['not enough witnesses'] = index_witness

    df_ic = df_res.loc[df_res[col_drone_delay] != 0]
    distance_field = 'Distance'
    df_ic[distance_field] = drone_unavail(df_ic, unavail_delta, avail_ini_)  # TODO

    for i, r in df_ic.iterrows():
        eff_speed = input_speed
        # distance covered during acceleration and brake
        acc_dist = 2 * eff_speed * input_acc / 3600
        acc = eff_speed / (input_acc * 3600)

        dist = r[distance_field]

        lin_dist = dist - acc_dist
        if lin_dist >= 0:
            lin_time = (dist / eff_speed) * 3600
            res_time = lin_time + dep_delay + arr_delay + 2 * input_acc
        else:
            res_time = dep_delay + arr_delay + 2 * math.sqrt(dist / acc)

        df_res.loc[i, col_drone_delay] = np.round(res_time)

    df_res[res_col_b] = df_res[res_col_a] - df_res[col_BLS_time]

    df_res.loc[df_res[res_col_a] == 0, res_col_b] = \
        df_res.loc[df_res[res_col_a] == 0, col_BLS_time]
    dfi = df_res.dropna(axis=0, how='all', thresh=None, subset=[res_col_b], inplace=False)

    # simple metrics
    n_tot = len(dfi)
    n_nodrone = len(dfi.loc[dfi[res_col_a] == 0])
    n_drone = len(dfi.loc[dfi[res_col_b] < 0])
    n_bls = len(dfi.loc[dfi[res_col_b] > 0]) - n_nodrone

    no_drone['detection'] = np.logical_not(no_drone['no detection'])
    # flight restriction reasons for the sunburst chart

    # number of no detected OHCA
    n_no_detec = no_drone['no detection'].sum()
    # # number of no detected OHCA which are also at night
    # n_no_detec_night = np.logical_and(no_drone['no detection'],
    #                                   no_drone['night']).sum()
    # # number of no detected OHCA which also don't have enough witnesses
    # n_no_detec_wit = np.logical_and(no_drone['no detection'],
    #                                 no_drone['not enough witnesses']).sum()
    # # number of no detected OHCA which also don't have enough witnesses and are at night
    # n_no_detec_both = np.logical_and(np.logical_and(no_drone['no detection'],
    #                                                 no_drone['night']),
    #                                  no_drone['not enough witnesses']).sum()
    # number of detected OHCA which are at night
    n_detec_night = np.logical_and(no_drone['detection'],
                                   no_drone['night']).sum()
    # number of detected OHCA which don't have enough witnesses
    n_detec_wit = np.logical_and(no_drone['detection'],
                                 no_drone['not enough witnesses']).sum()
    # number of detected OHCA which don't have enough witnesses and are at night
    n_detec_both = np.logical_and(np.logical_and(no_drone['detection'],
                                                 no_drone['night']),
                                  no_drone['not enough witnesses']).sum()

    n_detec_dw = n_detec_wit - n_detec_both

    # l_pie = np.array([n_drone, n_bls, n_nodrone,
    #                   n_no_detec, n_nodrone - n_no_detec,
    #                   n_no_detec_night - n_no_detec_both, n_no_detec_wit - n_no_detec_both,
    #                   n_no_detec_both,
    #                   n_detec_night - n_detec_both, n_detec_wit - n_detec_both, n_detec_both])
    # l_pie = np.around(l_pie * 100 / n_tot, 0).astype('int')

    # Create data-frame used by getSankey function
    if not input_jour:
        cols_sankey = ['Intervention', 'Detection', 'Nuit', 'Témoin', 'Drone', 'Total']
        df_sankey = pd.DataFrame(columns=cols_sankey, index=df_res.index)
        index_nuit_cp = copy.deepcopy(index_nuit)
        rate_nuit = int(np.round(100 * index_nuit_cp.sum() / len(index_nuit_cp), 0))
        index_nuit_cp = np.where(index_nuit_cp, str(rate_nuit) + '% ' + _('Night'), index_nuit_cp)
        index_nuit_cp = np.where(index_nuit_cp == 'False',
                                 str(100 - rate_nuit) + '% ' + _('Day'), index_nuit_cp)
        df_sankey['Nuit'] = index_nuit_cp

    else:
        cols_sankey = ['Intervention', 'Detection', 'Nuit', 'Témoin', 'Drone', 'Total']
        df_sankey = pd.DataFrame(columns=cols_sankey, index=df_res.index)

    df_sankey['Intervention'] = _('All incidents')
    df_sankey['Total'] = 0

    index_detec_cp = copy.deepcopy(np.logical_or(index_detec_rate_vp, index_detec_home))
    rate_ndetec = int(np.round(100 * index_detec_cp.sum() / len(index_detec_cp), 0))
    index_detec_cp = np.where(index_detec_cp,
                              str(rate_ndetec) + '% ' + _('OHCA undeteced'), index_detec_cp)
    index_detec_cp = np.where(index_detec_cp == 'False',
                              str(100 - rate_ndetec) + '% ' + _('OHCA Detected'),
                              index_detec_cp)
    df_sankey['Detection'] = index_detec_cp

    index_temoin_cp = copy.deepcopy(index_witness)
    rate_temoin = int(np.round(100 * index_temoin_cp.sum() / len(index_temoin_cp), 0))
    index_temoin_cp = np.where(index_temoin_cp,
                               str(rate_temoin) + '% ' + _('Not enough witnesses'), index_temoin_cp)
    index_temoin_cp = np.where(index_temoin_cp == 'False',
                               str(100 - rate_temoin) + '% ' + _('Enough witnesses'),
                               index_temoin_cp)
    df_sankey['Témoin'] = index_temoin_cp

    index_nodrone = dfi[res_col_a] == 0
    index_bls = (dfi[res_col_b] >= 0) & (dfi[res_col_a] > 0)
    index_drone = dfi[res_col_b] < 0

    rate_drone = int(np.round(100 * index_drone.sum() / len(index_drone), 0))
    rate_bls = int(np.round(100 * index_bls.sum() / len(index_bls), 0))
    index_drone = np.where(index_drone, str(rate_drone) + '% ' + _('Drone faster'), index_drone)
    index_drone = np.where(index_bls, str(rate_bls) + '% ' + _('BLS team faster'), index_drone)
    index_drone = np.where(index_nodrone,
                           str(100 - rate_drone - rate_bls) + '% ' + _('No drone'), index_drone)
    df_sankey['Drone'] = index_drone

    if not input_jour:
        dftest = df_sankey.groupby(['Intervention', 'Detection', 'Nuit', 'Témoin', 'Drone']) \
            .agg({'Total': 'count'})
        dftest.reset_index(inplace=True)
        sankey_data = genSankey(dftest,
                                cat_cols=['Intervention', 'Detection', 'Nuit', 'Témoin', 'Drone'],
                                value_cols='Total')
    else:
        dftest = df_sankey.groupby(['Intervention', 'Detection', 'Témoin', 'Drone']) \
            .agg({'Total': 'count'})
        dftest.reset_index(inplace=True)
        sankey_data = genSankey(dftest,
                                cat_cols=['Intervention', 'Detection', 'Témoin', 'Drone'],
                                value_cols='Total')

    trace1 = sankey_data

    # trace1 = go.Sunburst(
    #     labels=["Drone faster", "BLS team faster", "No drone",
    #             "No detection", "Detection with exclusion",
    #             "ND + N", "ND + NE-W", "ND + N + NE W",
    #             "D + N", "D + NE-W", "D + NE-W + N"],
    #     parents=["", "", "",
    #              "No drone", "No drone",
    #              "No detection", "No detection", "No detection",
    #             "Detection with exclusion", "Detection with exclusion",
    #             "Detection with exclusion"],
    #     values=l_pie,
    #     branchvalues="total",
    # )

    # trace1 = go.Bar(
    #     x=[0, 1, 2],
    #     text=['Faster drone', 'BLS team faster', 'No drone sent'],
    #     y=[per_drone, per_bls, per_nodrone],
    #     textposition='auto',
    #     name='Test'
    # )

    # for the histogram graph
    df_density = copy.deepcopy(dfi)
    df_density = df_density.loc[df_density[res_col_a] > 0]

    trace3 = go.Histogram(x=df_density[col_BLS_time],
                          name=_('BLS team'),
                          marker_color='#ff5959')
    trace4 = go.Histogram(x=df_density[res_col_a],
                          name=_('Drone'),
                          marker_color='#49beb7')

    # for the butterfly graph
    dfi['res_col_c'] = np.around(np.abs(dfi[res_col_b]), 0)
    dfi['wins'] = 'B'  # BLS team faster
    dfi.loc[dfi[res_col_b] < 0, 'wins'] = 'D'  # drone faster
    dfi.loc[dfi[res_col_a] == 0, 'wins'] = 'N'  # no drone

    dfi.loc[dfi['wins'] == 'D', 'text'] = \
        _('<b>Drone faster</b> <br> by: ') + \
        dfi.loc[dfi['wins'] == 'D', 'res_col_c'].map(str)
    dfi.loc[dfi['wins'] == 'B', 'text'] = \
        _('<b>BLS team faster</b> <br> by: ') + \
        dfi.loc[dfi['wins'] == 'B', 'res_col_c'].map(str)
    dfi.loc[dfi['wins'] == 'N', 'text'] = \
        _('<b>No drone</b> <br> BLS team time to arrival: ') + \
        dfi.loc[dfi['wins'] == 'N', 'res_col_c'].map(str)

    dfi.loc[dfi['wins'] == 'D', 'col_bar'] = 'rgba(0,128,0,0.8)'
    dfi.loc[dfi['wins'] == 'B', 'col_bar'] = 'rgba(222,45,38,0.8)'
    dfi.loc[dfi['wins'] == 'N', 'col_bar'] = 'rgba(186,190,222,1)'

    dfi[res_col_b] = - dfi[res_col_b]
    ynew = dfi.sort_values(res_col_b)
    list_col = list(ynew['col_bar'])
    list_text = list(ynew['text'])

    trace5 = go.Bar(
        x=[i for i in range(0, len(dfi))],
        y=ynew[res_col_b],
        name='',
        marker=dict(color=list_col),
        text=list_text,
        hovertemplate='%{text} seconds',  # %{y} seconds',
    )

    indicator_graphic_1 = {
        'data': [trace1],
        'layout': {'width': 500,
                   'height': 700,
                   'margin': {'l': 30, 'b': 100, 't': 50, 'r': 30},
                   'hovermode': 'closest',
                   'autosize': True}
    }

    fsize = 100 / n_tot
    flows = [
        dict(
            fill='#e7eaf6',
            size=fsize * n_no_detec,
            text=_('Not detected') + f' {int(np.floor(fsize * n_no_detec))}%',
        ),
        dict(
            fill='#a2a8d3',
            size=fsize * n_detec_night,
            text=_('Detected but by night') + f' {int(np.floor(fsize * n_detec_night))}%',
        ),
        dict(
            fill='#38598b',
            size=fsize * n_detec_wit,
            text=_('Detected but not enough witnesses') + f' {int(np.floor(fsize * n_detec_dw))}%',
        ),
        dict(
            fill='#ee4540',
            size=fsize * n_bls,
            text=_('BLS team faster than drone') + f' {int(np.floor(fsize * n_bls))}%',
        ),
        dict(
            fill='#58b368',
            size=fsize * n_drone,
            text=_('Drone faster') + f' {int(np.floor(fsize * n_drone))}%',
        ),
    ]

    indicator_graphic_3 = {
        'data': [trace3, trace4],
        'layout': go.Layout(
            xaxis={
                'title': _('Time to arrival when a drone is sent (in seconds)'),
                'type': 'linear',
            },
            yaxis={
                'title': _('Number of incidents'),
                'type': 'linear',
                'showticklabels': True,
            },
            width=500,
            height=400,
            # margin={'l': 30, 'b': 100, 't': 50, 'r': 30},
            hovermode='closest',
            autosize=True,
            legend={'yanchor': 'top',
                    'y': 0.99,
                    'xanchor': 'right',
                    'x': 0.98
                    }
        ),
    }

    indicator_graphic_4 = {
        'data': [trace5],
        'layout': {
            'xaxis': {
                'title': {'text': u'Interventions'},
                'type': 'linear',
                'showgrid': False,
                'showticklabels': True,
            },
            'yaxis': {
                'title': _('Time difference drone - BLS team (in seconds)'),
                'type': 'linear',
                'showticklabels': True,
                'dtick': 180,
            },
            'width': 500,
            'height': 400,
            # 'margin': {'l': 30, 'b': 100, 't': 50, 'r': 30, 'pad': 20},
            'hovermode': 'closest',
            'autosize': True
        }
    }

    return flows, indicator_graphic_3, indicator_graphic_4, flows, \
        indicator_graphic_3, indicator_graphic_4, indicator_graphic_1, indicator_graphic_1


@app.callback(
    Output('hash', 'value'),
    [Input('seq_start', 'n_clicks'), Input('app-tabs', 'active_tab')],
    [State('input_drone', 'value'),
     State('upload-starting-points', 'contents'),
     State('upload-incidents', 'contents'),
     State('speed', 'value'),
     State('acc', 'value'),
     State('vert-acc', 'value'),
     State('alt', 'value'),
     State('dep_delay', 'value'),
     State('arr_delay', 'value'),
     State('detec_delay', 'value'),
     State('day', 'value'),
     State('detec_rate_home', 'value'),
     State('wit_detec', 'value'),
     State('detec_rate_vp', 'value'),
     State('unavail_delta', 'value'),
     State('lang', 'value'),
     State('hash', 'value')])
def params_hash(unused_seq_start, unused_active_tab, *args):
    return _compute_params_hash(*args)


@app.callback(
    Output('hash_b', 'value'),
    [Input('seq_start_b', 'n_clicks'), Input('app-tabs', 'active_tab')],
    [State('input_drone_b', 'value'),
     State('upload-starting-points', 'contents'),
     State('upload-incidents', 'contents'),
     State('speed_b', 'value'),
     State('acc_b', 'value'),
     State('vert-acc_b', 'value'),
     State('alt_b', 'value'),
     State('dep_delay_b', 'value'),
     State('arr_delay_b', 'value'),
     State('detec_delay_b', 'value'),
     State('day_b', 'value'),
     State('detec_rate_home_b', 'value'),
     State('wit_detec_b', 'value'),
     State('detec_rate_vp_b', 'value'),
     State('unavail_delta_b', 'value'),
     State('lang', 'value'),
     State('hash_b', 'value')])
def params_hash_b(unused_seq_start, unused_active_tab, *args):
    return _compute_params_hash(*args)


def _compute_params_hash(
        drone_input, custom_drone_input, custom_incidents_csv,
        input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
        input_jour, detec_rate_home, no_witness_rate, detec_rate_vp, unavail_delta, lang,
        previous_hash):
    combined = hashlib.sha1()
    combined.update(str(drone_input).encode('utf-8'))
    if custom_drone_input:
        combined.update(str(custom_drone_input).encode('utf-8'))
    if custom_incidents_csv:
        combined.update(str(custom_incidents_csv).encode('utf-8'))
    combined.update(str(input_speed).encode('utf-8'))
    combined.update(str(input_acc).encode('utf-8'))
    combined.update(str(vert_acc).encode('utf-8'))
    combined.update(str(alt).encode('utf-8'))
    combined.update(str(dep_delay).encode('utf-8'))
    combined.update(str(arr_delay).encode('utf-8'))
    combined.update(str(detec_delay).encode('utf-8'))
    combined.update(str(input_jour).encode('utf-8'))
    combined.update(str(detec_rate_home).encode('utf-8'))
    combined.update(str(no_witness_rate).encode('utf-8'))
    combined.update(str(detec_rate_vp).encode('utf-8'))
    combined.update(str(unavail_delta).encode('utf-8'))
    if lang:
        combined.update(str(lang).encode('utf-8'))
    new_hash = combined.hexdigest()
    if new_hash == previous_hash:
        raise exceptions.PreventUpdate()
    return new_hash


@app.callback(
    [Output('flows-graphic', 'flows'),
     Output('indicator-graphic3', 'figure'),
     Output('indicator-graphic4', 'figure'),
     Output('flows-graphicu', 'flows'),
     Output('indicator-graphic3u', 'figure'),
     Output('indicator-graphic4u', 'figure'),
     Output('indicator-graphic1', 'figure'),
     Output('indicator-graphic1u', 'figure')],
    [Input('hash', 'value')],
    [State('input_drone', 'value'),
     State('upload-starting-points', 'contents'),
     State('upload-incidents', 'contents'),
     State('speed', 'value'),
     State('acc', 'value'),
     State('vert-acc', 'value'),
     State('alt', 'value'),
     State('dep_delay', 'value'),
     State('arr_delay', 'value'),
     State('detec_delay', 'value'),
     State('day', 'value'),
     State('detec_rate_home', 'value'),
     State('wit_detec', 'value'),
     State('detec_rate_vp', 'value'),
     State('unavail_delta', 'value'),
     State('lang', 'value')])
def drone_time(
        unused_hash_value,
        drone_input, custom_drone_input, custom_incidents_csv,
        input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
        input_jour_, detec_rate_home, no_witness_rate, detec_rate_vp, unavail_delta, lang):
    return _compute_drone_time(
        drone_input, custom_drone_input, custom_incidents_csv,
        input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
        input_jour_, detec_rate_home, no_witness_rate, detec_rate_vp, unavail_delta, lang)


def genSankey(df, cat_cols, value_cols=''):

    # maximum of 6 value cols -> 6 colors
    colorPalette = ['#4B8BBE', '#306998', '#FFE873', '#FFD43B', '#646464']
    labelList = []
    colorNumList = []
    for catCol in cat_cols:
        labelListTemp = list(set(df[catCol].values))
        colorNumList.append(len(labelListTemp))
        labelList = labelList + labelListTemp

    # remove duplicates from labelList
    labelList = list(dict.fromkeys(labelList))

    # define colors based on number of levels
    colorList = []
    for idx, colorNum in enumerate(colorNumList):
        colorList = colorList + [colorPalette[idx]] * colorNum

    # transform df into a source-target pair
    for i in range(len(cat_cols) - 1):
        if i == 0:
            sourceTargetDf = df[[cat_cols[i], cat_cols[i + 1], value_cols]]
            sourceTargetDf.columns = ['source', 'target', 'count']
        else:
            tempDf = df[[cat_cols[i], cat_cols[i + 1], value_cols]]
            tempDf.columns = ['source', 'target', 'count']
            sourceTargetDf = pd.concat([sourceTargetDf, tempDf])
        sourceTargetDf = sourceTargetDf.groupby(['source', 'target']) \
            .agg({'count': 'sum'}).reset_index()

    # add index for source-target pair
    sourceTargetDf['sourceID'] = sourceTargetDf['source'].apply(labelList.index)
    sourceTargetDf['targetID'] = sourceTargetDf['target'].apply(labelList.index)

    # add column for source-node-conditional count to retrieve rates
    sourceTargetDf['cond_count'] = 0
    for i in sourceTargetDf['sourceID'].unique():
        s = sourceTargetDf[sourceTargetDf.sourceID == i]['count'].sum()
        sourceTargetDf.loc[sourceTargetDf['sourceID'] == i, ['cond_count']] = s

    labelsDf = ((100 * sourceTargetDf['count'] / sourceTargetDf['cond_count'])
                .round(decimals=1)).astype(str) + '%'

    # creating the sankey diagram
    data = go.Sankey(
        node=dict(
            pad=15,
            thickness=30,
            line=dict(
                color='black',
                width=1
            ),
            label=labelList,
            color=colorList
        ),
        orientation='v',
        link=dict(
            source=sourceTargetDf['sourceID'],
            target=sourceTargetDf['targetID'],
            value=sourceTargetDf['count'],
            label=labelsDf
        ),
    )
    #
    # layout = dict(
    #     title=title,
    #     font=dict(
    #         size=10
    #     )
    # )

    return data


@app.callback(
    [Output('flows-graphic_b', 'flows'),
     Output('indicator-graphic3_b', 'figure'),
     Output('indicator-graphic4_b', 'figure'),
     Output('flows-graphicu_b', 'flows'),
     Output('indicator-graphic3u_b', 'figure'),
     Output('indicator-graphic4u_b', 'figure'),
     Output('indicator-graphic1_b', 'figure'),
     Output('indicator-graphic1u_b', 'figure')],
    [Input('hash_b', 'value')],
    [State('input_drone_b', 'value'),
     State('upload-starting-points', 'contents'),
     State('upload-incidents', 'contents'),
     State('speed_b', 'value'),
     State('acc_b', 'value'),
     State('vert-acc_b', 'value'),
     State('alt_b', 'value'),
     State('dep_delay_b', 'value'),
     State('arr_delay_b', 'value'),
     State('detec_delay_b', 'value'),
     State('day_b', 'value'),
     State('detec_rate_home_b', 'value'),
     State('wit_detec_b', 'value'),
     State('detec_rate_vp_b', 'value'),
     State('unavail_delta_b', 'value'),
     State('lang', 'value')])
def drone_time_b(
        unused_seq_start,
        drone_input, custom_drone_input, custom_incidents_csv,
        input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
        input_jour_, detec_rate_home, no_witness_rate, detec_rate_vp, unavail_delta, lang):
    return _compute_drone_time(
        drone_input, custom_drone_input, custom_incidents_csv,
        input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
        input_jour_, detec_rate_home, no_witness_rate, detec_rate_vp, unavail_delta, lang)


@app.callback(
    [Output('output-starting-points-upload', 'children'),
     Output('input_drone', 'options'),
     Output('input_drone_b', 'options')],
    [Input('upload-starting-points', 'contents')],
    [State('upload-starting-points', 'filename')])
def custom_starting_points(contents, filename):
    options = [{'label': i, 'value': i} for i in drones.STARTING_POINTS]
    if contents:
        options.append({'label': filename, 'value': _CUSTOM_DRONE_INPUT})
        return html.Div(filename), options, options
    return None, options, options


@app.callback(
    [Output('output-incidents-upload', 'children'),
     Output('unused', 'value')],
    [Input('upload-incidents', 'contents')],
    [State('upload-incidents', 'filename')])
def custom_incidents(contents, filename):
    if contents:
        return html.Div(filename), 0
    return None, 0
