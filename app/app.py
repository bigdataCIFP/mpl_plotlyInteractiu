import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
from datetime import date,datetime,timedelta
from flask import Flask


# Load data
df=pd.read_excel("REEmallorca_012021.xlsx")
df['tiempo']=pd.to_datetime(df['tiempo'])
df.sort_values(by='tiempo',inplace=True)
df.set_index('tiempo',inplace=True)
dfdia=df.loc['2021-01-10']
dfpie=dfdia.drop(['CODIGO','demanda','enlace_mallibi','enlace_mallmen'], axis=1)
labelsPie=[]
valoresPie=[]
labelsSelector=[]
for c in dfpie.columns:
    valor=dfpie[c].sum()
    if valor>0:
        labelsPie.append(c)
        valoresPie.append(valor)
        labelsSelector.append({'label':c,'value':c})
dmax=int(dfdia['demanda'].max())
dmin=int(dfdia['demanda'].min())
dmean=int(dfdia['demanda'].mean())

# Initialize the app
server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'mpl_plotlyInteractiu'
app.config.suppress_callback_exceptions = True

navbar = dbc.Navbar(
    [dbc.NavbarBrand("Demanda Elèctrica Mensual Mallorca ", className="ms-2",style={'textAlign': 'center','height':'80px'}),
    dcc.DatePickerSingle( id='date-picker', date=date(2021, 1, 10),style={'backgroundColor': '#1E1E1E','width':'100px'})
    ],
    color="info",
    dark=True
)

grafica1=dcc.Graph(id='grafica1', 
                    figure = {'data':[
                            go.Scatter(
                            x=dfdia.index,
                            y=dfdia['demanda'],
                            mode='lines',
                            )],
                    'layout':go.Layout(xaxis = {'title':'Tiempo'},yaxis = {'title':'Demanda Elèctrica [MWh]'},title="Demanda")}
        )
grafica2=dcc.Graph(id='grafica2', 
        figure = {'data':[go.Pie(labels=labelsPie,values=valoresPie)],
            'layout':go.Layout(
                  colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                  plot_bgcolor='rgba(100, 100, 100, 100)',title="Estructura de la generació"
                  )}
    )

selectorPie=dcc.Dropdown(id='tempselector', options=labelsSelector,value=labelsPie
            ,multi=True, className='stockselector')


app.layout =  html.Div(children=[navbar,
    dbc.Row([
        dbc.Col(html.Div([grafica1]),width=4),
        dbc.Col(html.Div([selectorPie,grafica2]),width=5),
        dbc.Col(html.Div([html.Br(),
            dbc.Alert([html.H5("Demanda Màxima", className="alert-heading",style={'textAlign': 'center'}),html.H3(str(dmax)+" MWh",id="dmax",style={'textAlign': 'center'})]),
            dbc.Alert([html.H5("Demanda Mínima", className="alert-heading",style={'textAlign': 'center'}),html.H3(str(dmin)+" MWh",id="dmin",style={'textAlign': 'center'})]),
            dbc.Alert([html.H5("Demanda Mitjana", className="alert-heading",style={'textAlign': 'center'}),html.H3(str(dmean)+" MWh",id="dmean",style={'textAlign': 'center'})])

            ]),width=3)]),
    dbc.Row([
        dbc.Col(html.Div([dbc.Alert("Dissenyat per JL Merino", color="dark")]),width=12)
    ])
    ])

@app.callback(Output('grafica1', 'figure'),
                Output('dmax', 'children'),
                Output('dmin', 'children'),
                Output('dmean', 'children'),
              [Input('date-picker', 'date')])
def update_graph(date_picker):
    dfdia=df.loc[date_picker]
    dmax=str(int(dfdia['demanda'].max()))+" MWh"
    dmin=str(int(dfdia['demanda'].min()))+" MWh"
    dmean=str(int(dfdia['demanda'].mean()))+" MWh"
    figure = {'data':[
                            go.Scatter(
                            x=dfdia.index,
                            y=dfdia['demanda'],
                            mode='lines',
                            )],
                    'layout':go.Layout(xaxis = {'title':'Tiempo'},yaxis = {'title':'Demanda Elèctrica [MWh]'},title="Demanda")}
    #figure.update_layout(legend_x=0,legend_y=1)
    return figure,dmax,dmin,dmean

@app.callback(Output('grafica2', 'figure'),
              [Input('date-picker', 'date'),
              Input('tempselector', 'value')])
def update_graph(date_picker,sel):
    dfdia=df.loc[date_picker]
    dfpie=dfdia.drop(['CODIGO','demanda','enlace_mallibi','enlace_mallmen'], axis=1)
    labelsPie=[]
    valoresPie=[]
    for c in sel:
        valor=dfpie[c].sum()
        if valor>0:
            labelsPie.append(c)
            valoresPie.append(valor)
    figure = {'data':[go.Pie(labels=labelsPie,values=valoresPie)],
            'layout':go.Layout(
                  colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                  plot_bgcolor='rgba(100, 100, 100, 100)',title="Estructura de la generació"
                  )}  #figure.update_layout(legend_x=0,legend_y=1)
    return figure


if __name__ == '__main__':
    app.run_server()
