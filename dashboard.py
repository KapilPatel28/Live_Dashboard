import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import requests
import plotly.graph_objs as go

# API URL
api_url = "https://api.thingspeak.com/channels/1596152/feeds.json?results=10"  # Fetch the last 10 records

# Fetch data from the API
def fetch_data():
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()["feeds"]
            return {
                "PM2.5": [float(entry.get("field1", 0)) for entry in data],
                "PM10": [float(entry.get("field2", 0)) for entry in data],
                "Ozone": [float(entry.get("field3", 0)) for entry in data],
                "Humidity": [float(entry.get("field4", 0)) for entry in data],
                "Temperature": [float(entry.get("field5", 0)) for entry in data],
                "CO": [float(entry.get("field6", 0)) for entry in data],
                "time": [entry.get("created_at", "N/A") for entry in data],
            }
    except Exception as e:
        print(f"Error fetching data: {e}")
    return {}

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Live Environmental Dashboard"

# Layout of the dashboard (6x1 grid)
app.layout = html.Div([
    html.H1("Live Environmental Data Dashboard", style={"textAlign": "center", "color": "white"}),
    html.Div([
        dcc.Graph(id="pm25-graph"),
        dcc.Graph(id="pm10-graph"),
        dcc.Graph(id="ozone-graph"),
        dcc.Graph(id="humidity-graph"),
        dcc.Graph(id="temperature-graph"),
        dcc.Graph(id="co-graph"),
    ], style={"display": "grid", "gridTemplateColumns": "1fr", "gap": "20px"}),  # 1-column layout
    dcc.Interval(id="interval-component", interval=10*1000, n_intervals=0)  # Refresh every 10 seconds
], style={"backgroundColor": "#121212", "padding": "20px"})

# Update graphs
@app.callback(
    [
        Output("pm25-graph", "figure"),
        Output("pm10-graph", "figure"),
        Output("ozone-graph", "figure"),
        Output("humidity-graph", "figure"),
        Output("temperature-graph", "figure"),
        Output("co-graph", "figure"),
    ],
    [Input("interval-component", "n_intervals")]
)
def update_graphs(n):
    data = fetch_data()
    
    def create_figure(key, name):
        return {
            "data": [
                go.Scatter(
                    x=data["time"],
                    y=data[key],
                    mode="lines+markers",
                    name=name,
                    marker={"color": "rgb(0, 204, 255)"},
                )
            ],
            "layout": go.Layout(
                title=f"{name} Over Time",
                xaxis={"title": "Time", "tickangle": -45},
                yaxis={"title": name},
                height=400,
                paper_bgcolor="#121212",  # Dark background for graph
                plot_bgcolor="#121212",
                font={"color": "white"},
                margin={"b": 50},  # Add some margin to avoid text overlap
            )
        }

    return [
        create_figure("PM2.5", "PM2.5"),
        create_figure("PM10", "PM10"),
        create_figure("Ozone", "Ozone"),
        create_figure("Humidity", "Humidity"),
        create_figure("Temperature", "Temperature"),
        create_figure("CO", "CO"),
    ]

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8000)

