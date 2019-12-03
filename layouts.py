import gettext
import dash_core_components as dcc
import dash_html_components as html
import sankey
import drones
import dash_bootstrap_components as dbc

_POSITIONS = list(drones.STARTING_POINTS.keys())


def create_tabs_layout():
    return dbc.Container(
        dbc.Container(id='app-control-tabs', className='control-tabs', children=[
            dbc.Tabs(id='app-tabs', children=[
                dbc.Tab(
                    label=_('About'),
                    tab_id='what-is',
                    children=dbc.Container(className='control-tab', children=[
                        html.H4(className='what-is', children=_('App presentation')),
                        html.P(
                            _('This app simulates drones sent with Automatic External '
                              'Defibrillators '
                              '(AEDs) to Out-of-Hospital Cardiac Arrest (OHCA) interventions. '
                              "Simulation is based on real life data, gathered in 2017 by Paris' "
                              'Firefighters, who intervened on more than 3000 OHCA in Paris and '
                              'Paris suburbs.')
                        ),
                        html.P(
                            _('The aim is to compare the hypothetical time to arrival of drones to '
                              'the actual time to arrival of BLS teams, and to estimate to what '
                              'extent drones could improve the chain of survival.')
                        ),
                        html.P(
                            _('This app allows the user to compute their own simulation, '
                              'by changing '
                              'both operational and drone flight parameters.')
                        ),

                    ])
                ),



                dbc.Tab(
                    #dcc.Tab(
                    label=_('Parameters simulation A'),
                    tab_id='simA',
                    #value='simA',
                    children=dbc.Container(
                        create_parameters_layout('A', style={
                        'border-right': 'solid 1px #ddd',
                        'margin-right': '15px',
                        'padding-right': '15px',
                    })),
                ),
                dbc.Tab(
                    label=_('Parameters simulation B'),
                    tab_id='simB',
                    children=dbc.Container(
                        create_parameters_layout(
                        'B', suffix='_b', input_drone='Centres de secours',
                    )),
                ),

                dbc.Tab(
                    label=_('Comparison of both simulations'),
                    tab_id='sims',
                    children=dbc.Col([
                          create_graphs_layout('A', style={
                              'border-right': 'solid 1px #ddd',
                              'margin-right': '15px',
                              'padding-right': '15px',
                          }),
                          create_graphs_layout('B', suffix='_b'),
                      ], style={'display': 'flex'}),
                ),


                dbc.Tab(
                    label=_('Parameters description'),
                    tab_id='datasets',
                    children=dbc.Container(className='control-tab', children=[
                        html.H4(className='datasets', children=_('Parameters description')),
                        html.H6(_("Operational parameters")),
                        dcc.Markdown(_('''
                            - Delay at departure: delay at departure needed for the operator to set up
                            flight information for the drone then for the fire station where the drone is stationed
                            to launch it.
                            - Delay on arrival: delay on arrival needed for the drone to narrow its landing and for
                            the bystander to catch the AED.
                            - Delay between detection of unconsciousness and OHCA detection:  mean time spent between
                            unconsciousness and OHCA detection by emergency call dispatchers. Unconsciousness detection
                            activates BLS teams whereas drones are activated only at OHCA detection.
                            - Rate of OHCA at home, which are detected by call center operators: when the OHCA is not
                            detected by the emergency dispatchers no drone is sent.
                            - Rate of OHCA in the streets, which are detected by call center operators: when the OHCA is
                            not detected by the emergency dispatchers no drone is sent.
                            - Rate of OHCA at home, which only have one witness alone: The simulation requires at least
                            two witnesses for OHCA at home : one to stay near the victim, the other to go out in the
                            street to get the AED brought by drone.
                            ''')),
                        html.H6(_("Drone parameters")),
                        dcc.Markdown(_('''
                            - Initial drone location : where drones are stationed. The simulator selects
                             the closest available drone (as the crow flies).
                             - Max drone speed: maximum horizontal speed.
                             - Drone's acceleration time: time needed for the drone to reach its
                                  maximum horizontal speed.
                             - Drone's vertical speed: maximum vertical speed. It is assumed that the time
                                   needed for the drone to reach this speed is negligible.
                            - Drone's cruise altitude: horizontal cruise altitude.
                            - Unavailability of the drone after a run: time needed after a run for the
                                  drone to be available again. It accounts for the time spent on the OHCA
                                  location and the time of refurbishment and rehabilitation of equipment.
                            - Flying restricted to aeronautical day: whether the drone can only fly
                                  during the aeronautical day or not.
                             ''')),
                    ]),
                ),
            ]),
        ],
                      #  style={'flex': 1}
                      ),

        #  dbc.Container(children=[html.A(
        #     id="gh-link",
        #     children=list(_('View on GitHub')),
        #     href="https://github.com/AlbaneMiron/drone-simulation",
        #     style={'color': "black", 'border': "solid 1px black"},
        # ),
        #     html.Img(src="../../assets/GitHub-Mark-64px.png"
        #              ),
        # ], style={'flex': 1})
    )


def create_graphs_layout(name, suffix='', style=None):
    return dbc.Container([
        html.H3(_('Simulation ') + name),
        html.H6(_('Results')),
        dcc.Loading(children=[
            # dcc.Graph(id=f'indicator-graphic1{suffix}'),
            dbc.Container(sankey.Sankey(id=f'flows-graphic{suffix}'), className='row'),
            dbc.Col(children=[dcc.Graph(id=f'indicator-graphic3{suffix}', className='row')]),
            dbc.Container(dcc.Graph(id=f'indicator-graphic4{suffix}'), className='row'),
        ]),
    ], style={'flex': 1} if style is None else dict(style, flex=1))


def create_parameters_layout(name, suffix='', input_drone=_POSITIONS[0], style=None):
    return dbc.Container([

        dbc.Container([
            html.H3(_('Simulation ') + name),
            dbc.Col([
                html.H6(_('Drone parameters')),

                html.Label(_('Initial drone location')),
                dcc.Dropdown(
                    id=f'input_drone{suffix}',
                    # TODO(pascal): Translate labels here.
                    options=[{'label': i, 'value': i} for i in _POSITIONS],
                    value=input_drone,
                ),

                html.Label(_('Max drone speed (in km/h)')),
                dbc.Input(id=f'speed{suffix}', value='80', type='text'),

                html.Label(_("Drone's acceleration time (in sec):")),
                dbc.Input(id=f'acc{suffix}', value='5', type='text'),

                html.Label(_("Drone's vertical speed (in m/s):")),
                dbc.Input(id=f'vert-acc{suffix}', value='9', type='text'),

                html.Label(_("Drone's cruise altitude (in m):")),
                dbc.Input(id=f'alt{suffix}', value='100', type='text'),

                html.Label(_('Unavailability of the drone after a run (in h):')),
                dbc.Input(id=f'unavail_delta{suffix}', value='6', type='text'),

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

                html.H6(_('Operational parameters')),

                dbc.Label(_("Delay at departure (in s):")),
                dbc.Input(id=f'dep_delay{suffix}', value='15', type='text'),

                dbc.Label(_("Delay on arrival (in s):")),
                dbc.Input(id=f'arr_delay{suffix}', value='15', type='text'),

                dbc.Label(_(
                    "Delay between detection of unconsciousness and OHCA detection (in s):")),
                dbc.Input(id=f'detec_delay{suffix}', value='104', type='text'),

                dbc.Label(_(
                    'Rate of OHCA at home, which are detected by call center operators (between 0 '
                    'and 1):')),
                dbc.Input(id=f'detec_rate_home{suffix}', value='0.8', type='text'),

                dbc.Label(_(
                    'Rate of OHCA in the streets, which are detected by call center operators '
                    '(between 0 and 1):')),
                dbc.Input(id=f'detec_rate_vp{suffix}', value='0.12', type='text'),

                dbc.Label(_(
                    "Rate of OHCA at home, which only have one witness alone (between 0 and 1):")),
                dbc.Input(id=f'wit_detec{suffix}', value='0.58', type='text'),

            ],
                style={'flex': 1}),
            dbc.Button(id=f'seq_start{suffix}', n_clicks=0, children=_('Update simulation'), block='center',
                       style={'flex': 1}),

        ], style={'flex': 1} if style is None else dict(style, flex=1)),
        dbc.Col(children=
                create_graphs_layout('A', style={
                    'border-right': 'solid 1px #ddd',
                    'margin-right': '15px',
                    'padding-right': '15px',
                }),
                )
    ], style={'display': 'flex'}
    )



def create(lang):
    lang = gettext.translation('messages', localedir='locales', languages=[lang], fallback=True)
    lang.install()
    return dbc.Container(
        children=[dbc.Container(className='title',
                                children=[html.H1(_('Airborne AED simulation'))]),
                  dbc.Container(id='vp-control-tabs', className='control-tabs', children=[create_tabs_layout()],),
                  # dbc.Container(id='vp-page-content', className='app-body', children=[
                  #     dbc.Col([
                  #         create_graphs_layout('A', style={
                  #             'border-right': 'solid 1px #ddd',
                  #             'margin-right': '15px',
                  #             'padding-right': '15px',
                  #         }),
                  #         create_graphs_layout('B', suffix='_b'),
                  #     ], style={'display': 'flex'}),
                  #
                  #     dbc.Col(children=_(
                  #         'This graph shows the time difference between the simulated time to arrival of a '
                  #         'drone and the actual time of arrival of the BLS team sent for every intervention. '
                  #         'On the right hand side (positive values) a drone would have been faster by the '
                  #         'number of seconds shown by the vertical bar. On the left hand side (negative '
                  #         'values) the BLS team would have been faster again by the number of seconds shown '
                  #         'by the vertical bar. Grey bars correspond to interventions for which a drone '
                  #         'would not be sent, vertical values are the actual BLS team time to arrival.'
                  #     )),
                  # ])
                  ], )
