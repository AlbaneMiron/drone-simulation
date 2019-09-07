import os

from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from app import app
from layouts import layout_FR, layout_EN


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/app1':
        return layout_FR
    elif pathname == '/apps/app2':
        return layout_EN
    return '404'

# barre à 1min de gain drone + ratio


if __name__ == '__main__':
    app.run_server(
        debug=bool(os.getenv('DEBUG')),
        host=os.getenv('BIND_HOST', 'localhost'),
        port=int(os.getenv('PORT', '8050')))
