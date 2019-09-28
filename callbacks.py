import copy
import datetime as dt
import gettext
import math

from dash.dependencies import Input, Output
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

col_drone_delay = 'col_res'

avail_ini_pc = np.genfromtxt('data/coords_pc.csv', delimiter=',', dtype=str)
avail_ini_cs = np.genfromtxt('data/coords_cs.csv', delimiter=',', dtype=str)

df_initial = pd.read_csv('data/dataACRtime_GPSCSPCpostime_v7.csv', encoding='latin-1', index_col=0)
df_initial[col_time_em_call] = pd.to_datetime(df_initial[col_time_em_call])
df_initial = df_initial.loc[df_initial[col_BLS_time] >= 0]
df_initial = df_initial.loc[df_initial[col_BLS_time] <= 25 * 60]


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
    all_interventions.loc[condition & selected, column] = 0


def _compute_drone_time(
        drone_input,
        input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
        input_jour_, detec_rate, no_witness_rate, detec_VP, unavail_delta, lang):

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
    :param detec_rate: (str) rate of OHCA detection by 18/112 operators ([0,1])
    :param no_witness_rate: (str) rate of OHCA at home, which only have one witness alone ([0,1])
    :param detec_VP: (str) odd ratio of OHCA in the streets vs OHCA at home or in a public place
        detection by 18/112 operators ([0,1])
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
    # detec_rate = '1'
    # no_witness_rate = '0.56'
    # detec_VP = '0.15'
    # unavail_delta = '6'
    # lang = 'fr'

    if lang:
        t11n = gettext.translation('messages', localedir='locales', languages=[lang], fallback=True)
        t11n.install()

    dep_delay = np.float(dep_delay) + np.float(detec_delay) + (np.float(alt) / np.float(vert_acc))
    arr_delay = np.float(arr_delay) + (np.float(alt) / np.float(vert_acc))
    input_acc = np.float(input_acc)
    detec_rate = np.float(detec_rate)
    no_witness_rate = np.float(no_witness_rate)
    detec_VP = np.float(detec_VP)
    unavail_delta = np.float(unavail_delta)

    input_jour = input_jour_ == 'Oui' or input_jour_ == 'Yes'
    input_speed = np.float(input_speed)

    avail_ini_ = drones.STARTING_POINTS[drone_input]

    res_col_a = 'col_res'
    res_col_b = 'apport_drone'
    df_res = copy.deepcopy(df_initial)

    # Apport drone: si négatif, temps gagné grâce au drone. Sinon, temps gagné grâce au VSAV.

    no_drone = dict()
    no_drone['night'] = []

    df_res[col_drone_delay] = np.nan
    if input_jour:
        index_nuit = df_res[col_indic_day] == 0
        df_res.loc[index_nuit, col_drone_delay] = 0
        no_drone['night'] = index_nuit

    in_a_public_place = df_res[col_indic_home] == 0
    # detection rate of OHCA in a public place
    select_interv(df_res, in_a_public_place, col_drone_delay, detec_rate * detec_VP)

    # detection rate of OHCA in a private place (at home)
    select_interv(df_res, ~in_a_public_place, col_drone_delay, detec_rate)

    # update no drone reasons : lack of detection
    # no_drone['no detection'] = np.append(index_detec_vp ,index_detec_priv)

    # rate of OHCA witnesses home alone
    select_interv(df_res, ~in_a_public_place, col_drone_delay, 1 - no_witness_rate)

    # update no drone reasons : not enough witnesses
    # no_drone['not enough witnesses'] = index_witness

    df_ic = df_res.loc[df_res[col_drone_delay] != 0]
    distance_field = 'Distance'
    df_ic[distance_field] = drone_unavail(df_ic, unavail_delta, avail_ini_)

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

    n_tot = len(dfi)
    n_nodrone = len(dfi.loc[dfi[res_col_a] == 0])
    n_drone = len(dfi.loc[dfi[res_col_b] < 0])
    n_bls = len(dfi.loc[dfi[res_col_b] > 0]) - n_nodrone

    per_drone = 100 * n_drone / n_tot
    per_bls = 100 * n_bls / n_tot
    per_nodrone = 100 * n_nodrone / n_tot

    # 1st graph: only when a drone is sent: res_col_a > 0
    df_density = copy.deepcopy(dfi)
    df_density = df_density.loc[df_density[res_col_a] > 0]

    trace3 = go.Histogram(x=df_density[col_BLS_time], name=_('BLS team'))
    trace4 = go.Histogram(x=df_density[res_col_a], name=_('Drone'))

    dfi['col_bar'] = ['rgba(222,45,38,0.8)'] * len(dfi)
    dfi.loc[dfi[res_col_a] == 0, 'col_bar'] = 'rgba(204,204,204,1)'
    dfi[res_col_b] = - dfi[res_col_b]
    ynew = dfi.sort_values(res_col_b)
    list_col = list(ynew['col_bar'])

    trace1 = go.Bar(
        x=[0, 1, 2],
        text=['Faster drone', 'BLS team faster', 'No drone sent'],
        y=[per_drone, per_bls, per_nodrone],
        textposition='auto',
        name=_('Test')
    )

    trace5 = go.Bar(
        x=[i for i in range(0, len(dfi))],
        y=ynew[res_col_b], name=_('Time saved with a drone'),
        marker=dict(color=list_col),
    )

    indicator_graphic_1 = {
        'data': [trace1],
        'layout': go.Layout(
            xaxis={
                'title': _('Intervention distribution'),
                'type': 'linear',
                'showticklabels': False,
            },
            yaxis={
                'title': _('Percentage of interventions'),
                'type': 'linear',
            },
            # margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest',
        ),

    }

    indicator_graphic_2 = {
        'data': [trace3, trace4],
        'layout': go.Layout(
            xaxis={
                'title': _('Time to arrival when a drone is sent'),
                'type': 'linear',
            },
            yaxis={
                'title': _('Number of interventions'),
                'type': 'linear',
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest',
        ),
    }

    indicator_graphic_3 = {
        'data': [trace5],
        'layout': go.Layout(
            xaxis={
                'title': u'Interventions',  # , quand le drone se présente avant le VSAV',
                'type': 'linear',
            },
            yaxis={
                'title': _("Time difference"),
                'type': 'linear',
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest',
        )}

    return indicator_graphic_1, indicator_graphic_2, indicator_graphic_3


@app.callback(
    [Output('indicator-graphic1', 'figure'),
     Output('indicator-graphic2', 'figure'),
     Output('indicator-graphic3', 'figure')],
    [Input('input_drone', 'value'),
     Input('speed', 'value'),
     Input('acc', 'value'),
     Input('vert-acc', 'value'),
     Input('alt', 'value'),
     Input('dep_delay', 'value'),
     Input('arr_delay', 'value'),
     Input('detec_delay', 'value'),
     Input('day', 'value'),
     Input('detec', 'value'),
     Input('wit_detec', 'value'),
     Input('detec_VP', 'value'),
     Input('unavail_delta', 'value'),
     Input('lang', 'value')])
def drone_time(
        drone_input,
        input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
        input_jour_, detec_rate, no_witness_rate, detec_VP, unavail_delta, lang):

    return _compute_drone_time(
        drone_input,
        input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
        input_jour_, detec_rate, no_witness_rate, detec_VP, unavail_delta, lang)


@app.callback(
    [Output('indicator-graphic1_b', 'figure'),
     Output('indicator-graphic2_b', 'figure'),
     Output('indicator-graphic3_b', 'figure')],
    [Input('input_drone_b', 'value'),
     Input('speed_b', 'value'),
     Input('acc_b', 'value'),
     Input('vert-acc_b', 'value'),
     Input('alt_b', 'value'),
     Input('dep_delay_b', 'value'),
     Input('arr_delay_b', 'value'),
     Input('detec_delay_b', 'value'),
     Input('day_b', 'value'),
     Input('detec_b', 'value'),
     Input('wit_detec_b', 'value'),
     Input('detec_VP_b', 'value'),
     Input('unavail_delta_b', 'value'),
     Input('lang', 'value')])
def drone_time_b(
        drone_input,
        input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
        input_jour_, detec_rate, no_witness_rate, detec_VP, unavail_delta, lang):

    return _compute_drone_time(
        drone_input,
        input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
        input_jour_, detec_rate, no_witness_rate, detec_VP, unavail_delta, lang)
