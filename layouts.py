import sys
sys.path.append("./sankey")

import gettext
import dash_core_components as dcc
import dash_html_components as html
import sankey
import drones


_POSITIONS = list(drones.STARTING_POINTS.keys())


def create_simulation_layout(name, suffix='', input_drone=_POSITIONS[0], style=None):

    return html.Div([
        html.H3(_('Simulation ') + name),

        html.Div([
            html.Div([
                html.H6(_('Drone parameters')),

                html.Label(_('Initial drone location')),
                dcc.Dropdown(
                    id=f'input_drone{suffix}',
                    # TODO(pascal): Translate labels here.
                    options=[{'label': i, 'value': i} for i in _POSITIONS],
                    value=input_drone,
                ),

                html.Label(_('Max drone speed (in km/h)')),
                dcc.Input(id=f'speed{suffix}', value='80', type='text'),

                html.Label(_("Drone's acceleration time (in sec):")),
                dcc.Input(id=f'acc{suffix}', value='5', type='text'),

                html.Label(_("Drone's vertical speed (in m/s):")),
                dcc.Input(id=f'vert-acc{suffix}', value='9', type='text'),

                html.Label(_("Drone's cruise altitude (in m):")),
                dcc.Input(id=f'alt{suffix}', value='100', type='text'),

                html.Label(_('Unavailability of the drone after a run (in h):')),
                dcc.Input(id=f'unavail_delta{suffix}', value='6', type='text'),

                html.Label(_('Flying restricted to aeronautical day')),
                dcc.RadioItems(
                    id=f'day{suffix}',
                    options=[
                        {'label': _('Yes'), 'value': 'Oui'},
                        {'label': _('No'), 'value': 'Non'},
                    ],
                    value='Non',
                    labelStyle={'display': 'inline-block'}
                ),

            ], style={'flex': 1}),

            html.Div([
                html.H6(_('Operational parameters')),

                html.Label(_("Delay at departure (in s):")),
                dcc.Input(id=f'dep_delay{suffix}', value='15', type='text'),

                html.Label(_("Delay on arrival (in s):")),
                dcc.Input(id=f'arr_delay{suffix}', value='15', type='text'),

                html.Label(_(
                    "Delay between detection of unconsciousness and OHCA detection (in s):")),
                dcc.Input(id=f'detec_delay{suffix}', value='104', type='text'),

                html.Label(_(
                    "Rate of OHCA at home, which are detected by call center operators (between 0 and 1):")),
                dcc.Input(id=f'detec_rate_home{suffix}', value='0.8', type='text'),

                html.Label(_(
                    "Rate of OHCA in the streets, which are detected by call center operators (between 0 and 1):")),
                dcc.Input(id=f'detec_rate_vp{suffix}', value='0.12', type='text'),

                html.Label(_(
                    "Rate of OHCA at home, which only have one witness alone (between 0 and 1):")),
                dcc.Input(id=f'wit_detec{suffix}', value='0.58', type='text'),

            ], style={'flex': 1}),

        ], style={'display': 'flex'}),

        html.H6(_('Results')),

        dcc.Loading(children=[
            # html.Div([
            #     _('Rate of faster drones among all interventions: '),
            #     html.Span(id=f'stats{suffix}'),
            # ]),
            dcc.Graph(id=f'indicator-graphic1{suffix}'),
            sankey.Sankey(id=f'flows-graphic{suffix}'),
            dcc.Graph(id=f'indicator-graphic3{suffix}'),
            dcc.Graph(id=f'indicator-graphic4{suffix}'),
        ]),

    ], style={'flex': 1} if style is None else dict(style, flex=1))


def create(lang):
    lang = gettext.translation('messages', localedir='locales', languages=[lang], fallback=True)
    lang.install()
    return html.Div([

        html.Div([

            create_simulation_layout('A', style={
                'border-right': 'solid 1px #ddd',
                'margin-right': '15px',
                'padding-right': '15px',
            }),
            create_simulation_layout('B', suffix='_b', input_drone='Centres de secours'),
        ], style={'display': 'flex'}),

        html.Div(children=_("This graph shows the time difference between the simulated time to arrival of a drone and "
                            "the actual time of arrival of the BLS team sent for every intervention. "
                            "On the right hand side (positive values) a drone would have been faster by the number of"
                            "seconds shown by the vertical bar. On the left hand side (negative values) the BLS team "
                            "would have been faster again by the number of seconds shown by the vertical bar. "
                            "Grey bars correspond to interventions for which a drone would not be sent, "
                            "vertical values are the actual BLS team time to arrival.")),
        ],
        style={'display': 'inline'})


