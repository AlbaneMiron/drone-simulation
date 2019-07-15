from dash.dependencies import Input, Output

from app import app

import geopy.distance
import datetime as dt
import pandas as pd
import numpy as np
import copy
import math
import plotly.graph_objs as go
from sklearn.neighbors import KernelDensity


col_time_em_call = 'DT_då_crochå_'  # datetime of the beginning of the emergency call
col_BLS_time = 'DeltaPresentation'  # in seconds, BLS team delay
col_drone_distance = 'Distance_'  # in km, horizontal distance flown by the drone
col_wind_speed = 'vitesse effective vent_'  # in m/s, wind speed in the direction
col_indic_day = 'jour_aeronautique'  # indicator: 1 if the intervention is during the day, 0 during the night
col_indic_streets = 'Voie publique'  # indicator : 1 if the intervention is in the streets, 0 otherwise
col_indic_pubplace = 'Lieu public' # indicator : 1 if the intervention is in a public place (excluding streets), 0 otherwise
col_indic_home = 'Domicile'  # indicator : 1 if the intervention is at home, 0 otherwise
col_lat_inter = 'new_lat'#'Latitude_WGS84.1'
col_lon_inter = 'new_lon'#'Longitude_WGS84.1'

col_drone_delay = 'col_res'
#
# # parameters
# drone_pos = 'PC le plus proche'  # where does the drone starts from
# input_wind_ = True  # whether the wind should be taken into consideration
# input_speed_ = 80  # in km/h, maximum horizontal drone speed
# input_acc_ = 9  # in s, number of seconds of horizontal acceleration to reach full speed
# vert_acc_ = 9  # in m/s^2, vertical acceleration
# alt_ = 100  # in m, cruise altitude of the drone
# dep_delay_ = 15  # in s, delay between OHCA detection and drone departure
# arr_delay_ = 15  # in s, delay between drone arrival and AED usage
# detec_delay_ = 104  # in s, delay between detection of unconsciousness (departure of the BLS team) and OHCA
# # detection (decision to launch a drone)
# input_jour_ = True  # whether the drone only flies during the day or not
# detec_rate_ = 0.70  # between 0 and 1, share of OHCA detected by the dispatch center
# no_witness_rate_ = 0.58  # share of bystander alone for OHCA at home
# detec_VP_ = 0.15  # odd ratio for detecting a OHCA in the streets compared to in a public place or at home
# unavail_delta_ = 6  # delta time of drone unavailability after being launched


avail_ini_pc = np.load('data/list_pc.npy', allow_pickle=True)
avail_ini_cs = np.load('data/list_cs.npy', allow_pickle=True)

df = pd.read_csv('data/dataACRtime_GPSCSPCpostime_v7.csv', encoding='latin-1', index_col=0)
df[col_time_em_call] = pd.to_datetime(df[col_time_em_call])


def update_avail(time_dec, avail, unavail):
    """
    Update of the available fleet of drones after each launch.
    :param time_dec: Datetime when the intervention started.
    :param avail: List of available drones (name, GPS location)
    :param unavail: List of unavailable drones (name, GPS location and datetime until when they are unavailable)
    :return: Updated list of available and unavailable drones.
    """
    drop_drone = []
    for i in range(0, unavail.shape[0]):
        if unavail[i][3] < time_dec:
            avail = np.append(avail, [[unavail[i][0], unavail[i][1], unavail[i][2]]], axis=0)
            drop_drone.append(i)

    res_unavail = np.delete(unavail, drop_drone, axis=0)
    return avail, res_unavail


def drone_unavail(df, duree, avail_ini, loc):
    """
    For all intervention selects the closest available drone to send.
    :param df:
    :param duree:
    :param avail_ini:
    :param loc:
    :return:
    """

    avail = copy.deepcopy(avail_ini)
    # init
    unavail = np.array([['NULL', 0.0, 0.0, dt.datetime(2017, 1, 1, 0, 0, 0)]])
    list_dist = []

    for i, r in df.iterrows():
        time_dec = r[col_time_em_call]
        avail, unavail = update_avail(time_dec, avail, unavail)
        latA = r[col_lat_inter]
        lonA = r[col_lon_inter]
        coordA = (latA, lonA)

        dist_tot = []
        for l in avail:
            coordD = (l[1], l[2])
            try:
                dist = geopy.distance.vincenty(coordD, coordA).km
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
            print('drone location empty')

    df['Distance_' + loc] = list_dist

    return df


@app.callback(
    [Output('indicator-graphic', 'figure'),
     Output('stats', 'children'),
     Output('indicator-graphic2', 'figure'),
     Output('indicator-graphic3', 'figure')],
    [Input('input_drone', 'value'),
     Input('wind', 'value'),
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
def drone_time(drone_input, input_wind, input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay, input_jour, detec_rate, no_witness_rate, detec_VP, unavail_delta):

    """
    Computes all drone presentation durations of a dataframe and puts them in a new column named
    new_col.
    :param df_: dataframe
    :param latD: column with departure latitude (str)
    :param lonD: column with departure longitude (str)
    :param latA: column with arrival latitude (str)
    :param lonA: column with arrival longitude (str)
    :param dep_delay: departure delay (float, default=0)
    :param arr_delay: arrival delay (float, default=0)
    :param speed: drone speed (float, default=10)
    :param acc_time: time drone acceleration (float, default=5.0s)
    :return: dataframe
    """

    dep_delay = np.float(dep_delay) + np.float(detec_delay) + (np.float(alt) / np.float(vert_acc))
    arr_delay = np.float(arr_delay) + (np.float(alt) / np.float(vert_acc))
    input_acc = np.float(input_acc)
    detec_rate = np.float(detec_rate)
    no_witness_rate = np.float(no_witness_rate)
    detec_VP = np.float(detec_VP)
    unavail_delta = np.float(unavail_delta)

    # TODO : pb de noms de variables !
    if input_jour == 'Oui':
        input_jour = True
    else:
        input_jour = False

    input_speed = np.float(input_speed)
    if input_wind == 'Oui':
        input_wind = True
    else:
        input_wind = False

    if drone_input == 'PC le plus proche':
        drone_departure = 'PCPP'
        drone_departure_bis = 'PC'
        avail_ini_ = avail_ini_pc
    else:
        drone_departure = 'CSPP'
        drone_departure_bis = 'CS'
        avail_ini_ = avail_ini_cs

    new_col ='col_res'
    df_ = df

    df_0 = df_.loc[df_[col_BLS_time] >= 0]
    df_ = df_0.loc[df_0[col_BLS_time] <= 25 * 60]

    # latA = 'Latitude_WGS84.1'
    # lonA = 'Longitude_WGS84.1'
    # latD = 'Latitude_' + drone_departure
    # lonD = 'Longitude_' + drone_departure

    col_dist = 'Distance_' + drone_departure_bis
    speed_col = 'vitesse effective vent_' + drone_departure

    df_res = copy.deepcopy(df_)

    # Apport drone: si négatif, temps gagné grâce au drone. Sinon, temps gagné grâce au VSAV.

    # écrire les exclusions ici, pas après
    df_res[col_drone_delay] = np.nan
    if input_jour:
        df_res[col_drone_delay] = df_res[col_drone_delay] * df_res[col_indic_day]

    # taux de détection des ACR au téléphone voie publique et lieu public  # TODO: ajouter lieu public - lieu public disparait
    df_resB = df_res.loc[df_res[col_indic_home] == 0]
    list_VP = list(df_resB.index)
    k_select = len(df_resB) - int(detec_rate * detec_VP * len(df_resB))
    list_select = np.random.choice(list_VP, k_select)
    df_res.loc[list_select, col_drone_delay] = 0

    # taux de détection des ACR au téléphone lieu privé
    df_resA = df_res.loc[df_res[col_indic_home] == 1]
    list_lieu = list(df_resA.index)
    k_select = len(df_resA) - int(detec_rate * len(df_resA))
    list_select = np.random.choice(list_lieu, k_select)
    df_res.loc[list_select, col_drone_delay] = 0

    # taux de témoin seul en lieu privé
    df_res2 = df_res.loc[df_res[col_indic_home] == 1]
    list_priv = list(df_res2.index)
    k_select = int(no_witness_rate * len(df_res2))
    list_select = np.random.choice(list_priv, k_select)
    df_res.loc[list_select, col_drone_delay] = 0

    df_ic = df_res.loc[df_res[col_drone_delay] != 0]
    df_ic = drone_unavail(df_ic, unavail_delta, avail_ini_, drone_departure_bis)

    for i, r in df_ic.iterrows():
        if input_wind:
            eff_speed = input_speed # + r[speed_col] # TODO: remove
        else:
            eff_speed = input_speed
        acc_dist = 2 * eff_speed * input_acc / 3600  # distance covered during acceleration and brake
        acc = eff_speed / (input_acc * 3600)

        dist = r[col_dist]

        lin_dist = dist - acc_dist
        if lin_dist >= 0:
            lin_time = (dist / eff_speed) * 3600
            res_time = lin_time + dep_delay + arr_delay + 2 * input_acc
        else:
            res_time = dep_delay + arr_delay + 2 * math.sqrt(dist / acc)

        df_res.loc[i, col_drone_delay] = np.round(res_time)


    df_res['apport_drone'] = df_res[new_col] - df_res['DeltaPresentation']  # TODO: 'DeltaPresentation' dataframe specific

    df_res.loc[df_res[new_col] == 0, 'apport_drone'] = df_res.loc[df_res[new_col] == 0, 'DeltaPresentation']
    dfi = df_res.dropna(axis=0, how='all', thresh=None, subset=['apport_drone'], inplace=False)

    # TODO: to remove in the final version
    dfi = dfi.head(500)

    n_tot = len(dfi)
    dfii = copy.deepcopy(dfi)

    # 1st graph: only when a drone is sent: 'col_res' > 0
    df_density = copy.deepcopy(dfi)
    df_density = df_density.loc[df_density['col_res'] > 0]

    df_drone = dfii.loc[dfii['apport_drone'] < 0]
    ind_VSAV = [n for n in list(dfi.index) if n not in list(df_drone.index)]
    df_VSAV = dfi.loc[ind_VSAV]

    n_drone = len(df_drone)
    per_drone = n_drone/n_tot

    x1 = [i for i in range(0, int(max(dfi['DeltaPresentation'])))]
    y1 = x1

    trace1 = go.Scatter(
        x=x1,
        y=y1,
        line=dict(color='rgb(0,100,80)'),
        mode='lines',
        text='A gauche, VSAV plus rapide. A droite drone plus rapide',
        name=u"Ligne d'égalité des temps de présentation",
    )

    trace2 = go.Scatter(
            x=dfi['DeltaPresentation'],
            y=dfi['col_res'],
            text=u'Temps présentation VSAV vs temps drone',
            name=u"Intervention",
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )

    X = df_density['DeltaPresentation'][:, np.newaxis]
    kde = KernelDensity(kernel='gaussian', bandwidth=2).fit(X)
    X_plot = np.linspace(0, 20*60, 20*4)[:, np.newaxis]
    log_dens = kde.score_samples(X_plot)
    trace3 = go.Scatter(x=X_plot[:, 0], y=np.exp(log_dens),
                        mode='lines',
                        #line='blue',
                        name="VSAV")

    X2 = df_density['col_res'][:, np.newaxis]
    kde2 = KernelDensity(kernel='gaussian', bandwidth=2).fit(X2)
    X_plot2 = np.linspace(0, 20*60, 20*4)[:, np.newaxis]
    log_dens = kde2.score_samples(X_plot2)
    trace4 = go.Scatter(x=X_plot[:, 0], y=np.exp(log_dens),
                        mode='lines',
                        #line='red',
                        name="Drone")

    dfi['col_bar'] = ['rgba(222,45,38,0.8)']*len(dfi)
    dfi.loc[dfi['col_res'] == 0, 'col_bar'] = 'rgba(204,204,204,1)'
    dfi['apport_drone'] = - dfi['apport_drone']
    ynew = dfi.sort_values('apport_drone')
    list_col = list(ynew['col_bar'])

    trace5 = go.Bar(x=[i for i in range(0, len(dfi))],
        y=ynew['apport_drone'], name=u'Temps gagné avec le drone',
        marker=dict(color=list_col),
    )

    return {
        'data': [trace2, trace1],
        'layout': go.Layout(
            xaxis={
                'title': 'Temps VSAV',
                'type': 'linear'
            },
            yaxis={
                'title': 'Temps drone ' + str(input_speed) + 'km/h, vent: ' + str(input_wind) + ' ' + str(drone_input),
                'type': 'linear'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }, per_drone, {'data': [trace3, trace4],
        'layout': go.Layout(
            xaxis={
                'title': u'Temps de présentation quand le drone est envoyé',
                'type': 'linear'
            },
            yaxis={
                'title': u"Nombre d'interventions",
                'type': 'linear'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )}, {'data': [trace5],
        'layout': go.Layout(
            xaxis={
                'title': u'Interventions',#, quand le drone se présente avant le VSAV',
                'type': 'linear'
            },
            yaxis={
                'title': u"Différence de temps",
                'type': 'linear'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )}


@app.callback(
    [Output('indicator-graphicb', 'figure'),
     Output('statsb', 'children'),
     Output('indicator-graphic2b', 'figure'),
     Output('indicator-graphic3b', 'figure')],
    [Input('input_drone2', 'value'),
     Input('wind2', 'value'),
     Input('speed2', 'value'),
     Input('acc2', 'value'),
     Input('vert-acc2', 'value'),
     Input('alt2', 'value'),
     Input('dep_delay2', 'value'),
     Input('arr_delay2', 'value'),
     Input('detec_delay2', 'value'),
     Input('day2', 'value'),
     Input('detec2', 'value'),
     Input('wit_detec2', 'value'),
     Input('detec_VP2', 'value'),
     Input('unavail_delta2', 'value')])
def drone_time(drone_input, input_wind, input_speed, input_acc, vert_acc, alt, dep_delay, arr_delay, detec_delay,
               input_jour, detec_rate, no_witness_rate, detec_VP, unavail_delta):

    dep_delay = np.float(dep_delay) + np.float(detec_delay) + (np.float(alt) / np.float(vert_acc))
    arr_delay = np.float(arr_delay) + (np.float(alt) / np.float(vert_acc))
    input_acc = np.float(input_acc)
    detec_rate = np.float(detec_rate)
    no_witness_rate = np.float(no_witness_rate)
    detec_VP = np.float(detec_VP)
    unavail_delta = np.float(unavail_delta)

    # TODO : pb de noms de variables !
    if input_jour == 'Oui':
        input_jour = True
    else:
        input_jour = False

    input_speed = np.float(input_speed)
    if input_wind == 'Oui':
        input_wind = True
    else:
        input_wind = False

    if drone_input == 'PC le plus proche':
        drone_departure = 'PCPP'
        drone_departure_bis = 'PC'
        avail_ini_ = avail_ini_pc
    else:
        drone_departure = 'CSPP'
        drone_departure_bis = 'CS'
        avail_ini_ = avail_ini_cs

    new_col ='col_res'
    df_ = df

    # latA = 'Latitude_WGS84.1'
    # lonA = 'Longitude_WGS84.1'
    # latD = 'Latitude_' + drone_departure
    # lonD = 'Longitude_' + drone_departure

    col_dist = 'Distance_' + drone_departure_bis
    speed_col = 'vitesse effective vent_' + drone_departure

    df_res = copy.deepcopy(df_)

    df_res[col_drone_delay] = np.nan
    if input_jour: # TODO
        df_res[col_drone_delay] = df_res[col_drone_delay] * df_res[col_indic_day]

    # taux de détection des ACR au téléphone voie publique et lieu public  # TODO: ajouter lieu public - lieu public disparait
    df_resB = df_res.loc[df_res[col_indic_home] == 0]
    list_VP = list(df_resB.index)
    k_select = len(df_resB) - int(detec_rate * detec_VP * len(df_resB))
    list_select = np.random.choice(list_VP, k_select)
    df_res.loc[list_select, col_drone_delay] = 0

    # taux de détection des ACR au téléphone lieu privé
    df_resA = df_res.loc[df_res[col_indic_home] == 1]
    list_lieu = list(df_resA.index)
    k_select = len(df_resA) - int(detec_rate * len(df_resA))
    list_select = np.random.choice(list_lieu, k_select)
    df_res.loc[list_select, col_drone_delay] = 0

    # taux de témoin seul en lieu privé
    df_res2 = df_res.loc[df_res[col_indic_home] == 1]
    list_priv = list(df_res2.index)
    k_select = int(no_witness_rate * len(df_res2))
    list_select = np.random.choice(list_priv, k_select)
    df_res.loc[list_select, col_drone_delay] = 0

    df_ic = df_res.loc[df_res[col_drone_delay] != 0]
    df_ic = drone_unavail(df_ic, unavail_delta, avail_ini_, drone_departure_bis)

    for i, r in df_ic.iterrows():
        if input_wind:
            eff_speed = input_speed # + r[speed_col] # TODO: remove
        else:
            eff_speed = input_speed
        acc_dist = 2 * eff_speed * input_acc / 3600  # distance covered during acceleration and brake
        acc = eff_speed / (input_acc * 3600)

        dist = r[col_dist]

        lin_dist = dist - acc_dist
        if lin_dist >= 0:
            lin_time = (dist / eff_speed) * 3600
            res_time = lin_time + dep_delay + arr_delay + 2 * input_acc
        else:
            res_time = dep_delay + arr_delay + 2 * math.sqrt(dist / acc)

        df_res.loc[i, col_drone_delay] = np.round(res_time)


    # Apport drone: si négatif, temps gagné grâce au drone. Sinon, temps gagné grâce au VSAV.
    df_res['apport_drone'] = df_res[new_col] - df_res['DeltaPresentation']  # TODO: 'DeltaPresentation' dataframe specific

    df_res.loc[df_res[new_col] == 0, 'apport_drone'] = df_res.loc[df_res[new_col] == 0, 'DeltaPresentation']
    dfi = df_res.dropna(axis=0, how='all', thresh=None, subset=['apport_drone'], inplace=False)
    

    # filtre présentation VSAV incohérente
    dfi = dfi.loc[dfi['DeltaPresentation'] >= 0]
    dfi = dfi.loc[dfi['DeltaPresentation'] <= 15 * 60]

    # TODO: to remove in the final version
    dfi = dfi.head(500)

    n_tot = len(dfi)
    dfii = copy.deepcopy(dfi)

    # 1st graph: only when a drone is sent: 'col_res' > 0
    df_density = copy.deepcopy(dfi)
    df_density = df_density.loc[df_density['col_res'] > 0]

    # dfii.loc[dfii['apport_drone'] > 0] = 0
    # dfii.loc[dfii['col_res'] == 0, 'apport_drone'] = 0
    df_drone = dfii.loc[dfii['apport_drone'] < 0]
    ind_VSAV = [n for n in list(dfi.index) if n not in list(df_drone.index)]
    df_VSAV = dfi.loc[ind_VSAV]

    n_drone = len(df_drone)
    per_drone = n_drone/n_tot

    x1 = [i for i in range(0, int(max(dfi['DeltaPresentation'])))]
    y1 = x1

    trace1 = go.Scatter(
        x=x1,
        y=y1,
        line=dict(color='rgb(0,100,80)'),
        mode='lines',
        text='A gauche, VSAV plus rapide. A droite drone plus rapide',
        name=u"Ligne d'égalité des temps de présentation",
    )

    trace2 = go.Scatter(
            x=dfi['DeltaPresentation'],
            y=dfi['col_res'],
            text=u'Temps présentation VSAV vs temps drone',
            name=u"Intervention",
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )

    X = df_density['DeltaPresentation'][:, np.newaxis]
    kde = KernelDensity(kernel='gaussian', bandwidth=2).fit(X)
    X_plot = np.linspace(0, 20*60, 20*4)[:, np.newaxis]
    log_dens = kde.score_samples(X_plot)
    trace3 = go.Scatter(x=X_plot[:, 0], y=np.exp(log_dens),
                        mode='lines',
                        #line='blue',
                        name="VSAV")

    X2 = df_density['col_res'][:, np.newaxis]
    kde2 = KernelDensity(kernel='gaussian', bandwidth=2).fit(X2)
    X_plot2 = np.linspace(0, 20*60, 20*4)[:, np.newaxis]
    log_dens = kde2.score_samples(X_plot2)
    trace4 = go.Scatter(x=X_plot[:, 0], y=np.exp(log_dens),
                        mode='lines',
                        #line='red',
                        name="Drone")

    dfi['col_bar'] = ['rgba(222,45,38,0.8)']*len(dfi)
    dfi.loc[dfi['col_res'] == 0, 'col_bar'] = 'rgba(204,204,204,1)'
    dfi['apport_drone'] = - dfi['apport_drone']
    ynew = dfi.sort_values('apport_drone')
    list_col = list(ynew['col_bar'])

    trace5 = go.Bar(x=[i for i in range(0, len(dfi))],
        y=ynew['apport_drone'], name=u'Temps gagné avec le drone',
        marker=dict(color=list_col),
    )

    return {
        'data': [trace2, trace1],
        'layout': go.Layout(
            xaxis={
                'title': 'Temps VSAV',
                'type': 'linear'
            },
            yaxis={
                'title': 'Temps drone ' + str(input_speed) + 'km/h, vent: ' + str(input_wind) + ' ' + str(drone_input),
                'type': 'linear'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }, per_drone, {'data': [trace3, trace4],
        'layout': go.Layout(
            xaxis={
                'title': u'Temps de présentation quand le drone est envoyé',
                'type': 'linear'
            },
            yaxis={
                'title': u"Nombre d'interventions",
                'type': 'linear'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )}, {'data': [trace5],
        'layout': go.Layout(
            xaxis={
                'title': u'Interventions',#, quand le drone se présente avant le VSAV',
                'type': 'linear'
            },
            yaxis={
                'title': u"Différence de temps",
                'type': 'linear'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )}