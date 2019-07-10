from app import app

import geopy.distance
import pandas as pd
import numpy as np
import copy
import math
import plotly.graph_objs as go

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv('/Users/albane_95/Documents/Projet BSPP/code/data/dataACRtime_GPSCSPCpostime2.csv', encoding='latin-1', index_col=0)
positions = ['PC le plus proche', 'CS le plus proche']

# takes into account the time needed to reach maximal speed
# dep_delay : 15 sec + temps de montée : détermine altitude 100m dans la fiche projet à 9m/s
# arr_delay : 0 sec + temps de descente


layout = html.Div([
    html.Div([


        html.Div([

            html.Label('Vitesse maximale du drone (en km/h)'),
            dcc.Input(id='speed', value='80', type='text'),

            html.Label(u"Nombre de secondes d'accelération du drone :"),
            dcc.Input(id='acc', value='5', type='text'),

            html.Label(u"Vitesse accelération verticale (en m/s) :"),
            dcc.Input(id='vert-acc', value='9', type='text'),

        ], style={'width': '31%', 'display': 'inline-block'}),

        html.Div([

            html.Label(u"Altitude de croisière (en m) :"),
            dcc.Input(id='alt', value='100', type='text'),

            html.Label(u"Retard au départ et à l'arrivée (en s) :"),
            dcc.Input(id='delay', value='15', type='text'),

            html.Label(u"Taux de détection ACR à la prise d'appel (entre 0 et 1) :"),
            dcc.Input(id='detec', value='1', type='text'),

        ], style={'width': '31%', 'display': 'inline-block'}),

        html.Div([

            html.Label('Position initiale du drone'),
            dcc.Dropdown(
                id='input_drone',
                options=[{'label': i, 'value': i} for i in positions],
                value='PC le plus proche'
            ),

            html.Label('Prise en compte du vent'),
            dcc.RadioItems(
                id='wind',
                options=[{'label': i, 'value': i} for i in ['Oui', 'Non']],
                value='Oui',
                labelStyle={'display': 'inline-block'}
            ),

            html.Label('Vol uniquement durant jour aéronautique'),
            dcc.RadioItems(
                id='day',
                options=[{'label': i, 'value': i} for i in ['Oui', 'Non']],
                value='Non',
                labelStyle={'display': 'inline-block'}
            ),
        ], style={'width': '31%', 'display': 'inline-block'})
    ]),

    html.Div([
        html.Table([
                html.Tr([html.Td(['Taux de drones plus rapides, sur toutes les interventions : ']), html.Td(id='stats')]),
                # html.Tr([html.Td(['', html.Sup(3)]), html.Td(id='cube')]),
                # html.Tr([html.Td([2, html.Sup('x')]), html.Td(id='twos')]),
                # html.Tr([html.Td([3, html.Sup('x')]), html.Td(id='threes')]),
                # html.Tr([html.Td(['x', html.Sup('x')]), html.Td(id='x^x')]),
        ],
        style={'width': '100%', 'display': 'inline-block'}),
    ]),


    html.Div([
        html.Div([
            dcc.Graph(id='indicator-graphic2'),
        ],
            style={'width': '48%', 'display': 'inline-block'}),
    html.Div([
            dcc.Graph(id='indicator-graphic3'),
        ],
            style={'width': '48%', 'display': 'inline-block'}),
    ]),

    dcc.Graph(id='indicator-graphic'),

    # dcc.Slider(
    #     id='speed--slider',
    #     min=20,  # km/h
    #     max=150, #km/h
    #     value=80,
    #     #marks={str(year): str(year) for year in df['Year'].unique()},
    #     step=10
    #)
])

@app.callback(
    [Output('indicator-graphic', 'figure'), Output('stats', 'children'), Output('indicator-graphic2', 'figure'), Output('indicator-graphic3', 'figure')],
    [Input('input_drone', 'value'),
     Input('wind', 'value'),
     Input('speed', 'value'),
     Input('acc', 'value'),
     Input('vert-acc', 'value'),
     Input('alt', 'value'),
     Input('delay', 'value'),
     Input('day', 'value'),
     Input('detec', 'value')])
def drone_time(drone_input, input_wind, input_speed, input_acc, vert_acc, alt, delay, input_jour, detec_rate):
    dep_delay = np.float(delay) + (np.float(alt) / np.float(vert_acc))
    arr_delay = np.float(delay) + (np.float(alt) / np.float(vert_acc))
    acc_time = np.float(input_acc)
    detec_rate = np.float(detec_rate)

    jour_ae = False
    if input_jour == 'Oui':
        jour_ae = True

    speed = np.float(input_speed)
    vent = False
    if input_wind == 'Oui':
        vent = True

    if drone_input == 'PC le plus proche':
        drone_departure = 'PCPP'
    else:
        drone_departure = 'CSPP'

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

    new_col ='col_res'
    df_ = df

    latA = 'Latitude_WGS84.1'
    lonA = 'Longitude_WGS84.1'
    latD = 'Latitude_' + drone_departure
    lonD = 'Longitude_' + drone_departure
    speed_col = 'vitesse effective vent_' + drone_departure

    df_res = copy.deepcopy(df_)

    for i, r in df_.iterrows():
        if vent:
            eff_speed = speed + r[speed_col]  # TODO
        else:
            eff_speed = speed
        acc_dist = 2 * eff_speed * acc_time / 3600  # distance parcourue pendant l'acceleration et le ralentissement
        acc = eff_speed / (acc_time * 3600)

        coordD = (r[latD], r[lonD])
        coordA = (r[latA], r[lonA])
        try:
            dist = geopy.distance.vincenty(coordD, coordA).km
        except ValueError:
            dist = np.nan
        lin_dist = dist - acc_dist
        if lin_dist >= 0:
            lin_time = (dist / eff_speed) * 3600
            res_time = lin_time + dep_delay + arr_delay + 2 * acc_time
        else:
            res_time = dep_delay + arr_delay + 2 * math.sqrt(dist / acc)

        df_res.loc[i, new_col] = np.round(res_time)

    # jour aeronautique
    if jour_ae:
        df_res['col_res'] = df_res['col_res'] * df_res['jour_aeronautique']

    # taux de détection des ACR au téléphone
    detec_vec = [1] * int(detec_rate * len(df_res)) + [0] * (
            len(df_res) - int(detec_rate * len(df_res)))

    detec_vec = np.random.permutation(detec_vec)
    df_res['col_res'] = df_res['col_res'] * detec_vec

    df_res['apport_drone'] = df_res['DeltaPresentation'] - df_res[new_col]  # TODO: 'DeltaPresentation' dataframe specific
    dfi = df_res.dropna(axis=0, how='all', thresh=None, subset=['apport_drone'], inplace=False)

    dfi = dfi.loc[dfi['DeltaPresentation'] >= 0]
    dfi = dfi.loc[dfi['DeltaPresentation'] <= 15 * 60]

    dfi = dfi.head(500)

    n_tot = len(dfi)
    dfii = copy.deepcopy(dfi)


    dfii.loc[dfii['apport_drone'] < 0] = 0
    dfii.loc[dfii['col_res'] == 0, 'apport_drone'] = 0
    df_drone = dfii.loc[dfii['apport_drone'] > 0]
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

    trace3 = go.Histogram(
        x=df_drone['DeltaPresentation'], name=u'VSAV',
        marker=dict(color='rgb(102,0,0)'),
        #yaxis='y2'
    )

    trace4 = go.Histogram(
        x=df_drone['col_res'], name=u'Drone',
        marker=dict(color='rgb(0,100,0)'),
        # yaxis='y2'
    )

    trace5 = go.Histogram(
        x=dfii['apport_drone'], name=u'Temps gagné avec le drone',
        marker=dict(color='rgb(0,0,100)'),
        # yaxis='y2'
    )

    return {
        'data': [trace2, trace1],
        'layout': go.Layout(
            xaxis={
                'title': 'Temps VSAV',
                'type': 'linear'
            },
            yaxis={
                'title': 'Temps drone ' + input_speed + 'km/h, vent: ' + input_wind + ' ' + drone_input,
                'type': 'linear'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }, per_drone, {'data': [trace3, trace4],
        'layout': go.Layout(
            xaxis={
                'title': u'Temps de présentation quand le drone va plus vite',
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
                'title': u'Temps gagné avec un drone',#, quand le drone se présente avant le VSAV',
                'type': 'linear'
            },
            yaxis={
                'title': u"Nombre d'interventions",
                'type': 'linear'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )}



#print(dfnew['col_res'])

if __name__ == '__main__':
    app.run_server(debug=True)