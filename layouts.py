import dash_core_components as dcc
import dash_html_components as html

import drones

_POSITIONS = list(drones.STARTING_POINTS.keys())


def create_simulation_layout(name, suffix='', input_drone=_POSITIONS[0], style=None):
    return html.Div([
        html.H3(f'Simulation {name}'),

        html.Div([
            html.Div([
                html.H6('Drone parameters'),

                html.Label('Position initiale du drone'),
                dcc.Dropdown(
                    id=f'input_drone{suffix}',
                    options=[{'label': i, 'value': i} for i in _POSITIONS],
                    value=input_drone,
                ),

                html.Label('Vitesse maximale du drone (en km/h)'),
                dcc.Input(id=f'speed{suffix}', value='80', type='text'),

                html.Label(u"Nombre de secondes d'accelération du drone :"),
                dcc.Input(id=f'acc{suffix}', value='5', type='text'),

                html.Label(u"Vitesse verticale (en m/s) :"),
                dcc.Input(id=f'vert-acc{suffix}', value='9', type='text'),

                html.Label(u"Altitude de croisière (en m) :"),
                dcc.Input(id=f'alt{suffix}', value='100', type='text'),

                html.Label(u"Nombre d'heures d'indispo après lancer :"),
                dcc.Input(id=f'unavail_delta{suffix}', value='6', type='text'),

                # html.Label('Prise en compte du vent'),
                # dcc.RadioItems(
                #     id='wind',
                #     options=[{'label': i, 'value': i} for i in ['Oui', 'Non']],
                #     value='Oui',
                #     labelStyle={'display': 'inline-block'}
                # ),

                html.Label('Vol uniquement durant jour aéronautique'),
                dcc.RadioItems(
                    id=f'day{suffix}',
                    options=[{'label': i, 'value': i} for i in ['Oui', 'Non']],
                    value='Non',
                    labelStyle={'display': 'inline-block'}
                ),

            ], style={'flex': 1}),

            html.Div([
                html.H6('Operational parameters'),

                html.Label(u"Retard au départ (en s) :"),
                dcc.Input(id=f'dep_delay{suffix}', value='15', type='text'),

                html.Label(u"Retard à l'arrivée (en s) :"),
                dcc.Input(id=f'arr_delay{suffix}', value='15', type='text'),

                html.Label(u"Décalage de détection inconscience/ACR (en s) :"),
                dcc.Input(id=f'detec_delay{suffix}', value='104', type='text'),

                html.Label(u"Taux de détection ACR à la prise d'appel (entre 0 et 1) :"),
                dcc.Input(id=f'detec{suffix}', value='0.8', type='text'),

                html.Label(u"Odd ratio de la détection ACR voie publique à la prise d'appel :"),
                dcc.Input(id=f'detec_VP{suffix}', value='0.15', type='text'),

                html.Label(u"Taux de témoins seuls ACR lieu privé (entre 0 et 1) :"),
                dcc.Input(id=f'wit_detec{suffix}', value='0.58', type='text'),

            ], style={'flex': 1}),

        ], style={'display': 'flex'}),

        html.H6('Results'),

        html.Div([
            'Taux de drones plus rapides, sur toutes les interventions : ',
            html.Span(id=f'stats{suffix}'),
        ]),
        dcc.Graph(id=f'indicator-graphic2{suffix}'),
        dcc.Graph(id=f'indicator-graphic3{suffix}'),

    ], style={'flex': 1} if style is None else dict(style, flex=1))


layout = html.Div([  # pylint: disable=invalid-name

    create_simulation_layout('A', input_drone='PC le plus proche', style={
        'border-right': 'solid 1px #ddd',
        'margin-right': '15px',
        'padding-right': '15px',
    }),
    create_simulation_layout('B', suffix='_b', input_drone='CS le plus proche'),

], style={'display': 'flex'})
