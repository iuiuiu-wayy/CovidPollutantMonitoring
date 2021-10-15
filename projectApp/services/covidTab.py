# from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
# import dash_bootstrap_components as dbc
from ..models.covid import covidDF, tot_caseDF
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from .utils import strdate2date
from datetime import date, timedelta
import plotly.express as px


dff = covidDF
covid = html.Div([
    html.Div([
        html.Label(['Category:']),
        dcc.Dropdown(
            id='covid_dropdown',
            options=[
                {'label': 'State', 'value':'StateName'},
                {'label': 'Nationality', 'value':'Nationality'},
                {'label': 'Gender', 'value':'Gender'},
                {'label': 'Age', 'value':'Age'},
                {'label': 'Chronic', 'value':'ChronicDisease?'}
            ],
            value = 'StateName',
            multi = False,
            clearable=False,
            style = {'width':"50%"}
        )
    ]),

    html.Div([
        dcc.Graph(id='pieChart')
    ]),

    html.Div([
        html.Label(['Time window range:']),
        dcc.DatePickerRange(
            id='covid_date_picker',
            # day_size = 62,
            display_format='DD, MMM, YYYY' ,
            min_date_allowed=date(2020, 1, 13),
            max_date_allowed=date.today() - timedelta(days=10),
            # initial_visible_month=date(2019, 1, 1),
            end_date=date.today() - timedelta(days=10),
            start_date=date(2020,1,13),
            number_of_months_shown =2,
            show_outside_days = True,
            style = {'width':"100%"}
        )
    ]),
    html.Div([
        dcc.Graph(id='line_covid')
    ]),
])


def covid_calback(app):
    @app.callback(
        Output('pieChart', 'figure'),
        [Input('covid_dropdown', 'value')]
    )
    def update_graph(val):
        dfff = dff.copy()
        clases = ['<= 5', '5 < Age <= 17', '17 < Age <= 50', 'Age > 50']
        if val == 'Age':
            age_class = []
            for i in dfff[val]:
                if i <= 5:
                    age_class.append(clases[0])
                elif i <= 17:
                    age_class.append(clases[1])
                elif i <= 50:
                    age_class.append(clases[2])
                else:
                    age_class.append(clases[3])
            dfff['Age'] = age_class
        elif val == 'ChronicDisease?':
            clases = ['Chronic disease', 'No chronic disease']
            chronic_class = []
            for i in dfff[val]:
                if i:
                    chronic_class.append(clases[0])
                else:
                    chronic_class.append(clases[1])
            dfff[val] = chronic_class

        vals = dfff[val].value_counts()
        labs = vals.index
        piechart = go.Figure(
            data = go.Pie(
                title='Fatality',
                titlefont =dict(size=15),
                values=vals,
                labels=labs,
                hole=.3,
                hoverinfo  ='label',
            )
        )
        # piechart = px.pie(
            # data_frame=dff,
            # names=val,
            # hole=.3,
            # hoverinfo  ='text',
        # )
        return (piechart)

    @app.callback(
        Output('line_covid', 'figure'),
        [Input('covid_date_picker', 'start_date'),
        Input('covid_date_picker', 'end_date')]
    )
    def covid_line_graph(start, end):
        # sdf = (tot_caseDF.TimeStamp > strdate2date(start)) & (tot_caseDF.TimeStamp < strdate2date(end))
        df=tot_caseDF.set_index('TimeStamp')
        df = df[strdate2date(start):strdate2date(end)]
        # print(df.head())
        fig = px.line(df, title="Covid 19 total case")
        return fig
