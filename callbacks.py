import copy
import datetime as dt
import gettext
import math

from dash.dependencies import Input, Output, State
import geopy.distance
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from app import app
import drones

# datetime of the beginning of the emergency call
col_time_em_call = 'DT_då_crochå_'
# in seconds, BLS team delay
col_BLS_time = 'DeltaPresentation'
# in m/s, wind speed in the direction
col_wind_speed = 'vitesse effective vent_'
# indicator: 1 if the intervention is during the day, 0 during the night
col_indic_day = 'jour_aeronautique'
# indicator : 1 if the intervention is in the streets, 0 otherwise
col_indic_streets = 'Voie publique'
# indicator : 1 if the intervention is in a public place (excluding streets), 0 otherwise
col_indic_pubplace = 'Lieu public'
# indicator : 1 if the intervention is at home, 0 otherwise
col_indic_home = 'Domicile'
# Latitude WGS84
col_lat_inter = 'new_lat'
# Longitude WGS84
col_lon_inter = 'new_lon'

# indicator: 1 if wind is low enough to fly (less than 50 km/h)
col_indic_wind = 'rafales < 50 km/h'
# indicator: 1 if sight is clear enough to fly
col_indic_sight = 'visibilite > 200m'

col_drone_delay = 'col_res'

avail_ini_pc = np.genfromtxt('data/coords_pc.csv', delimiter=',', dtype=str)
avail_ini_cs = np.genfromtxt('data/coords_cs.csv', delimiter=',', dtype=str)

df_initial = pd.read_csv('data/dataACRtime_GPSCSPCpostime_v7.csv', encoding='latin-1', index_col=0)
df_initial[col_time_em_call] = pd.to_datetime(df_initial[col_time_em_call])
df_initial = df_initial.loc[df_initial[col_BLS_time] >= 0]
df_initial = df_initial.loc[df_initial[col_BLS_time] <= 25 * 60]

df_initial = df_initial.head(100)


def update_avail(time_dec, avail, unavail):
    """
    Update of the available fleet of drones after each launch.

    :param time_dec: (dt.datetime) Datetime when the intervention started.
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
    For all intervention selects the closest available drone to send.
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


def select_interv(all_interventions, condition, column, rate):
    """Select randomly some interventions.

    :param all_interventions: a DataFrame containing interventions. This will be modified.
    :param condition: a boolean array, the same size of df to restrict the rows that can be
        affected: True for those that can be selected, False if not.
    :param column: (str) The name of the column of df to null if not selected.
    :param rate (float) The rate (between 0 and 1) of rows that should be kept.
    """
    selected = np.random.rand(len(all_interventions)) > rate
    selected_final = condition & selected
    all_interventions.loc[selected_final, column] = 0
    return all_interventions, selected_final


def _compute_drone_time(
        seq_start,
        drone_input,
        input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
        input_jour_, detec_rate_home, no_witness_rate, detec_rate_vp, unavail_delta, lang):

    """
    Computes drone simulated flights.

    :param drone_input: (str) drones initial locations
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

    print(seq_start)

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

    avail_ini_ = drones.STARTING_POINTS[drone_input]

    res_col_a = 'col_res'
    res_col_b = 'apport_drone'
    df_res = copy.deepcopy(df_initial)

    # Apport drone: si négatif, temps gagné grâce au drone. Sinon, temps gagné grâce au VSAV.

    no_drone = dict()
    no_drone['night'] = np.full((len(df_res),), False)

    df_res[col_drone_delay] = np.nan
    if input_jour:
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

    # per_drone = 100 * n_drone / n_tot
    #     # per_bls = 100 * n_bls / n_tot
    #     # per_nodrone = 100 * n_nodrone / n_tot

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
    dfi.loc[dfi['wins'] == 'N', 'col_bar'] = 'rgba(204,204,204,1)'

    dfi[res_col_b] = - dfi[res_col_b]
    ynew = dfi.sort_values(res_col_b)
    list_col = list(ynew['col_bar'])
    list_text = list(ynew['text'])

    # trace1 = go.Bar(
    #     x=[0, 1, 2],
    #     text=['Faster drone', 'BLS team faster', 'No drone sent'],
    #     y=[per_drone, per_bls, per_nodrone],
    #     textposition='auto',
    #     name='Test'
    # )

    # flight restriction reasons
    n_pub_place = in_a_public_place.sum()

    n_no_detec = no_drone['no detection'].sum()
    # n_no_detec_night = np.logical_and(no_drone['no detection'],
    # no_drone['night']).sum()
    # n_no_detec_wit = np.logical_and(no_drone['no detection'],
    # no_drone['not enough witnesses']).sum()
    # n_no_detec_both = np.logical_and(np.logical_and(no_drone['no detection'],
    # no_drone['night']),
    #                                  no_drone['not enough witnesses']).sum()

    no_drone['detection'] = np.logical_not(no_drone['no detection'])
    n_detec_night = np.logical_and(no_drone['detection'], no_drone['night']).sum()
    n_detec_wit = np.logical_and(no_drone['detection'], no_drone['not enough witnesses']).sum()
    n_detec_both = np.logical_and(np.logical_and(no_drone['detection'], no_drone['night']),
                                  no_drone['not enough witnesses']).sum()

    y_waterf = np.array([n_pub_place, (n_tot - n_pub_place), n_tot,
                         - n_no_detec, - n_detec_wit, -(n_detec_night - n_detec_both),
                         (n_drone + n_bls), -n_bls, n_drone])
    text_waterf = np.around(y_waterf * 100 / n_tot, 0).astype('int')
    text_waterf = np.core.defchararray.add(text_waterf.astype('str'),
                                           np.array(['%'] * len(text_waterf)))

    # graph: only when a drone is sent: res_col_a > 0
    df_density = copy.deepcopy(dfi)
    df_density = df_density.loc[df_density[res_col_a] > 0]

    trace3 = go.Histogram(x=df_density[col_BLS_time],
                          name=_('BLS team'))
    trace4 = go.Histogram(x=df_density[res_col_a], name=_('Drone'))

    trace5 = go.Bar(
        x=[i for i in range(0, len(dfi))],
        y=ynew[res_col_b],
        name='',
        marker=dict(color=list_col),
        text=list_text,
        hovertemplate='%{text} seconds',  # %{y} seconds',
    )

    # indicator_graphic_1 = {
    #     'data': [trace1],
    #     'layout': go.Layout(
    #         xaxis={
    #             'title': _('Intervention distribution'),
    #             'type': 'linear',
    #             'showticklabels': False,
    #         },
    #         yaxis={
    #             'title': _('Percentage of interventions'),
    #             'type': 'linear',
    #         },
    #         # margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
    #         hovermode='closest',
    #     ),
    #
    # }

    fsize = 100 / n_tot
    flows = [
        dict(
            fill='red',
            size=fsize * n_no_detec,
            text=_('Not detected') + f' {round(fsize * n_no_detec)}%',
        ),
        dict(
            fill='blue',
            size=fsize * n_no_detec,
            text=_('Not enough witnesses') + f' {round(fsize * n_detec_wit)}%',
        ),
        dict(
            fill='orange',
            size=fsize * n_bls,
            text=_('BLS team faster than drone') + f' {round(fsize * n_bls)}%',
        ),
        dict(
            fill='green',
            size=fsize * n_drone,
            text=_('Drone faster') + f' {round(fsize * n_drone)}%',
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
                'title': _('Number of interventions'),
                'type': 'linear',
                'showticklabels': False,
            },
            width=500,
            height=400,
            margin={'l': 30, 'b': 100, 't': 50, 'r': 30},
            hovermode='closest',
            autosize=True,
        ),
    }

    indicator_graphic_4 = {
        'data': [trace5],
        'layout': {
            'xaxis': {
                'title': {'text': u'Interventions', 'standoff': 100},
                'type': 'linear',
                'showgrid': False,
                'showticklabels': False,
            },
            'yaxis': {
                'title': _("Time difference drone - BLS team (in seconds)"),
                'type': 'linear',
                'showticklabels': False,
            },
            'width': 500,
            'height': 400,
            'margin': {'l': 30, 'b': 100, 't': 50, 'r': 30},
            'hovermode': 'closest',
            'autosize': True
        }
    }

    return flows, indicator_graphic_3, indicator_graphic_4, flows, \
        indicator_graphic_3, indicator_graphic_4


@app.callback(
    [Output('flows-graphic', 'flows'),
     Output('indicator-graphic3', 'figure'),
     Output('indicator-graphic4', 'figure'),
     Output('flows-graphicu', 'flows'),
     Output('indicator-graphic3u', 'figure'),
     Output('indicator-graphic4u', 'figure')],
    [Input('seq_start', 'n_clicks')],
    [State('input_drone', 'value'),
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
        seq_start,
        drone_input,
        input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
        input_jour_, detec_rate_home, no_witness_rate, detec_rate_vp, unavail_delta, lang):

    return _compute_drone_time(
        seq_start,
        drone_input,
        input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
        input_jour_, detec_rate_home, no_witness_rate, detec_rate_vp, unavail_delta, lang)


@app.callback(
    [Output('flows-graphic_b', 'flows'),
     Output('indicator-graphic3_b', 'figure'),
     Output('indicator-graphic4_b', 'figure'),
     Output('flows-graphicu_b', 'flows'),
     Output('indicator-graphic3u_b', 'figure'),
     Output('indicator-graphic4u_b', 'figure')],
    [Input('seq_start_b', 'n_clicks')],
    [State('input_drone_b', 'value'),
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
        seq_start,
        drone_input,
        input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
        input_jour_, detec_rate_home, no_witness_rate, detec_rate_vp, unavail_delta, lang):

    return _compute_drone_time(
        seq_start,
        drone_input,
        input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
        input_jour_, detec_rate_home, no_witness_rate, detec_rate_vp, unavail_delta, lang)
