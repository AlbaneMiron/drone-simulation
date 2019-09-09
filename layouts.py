import dash_core_components as dcc
import dash_html_components as html

import drones

_POSITIONS = list(drones.STARTING_POINTS.keys())

_POSITIONS = [['Postes de commandement', 'Centres de secours'], ['Main fire stations', 'Every fire station']]
_BOOL = [['Oui', 'Non'], ['Yes', 'No']]

dict_drone = {
    'drone_param': ['Paramètres du drone', 'Drone parameters'],
    'drone_pos': ['Position initiale du drone', 'Drone launch location'],
    'drone_spe': ['Vitesse maximale (km/h)', 'Maximum horizontal cruise speed (km/h)'],
    'drone_acc': ["Durée d'accelération horizontale (s)", 'Horizontal acceleration duration (s)'],
    'drone_vert': ['Vitesse verticale (m/s)', 'Vertical speed (m/s)'],
    'drone_alt': ['Altitude de croisière (m)', 'Cruise altitude (m)'],
    'drone_unav': ["Durée de l'indisponibilité du drone après le lancer (h)",
                   'Drone unavailability duration after launch (h)'],
    'drone_day' : ['Vol uniquement durant jour aéronautique', 'Flight only during day time']
}

dict_oper = {
    'oper_param': ['Paramètres opérationnels', 'Operational parameters'],
    'oper_ddelay': ['Retard au départ (s)', 'Departure delay (s)'],
    'oper_adelay': ["Retard à l'arrivée (s)", 'Arrival delay (s)'],
    'oper_detecd': ["Décalage de détection inconscience/ACR (s)",
                    'Delay between unconsciousness detection and OHCA detection by 18/112 operators (s)'],
    'oper_detecr': ["Taux de détection ACR à la prise d'appel ([0,1])",
                    "Rate of OHCA detection by 18/112 operators ([0,1])" ],
    'oper_detecs': ["Odd ratio de la détection ACR voie publique à la prise d'appel",
                    "Odd ratio of OHCA in the streets vs OHCA at home or in a public place detection by 18/112 operators"],
    'oper_witn': ["Taux de témoins seuls ACR lieu privé ([0,1])",
                  "Rate of OHCA at home with only have one witness alone ([0,1])"]
}

dict_res = {'res': ['Résultats', 'Results'],
            'rate': ['Taux de drones plus rapides, sur toutes les interventions : ',
                     'Rate of faster drones among all interventions : ']}


def create_simulation_layout(name,  suffix='', language='FR', input_drone=_POSITIONS[0][1], style=None,
                             dict_drone_=dict_drone, dict_oper_=dict_oper, dict_res_=dict_res):

    i = int(language == 'EN')

    return html.Div([
        html.H3(f'Simulation {name}'),

        html.Div([
            html.Div([
                html.H6(dict_drone_['drone_param'][i]),

                html.Label(dict_drone_['drone_pos'][i]),
                dcc.Dropdown(
                    id=f'input_drone{suffix}',
                    options=[{'label': i, 'value': i} for i in _POSITIONS[i]],
                    value=input_drone,
                ),

                html.Label(dict_drone_['drone_spe'][i]),
                dcc.Input(id=f'speed{suffix}', value='80', type='text'),

                html.Label(dict_drone_['drone_acc'][i]),
                dcc.Input(id=f'acc{suffix}', value='5', type='text'),

                html.Label(dict_drone_['drone_vert'][i]),
                dcc.Input(id=f'vert-acc{suffix}', value='9', type='text'),

                html.Label(dict_drone_['drone_alt'][i]),
                dcc.Input(id=f'alt{suffix}', value='100', type='text'),

                html.Label(dict_drone_['drone_unav'][i]),
                dcc.Input(id=f'unavail_delta{suffix}', value='6', type='text'),

                html.Label(dict_drone_['drone_day'][i]),
                dcc.RadioItems(
                    id=f'day{suffix}',
                    options=[{'label': i, 'value': i} for i in _BOOL[i]],
                    value=_BOOL[i][1],
                    labelStyle={'display': 'inline-block'}
                ),

            ], style={'flex': 1}),

            html.Div([
                html.H6(dict_oper_['oper_param'][i]),

                html.Label(dict_oper_['oper_ddelay'][i]),
                dcc.Input(id=f'dep_delay{suffix}', value='15', type='text'),

                html.Label(dict_oper_['oper_adelay'][i]),
                dcc.Input(id=f'arr_delay{suffix}', value='15', type='text'),

                html.Label(dict_oper_['oper_detecd'][i]),
                dcc.Input(id=f'detec_delay{suffix}', value='104', type='text'),

                html.Label(dict_oper_['oper_detecr'][i]),
                dcc.Input(id=f'detec{suffix}', value='0.8', type='text'),

                html.Label(dict_oper_['oper_detecs'][i]),
                dcc.Input(id=f'detec_VP{suffix}', value='0.15', type='text'),

                html.Label(dict_oper_['oper_witn'][i]),
                dcc.Input(id=f'wit_detec{suffix}', value='0.58', type='text'),

            ], style={'flex': 1}),

        ], style={'display': 'flex'}),

        html.H6(dict_res_['res'][i]),

        html.Div([
            dict_res_['rate'][i],
            html.Span(id=f'stats{suffix}'),
        ]),
        dcc.Graph(id=f'indicator-graphic2{suffix}'),
        dcc.Graph(id=f'indicator-graphic3{suffix}'),

    ], style={'flex': 1} if style is None else dict(style, flex=1))


layout_FR = html.Div([  # pylint: disable=invalid-name

    create_simulation_layout('A',  style={
        'border-right': 'solid 1px #ddd',
        'margin-right': '15px',
        'padding-right': '15px',
    }),
    create_simulation_layout('B', suffix='_b', input_drone='Postes de commandement'),

], style={'display': 'flex'})


layout_EN = html.Div([  # pylint: disable=invalid-name
    create_simulation_layout('A', language='EN', input_drone='Main fire stations', style={
        'border-right': 'solid 1px #ddd',
        'margin-right': '15px',
        'padding-right': '15px',
    }),
    create_simulation_layout('B', suffix='_b', language='EN', input_drone='Every fire station'),

], style={'display': 'flex'})
