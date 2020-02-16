import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash.Dash(  # pylint: disable=invalid-name
    __name__,
    external_stylesheets=[
        dbc.themes.CERULEAN,
        {
            'href': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css',
            'rel': 'stylesheet',
            # 'integrity': 'sha384-50oBUHEmvpQ+1'
            # 'lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf',
            # 'crossorigin': 'anonymous'
        },
        {
            'href': 'https://cdnjs.cloudflare.com/ajax/libs/github-fork-ribbon-css/0.2.3/gh-fork-ribbon.min.css',
            'rel': 'stylesheet',
        },
        {
            'href': '/assets/app.css',
            'rel': 'stylesheet',
        },
    ])  # ['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.config.suppress_callback_exceptions = True

app.title = 'Airborne AED Simulation'
