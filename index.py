import os

from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from app import app
import callbacks  # pylint: disable=unused-import
import layouts


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='lang', style=dict(display='none')),
    html.Div(id='page-content')
])


@app.callback(
    Output('lang', 'children'),
    [Input('url', 'pathname')])
def pick_lang(pathname):
    if pathname == '/fr/':
        return 'fr'
    return 'en'


@app.callback(
    Output('page-content', 'children'),
    [Input('lang', 'children')])
def display_page(lang):
    if not lang:
        return '404'
    return layouts.create(lang)


# barre à 1min de gain drone + ratio


if __name__ == '__main__':
    app.run_server(
        debug=bool(os.getenv('DEBUG')),
        host=os.getenv('BIND_HOST', 'localhost'),
        port=int(os.getenv('PORT', '8050')))
