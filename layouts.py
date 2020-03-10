import gettext
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import sankey
import drones

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
                            _('This website simulates drones sent with Automatic External '
                              'Defibrillators '
                              'to Out-of-Hospital Cardiac Arrest interventions. '
                              "Simulation is based on real life data, gathered in 2017 by Paris' "
                              'Firefighters, who intervened on more than 3000 OHCA in Paris and '
                              'Paris suburbs.')
                        ),
                        html.P(
                            _('The aim is to compare the hypothetical time to arrival of drones to'
                              ' the actual time to arrival of BLS teams, and to estimate to what '
                              'extent drones could improve the chain of survival.')
                        ),
                        html.P([
                            _('This app allows the user to compute their own simulation, '
                              'by changing '
                              'both dispatch center and drone flight parameters. '
                              'The source code is '
                              'available on '),
                            dbc.CardLink('Github',
# <<<<<<< HEAD
#                                          href="https://github.com/AlbaneMiron/drone-simulation"),
#                             _(' to allow for expertise and replication.'),
#                         ]),
#                         html.P(
#                             _("Default parameters correspond to what is assumed to be the "
# =======
                                         href='https://github.com/AlbaneMiron/drone-simulation'),
                            _(' to allow for expertise and replication.'),
                        ]),
                        html.P(
                            _('Default parameters correspond to what is assumed to be the '
                              'most likely set of drone characteristics and to the actual '
                              'operational'
                              "performance of Paris'firefighters medical dispatch center.")
                        ),
                        html.Div([
                            html.Img(
                                src='https://maps.googleapis.com/maps/api/staticmap?center=Paris,+France&zoom=11&scale=false&size=600x300&maptype=roadmap&key=AIzaSyAMs0JsrC88jq_yxCxfFqZ8dIBt0wEl3CY&format=png&visual_refresh=true',
                            ),
                        ], style={'text-align': 'center'}),
                        # dbc.Card(
                        #     dbc.Button(" GitHub",
                        #                id='submit-button', className='fa fa-github',
                        #                size='lg',
                        #                href="https://github.com/AlbaneMiron/drone-simulation"),
                        #     style={"width": "12rem",
                        #            "margin-left": "auto",
                        #            "margin-right": "auto"
                        #            }),

                    ],)

                ),

                dbc.Tab(
                    label=_('Simulation description'),
                    tab_id='datasets',
                    children=dbc.Container(className='control-tab', children=[
                        html.H4(className='datasets',
                                children=_('Rescue chain: BLS teams vs drones')),
                        html.Img(src='../../assets/tab-layout1.png', width='1000px'),
                    ]),
                ),

                dbc.Tab(
                    label=_('Parameters simulation A'),
                    tab_id='simA',
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
                            'B', suffix='_b', style={
                                'border-right': 'solid 1px #ddd',
                                'margin-right': '15px',
                                'padding-right': '15px',
                            },
                            input_drone='Centres de secours',
                        )),
                ),

                dbc.Tab(
                    label=_('Comparison of both simulations'),
                    tab_id='sims',
                    children=dbc.Col(
                        [
                            create_both_graphs('A', style={
                                'border-right': 'solid 1px #ddd',
                                'margin-right': '15px',
                                'padding-right': '15px',
                            }),
                            create_both_graphs('B', suffix='_b'),
                        ],
                        style={'display': 'flex'}),
                ),
            ]),
        ]),
    )


def create_parameters_layout(name, suffix='', input_drone=_POSITIONS[0], style=None):
    return dbc.Container([

        dbc.Container([
            html.H3(_('Simulation ') + name),
            html.P(html.Small(html.I(_(
                'You can get additional info on parameters descriptions by running your mouse over '
                'each of them.')))),
            dbc.Col([
                html.H6(_('Drone parameters')),

                html.Div([
                    html.Label(_('Initial drone location'), id='ini_pos'),
                    dbc.Tooltip(
                        _('Where drones are stationed. The simulator selects the closest available '
                          'drone (as the crow flies)'),
                        target='ini_pos',
                        placement='left')]),
                dcc.Dropdown(
                    id=f'input_drone{suffix}',
                    # TODO(pascal): Translate labels here.
                    options=[{'label': i, 'value': i} for i in _POSITIONS],
                    value=input_drone,
                ),

                html.Div([
                    html.Label(_('Max drone speed (in km/h)'), id="speed_e"),
                    dbc.Tooltip(
                        _('Maximum horizontal speed'),
                        target="speed_e",
                        placement="left")]),
                dbc.Input(id=f'speed{suffix}', value='80', type='text'),

                html.Div([
                    html.Label(_("Drone's acceleration time (in sec):"), id="acc_e"),
                    dbc.Tooltip(
                        _('Time needed for the drone to reach its maximum horizontal speed.'),
                        target="acc_e",
                        placement="left")]),
                dbc.Input(id=f'acc{suffix}', value='5', type='text'),

                html.Div([
                    html.Label(_("Drone's vertical speed (in m/s):"), id="vert-acc_e"),
                    dbc.Tooltip(
                        _('Maximum vertical speed. It is assumed that the time needed for the '
                          'drone to reach this speed is negligible.'),
                        target="vert-acc_e",
                        placement="left")]),
                dbc.Input(id=f'vert-acc{suffix}', value='9', type='text'),

                html.Div([
                    html.Label(_("Drone's cruise altitude (in m):"), id="alt_e"),
                    dbc.Tooltip(
                        _('Horizontal cruise altitude'),
                        target="alt_e",
                        placement="left")]),
                dbc.Input(id=f'alt{suffix}', value='100', type='text'),

                html.Div([
                    html.Label(_('Unavailability of the drone after a run (in h):'), id="unav_e"),
                    dbc.Tooltip(
                        _('Time needed after a run for the drone to be available again. It '
                          'accounts for the time spent on the OHCA location and the time of '
                          'refurbishment and rehabilitation of equipment.'),
# <<<<<<< HEAD
#                         target="unav_e",
#                         placement="left")]),
#                 dbc.Input(id=f'unavail_delta{suffix}', value='6', type='text'),
#
#                 html.Div([
#                     html.Label(_('Drone can fly during aeronautical night'), id="day_e"),
#                     dbc.Tooltip(
#                         _('Whether the drone can only fly during the aeronautical day or not'),
#                         target="day_e",
#                         placement="left")]),
# =======
                        target='unav_e',
                        placement='left')]),
                dbc.Input(id=f'unavail_delta{suffix}', value='6', type='text'),

                html.Div([
                    html.Label(_('Drone can fly during aeronautical night'), id='day_e'),
                    dbc.Tooltip(
                        _('Whether the drone can only fly during the aeronautical day or not'),
                        target='day_e',
                        placement='left')]),
# >>>>>>> a0ca58869bd054cd8bfc2e8dacbce68931501cde
                dcc.RadioItems(
                    id=f'day{suffix}',
                    options=[
                        {'label': ' ' + _('Yes'), 'value': 'Oui'},
                        {'label': ' ' + _('No'), 'value': 'Non'},
                    ],
                    value='Non',
                    labelStyle={'display': 'inline-block', 'margin-right': '1em'},
                ),

                html.H6(_('Operational parameters')),

                html.Div([
                    html.Label(_('Delay at departure (in s):'), id='dep_e'),
                    dbc.Tooltip(
                        _('Delay at departure needed for the operator to set up flight information '
                          'for the drone then for the fire station where the drone is stationed to '
                          'launch it.'),
                        target='dep_e',
                        placement='left')]),
                dbc.Input(id=f'dep_delay{suffix}', value='15', type='text'),

                html.Div([
                    html.Label(_('Delay on arrival (in s):'), id='arr_e'),
                    dbc.Tooltip(
                        _('Delay on arrival needed for the drone to narrow its landing and for '
                          'the bystander to catch the AED.'),
                        target='arr_e',
                        placement='left')]),
                dbc.Input(id=f'arr_delay{suffix}', value='15', type='text'),

                html.Div([
                    html.Label(
                        _("Delay between detection of unconsciousness  and OHCA detection (in s):"),
                        id="del_e"),
                    dbc.Tooltip(
                        _('Mean time spent between unconsciousness and OHCA detection by '
                          'emergency call dispatchers. Unconsciousness detection activates BLS '
                          'teams whereas drones are activated only at OHCA detection.'),
                        target='del_e',
                        placement='left')]),
                dbc.Input(id=f'detec_delay{suffix}', value='104', type='text'),

                html.Div([
                    html.Label(
                        _('Rate of OHCA at home, which are detected by call center operators '
                          '(between 0 and 1):'),
                        id='deth_e'),
                    dbc.Tooltip(
                        _('When the OHCA is not detected by the emergency dispatchers no drone is '
                          'sent.'),
                        target='deth_e',
                        placement='left')]),
                dbc.Input(id=f'detec_rate_home{suffix}', value='0.8', type='text'),

                html.Div([
                    html.Label(
                        _('Rate of OHCA in the streets, which are detected by call center '
                          'operators (between 0 and 1):'),
                        id='dets_e'),
                    dbc.Tooltip(
                        _('When the OHCA is not detected by the emergency dispatchers no drone is '
                          'sent.'),
                        target='dets_e',
                        placement='left')]),
                dbc.Input(id=f'detec_rate_vp{suffix}', value='0.12', type='text'),

                html.Div([
                    html.Label(
                        _('Rate of OHCA at home, which only have one witness alone (between 0 and '
                          '1):'),
                        id='wit_e'),
                    dbc.Tooltip(
                        _('The simulation requires at least two witnesses for OHCA at home : one '
                          'to stay near the victim, the other to go out in the street to get the '
                          'AED brought by drone.'),
                        target='wit_e',
                        placement='left')]),
                dbc.Input(id=f'wit_detec{suffix}', value='0.58', type='text'),

            ], style={'flex': 1}),

            dbc.Button(
                id=f'seq_start{suffix}', n_clicks=0,
                children=_('Update simulation'), block='center',
                style={'flex': 1}),

        ], style={'flex': 1} if style is None else dict(style, flex=1)),
        dbc.Col(children=create_graphs_layout(
            suffix=suffix,
            style={'display': 'flex', 'flex': 'initial'}))
    ], style={'display': 'flex', 'flex': 'auto'})


def create_graphs_layout(suffix='', style=None):
    return dbc.Container([
        dcc.Loading(children=[
            html.H6(_('Intervention distribution')),
            dbc.Container(
                sankey.Sankey(
                    id=f'flows-graphic{suffix}',
                    width=500, height=500,
                ),
                className='row'),
            html.H6(_('Time to arrival histogram when a drone is sent')),
            dbc.Col(children=[dcc.Graph(id=f'indicator-graphic3{suffix}', className='row')]),
            html.H6(_('Comparison of times to arrival for all interventions')),
            dbc.Container(dcc.Graph(id=f'indicator-graphic4{suffix}'), className='row'),
        ]),
    ], style={'flex': 1} if style is None else dict(style, flex=1))


def create_both_graphs(name, suffix='', style=None):
    return dbc.Container([
        html.H3(_('Simulation ') + name),
        dcc.Loading(children=[
            html.H6(_('Intervention distribution')),
            dbc.Container(sankey.Sankey(
                id=f'flows-graphicu{suffix}',
                width=500, height=500,
            ), className='row'),
            html.H6(_('Time to arrival histogram when a drone is sent')),
            dbc.Col(children=[dcc.Graph(id=f'indicator-graphic3u{suffix}', className='row')]),
            html.H6(_('Comparison of times to arrival for all interventions')),
            dbc.Container(dcc.Graph(id=f'indicator-graphic4u{suffix}'), className='row'),
        ]),
    ], style={'flex': 1} if style is None else dict(style, flex=1))


def create(lang):
    lang = gettext.translation('messages', localedir='locales', languages=[lang], fallback=True)
    lang.install()
    return dbc.Container(children=[
        dbc.Container(
            className='title',
            children=[html.H1(_('Airborne AED simulation')),
                      dbc.Card(dbc.Button(' GitHub',
                                          id='submit-button',
                                          className='fa fa-github',
                                          size='lg',
                                          href='https://github.com/AlbaneMiron/drone-simulation'),
                               style={'width': '12rem'},
                               color='light', outline=True
                               )
                      ],
            style={'display': 'flex', 'justify-content': 'space-between'}
        ),
        dbc.Container(
            id='vp-control-tabs', className='control-tabs', children=[create_tabs_layout()],
        ),
    ])
