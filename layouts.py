import dash_core_components as dcc
import dash_html_components as html

_POSITIONS = ['PC le plus proche', 'CS le plus proche']


layout1 = html.Div([  # pylint: disable=invalid-name
    html.Div([

        html.Div([
            html.H3('Simulation 1'),
            html.H6('Drone parameters'),

            html.Label('Position initiale du drone'),
            dcc.Dropdown(
                id='input_drone',
                options=[{'label': i, 'value': i} for i in _POSITIONS],
                value='PC le plus proche'
            ),

            html.Label('Vitesse maximale du drone (en km/h)'),
            dcc.Input(id='speed', value='80', type='text'),

            html.Label(u"Nombre de secondes d'accelération du drone :"),
            dcc.Input(id='acc', value='5', type='text'),

            html.Label(u"Vitesse verticale (en m/s) :"),
            dcc.Input(id='vert-acc', value='9', type='text'),

            html.Label(u"Altitude de croisière (en m) :"),
            dcc.Input(id='alt', value='100', type='text'),

            html.Label(u"Nombre d'heures d'indispo après lancer :"),
            dcc.Input(id='unavail_delta', value='6', type='text'),



            # html.Label('Prise en compte du vent'),
            # dcc.RadioItems(
            #     id='wind',
            #     options=[{'label': i, 'value': i} for i in ['Oui', 'Non']],
            #     value='Oui',
            #     labelStyle={'display': 'inline-block'}
            # ),

            html.Label('Vol uniquement durant jour aéronautique'),
            dcc.RadioItems(
                id='day',
                options=[{'label': i, 'value': i} for i in ['Oui', 'Non']],
                value='Non',
                labelStyle={'display': 'inline-block'}
            ),

        ], style={'width': '23%', 'display': 'inline-block'}),

        html.Div([
            html.H6('Operational parameters'),

            html.Label(u"Retard au départ (en s) :"),
            dcc.Input(id='dep_delay', value='15', type='text'),

            html.Label(u"Retard à l'arrivée (en s) :"),
            dcc.Input(id='arr_delay', value='15', type='text'),

            html.Label(u"Décalage de détection inconscience/ACR (en s) :"),
            dcc.Input(id='detec_delay', value='104', type='text'),

            html.Label(u"Taux de détection ACR à la prise d'appel (entre 0 et 1) :"),
            dcc.Input(id='detec', value='0.8', type='text'),

            html.Label(u"Odd ratio de la détection ACR voie publique à la prise d'appel :"),
            dcc.Input(id='detec_VP', value='0.15', type='text'),

            html.Label(u"Taux de témoins seuls ACR lieu privé (entre 0 et 1) :"),
            dcc.Input(id='wit_detec', value='0.58', type='text'),



        ], style={'width': '23%', 'display': 'inline-block'}),


        html.Div([
            html.H3('Simulation 2'),
            html.H6('Drone parameters'),
            html.Label('Position initiale du drone'),
            dcc.Dropdown(
                id='input_drone2',
                options=[{'label': i, 'value': i} for i in _POSITIONS],
                value='CS le plus proche'
            ),

            html.Label('Vitesse maximale du drone (en km/h)'),
            dcc.Input(id='speed2', value='80', type='text'),

            html.Label(u"Nombre de secondes d'accelération du drone :"),
            dcc.Input(id='acc2', value='5', type='text'),

            html.Label(u"Vitesse verticale (en m/s) :"),
            dcc.Input(id='vert-acc2', value='9', type='text'),

            html.Label(u"Altitude de croisière (en m) :"),
            dcc.Input(id='alt2', value='100', type='text'),

            html.Label(u"Nombre d'heures d'indispo après lancer :"),
            dcc.Input(id='unavail_delta2', value='6', type='text'),



            # html.Label('Prise en compte du vent'),
            # dcc.RadioItems(
            #     id='wind2',
            #     options=[{'label': i, 'value': i} for i in ['Oui', 'Non']],
            #     value='Oui',
            #     labelStyle={'display': 'inline-block'}
            # ),

            html.Label('Vol uniquement durant jour aéronautique'),
            dcc.RadioItems(
                id='day2',
                options=[{'label': i, 'value': i} for i in ['Oui', 'Non']],
                value='Non',
                labelStyle={'display': 'inline-block'}
            ),

        ], style={'width': '23%', 'display': 'inline-block'}),

        html.Div([
            html.H6('Operational parameters'),


            html.Label(u"Retard au départ (en s) :"),
            dcc.Input(id='dep_delay2', value='15', type='text'),

            html.Label(u"Retard à l'arrivée (en s) :"),
            dcc.Input(id='arr_delay2', value='15', type='text'),

            html.Label(u"Décalage de détection inconscience/ACR (en s) :"),
            dcc.Input(id='detec_delay2', value='104', type='text'),

            html.Label(u"Taux de détection ACR à la prise d'appel (entre 0 et 1) :"),
            dcc.Input(id='detec2', value='0.8', type='text'),

            html.Label(u"Odd ratio de la détection ACR voie publique à la prise d'appel :"),
            dcc.Input(id='detec_VP2', value='0.15', type='text'),

            html.Label(u"Taux de témoins seuls ACR lieu privé (entre 0 et 1) :"),
            dcc.Input(id='wit_detec2', value='0.58', type='text'),

        ], style={'width': '23%', 'display': 'inline-block'}),

    ]),
])

layout2 = html.Div([  # pylint: disable=invalid-name

    html.Div([
        html.Table(
            [html.Tr([
                html.Td(['Taux de drones plus rapides, sur toutes les interventions : ']),
                html.Td(id='stats'),
            ])],
            style={'width': '48%', 'display': 'inline-block'}),
        html.Table(
            [html.Tr([
                html.Td(['Taux de drones plus rapides, sur toutes les interventions : ']),
                html.Td(id='statsb'),
            ])],
            style={'width': '48%', 'display': 'inline-block'}),
    ]),


    html.Div([
        html.Div(
            [dcc.Graph(id='indicator-graphic2')],
            style={'width': '48%', 'display': 'inline-block'}),
        html.Div(
            [dcc.Graph(id='indicator-graphic2b')],
            style={'width': '48%', 'display': 'inline-block'}),
    ]),


    html.Div([
        html.Div(
            [dcc.Graph(id='indicator-graphic3')],
            style={'width': '48%', 'display': 'inline-block'}),
        html.Div(
            [dcc.Graph(id='indicator-graphic3b')],
            style={'width': '48%', 'display': 'inline-block'}),
    ]),
])
