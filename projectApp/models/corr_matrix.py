import pandas as pd
import sqlalchemy as dbs
from . import db
from datetime import date
from scipy.stats import pearsonr
from dateutil.rrule import rrule, DAILY

class corr_grabber():
    """
    class to construct correlation matrix
    """
    def __init__(self):
        #define golbals
        self.STATEDICT = {
            'Johor' : 'Johor',
            'Kedah' : 'Kedah',
            'Kelantan' : 'Kelantan',
            'Melaka' : 'Melaka',
            'Negeri Sembilan' : 'Negeri',
            'Pahang' : 'Pahang',
            'Perak' : 'Perak',
            'Perlis' : 'Perlis',
            'Pulau Pinang' : 'Pulau',
            'Sabah' : 'Sabah',
            'Sarawak' : 'Sarawak',
            'Selangor' : 'Selangor',
            'Terengganu' : 'Terengganu',
            'Kuala Lumpur': 'Kuala',
            'Labuan' : 'Labuan',
            'Putrajaya' : 'Putrajaya'
        }
        self.POLL = ['NO2', 'O3', 'SO2', 'UVAI', 'CO', 'HCHO', 'CH4']
        


    # important functions

    def grabber(self, state, pollutant):
        """ grab pollutant data from viewes of database for each pollutant and states"""
        connection = self.engine.connect()
        metadata = dbs.MetaData(bind=self.engine)
        raw = dbs.Table(self.STATEDICT[state]+ '_' + pollutant, metadata, autoload=True)
        query = dbs.select([raw])
        result = connection.execute(query).fetchall()
        df = pd.DataFrame(result)
        df.columns = result[0].keys()
        connection.close()
        df.set_index('TimeStamp')
        return df


    def omega_grabber(self):
        """ grab omega data from omega table"""
        connection = self.engine.connect()
        metadata = dbs.MetaData(bind=self.engine)
        raw = dbs.Table('Omega', metadata, autoload=True)
        query = dbs.select([raw])
        result = connection.execute(query).fetchall()
        df = pd.DataFrame(result)
        df.columns = result[0].keys()
        connection.close()
        return df


    def station_grabber(self, state):
        """ grab list of weather station within the state"""
        connection = self.engine.connect()
        metadata = dbs.MetaData(bind=self.engine)
        raw = dbs.Table('ObsStation', metadata, autoload=True)
        query = dbs.select([raw]).where(raw.columns.StateName == state)
        result = connection.execute(query).fetchall()
        df = pd.DataFrame(result)
        if not df.empty:
            df.columns = result[0].keys()
        connection.close()
        return df


    def weather_grabber(self, wmoid, state):
        """ grab weather station data for spesified wmoid"""
        # print(state, wmoid)
        connection = self.engine.connect()
        metadata = dbs.MetaData(bind=self.engine)
        raw = dbs.Table('Obs', metadata, autoload=True)
        query = dbs.select([raw]).where(raw.columns.WMOID == wmoid)
        result = connection.execute(query).fetchall()
        df = pd.DataFrame(result)
        connection.close()
    #     print(df)
        if not df.empty:
            df.columns = result[0].keys()
        return df

    def pairwise_deletion(self, r,c):
            dff = pd.DataFrame({
                'r' : r,
                'c' : c
            }, columns=['r','c'])
            # print(dff.head())
            dff = dff.dropna()#._get_numeric_data()
            # print(dff.head())
            # print(dff.head())
            # print('r ',r[:5])
            # print('c ', c[:5])

            try:
                return (dff['r'], dff['c'])
            except:
                dff.to_csv('problem.csv')
                dff = pd.DataFrame({
                    'r' : r,
                    'c' : c
                }, columns=['r','c'])
                dff.to_csv('problem2.csv')
                raise Exception('data has been captured')

    def calculate_pvalues(self, df):
        """calculate p value as well as correlation 
        returning matrix of pvalues and correlations"""
        # df = df.dropna()._get_numeric_data()
        
        dfcols = pd.DataFrame(columns=df.columns)
        pvalues = dfcols.transpose().join(dfcols, how='outer')
        corr = pvalues.copy()
        for r in df.columns:
            for c in df.columns:
                (row,col) = self.pairwise_deletion(df[r], df[c])
                # print(len(row), len(col))
                a = pearsonr(row,col)
                pvalues[r][c] = a[1]
                corr[r][c] = a[0]
        return (corr, pvalues)
        
    def state_grabber(self, state):
        """combine all data avaiable for the given state"""
        dfi = []
        for i in rrule(DAILY, date(2019,1,1), 1, until=date.today()):
            dfi.append(date(i.year, i.month, i.day))

        df = pd.DataFrame(index=dfi)
        # df = self.grabber(state, 'NO2')
        # # print(df.head())
        # df = df.rename(columns={'Concentration' : 'NO2'})
        
        for poll in self.POLL:
            
            df_poll = self.grabber(state, poll)

            df[poll] = df.index.to_series().map(df_poll.set_index('TimeStamp')['Concentration'])
            # df[poll] = df.rename(index=df_poll.set_index('TimeStamp')['Concentration']).index
            # df[poll] = self.grabber(state, poll).Concentration
            
        omegadf = self.omega_grabber()
        df['Omega'] = df.index.to_series().map(omegadf.set_index('TimeStamp')['Omega'])
        # df['Omega'] = omegadf.Omega
        
        # pull weather data
        station = self.station_grabber(state)
    #     print(station.WMOID)
    #     print(dir(station.WMOID))
        # print(df.tail(30))
        if not station.empty:
            for wmoid in station.WMOID:
                weatherdf = self.weather_grabber(str(wmoid), state)
                if not weatherdf.empty:
                    # weatherdf = weatherdf.rename(columns={'Precipitation' : 'Precipitation_' + str(wmoid)})
                    # weather_prec_df = weatherdf['Precipitation_' + str(wmoid)]

                    df['Precipitation_'+ str(wmoid)] = df.index.to_series().map(weatherdf.set_index('TimeStamp')['Precipitation'])
                    df['Temperature_'+ str(wmoid)] = df.index.to_series().map(weatherdf.set_index('TimeStamp')['AvgTmp'])
                    df['RH_'+ str(wmoid)] = df.index.to_series().map(weatherdf.set_index('TimeStamp')['RH'])
                    df['WindSpeed_'+ str(wmoid)] = df.index.to_series().map(weatherdf.set_index('TimeStamp')['WndSpd'])
                    # df = pd.concat([df, weather_prec_df], axis=1)
                    # df['Precipitation_'+ str(wmoid)] = weatherdf.Precipitation.values
                    # df['Temperature_'+ str(wmoid)] = weatherdf.AvgTmp.values
                    # df['RH_'+ str(wmoid)] = weatherdf.RH.values
                    # df['WindSpeed_'+ str(wmoid)] = weatherdf.WndSpd.values
        
        # df = df.set_index("TimeStamp")

        return df
    
    def corr_matrix(self, state):
        """
        take state as input and return correlation and pvalue matrix of the given state
        """
        self.engine = db.engine
        df = self.state_grabber(state)
        # df.head(7)
        df = df.astype(float)
        df = df.drop(columns='CH4')
        # df = df.drop(columns='Count')

        #assign df to global value
        self.DF = df.copy()
        
        #standardize
        df =(df-df.mean())/df.std()

        # missing value removal is through removing the entire row for the dataframe
        # to implement pair wise, add a temporal df with only two series of desired input and implement dropna
        (cor, pval) = self.calculate_pvalues(df)
        
        return (cor, pval)
    
    def kill_self(self):
        # print('killing self')
        del self

    def calc_cov_cor(self, df, cumsum):
        # dfcols = pd.DataFrame(index=[0,1], columns=df.columns)
        corr = []
        pval = []
        for col in df.columns:
            (r1,r2) = self.pairwise_deletion(df[col], cumsum)
            a = pearsonr(r1.astype('float32'),r2.astype('float32'))
            pval.append(a[1])
            corr.append(a[0])
            # dfcols[0][col] = a[1]
            # dfcols[1][col] = a[0]

        return corr, pval

    def covid_grabber(self, start, end, state):
        connection = self.engine.connect()
        metadata = dbs.MetaData(bind=self.engine)

        lastupdateT = dbs.Table('LastUpdate', metadata, autoload=True)
        query = dbs.select([lastupdateT]).where(lastupdateT.columns.Param == 'fatality')
        result = connection.execute(query).fetchall()
        ludf = pd.DataFrame(result)
        ludf.columns = result[0].keys()
        lastupdateDate = ludf['LastUpdate'].tail(1).values[0]

        raw = dbs.Table('DeathCase', metadata, autoload=True)
        query = dbs.select([raw]).where(
            dbs.and_(
                raw.columns.StateName == state,
                raw.columns.UpdateDate == lastupdateDate
            )
        )
        result = connection.execute(query).fetchall()
        df = pd.DataFrame(result)
        if not df.empty:
            df.columns = result[0].keys()
            case = df.DeceasedTIme
        connection.close()
        #construct timeseries
        
        dfi = []
        for i in rrule(DAILY, start, 1, until=end):
            dfi.append(date(i.year, i.month, i.day))
        # dfi = pd.date_range(start=start, end=end)
        df2 = pd.DataFrame(0,index=dfi, columns=['DeathCase'])
        # print('df2index', df2.index.values)
        if not df.empty:
            for i in case:
                # print('ini iii', i, type(i))
                # print('ini deathcase 000', df2.DeathCase.index.values[0],type(df2.DeathCase.index.values[0]))
                if df2.DeathCase.index.values.__contains__(i):
                    
                    df2.DeathCase[i] = df2.DeathCase[i] + 1

        # print('cumsum = ', df2.DeathCase.cumsum())
        return df2.DeathCase#.cumsum()



    def totalcase_grabber(self, start, end, state):
        connection = self.engine.connect()
        metadata = dbs.MetaData(bind=self.engine)

        raw = dbs.Table('TotalCase', metadata, autoload=True)
        query = dbs.select([raw]).where(
            raw.columns.StateName == state
        )
        result = connection.execute(query).fetchall()
        df = pd.DataFrame(result)
        if not df.empty:
            df.columns = result[0].keys()
            # case = df.DeceasedTIme
            df = df.set_index("TimeStamp")
            # df = df[start:end]
        connection.close()
        # df = df.diff(axis=0)
        dfi = []
        for i in rrule(DAILY, start, 1, until=end):
            dfi.append(date(i.year, i.month, i.day))
        # dfi = pd.date_range(start=start, end=end)
        df2 = pd.DataFrame(index=dfi)
        # df[poll] = df.index.to_series().map(df_poll.set_index('TimeStamp')['Concentration'])
        df2['TotalCase'] = df2.index.to_series().map(df['TotalCase'])
        for i in range(len(df2.index)):
            if pd.isna(df2['TotalCase'][i]):
                if not i == 0:
                    df2['TotalCase'][i] = df2['TotalCase'][i-1]
                else:
                    df2['TotalCase'][i] = 0
        # print("type of time in db {}".format(type(df.index.tolist()[0])))
        # if not df.empty:
        #     for dt in df.index.tolist():
        #         df2[dt] = df[dt]
        # print(df2.diff(axis=0).head(50))
        return df2.diff(axis=0)

    def calc_cov(self, start, end, state):
        # print(self.DF.index, type(self.DF.index[0]))

        # for i in self.DF.index.tolist():
        #     print(i)
        df = self.DF[start:end]
        cumsum = self.covid_grabber(start, end, state)
        # print('cumsumlen {}'.format(len(cumsum)))
        total_case = self.totalcase_grabber(start, end, state)['TotalCase']
        (cor, pval) = self.calc_cov_cor(df, cumsum)
        (cor_tot, pval_tot) = self.calc_cov_cor(df, total_case)
        return (cor, pval, cor_tot, pval_tot)


