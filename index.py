import os

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from layouts import layout1, layout2
import callbacks
#from apps import app_params#, app_graphs


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/app1':
         return layout1, layout2
    # elif pathname == '/apps/app2':
    #      return layout2
    else:
        return '404'

# barre à 1min de gain drone + ratio


# @app.callback(Output('page-content', 'children'),
#               [Input('url', 'pathname')])
# def display_page(pathname):
#     if pathname == '/apps/app1':
#         return app_params.layout
#     # elif pathname == '/apps/app2':
#     #     return app_graphs.layout
#     else:
#         return '404'

if __name__ == '__main__':
    app.run_server(
        debug=bool(os.getenv('DEBUG')),
        host=os.getenv('BIND_HOST', 'localhost'),
        port=int(os.getenv('PORT', '8050')))
