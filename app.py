import dash


app = dash.Dash(  # pylint: disable=invalid-name
    __name__,
    external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.config.suppress_callback_exceptions = True
