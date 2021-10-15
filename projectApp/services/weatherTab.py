import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from datetime import date
from dash.dependencies import Input, Output
from .utils import strdate2date
import plotly.express as px
from projectApp.models.omega import omegaDF
from projectApp.models.obsStation import ObsStationDF
from projectApp.models.obs import obsDF


# from projectApp.models.omega import omegaDF

weatab = html.Div([
    html.Div([
        html.Label(['Time window range:']),
        dcc.DatePickerRange(
            id='weather_date_picker',
            # day_size = 62,
            display_format='DD, MMM, YYYY' ,
            min_date_allowed=date(2019, 1, 1),
            max_date_allowed=date(2020, 9, 1),
            # initial_visible_month=date(2019, 1, 1),
            end_date=date(2020, 9, 1),
            start_date=date(2019,1,1),
            number_of_months_shown =2,
            show_outside_days = True,
            style = {'width':"100%"}
        )
    ]),
    html.Div([
        dcc.Graph(id='line_weather')
    ]),

    html.Div([
        dbc.Table(
            id='weather_table',
            bordered=True,
            # dark=True,
            hover=True,
            responsive=True,
            striped=True 
        )
    ])    
])


def weather_callback(app):
    @app.callback(
        [Output('line_weather', 'figure'),
        Output('weather_table', 'children')],
        [Input('weather_date_picker', 'start_date'),
        Input('weather_date_picker', 'end_date')]
    )
    def update_weather_graph(start, end):
        sdf = (omegaDF.TimeStamp > strdate2date(start)) & (omegaDF.TimeStamp < strdate2date(end))
        df = omegaDF.loc[sdf]
        # print(df.head())

        # fig = go.Figure(
        #     data=go.scatter(x=df.TimeStamp,y=df.Omega)
        # )
        fig = px.line(df, x="TimeStamp", y="Omega", title="Atmospheric condition")

        headlist = ['Station ID', 'Temperature', 'Relative humidity',  'Wind speed', 'Precipitation']
        table_header = [
            html.Thead(
                [html.Td(pol) for pol in headlist]
            )
        ]

        COLLIST = ['AvgTmp', 'RH', 'WndSpd', 'Precipitation']
        weatherDict = {}
        for wmoid in ObsStationDF.WMOID:
            for col in COLLIST:
                # print(obsDF.head())
                tmpseries = obsDF.loc[obsDF['WMOID'] == wmoid ][col]
                # tmpseries = tmpseries.fillna(value=np.nan)
                # print(wmoid, col, type(tmpseries))
                # print(type(x) for x in tmpseries)
                # print(wmoid,col)
                # print(tmpseries)
                nan = len(tmpseries) - tmpseries.count()
                ma = tmpseries.max()
                mi = tmpseries.min()
                # print(ma,mi,nan)
                weatherDict[(wmoid,col)] = [ma,mi,nan]

        trr = []
        for i in ObsStationDF.WMOID:
            tdd = []
            tdd.append(html.Td(i))
            for j in COLLIST:
                lab = []
                k = weatherDict[(i,j)]
                lab.append(html.P('max: {:2.1f}'.format(k[0])))
                lab.append(html.P('min: {:2.1f}'.format(k[1])))
                lab.append(html.P('nan: {:n}'.format(k[2])))
                # lab.append(html.P( '{:3.5e}'.format(k) if k else '0' ))
                tdd.append(html.Td(lab))
            trr.append(html.Tr(tdd))
        table_body = [html.Tbody(trr)]
        return fig , table_header + table_body