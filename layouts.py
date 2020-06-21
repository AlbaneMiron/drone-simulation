import gettext
import textwrap
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import sankey
import drones

_POSITIONS = list(drones.STARTING_POINTS.keys())


def create_tabs_layout(simu_desc_file):
    # return dbc.Container(id='app-control-tabs', className='control-tabs', children=[
    return dbc.Tabs(id='app-tabs', children=[
        dbc.Tab(
            label=_('About'),
            tab_id='what-is',
            children=dbc.Container(className='control-tab', children=[
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

            ], style={'margin-top': '10px',
                      'padding-right': '0', 'padding-left': '0'})

        ),

        dbc.Tab(
            label=_('Simulation description'),
            tab_id='datasets',
            children=dbc.Container(className='control-tab', children=[
                html.H4(className='datasets',
                        children=_('Rescue chain: BLS teams vs drones')),
                html.Img(src=simu_desc_file,
                         style={'max-width': '100%', 'max-height': '100%'}),
            ], style={'margin-top': '10px',
                      'padding-right': '0', 'padding-left': '0'}),
        ),

        dbc.Tab(
            label=_('Parameters simulation A'),
            tab_id='simA',
            children=dbc.Container(
                create_parameters_layout('A')),
        ),
        dbc.Tab(
            label=_('Parameters simulation B'),
            tab_id='simB',
            children=dbc.Container(
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
                        'border-right': 'solid 1px #ddd',
                        'margin-right': '15px',
                        'padding-right': '15px',
                    }),
                    create_both_graphs('B', suffix='_b'),
                ],
                style={'display': 'flex', 'margin-top': '10px',
                       'padding-right': '0', 'padding-left': '0'}),
        ),

        dbc.Tab(
            label=_('Custom Datasets'),
            tab_id='data',
            children=dbc.Container([
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
                    'Upload a CSV file containing a list of incidents. Each row represents '
                    'one incident and should contain the following fields:'
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
                ]),
                dcc.Upload(
                    id='upload-incidents',
                    children=html.Div([
                        _('Drag and Drop or '),
                        html.A(html.Button(_('Select a File'))),
                        # TODO(pascal): Handle custom incidents.
                        'Coming soon…'
                    ]),
                    disabled=True,
                ),
                html.Div(id='output-incidents-upload'),
            ], style={'margin-top': '10px',
                      'padding-right': '0', 'padding-left': '0'}),
        ),
    ], style={'margin-top': '10px',
              'padding-right': '0', 'padding-left': '0'})
    #   ,
    # ], style={'margin-top': '15px', 'padding-right': '0', 'padding-left': '0'})


def create_parameters_layout(name, suffix='', input_drone=_POSITIONS[0]):
    return dbc.Col([
        dbc.Col([
            dbc.Col(children=[html.H3(_('Simulation ') + name),
                              html.P(html.Small(html.I(_(
                                  'You can get additional info '
                                  'on parameters descriptions by hovering '
                                  'your mouse over '
                                  'each of them.'))))],
                    style={
                        'margin-right': '15px',
                        'padding-right': '0',
                        'padding-left': '0'}),
            dbc.Row([
                dbc.Col([
                    html.H6(_('Drone parameters')),
                    html.Div([
                        html.Label(_('Initial drone location'), id='ini_pos'),
                        dbc.Tooltip(
                            _('Where drones are stationed. '
                              'The simulator selects the closest available '
                              'drone (as the crow flies)'),
                            target='ini_pos',
                            placement='left')]),
                    dcc.Dropdown(
                        id=f'input_drone{suffix}',
                        # TODO(pascal): Translate labels here.
                        options=[{'label': i, 'value': i} for i in _POSITIONS],
                        value=input_drone,
                        clearable=False,
                        style={'width': '250px'}
                    ),
                    # dbc.FormGroup
                    html.Div([
                        html.Label(_('Max drone speed (in km/h)'), id='speed_e'),
                        dbc.Tooltip(
                            _('Maximum horizontal speed'),
                            target='speed_e',
                            placement='left')]),
                    dbc.Input(id=f'speed{suffix}', value='80',
                              type='text',
                              style={'width': '70px'}),

                    html.Div([
                        html.Label(_("Drone's acceleration time (in sec):"), id='acc_e'),
                        dbc.Tooltip(
                            _('Time needed for the drone to reach its maximum horizontal speed.'),
                            target='acc_e',
                            placement='left')]),
                    dbc.Input(id=f'acc{suffix}', value='5',
                              type='text',
                              style={'width': '70px'}),

                    html.Div([
                        html.Label(_("Drone's vertical speed (in m/s):"), id='vert-acc_e'),
                        dbc.Tooltip(
                            _('Maximum vertical speed. It is assumed that the time needed for the '
                              'drone to reach this speed is negligible.'),
                            target='vert-acc_e',
                            placement='left')]),
                    dbc.Input(id=f'vert-acc{suffix}', value='9',
                              type='text',
                              style={'width': '70px'}),

                    html.Div([
                        html.Label(_("Drone's cruise altitude (in m):"), id='alt_e'),
                        dbc.Tooltip(
                            _('Horizontal cruise altitude'),
                            target='alt_e',
                            placement='left')]),
                    dbc.Input(id=f'alt{suffix}', value='100',
                              type='text',
                              style={'width': '70px'}),

                    html.Div([
                        html.Label(_('Unavailability of the drone after a run (in h):'),
                                   id='unav_e'),
                        dbc.Tooltip(
                            _('Time needed after a run for the drone to be available again. It '
                              'accounts for the time spent on the OHCA location and the time of '
                              'refurbishment and rehabilitation of equipment.'),
                            target='unav_e',
                            placement='left')]),
                    dbc.Input(id=f'unavail_delta{suffix}', value='6',
                              type='text',
                              style={'width': '70px'}),

                    html.Div([
                        html.Label(_('Drone can fly during aeronautical night'), id='day_e'),
                        dbc.Tooltip(
                            _('Whether the drone can only fly during the aeronautical day or not'),
                            target='day_e',
                            placement='left')]),
                    dcc.RadioItems(
                        id=f'day{suffix}',
                        options=[
                            {'label': ' ' + _('Yes'), 'value': 'Oui'},
                            {'label': ' ' + _('No'), 'value': 'Non'},
                        ],
                        value='Non',
                        labelStyle={'display': 'inline-block', 'margin-right': '1em'},
                    ), ]),
                dbc.Col(children=[
                    html.H6(_('Operational parameters')),

                    html.Div([
                        html.Label(_('Delay at departure (in s):'), id='dep_e'),
                        dbc.Tooltip(
                            _('Delay at departure needed for the operator to '
                              'set up flight information '
                              'for the drone then for the fire station '
                              'where the drone is stationed to '
                              'launch it.'),
                            target='dep_e',
                            placement='left')]),
                    dbc.Input(id=f'dep_delay{suffix}', value='15',
                              type='text',
                              style={'width': '70px'}),

                    html.Div([
                        html.Label(_('Delay on arrival (in s):'), id='arr_e'),
                        dbc.Tooltip(
                            _('Delay on arrival needed for the drone to narrow its landing and for '
                              'the bystander to catch the AED.'),
                            target='arr_e',
                            placement='left')]),
                    dbc.Input(id=f'arr_delay{suffix}', value='15',
                              type='text',
                              style={'width': '70px'}),

                    html.Div([
                        html.Label(
                            _('Delay between detection of unconsciousness '
                              'and OHCA detection (in s):'),
                            id='del_e'),
                        dbc.Tooltip(
                            _('Mean time spent between unconsciousness and OHCA detection by '
                              'emergency call dispatchers. Unconsciousness detection activates BLS '
                              'teams whereas drones are activated only at OHCA detection.'),
                            target='del_e',
                            placement='left')]),
                    dbc.Input(id=f'detec_delay{suffix}', value='104',
                              type='text',
                              style={'width': '70px'}),

                    html.Div([
                        html.Label(
                            _('Rate of OHCA at home, which are detected by call center operators '
                              '(between 0 and 1):'),
                            id='deth_e'),
                        dbc.Tooltip(
                            _('When the OHCA is not detected by '
                              'the emergency dispatchers no drone is '
                              'sent.'),
                            target='deth_e',
                            placement='left')]),
                    dbc.Input(id=f'detec_rate_home{suffix}', value='0.87',
                              type='number', max=1, min=0, step=0.01,
                              style={'width': '70px'}),

                    html.Div([
                        html.Label(
                            _('Rate of OHCA in the streets, which are detected by call center '
                              'operators (between 0 and 1):'),
                            id='dets_e'),
                        dbc.Tooltip(
                            _('When the OHCA is not detected by '
                              'the emergency dispatchers no drone is '
                              'sent.'),
                            target='dets_e',
                            placement='left')]),
                    dbc.Input(id=f'detec_rate_vp{suffix}', value='0.71',
                              type='number', max=1, min=0, step=0.01,
                              style={'width': '70px'}),

                    html.Div([
                        html.Label(
                            _('Rate of OHCA at home, which only have '
                              'one witness alone (between 0 and '
                              '1):'),
                            id='wit_e'),
                        dbc.Tooltip(
                            _('The simulation requires at least two witnesses for '
                              'OHCA at home : one '
                              'to stay near the victim, the other '
                              'to go out in the street to get the '
                              'AED brought by drone.'),
                            target='wit_e',
                            placement='left')]),
                    dbc.Input(id=f'wit_detec{suffix}', value='0.58',
                              type='number', max=1, min=0, step=0.01,
                              style={'width': '70px'}),

                ], style={'flex': 1}),
            ], style={
                'margin-right': '15px',
                'padding-right': '0',
            }),
            dbc.Button(
                id=f'seq_start{suffix}', n_clicks=0,
                children=_('Update simulation'), block='center',
                style={'flex': 1, 'margin-top': '20px', 'margin-bottom': '20px'}
            ), ]),
        dbc.Row(children=create_graphs_layout(
            suffix=suffix
        ))
    ], style={
        # 'display': 'flex', #'flex': 'auto',
        'margin-top': '20px', 'padding-right': '0', 'padding-left': '0'})


def create_graphs_layout(suffix=''):
    return dcc.Loading(children=[
        dbc.Col(children=[html.H6(_('Flight exclusions')),
                          dcc.Graph(id=f'indicator-graphic1{suffix}', className='row')]),
        dbc.Col(children=[html.H6(_('Time to arrival histogram when a drone is sent')),
                          dcc.Graph(id=f'indicator-graphic3{suffix}', className='row')]),
        dbc.Col(children=[html.H6(_('Comparison of times to arrival for all incidents')),
                          html.P(html.Small(html.I(_('Hover over the graph to get more info')))),
                          dcc.Graph(id=f'indicator-graphic4{suffix}', className='row')]),
        dbc.Col(children=[html.H6(_('Intervention distribution')),
                          sankey.Sankey(
                              id=f'flows-graphic{suffix}',
                              width=500, height=500,)],
                className='row')
    ])


def create_both_graphs(name, suffix='', style=None):
    return dbc.Container([
        html.H3(_('Simulation ') + name),
        dcc.Loading(children=[
            dbc.Col(children=[html.H6(_('Flight exlcusions')),
                              dcc.Graph(id=f'indicator-graphic1u{suffix}', className='row')]),
            dbc.Col(children=[html.H6(_('Intervention distribution')),
                              sankey.Sankey(
                                  id=f'flows-graphicu{suffix}',
                                  width=500, height=500)]),
            dbc.Col(children=[html.H6(_('Time to arrival histogram when a drone is sent')),
                              dcc.Graph(id=f'indicator-graphic3u{suffix}', className='row')]),
            dbc.Col(children=[html.H6(_('Comparison of times to arrival for all incidents')),
                              dcc.Graph(id=f'indicator-graphic4u{suffix}')]),
        ]),
    ], style={'flex': 1} if style is None else dict(style, flex=1))


def create(lang):
    desc_file = '../../assets/tab-layout2.png'
    if lang == 'fr':
        desc_file = '../../assets/tab-layout2fr.png'
    lang = gettext.translation('messages', localedir='locales', languages=[lang], fallback=True)
    lang.install()
    return dbc.Col(
        children=[
            dbc.Col(
                className='title',
                children=[
                    html.H1(_('Airborne AED simulation')),
                    html.A(
                        _('Fork me on GitHub'),
                        href='https://github.com/AlbaneMiron/drone-simulation',
                        className='github-fork-ribbon',
                        **{'data-ribbon': _('Fork me on GitHub')}
                    ),
                ],
                style={'display': 'flex', 'justify-content': 'space-between',
                       'padding-right': '0', 'padding-left': '0'}
            ),
            dbc.Col(
                id='vp-control-tabs', className='control-tabs',
                children=[create_tabs_layout(desc_file)],
                style={'margin-top': '20px', 'padding-right': '0', 'padding-left': '0'})],
        style={'padding-top': '20px', 'padding-left': '20px'})
