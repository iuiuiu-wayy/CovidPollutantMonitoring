from dash import Dash
# import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


def init_dash(server):
    app = Dash(
        server=server, 
        suppress_callback_exceptions=True,
        external_stylesheets=[dbc.themes.SANDSTONE],
        url_base_pathname='/')

    with app.server.app_context():
        from .covidTab import covid, dff, covid_calback
        from .pollutantTab import pollutant, stateDF, pollutantDF, pollDF, pollutant_callback
        from .weatherTab import weatab, weather_callback
        
        from .mainTab import main, main_callback
        # from ..models.corr_matrix import corr_grabber
        # c = corr_grabber()
        # (cdf, pdf) = c.corr_pval('Johor')

    mainTab = dbc.Card(
        dbc.CardBody(
            main
        ),
        className="mt-3",
    )

    tab1 = dbc.Card(
        dbc.CardBody([
            covid
        ]),className="mt-3",
    )

    tab2_content = dbc.Card(
        dbc.CardBody(
            pollutant
        ),
        className="mt-3",
    ) 

    tab3 = dbc.Card(
        dbc.CardBody(
           weatab 
        ),
        className="mt-3", 
    )


    tabs = dbc.Tabs(
        [
            dbc.Tab(mainTab, label="Main dashboard"),
            dbc.Tab(tab1, label="Covid-19 Statistics"),
            dbc.Tab(tab2_content, label="Pollutant Statistics"),
            dbc.Tab(tab3, label="weather statistics")
        ]
    )

    app.layout = html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col(html.H1('Covid and Air Pollutant Monitoring Dashboard'), 
                align='center', width={'size':True})
            ], justify='center'),
            dbc.Row([
                dbc.Col(tabs, width=True)
            ])    
        ])
        
    ])

    ####### COVID STATISTICS piechart       ###################################################################
    covid_calback(app)
    ######## Pollutant Statistics table and line    ###################################################################
    pollutant_callback(app)
    ######### weather line graph and table ###################################################################
    weather_callback(app)
    ######## main tab scatter and heatmap    ###################################################################
    main_callback(app)