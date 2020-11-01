import gettext
import textwrap
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
# import sankey
import drones

_POSITIONS = list(drones.STARTING_POINTS.keys())


def create_tabs_layout(simu_desc_file):
    # return dbc.Container(id='app-control-tabs', className='control-tabs', children=[
    return dbc.Tabs(id='app-tabs', children=[
        dbc.Tab(
            label=_('About'),
            tab_id='what-is',
            children=dbc.Col(className='control-tab', children=[
                html.H4(className='what-is', children=_('App presentation')),
                html.P(
                    _('This website simulates drones sent with Automatic External '
                      'Defibrillators '
                      'to Out-of-Hospital Cardiac Arrest incidents. '
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
                ], style={'textAlign': 'center'}),
                # dbc.Card(
                #     dbc.Button(" GitHub",
                #                id='submit-button', className='fa fa-github',
                #                size='lg',
                #                href="https://github.com/AlbaneMiron/drone-simulation"),
                #     style={"width": "12rem",
                #            "marginLeft": "auto",
                #            "marginRight": "auto"
                #            }),

            ], style={'marginTop': '10px',
                      'paddingRight': '0', 'paddingLeft': '0'})

        ),

        dbc.Tab(
            label=_('Simulation description'),
            tab_id='datasets',
            children=dbc.Col(className='control-tab', children=[
                html.H4(className='datasets',
                        children=_('Rescue chain: BLS teams vs drones')),
                html.Img(src=simu_desc_file,
                         style={'maxWidth': '100%', 'maxHeight': '100%'}),
            ], style={'marginTop': '10px',
                      'paddingRight': '0', 'paddingLeft': '0'}),
        ),

        dbc.Tab(
            label=_('Parameters simulation A'),
            tab_id='simA',
            children=dbc.Col(
                create_parameters_layout('A')),
        ),
        dbc.Tab(
            label=_('Parameters simulation B'),
            tab_id='simB',
            children=dbc.Col(
                create_parameters_layout(
                    'B', suffix='_b',
                    input_drone='Centres de secours',
                )),
        ),

        dbc.Tab(
            label=_('Comparison of both simulations'),
            tab_id='sims',
            children=dbc.Col(
                [
                    create_both_graphs('A', style={
                        'borderRight': 'solid 1px #ddd',
                        'marginRight': '15px',
                        'paddingRight': '15px',
                    }),
                    create_both_graphs('B', suffix='_b'),
                ],
                style={'display': 'flex', 'marginTop': '10px',
                       'paddingRight': '0', 'paddingLeft': '0'}),
        ),

        dbc.Tab(
            label=_('Custom Datasets'),
            tab_id='data',
            children=dbc.Col([
                html.H3(children=_('Custom Datasets')),

                html.Div(_('Launch a simulation on your own data:')),
                html.H4(children=_('Starting Points'), style={'marginTop': 30}),
                html.Div([_(
                    'Upload a CSV file containing a list of starting points for drones. '
                    'Each row represents one starting point and should contain an index '
                    'followed by the latitude and longitude of the point. Example:'
                )]),
                html.Textarea(
                    children=textwrap.dedent('''\
                                COBI,48.8511191742212,2.33150232324835
                                MALA,48.8615396838525,2.3057037964225398
                                CHPY,48.8079548017692,2.53121646098508'''),
                    disabled=True, style={'height': 80, 'width': 400}),
                dcc.Upload(
                    id='upload-starting-points',
                    children=html.Div([
                        _('Drag and Drop or '),
                        html.A(html.Button(_('Select a File'))),
                    ]),
                ),
                html.Div(id='output-starting-points-upload'),

                html.H4(children=_('Incidents'), style={'marginTop': 30}),
                html.Div([_(
                    'Upload a CSV file containing a list of incidents. Each row (except the first '
                    'one used for fields headers) represents one incident and should contain the '
                    'following fields:'
                )]),
                html.Ul([
                    html.Li(_('time_call: the date and time of the emergency call')),
                    html.Li(_('latitude: the latitude of the incident, as a float')),
                    html.Li(_('longitude: the longitude of the incident as a float')),
                    html.Li(_(
                        'BLS_time: the time taken by the BLS team to reach the incident, '
                        'in seconds',
                    )),
                    html.Li(_(
                        'home: a flag indicating whether the incident happened at home (1) '
                        'or in a street or public place (0)',
                    )),
                    html.Li(_(
                        'day: a flag indicating whether the incident happened during the '
                        'aeronautical day (1) or night (0)',
                    )),
                    html.Li(_(
                        'low_wind: a flag indicating whether the wind during incident was low '
                        'enough to fly (1) or faster than 50 km/h (0)',
                    )),
                    html.Li(_(
                        'clear_sight: a flag indicating whether the sight during incident was '
                        'clear enough to fly (1) or below 200m (0)',
                    )),
                ]),
                html.Textarea(
                    children=textwrap.dedent('''\
                        ,time_call,BLS_time,day,low_wind,clear_sight,home,latitude,longitude
                        0,01/01/17 00:13,214.0,0,1,1,1,48.8240664,2.3680644
                        1,01/01/17 03:49,1062.0,0,1,1,1,48.785867700000004,2.4296106
                        2,01/01/17 06:03,442.0,0,1,1,1,48.8405163,2.2878906000000003
                        3,01/01/17 06:15,486.0,0,1,1,1,48.8759425,2.1920694
                        4,01/01/17 08:56,366.0,1,1,1,1,48.7890453,2.4475238999999998
                        5,01/01/17 12:14,630.0,1,1,1,1,48.873926899999994,2.1894501'''),
                    disabled=True, style={'height': 150, 'width': '100%'}),
                dcc.Upload(
                    id='upload-incidents',
                    children=html.Div([
                        _('Drag and Drop or '),
                        html.A(html.Button(_('Select a File'))),
                    ]),
                ),
                html.Div(id='output-incidents-upload'),
            ], style={'marginTop': '10px',
                      'paddingRight': '0', 'paddingLeft': '0'}),
        ),
    ], style={'marginTop': '10px',
              'paddingRight': '0', 'paddingLeft': '0'})
    #   ,
    # ], style={'marginTop': '15px', 'paddingRight': '0', 'paddingLeft': '0'})


def create_parameters_layout(name, suffix='', input_drone=_POSITIONS[0]):
    # return dbc.Col([
    return dbc.Col([
        dbc.Input(id=f'hash{suffix}', value='', type='text', style={'display': 'none'}),
        dbc.Col(children=[html.H3(_('Simulation ') + name),
                          html.P(html.Small(html.I(_(
                              'You can get additional info '
                              'on parameters descriptions by hovering '
                              'your mouse over '
                              'each of them.'))))],
                style={
                    'marginRight': '15px',
                    'paddingRight': '0',
                    'paddingLeft': '0'}),
        dbc.Row([
            dbc.Col([
                html.H6(_('Drone parameters')),
                dbc.FormGroup([
                    dbc.Label(_('Initial drone location'), id='ini_pos', width=6),
                    dbc.Tooltip(
                        _('Where drones are stationed. '
                          'The simulator selects the closest available '
                          'drone (as the crow flies)'),
                        target='ini_pos',
                        placement='top'),
                    dcc.Dropdown(
                        id=f'input_drone{suffix}',
                        # TODO(pascal): Translate labels here.
                        options=[{'label': i, 'value': i} for i in _POSITIONS],
                        value=input_drone,
                        clearable=False,
                        style={'width': '250px'}
                    )], row=True),

                dbc.FormGroup([
                    dbc.Label(_('Max drone speed (in km/h):'), id='speed_e', width=8),
                    dbc.Tooltip(
                        _('Maximum horizontal speed'),
                        target='speed_e',
                        placement='top'),
                    dbc.Input(id=f'speed{suffix}', value='80',
                              type='text',
                              style={'width': '70px'})
                ], row=True),

                dbc.FormGroup([
                    dbc.Label(_("Drone's acceleration time (in sec):"), id='acc_e', width=8),
                    dbc.Tooltip(
                        _('Time needed for the drone to reach its maximum horizontal speed.'),
                        target='acc_e',
                        placement='top'),
                    dbc.Input(id=f'acc{suffix}', value='5',
                              type='text',
                              style={'width': '70px'})], row=True),

                dbc.FormGroup([
                    dbc.Label(_("Drone's vertical speed (in m/s):"), id='vert-acc_e', width=8),
                    dbc.Tooltip(
                        _('Maximum vertical speed. It is assumed that the time needed for the '
                          'drone to reach this speed is negligible.'),
                        target='vert-acc_e',
                        placement='top'),
                    dbc.Input(id=f'vert-acc{suffix}', value='9',
                              type='text',
                              style={'width': '70px'})], row=True),

                dbc.FormGroup([
                    dbc.Label(_("Drone's cruise altitude (in m):"), id='alt_e', width=8),
                    dbc.Tooltip(
                        _('Horizontal cruise altitude'),
                        target='alt_e',
                        placement='top'),
                    dbc.Input(id=f'alt{suffix}', value='100',
                              type='text',
                              style={'width': '70px'})], row=True),

                dbc.FormGroup([
                    dbc.Label(_('Unavailability of the drone after a run (in h):'),
                              id='unav_e', width=8),
                    dbc.Tooltip(
                        _('Time needed after a run for the drone to be available again. It '
                          'accounts for the time spent on the OHCA location and the time of '
                          'refurbishment and rehabilitation of equipment.'),
                        target='unav_e',
                        placement='top'),
                    dbc.Input(id=f'unavail_delta{suffix}', value='6',
                              type='text',
                              style={'width': '70px'})], row=True),

                dbc.FormGroup([
                    dbc.Label(_('Drone can fly during aeronautical night'), id='day_e', width=8),
                    dbc.Tooltip(
                        _('Whether the drone can only fly during the aeronautical day or not'),
                        target='day_e',
                        placement='top'),
                    dcc.RadioItems(
                        id=f'day{suffix}',
                        options=[{'label': ' ' + _('Yes'), 'value': 'Oui'},
                                 {'label': ' ' + _('No'), 'value': 'Non'}],
                        value='Non',
                        labelStyle={'display': 'inline-block', 'marginRight': '1em'})
                ], row=True)
            ]),

            dbc.Col(children=[
                html.H6(_('Operational parameters')),

                dbc.FormGroup([
                    dbc.Label(_('Delay at departure (in s):'), id='dep_e', width=8),
                    dbc.Tooltip(
                        _('Delay at departure needed for the operator to '
                          'set up flight information '
                          'for the drone then for the fire station '
                          'where the drone is stationed to '
                          'launch it.'),
                        target='dep_e',
                        placement='top'),
                    dbc.Input(id=f'dep_delay{suffix}', value='15',
                              type='text',
                              style={'width': '70px'})], row=True),

                dbc.FormGroup([
                    dbc.Label(_('Delay on arrival (in s):'), id='arr_e', width=8),
                    dbc.Tooltip(
                        _('Delay on arrival needed for the drone to narrow its landing and for '
                          'the bystander to catch the AED.'),
                        target='arr_e',
                        placement='top'),
                    dbc.Input(id=f'arr_delay{suffix}', value='15',
                              type='text',
                              style={'width': '70px'})], row=True),

                dbc.FormGroup([
                    dbc.Label(
                        _('Delay between detection of unconsciousness '
                          'and OHCA detection (in s):'),
                        id='del_e', width=8),
                    dbc.Tooltip(
                        _('Mean time spent between unconsciousness and OHCA detection by '
                          'emergency call dispatchers. Unconsciousness detection activates BLS '
                          'teams whereas drones are activated only at OHCA detection.'),
                        target='del_e',
                        placement='top'),
                    dbc.Input(id=f'detec_delay{suffix}', value='104',
                              type='text',
                              style={'width': '70px'})], row=True),

                dbc.FormGroup([
                    dbc.Label(
                        _('Rate of OHCA at home, which are detected by call center operators'
                          ':'),
                        id='deth_e', width=8),
                    dbc.Tooltip(
                        _('When the OHCA is not detected by '
                          'the emergency dispatchers no drone is '
                          'sent. (Value between 0 and 1)'),
                        target='deth_e',
                        placement='top'),
                    dbc.Input(id=f'detec_rate_home{suffix}', value='0.87',
                              type='number', max=1, min=0, step=0.01,
                              style={'width': '70px'})], row=True),

                dbc.FormGroup([
                    dbc.Label(
                        _('Rate of OHCA in the streets, which are detected by call center '
                          'operators:'),
                        id='dets_e', width=8),
                    dbc.Tooltip(
                        _('When the OHCA is not detected by '
                          'the emergency dispatchers no drone is '
                          'sent. (Value between 0 and 1)'),
                        target='dets_e',
                        placement='top'),
                    dbc.Input(id=f'detec_rate_vp{suffix}', value='0.71',
                              type='number', max=1, min=0, step=0.01,
                              style={'width': '70px'})], row=True),

                dbc.FormGroup([
                    dbc.Label(
                        _('Rate of OHCA at home, which only have '
                          'one witness alone:'),
                        id='wit_e', width=8),
                    dbc.Tooltip(
                        _('The simulation requires at least two witnesses for '
                          'OHCA at home : one '
                          'to stay near the victim, the other '
                          'to go out in the street to get the '
                          'AED brought by drone. (Value between 0 and '
                          '1)'),
                        target='wit_e',
                        placement='top'),
                    dbc.Input(id=f'wit_detec{suffix}', value='0.58',
                              type='number', max=1, min=0, step=0.01,
                              style={'width': '70px'})], row=True),

            ], style={'flex': 1}),
        ], style={
            'marginRight': '15px',
            'paddingRight': '0',
        }),
        dbc.Button(
            id=f'seq_start{suffix}', n_clicks=0,
            children=_('Update simulation'), block='center',
            style={'flex': 1, 'marginTop': '20px', 'marginBottom': '20px'}
        )], style={'marginTop': '20px', 'paddingRight': '0', 'paddingLeft': '0'}), \
        dbc.Row(children=[html.H3(_('Results')), create_graphs_layout(suffix=suffix)])
    # ], style={'marginTop': '20px', 'paddingRight': '0', 'paddingLeft': '0'})


def create_graphs_layout(suffix=''):
    return dbc.Col([dcc.Loading(
        children=[
            dbc.Row(children=[dbc.Col(children=[html.H6(_('Intervention distribution')),
                                                dcc.Graph(id=f'indicator-graphic2{suffix}',
                                                          className='row')],
                                      style={'marginTop': '20px', 'flex': 1}),
                              dbc.Col(children=[html.H6(_('Flight exclusions')),
                                                dcc.Graph(id=f'indicator-graphic1{suffix}',
                                                          className='row')],
                                      style={'marginTop': '20px', 'flex': 1}),

                              # dbc.Col(children=[html.H6(_('Intervention distribution')),
                              #                   sankey.Sankey(
                              #                       id=f'flows-graphic{suffix}',
                              #                       width=500, height=500, ),
                              #                   ], style={'marginTop': '20px', 'flex': 1},
                              #         className='row')
                              ],
                    style={'marginTop': '20px', 'paddingRight': '20px', 'paddingLeft': '20px'}),
            dbc.Row(children=[
                dbc.Col(children=[html.H6(_('Time to arrival histogram when a drone is sent')),
                                  dcc.Graph(id=f'indicator-graphic3{suffix}', className='row')],
                        style={'marginTop': '20px', 'flex': 1}),
                dbc.Col(children=[html.H6(_('Comparison of times to arrival for all incidents')),
                                  html.Small(html.I(_('Hover over the graph to get more info'))),
                                  dcc.Graph(id=f'indicator-graphic4{suffix}', className='row')],
                        style={'marginTop': '20px', 'flex': 1})],
                    style={'marginTop': '20px', 'paddingRight': '20px', 'paddingLeft': '20px'})],
        style={'paddingRight': '20px', 'paddingLeft': '20px'})])


def create_both_graphs(name, suffix='', style=None):
    return dbc.Container([
        html.H3(_('Simulation ') + name),
        dcc.Loading(children=[
            dbc.Col(children=[html.H6(_('Intervention distribution')),
                              dcc.Graph(id=f'indicator-graphic2u{suffix}', className='row')]),
            dbc.Col(children=[html.H6(_('Flight exlcusions')),
                              dcc.Graph(id=f'indicator-graphic1u{suffix}', className='row')]),
            # dbc.Col(children=[html.H6(_('Intervention distribution')),
            #                   sankey.Sankey(
            #                       id=f'flows-graphicu{suffix}',
            #                       width=500, height=500)]),
            dbc.Col(children=[html.H6(_('Time to arrival histogram when a drone is sent')),
                              dcc.Graph(id=f'indicator-graphic3u{suffix}', className='row')]),
            dbc.Col(children=[html.H6(_('Comparison of times to arrival for all incidents')),
                              dcc.Graph(id=f'indicator-graphic4u{suffix}')]),
        ]),
    ], style={'flex': 1} if style is None else dict(style, flex=1))


def create_title():
    return html.Div(
        children=[
            dbc.Row(
                dbc.Col(children=[html.A(html.Img(src='../assets/fr.gif', alt='fr'),
                                         href='https://airborne-aed.org/fr/',
                                         style={'margin-right': '10px'}
                                         ),
                                  html.A(html.Img(src='../assets/en.gif', alt='en'),
                                         href='https://airborne-aed.org/en/'
                                         )], align='end')),
            dbc.Row(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(
                                html.A(html.Img(src='../assets/logo-bspp.png', width='70%'),
                                       href='https://www.pompiersparis.fr/fr/'),
                                width=2,
                                style={'justifyContent': 'spaceBetween',
                                       'margin-right': '20', 'paddingLeft': '0'}),
                            dbc.Col(html.H1(_('Airborne AED simulation')), width=8),
                            dbc.Col(children=[
                                html.A(
                                    html.Img(src='../assets/logo_bayes_impact.png', width='70%'),
                                    href='https://www.bayesimpact.org/')
                            ],
                                width=2,
                                style={'justifyContent': 'spaceBetween',
                                       'margin-right': '20', 'paddingLeft': '0'})],
                        align='center',
                        style={'display': 'flex', 'text-align': 'center'}),
                    html.A(
                        _('Fork me on GitHub'),
                        href='https://github.com/AlbaneMiron/drone-simulation',
                        className='github-fork-ribbon',
                        style={'position': 'fixed'},
                        **{'data-ribbon': _('Fork me on GitHub')})
                ],
                style={'display': 'flex', 'justifyContent': 'spaceBetween',
                       'paddingRight': '0', 'paddingLeft': '0', 'md': '11'},
                className='title'
            ),
        ]
    )


def create(lang):
    desc_file = '../../assets/tab-layout2.png'
    if lang == 'fr':
        desc_file = '../../assets/tab-layout2fr.png'
    lang = gettext.translation('messages', localedir='locales', languages=[lang], fallback=True)
    lang.install()
    return dbc.Col(
        children=[
            create_title(),
            dbc.Col(
                id='vp-control-tabs', className='control-tabs',
                children=[create_tabs_layout(desc_file)],
                style={'marginTop': '20px', 'paddingRight': '0', 'paddingLeft': '0'})
        ],
        style={'paddingTop': '20px', 'paddingLeft': '20px'})
