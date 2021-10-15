import numpy as np
import dash_core_components as dcc
import dash_html_components as html
from datetime import date, timedelta
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import plotly.express as px
from .utils import strdate2date
from plotly.subplots import make_subplots

####### for easychari submission
from plotly.validators.scatter.marker import SymbolValidator
raw_symbols = SymbolValidator().values
namestems = []
namevariants = []
symbols = []
for i in range(0,len(raw_symbols),3):
    name = raw_symbols[i+2]
    symbols.append(raw_symbols[i])
    namestems.append(name.replace("-open", "").replace("-dot", ""))
    namevariants.append(name[len(namestems[-1]):])

newsymbols = []
for i in range(len(symbols)):
    if not (( i % 4 == 2 ) or ( i % 4 == 3)):
        newsymbols.append(symbols[i])

main = html.Div([
    html.Div([
        dbc.Row([
            dbc.Col([
                html.Label(['Time window range:']),
                dcc.DatePickerRange(
                    id='main_date_picker',
                    # day_size = 62,
                    display_format='DD, MMM, YYYY' ,
                    min_date_allowed=date(2020, 3, 13),
                    max_date_allowed=date.today() - timedelta(days=10),
                    # initial_visible_month=date(2019, 1, 1),
                    end_date=date(2020,5,3),
                    start_date=date(2020, 3, 18),
                    number_of_months_shown =2,
                    show_outside_days = True,
                    style = {'width':"100%"}
                )
            ],width=6),

            dbc.Col([
                html.Label(['Select state:']),
                dcc.Dropdown(
                    id='main_dropdown',
                    options=[
                        {'label': 'Johor', 'value':'Johor'},
                        {'label': 'Kedah', 'value':'Kedah'},
                        {'label': 'Kelantan', 'value':'Kelantan'},
                        {'label': 'Melaka', 'value':'Melaka'},
                        {'label': 'Negeri Sembilan', 'value':'Negeri Sembilan'},
                        {'label': 'Pahang', 'value':'Pahang'},
                        {'label': 'Perak', 'value':'Perak'},
                        {'label': 'Perlis', 'value':'Perlis'},
                        {'label': 'Pulau Pinang', 'value':'Pulau Pinang'},
                        {'label': 'Sabah', 'value':'Sabah'},
                        {'label': 'Sarawak', 'value':'Sarawak'},
                        {'label': 'Selangor', 'value':'Selangor'},
                        {'label': 'Terengganu', 'value':'Terengganu'},
                        {'label': 'Kuala Lumpur', 'value':'Kuala Lumpur'},
                        {'label': 'Labuan', 'value':'Labuan'},
                        {'label': 'Putrajaya', 'value':'Putrajaya'}
                    ],
                    value = 'Johor',
                    multi = False,
                    clearable=False,
                    style = {'width':"70%"}
                )
            ], width=True),
            
        ])
        
    ]),

    # html.Div([
        
    # ]),

    dcc.Loading(
        type="circle", 
        fullscreen=False,
        children=html.Div([
            html.Div([
                dcc.Graph(id='scatter_cov')
            ]),
            
            html.Div([
                dcc.Graph(id='heatmap')
            ]),        
        ])
    ),

    
    

    

    # html.Div([
    #     dbc.Table(
    #         id='covid_table',
    #         bordered=True,
    #         # dark=True,
    #         hover=True,
    #         responsive=True,
    #         striped=True 
    #     )
    # ])
])

##call back function
def main_callback(app):
    @app.callback(
    [Output('heatmap', 'figure'),
    # Output('covid_table', 'children'),
    Output('scatter_cov', 'figure')],
    [Input('main_dropdown', 'value'),
    Input('main_date_picker', 'start_date'),
    Input('main_date_picker', 'end_date')]
    )
    def update_heatmat(state, start, end):
        with app.server.app_context():
            from ..models.corr_matrix import corr_grabber
            c = corr_grabber()
            (cdf, pdf) = c.corr_matrix(state)
            (corr, pval, corr_tot, pval_tot) = c.calc_cov(strdate2date(start), strdate2date(end), state)
            # c.kill_self()
            
        fig = go.Figure(
            data=go.Heatmap(
                x=cdf.columns,
                y=cdf.columns,
                z=cdf,
                zmax=1,
                zmin=-1,
                # hoverinfo='text',
                hovertemplate ='%{z:.2f} %{x}, %{y}  <extra></extra>'
            ),
            layout_title_text='Weather variables correlation matrix'
        )
        # cov_df = {
        #     'x' : corr,
        #     'y' : pval, 
        #     'name' : 'AAA',
        #     'mode':'markers'
        #     # 'Category' : cdf.columns
        # }

        tot_df ={
            'x' : corr_tot,
            'y': pval_tot,
            'name': 'BBB',
            'mode':'markers'
            # 'Category' : cdf.columns
        }

        line_colors = ['red', 'blue', 'yellow', 'gray', 'pink', 'brown', 'green', 'black', 'purple', 'lime', 'dimgray', 'deepskyblue','yellowgreen', 'turquoise', 'springgreen', 'slategrey', 'slateblue', 'peachpuff', 'papayawhip', 'palevioletred', 'navy', 'navajowhite']
        figs = make_subplots(rows=1, cols=2, subplot_titles=("Weather variables VS Covid death case", "Weather variables VS Covid total case"))
        for i in range(len(corr)):
            if pval[i] <0.05:
                op1 = 0.2  
            else:
                op1=1
            figs.add_trace(
                go.Scatter(
                    x = [corr[i]],
                    y = [pval[i]],
                    opacity=op1,
                    name = cdf.columns.tolist()[i],
                    legendgroup = cdf.columns.tolist()[i],
                    line_color = line_colors[i],
                    mode = 'markers',
                    marker_symbol = newsymbols[i],
                    hoverinfo='text + x',
                    hovertext = cdf.columns.tolist()[i]
                ),
                row=1, col=1
            )
            if pval_tot[i] <0.05:

                op2 =0.2  
            else: 
                op2=1

            figs.add_trace(
                go.Scatter(
                    x = [corr_tot[i]],
                    y = [pval_tot[i]],
                    
                    opacity=op2,
                    name = cdf.columns.tolist()[i],
                    legendgroup = cdf.columns.tolist()[i],
                    line_color = line_colors[i],
                    mode = 'markers',
                    marker_symbol = newsymbols[i],
                    showlegend=False,
                    hoverinfo='text+x',
                    hovertext = cdf.columns.tolist()[i]
                ),
                row=1, col=2
            )

        figs.add_trace(
            go.Scatter(
                x = [-1,1],
                y = [0.05, 0.05],
                
                # name = cdf.columns.tolist()[i],
                # legendgroup = cdf.columns.tolist()[i],
                line_color = line_colors[-1],
                showlegend=False,

                mode = 'lines',
                # hoverinfo='text',
                # hovertext = cdf.columns.tolist()[i]
            ),
            row=1, col=1
        )

        figs.add_trace(
            go.Scatter(
                x = [-1,1],
                y = [0.05, 0.05],
                # name = cdf.columns.tolist()[i],
                # legendgroup = cdf.columns.tolist()[i],
                line_color = line_colors[-1],
                mode = 'lines',
                showlegend=False,
                # hoverinfo='text',
                # hovertext = cdf.columns.tolist()[i]
            ),
            row=1, col=2
        )

        # Update xaxis properties
        figs.update_xaxes(title_text="Correlation",range=[-1,1], row=1, col=1)
        figs.update_xaxes(title_text="Correlation", range=[-1, 1], row=1, col=2)
        # Update yaxis properties
        figs.update_yaxes(title_text="P-Value", range=[-0.1,1], row=1, col=1)
        figs.update_yaxes(title_text="P-Value", range=[-0.1, 1], row=1, col=2)
           # figs.add_trace(
        #     go.Scatter(tot_df,
        #     # title='Covid total case X Meteorological variables',
        #     # x="Correlation",
        #     # y="P value",
        #     # color="Category",
        #     # range_x=[-1, 1],
        #     # labels={"Category": "Parameter"}
        #     ),
        #     row=1, col=1
        # )

        # fig2 = px.scatter(cov_df,
        #     title='Covid fatality X Meteorological variables',
        #     x="Correlation",
        #     y="P value",
        #     color="Category",
        #     range_x=[-1, 1],
        #     labels={"Category": "Parameter"})

        #define table
        
        # table_header = [
        #     html.Thead(
        #         [html.Td(head) for head in cdf.columns]
        #     )
        # ]

        # table_body = [
        #     html.Tbody([
        #         html.Tr([
        #             html.Td(html.P('{:2.2e}'.format(i))) for i in corr
        #         ]),
        #         html.Tr([
        #             html.Td(html.P('{:2.2e}'.format(i))) for i in pval
        #         ])
        #     ])
        # ]

        return fig, figs #table_header + table_body
