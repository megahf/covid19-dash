import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import numpy as np
from datetime import datetime, timedelta


def prepare_daily_report():

    current_date = (datetime.today() - timedelta(days=1)).strftime('%m-%d-%Y')

    df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/' + current_date + '.csv')
    df_country = df.groupby(['Country_Region']).sum().reset_index()
    df_country.replace('US', 'United States', inplace=True)
    df_country.replace(0, 1, inplace=True)
    
    code_df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_with_codes.csv')
    code_df_unique = code_df[["country", "iso_alpha"]].drop_duplicates()
    code_df_unique = code_df_unique.append({'country': 'Russia', 'iso_alpha': 'RUS'}, ignore_index=True)
    

    df_country_code = df_country.merge(code_df_unique, left_on='Country_Region', right_on='country')
    df_country_code.to_csv('df_processed.csv')
    return(df_country_code)

def prepare_confirmed_data():
    us_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv')
    us_df_agg = us_df.groupby(['Country_Region']).sum().reset_index()
    us_df_agg.replace('US', 'United States', inplace=True)
    us_df_agg.rename(columns={'Country_Region': 'Country/Region'}, inplace=True)

    df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
    df_country = df.groupby(['Country/Region']).sum().reset_index()

    df_all_country = pd.concat([us_df_agg, df_country], axis=0)

    
    code_df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_with_codes.csv')
    code_df_unique = code_df[["country", "iso_alpha"]].drop_duplicates()

    df_country_code = df_all_country.merge(code_df_unique, left_on='Country/Region', right_on='country')

    return (df_country_code)



df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_with_codes.csv')



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Covid19-Dash'


app.layout = html.Div([html.Div([html.H1("COVID19 Impact by Country")],
                                style={'textAlign': "center", "padding-bottom": "30"}),
                       html.Div([html.Span("Metric to display : ", className="six columns",
                                           style={"text-align": "right", "width": "40%", "padding-top": 10}),
                                 dcc.Dropdown(id="value-selected", value='Confirmed',
                                              options=[{'label': "Confirmed ", 'value': 'Confirmed'},
                                                       {'label': "Recovered ", 'value': 'Recovered'},
                                                       {'label': "Deaths ", 'value': 'Deaths'},
                                                       {'label': "Active ", 'value': 'Active'}],
                                              style={"display": "block", "margin-left": "auto", "margin-right": "auto",
                                                     "width": "70%"},
                                              className="six columns")], className="row"),
                       dcc.Graph(id="my-graph")
                       ], className="container")


@app.callback(
    dash.dependencies.Output("my-graph", "figure"),
    [dash.dependencies.Input("value-selected", "value")]
)
def update_figure(selected):
    #dff = prepare_confirmed_data()

    dff = prepare_daily_report()
    dff['hover_text'] = dff["Country_Region"] + ": " + dff[selected].apply(str)

    trace = go.Choropleth(locations=dff['iso_alpha'],z=np.log(dff[selected]),
                          text=dff['hover_text'],
                          hoverinfo="text",
                          autocolorscale=False,
                          reversescale=True,
                          colorscale="RdBu",marker={'line': {'color': 'rgb(180,180,180)','width': 0.5}},
                          colorbar={"thickness": 10,"len": 0.3,"x": 0.9,"y": 0.7,
                                    'title': {"text": 'persons', "side": "bottom"},
                                    'tickvals': [ 2, 10],
                                    'ticktext': ['100', '100,000']})   
    return {"data": [trace],
            "layout": go.Layout(height=800,geo={'showframe': False,'showcoastlines': False,
                                                                      'projection': {'type': "miller"}})}

if __name__ == '__main__':
    app.run_server(debug=True)
