import dash_core_components as dcc
import dash_html_components as html

positions = ['PC le plus proche', 'CS le plus proche']

layout1 = html.Div([
    html.Div([


        html.Div([
        html.H3('Simulation 1'),
            html.Label('Vitesse maximale du drone (en km/h)'),
            dcc.Input(id='speed', value='80', type='text'),

            html.Label(u"Nombre de secondes d'accelération du drone :"),
            dcc.Input(id='acc', value='5', type='text'),

            html.Label(u"Vitesse verticale (en m/s) :"),
            dcc.Input(id='vert-acc', value='9', type='text'),

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

        ], style={'width': '23%', 'display': 'inline-block'}),

        html.Div([

            html.Label(u"Altitude de croisière (en m) :"),
            dcc.Input(id='alt', value='100', type='text'),

            html.Label(u"Retard au départ (en s) :"),
            dcc.Input(id='dep_delay', value='15', type='text'),

            html.Label(u"Retard à l'arrivée (en s) :"),
            dcc.Input(id='arr_delay', value='15', type='text'),

            html.Label(u"Décalage de détection inconscience/ACR (en s) :"),
            dcc.Input(id='detec_delay', value='108', type='text'),

            html.Label(u"Taux de détection ACR à la prise d'appel (entre 0 et 1) :"),
            dcc.Input(id='detec', value='1', type='text'),

            html.Label(u"Odd ratio de la détection ACR voie publique à la prise d'appel :"),
            dcc.Input(id='detec_VP', value='0.15', type='text'),

            html.Label(u"Taux de témoins seuls ACR lieu privé (entre 0 et 1) :"),
            dcc.Input(id='wit_detec', value='0', type='text'),

            html.Label(u"Nombre d'heures d'indispo après lancer :"),
            dcc.Input(id='unavail_delta', value='6', type='text'),

        ], style={'width': '23%', 'display': 'inline-block'}),


        html.Div([
        html.H3('Simulation 2'),
            html.Label('Vitesse maximale du drone (en km/h)'),
            dcc.Input(id='speed2', value='80', type='text'),

            html.Label(u"Nombre de secondes d'accelération du drone :"),
            dcc.Input(id='acc2', value='5', type='text'),

            html.Label(u"Vitesse verticale (en m/s) :"),
            dcc.Input(id='vert-acc2', value='9', type='text'),

            html.Label('Position initiale du drone'),
            dcc.Dropdown(
                id='input_drone2',
                options=[{'label': i, 'value': i} for i in positions],
                value='PC le plus proche'
            ),

            html.Label('Prise en compte du vent'),
            dcc.RadioItems(
                id='wind2',
                options=[{'label': i, 'value': i} for i in ['Oui', 'Non']],
                value='Oui',
                labelStyle={'display': 'inline-block'}
            ),

            html.Label('Vol uniquement durant jour aéronautique'),
            dcc.RadioItems(
                id='day2',
                options=[{'label': i, 'value': i} for i in ['Oui', 'Non']],
                value='Non',
                labelStyle={'display': 'inline-block'}
            ),

        ], style={'width': '23%', 'display': 'inline-block'}),

        html.Div([

            html.Label(u"Altitude de croisière (en m) :"),
            dcc.Input(id='alt2', value='100', type='text'),

            html.Label(u"Retard au départ (en s) :"),
            dcc.Input(id='dep_delay2', value='15', type='text'),

            html.Label(u"Retard à l'arrivée (en s) :"),
            dcc.Input(id='arr_delay2', value='15', type='text'),

            html.Label(u"Décalage de détection inconscience/ACR (en s) :"),
            dcc.Input(id='detec_delay2', value='108', type='text'),

            html.Label(u"Taux de détection ACR à la prise d'appel (entre 0 et 1) :"),
            dcc.Input(id='detec2', value='1', type='text'),

            html.Label(u"Odd ratio de la détection ACR voie publique à la prise d'appel :"),
            dcc.Input(id='detec_VP2', value='0.15', type='text'),

            html.Label(u"Taux de témoins seuls ACR lieu privé (entre 0 et 1) :"),
            dcc.Input(id='wit_detec2', value='0', type='text'),

            html.Label(u"Nombre d'heures d'indispo après lancer :"),
            dcc.Input(id='unavail_delta2', value='6', type='text'),

        ], style={'width': '23%', 'display': 'inline-block'}),

    ]),
    #dcc.Link('Go to App 2', href='/apps/app2'),

    # html.Div([
    #     html.Table([
    #             html.Tr([html.Td(['Taux de drones plus rapides, sur toutes les interventions : ']), html.Td(id='stats')]),
    #             # html.Tr([html.Td(['', html.Sup(3)]), html.Td(id='cube')]),
    #             # html.Tr([html.Td([2, html.Sup('x')]), html.Td(id='twos')]),
    #             # html.Tr([html.Td([3, html.Sup('x')]), html.Td(id='threes')]),
    #             # html.Tr([html.Td(['x', html.Sup('x')]), html.Td(id='x^x')]),
    #     ],
    #     style={'width': '100%', 'display': 'inline-block'}),
    # ]),
    #
    #
    # html.Div([
    #     html.Div([
    #         dcc.Graph(id='indicator-graphic2'),
    #     ],
    #         style={'width': '48%', 'display': 'inline-block'}),
    # html.Div([
    #         dcc.Graph(id='indicator-graphic3'),
    #     ],
    #         style={'width': '48%', 'display': 'inline-block'}),
    # ]),
    #
    # dcc.Graph(id='indicator-graphic'),

    # dcc.Slider(
    #     id='speed--slider',
    #     min=20,  # km/h
    #     max=150, #km/h
    #     value=80,
    #     #marks={str(year): str(year) for year in df['Year'].unique()},
    #     step=10
    #)
 ])

layout2 = html.Div([

    html.Div([
        html.Table([
            html.Tr([html.Td(['Taux de drones plus rapides, sur toutes les interventions : ']), html.Td(id='stats')]),
            ],
                style={'width': '48%', 'display': 'inline-block'}),
        html.Table([
            html.Tr([html.Td(['Taux de drones plus rapides, sur toutes les interventions : ']), html.Td(id='statsb')]),
            ],
                style={'width': '48%', 'display': 'inline-block'}),
        ]),


    html.Div([
        html.Div([
                dcc.Graph(id='indicator-graphic2'),
            ],
                style={'width': '48%', 'display': 'inline-block'}),
        html.Div([
                dcc.Graph(id='indicator-graphic2b'),
            ],
                style={'width': '48%', 'display': 'inline-block'}),
        ]),


    html.Div([
        html.Div([
                dcc.Graph(id='indicator-graphic3'),
            ],
                style={'width': '48%', 'display': 'inline-block'}),
        html.Div([
                dcc.Graph(id='indicator-graphic3b'),
            ],
                style={'width': '48%', 'display': 'inline-block'}),
        ]),

        #dcc.Graph(id='indicator-graphic'),
    #dcc.Link('Go to App 1', href='/apps/app1'),
    ])

# layout1 = html.Div([
#     html.H3('App 1'),
#     dcc.Dropdown(
#         id='app-1-dropdown',
#         options=[
#             {'label': 'App 1 - {}'.format(i), 'value': i} for i in [
#                 'NYC', 'MTL', 'LA'
#             ]
#         ]
#     ),
#     html.Div(id='app-1-display-value'),
#     dcc.Link('Go to App 2', href='/apps/app2')
# ])
#
# layout2 = html.Div([
#     html.H3('App 2'),
#     dcc.Dropdown(
#         id='app-2-dropdown',
#         options=[
#             {'label': 'App 2 - {}'.format(i), 'value': i} for i in [
#                 'NYC', 'MTL', 'LA'
#             ]
#         ]
#     ),
#     html.Div(id='app-2-display-value'),
#     dcc.Link('Go to App 1', href='/apps/app1')
# ])