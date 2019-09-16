import copy
import datetime as dt
import math

from dash.dependencies import Input, Output
import geopy.distance
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from sklearn.neighbors import KernelDensity

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
                dist = geopy.distance.vincenty(coord_drone, coord_a).km
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


def select_interv(df_, df_sub, col_, rate_):
    n = int(len(df_sub) * rate_)
    df_.loc[np.random.choice(df_sub.index, n, replace=False), col_] = 0
    return df_


def _compute_drone_time(
        drone_input,
        input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
        input_jour_, detec_rate, no_witness_rate, detec_VP, unavail_delta):

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

    :return: graphs for Dash visualisation
    """
    # drone_input = 'PC le plus proche'
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
    df_ = copy.deepcopy(df_initial)

    df_res = copy.deepcopy(df_)

    # Apport drone: si négatif, temps gagné grâce au drone. Sinon, temps gagné grâce au VSAV.
    df_res[col_drone_delay] = np.nan
    if input_jour:
        index_nuit = df_res[df_res[col_indic_day] == 0].index
        df_res.loc[index_nuit, col_drone_delay] = 0

    # taux de détection des ACR au téléphone voie publique et lieu public
    df_resb = df_res.loc[df_res[col_indic_home] == 0]
    df_res = select_interv(df_res, df_resb, col_drone_delay, (1 - detec_rate * detec_VP))

    # taux de détection des ACR au téléphone lieu privé
    df_resa = df_res.loc[df_res[col_indic_home] == 1]
    df_res = select_interv(df_res, df_resa, col_drone_delay, (1 - detec_rate))

    # taux de témoin seul en lieu privé
    df_res = select_interv(df_res, df_resa, col_drone_delay, no_witness_rate)

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
    dfii = copy.deepcopy(dfi)

    # 1st graph: only when a drone is sent: res_col_a > 0
    df_density = copy.deepcopy(dfi)
    df_density = df_density.loc[df_density[res_col_a] > 0]

    df_drone = dfii.loc[dfii[res_col_b] < 0]

    n_drone = len(df_drone)
    per_drone = np.around(n_drone / n_tot, 2)

    X = df_density[col_BLS_time][:, np.newaxis]
    kde = KernelDensity(kernel='gaussian', bandwidth=2).fit(X)
    X_plot = np.linspace(0, 20 * 60, 20 * 4)[:, np.newaxis]
    log_dens = kde.score_samples(X_plot)
    trace3 = go.Scatter(
        x=X_plot[:, 0], y=np.exp(log_dens),
        mode='lines',
        # line='blue',
        name="VSAV",
    )

    X2 = df_density[res_col_a][:, np.newaxis]
    kde2 = KernelDensity(kernel='gaussian', bandwidth=2).fit(X2)
    X_plot2 = np.linspace(0, 20 * 60, 20 * 4)[:, np.newaxis]
    log_dens = kde2.score_samples(X_plot2)
    trace4 = go.Scatter(
        x=X_plot[:, 0], y=np.exp(log_dens),
        mode='lines',
        # line='red',
        name="Drone",
    )

    # trace3 = go.Figure(data=[go.Histogram(x=df_density[col_BLS_time])])
    # trace4 = go.Figure(data=[go.Histogram(x=df_density[res_col_a])])

    dfi['col_bar'] = ['rgba(222,45,38,0.8)'] * len(dfi)
    dfi.loc[dfi[res_col_a] == 0, 'col_bar'] = 'rgba(204,204,204,1)'
    dfi[res_col_b] = - dfi[res_col_b]
    ynew = dfi.sort_values(res_col_b)
    list_col = list(ynew['col_bar'])

    trace5 = go.Bar(
        x=[i for i in range(0, len(dfi))],
        y=ynew[res_col_b], name=u'Temps gagné avec le drone',
        marker=dict(color=list_col),
    )

    stats = per_drone

    indicator_graphic_2 = {
        'data': [trace3, trace4],
        'layout': go.Layout(
            xaxis={
                'title': u'Temps de présentation quand le drone est envoyé',
                'type': 'linear',
            },
            yaxis={
                'title': u"Nombre d'interventions",
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
                'title': u"Différence de temps",
                'type': 'linear',
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest',
        )}

    return stats, indicator_graphic_2, indicator_graphic_3


@app.callback(
    [Output('stats', 'children'),
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
     Input('unavail_delta', 'value')])
def drone_time(
        drone_input,
        input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
        input_jour_, detec_rate, no_witness_rate, detec_VP, unavail_delta):

    return _compute_drone_time(
        drone_input,
        input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
        input_jour_, detec_rate, no_witness_rate, detec_VP, unavail_delta)


@app.callback(
    [Output('stats_b', 'children'),
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
     Input('unavail_delta_b', 'value')])
def drone_time_b(
        drone_input,
        input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
        input_jour_, detec_rate, no_witness_rate, detec_VP, unavail_delta):

    return _compute_drone_time(
        drone_input,
        input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
        input_jour_, detec_rate, no_witness_rate, detec_VP, unavail_delta)
