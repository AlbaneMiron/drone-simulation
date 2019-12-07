import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash.Dash(  # pylint: disable=invalid-name
    __name__,
    external_stylesheets=[dbc.themes.CERULEAN])  # ['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.config.suppress_callback_exceptions = True

app.title = 'Airborne AED Simulation'
