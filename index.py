import os

from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from app import app
import callbacks  # pylint: disable=unused-import
import layouts


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/fr/':
        return layouts.create('fr')
    if pathname == '/en/':
        return layouts.create('en')
    return '404'

# barre à 1min de gain drone + ratio


if __name__ == '__main__':
    app.run_server(
        debug=bool(os.getenv('DEBUG')),
        host=os.getenv('BIND_HOST', 'localhost'),
        port=int(os.getenv('PORT', '8050')))
