import sankey
import dash
from dash.dependencies import Input, Output
import dash_html_components as html

app = dash.Dash(__name__)

app.layout = html.Div([
    sankey.Sankey(
        flows=[
            {'fill': 'red', 'size': 37, 'text': 'Not detected (37%)'},
            {'fill': 'blue', 'size': 35, 'text': 'Not enough witnesses (35%)'},
            {'fill': 'orange', 'size': 2, 'text': 'BLS team faster than drone (2%)'},
            {'fill': 'green', 'size': 26, 'text': 'Drone faster (26%)'},
        ],
    ),
])


if __name__ == '__main__':
    app.run_server(debug=True)
