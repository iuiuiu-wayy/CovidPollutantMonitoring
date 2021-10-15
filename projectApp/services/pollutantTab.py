import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from datetime import date, timedelta
from projectApp.models.pollutantRecord import pollutantDF, stateDF, pollDF
from dash.dependencies import Input, Output
from .utils import strdate2date
import pandas as pd
from projectApp.models.omega import omegaDF
import plotly.express as px
from dateutil.rrule import rrule, DAILY


plot_by = ''
pollutant = html.Div([
    html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Label(['Time window range:']),
                    dcc.DatePickerRange(
                        id='pollutant-date-picker',
                        display_format='DD, MMM, YYYY' ,
                        min_date_allowed=date(2019, 1, 1),
                        max_date_allowed=date.today() - timedelta(days=10),
                        # initial_visible_month=date(2019, 1, 1),
                        end_date=date.today() - timedelta(days=10),
                        start_date=date(2019,1,1),
                        number_of_months_shown =2,
                        show_outside_days = True,
                        style = {'width':"100%"}
                    )
                ]),
            ],width=6),

            dbc.Col([
                html.Label(['Plot by:']),
                
                dcc.Dropdown(
                    id='plot_dropdown',
                    options=[
                        {'label': 'State', 'value':'state'},
                        {'label': 'Pollutant', 'value':'Pollutant'},
                    ],
                    value = 'Pollutant',
                    multi = False,
                    clearable=False,
                    # style = {'width':"50%"},
                    
                ),
            ], width=2),

            dbc.Col([

                html.Label(['Select state:'], id='select_type_label'),
                dcc.Dropdown(
                    id='pollutant_dropdown',
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
                    # style = {'width':"70%"}
                )
            ], width=2),


            dbc.Col([
                html.Label(['Smoothing:']),
                dcc.Dropdown(
                    id='smoothing_dropdown',
                    options=[
                        {'label': '28 days window', 'value':28},
                        {'label': '14 days window', 'value':14},
                        {'label': '7 days window', 'value':7},
                        {'label': 'No smoothing', 'value':'NoSmoothing'}
                    ],
                    value = 28,
                    multi = False,
                    clearable=False,
                    # style = {'width':"50%"}
                )
            ], width=2)
            
        ])
        
    ]),
    dcc.Loading(
        type="circle", 
        fullscreen=False,
        children= html.Div([
            html.Div([
                dcc.Graph(id='line_pollutant')
            ]),
            
            html.Div([
                dbc.Table(
                    id='pollutant-table',
                    bordered=True,
                    # dark=True,
                    hover=True,
                    responsive=True,
                    striped=True 
                )
            ])       
        ])
    )
])


def pollutant_callback(app):
    @app.callback(
        [Output('pollutant_dropdown', 'options'),
        Output('pollutant_dropdown', 'value'),
        Output( 'select_type_label' , 'children')],
        [Input('plot_dropdown', 'value')]
    )
    def plot_by_update(plot_type):
        if plot_type == 'state':
            label = 'Select  a state:'
            ret =[
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
                    ]
        else:
            ret = [
                {'label': 'NO2', 'value':'NO2'},
                {'label': 'O3', 'value':'O3'},
                {'label': 'SO2', 'value':'SO2'},
                {'label': 'UVAI', 'value':'UVAI'},
                {'label': 'CO', 'value':'CO'},
                {'label': 'HCHO', 'value':'HCHO'},
            ]
            label = 'Select a pollutant:'
        return ret, ret[0]['value'], label

    
    @app.callback(
        [Output('pollutant-table', 'children'),
        Output('line_pollutant', 'figure')],
        [Input('pollutant-date-picker', 'start_date'),
        Input('pollutant-date-picker', 'end_date'),
        Input('pollutant_dropdown', 'value'),
        Input('plot_dropdown', 'value'),
        Input('smoothing_dropdown', 'value')]
    )
    def update_table(start, end, lineState, plot_dropdown, smoothing):
        # with app.server.app_context():
        #     from ..models.PollutantTrends import df
        # df = app.c.DF.copy()
        # print(df.head())
        headlist = pollutantDF.PollutantID.tolist()
        headlist.insert(0,'States')
        # print(headlist)
        # header = head.insert(0, html.Td(pol))
        table_header = [
            html.Thead(
                [html.Td(pol) for pol in headlist]
            )
        ]

        sdf = (pollDF.TimeStamp > strdate2date(start)) & (pollDF.TimeStamp < strdate2date(end))
        df = pollDF.loc[sdf]
        # print(df.tail())
        sumDict = {}
        

        timestamp = []
        for i in rrule(DAILY, strdate2date(start), 1, until=strdate2date(end)):
            timestamp.append(date(i.year, i.month, i.day))
        trends = pd.DataFrame(index=timestamp)
        # trends_by_state =  pd.DataFrame()
        for state in stateDF.StateName:
            for poll in pollutantDF.PollutantID:
                # print(type(state), type(poll), type(df['StateName']), type(df['PollutantID']))
                # tmpmask = df[lambda df: ((df['StateName'] == state) and (df['PollutantID'] == poll))]
                # tmpmask = (df['StateName'] == state) & (df['PollutantID'] == poll)
                tmpseries = df.loc[(df['StateName'] == state) & (df['PollutantID'] == poll)]#['Concentration']
                # print(tmpseries)
                series = tmpseries['Concentration']
                nan = len(series) - series.count()
                ma = series.max()
                mi = series.min()
                # dff = tmpseries.to_frame().reset_index()
                # dff['TimeStamp'] =
                sumDict[(state,poll)] = [ma,mi,nan]
                if plot_dropdown == 'state':      
                    if state == lineState:
                        # print(poll, tmpseries.values)
                        # tmpseries2 = df.loc[(df['StateName'] == lineState) & (df['PollutantID'] == poll)]['Concentration']
                        if not poll == 'CH4':
                            trends[poll] = trends.index.to_series().map(tmpseries.set_index('TimeStamp')['Concentration'])
                            # try:
                            #     trends[poll] = tmpseries.values
                            # except ValueError:
                            #     print('log fail')
                            #     print(trends.head())
                            #     print('len of val', len(tmpseries.values))
                else:
                    if poll == lineState:
                        # trends[state] = tmpseries.values
                        trends[state] = trends.index.to_series().map(tmpseries.set_index('TimeStamp')['Concentration'])

        # print(trends.tail())
        # omegaDF2 = omegaDF.copy()
        # sdf2 = (omegaDF2.TimeStamp > strdate2date(start)) & (omegaDF2.TimeStamp < strdate2date(end))
        # timestamp = omegaDF.loc[sdf2]['TimeStamp']
        trr = []
        for i in stateDF.StateName:
            tdd = []
            tdd.append(html.Td(i))
            for j in pollutantDF.PollutantID:
                
                lab = []
                k = sumDict[(i,j)]
                lab.append(html.P('max: {:1.2e}'.format(k[0])))
                lab.append(html.P('min: {:1.2e}'.format(k[1])))
                lab.append(html.P('nan: {:n}'.format(k[2])))
                # lab.append(html.P( '{:3.5e}'.format(k) if k else '0' ))
                
                tdd.append(html.Td(lab))
            trr.append(html.Tr(tdd))
        
        table_body = [html.Tbody(trr)]
        # print(len(trends['NO2']), tmpseries.index)
        # trends = trends.drop(columns='CH4')
        if not smoothing == 'NoSmoothing':
            trends = trends.rolling(smoothing,min_periods=1).mean()
        if plot_dropdown == 'state':
            # trends_smooth = trends.rolling(14,min_periods=1)
            normalized_df=(trends-trends.min())/(trends.max()-trends.min())
            line_fig = px.line(normalized_df, x=timestamp ,y=trends.columns, title="Normalized pollutant trends")
        else:
            # print(trends.columns)

            # for easychair submission
            trends = trends.drop(['Kedah', 'Kelantan', 'Melaka', 'Negeri Sembilan', 'Pahang', 'Perak', 'Perlis', 'Pulau Pinang', 'Sarawak', 'Terengganu', 'Labuan', 'Putrajaya'], axis = 1)
            newdf = pd.DataFrame()
            xx = []
            x1 = []
            x2 = []
            for statee in trends.columns:
                xx = xx + timestamp
                x1 = x1 + trends[statee].tolist()
                x2 = x2 + [statee for i in range(len(trends[statee]))]
            newdf['value'] = x1
            newdf['state'] = x2
            try:
                # line_fig = px.line(trends, x=timestamp ,y=trends.columns, title= lineState +  " Concentration")

                # for easy chair
                line_fig = px.line(newdf, x=xx, y='value', line_dash='state', color='state')
            except KeyError:
                line_fig = ''
        return table_header + table_body, line_fig

    
    