from sqlalchemy import Table, MetaData
import sqlalchemy as dbs
from . import db
import pandas as pd
from .corr_matrix import corr_grabber
from collections import defaultdict

cg = corr_grabber()
metadata = MetaData(bind=db.engine)
connection = db.engine.connect()



lastupdateT = dbs.Table('LastUpdate', metadata, autoload=True)
query = dbs.select([lastupdateT]).where(lastupdateT.columns.Param == 'fatality')
result = connection.execute(query).fetchall()
ludf = pd.DataFrame(result)
ludf.columns = result[0].keys()
lastupdateDate = ludf['LastUpdate'].tail(1).values[0]

raw = Table('DeathCase', metadata, autoload=True)
query = dbs.select([raw]).where(raw.columns.UpdateDate == lastupdateDate)
result = connection.execute(query).fetchall()
covidDF = pd.DataFrame(result)
if not covidDF.empty:
    covidDF.columns = result[0].keys()
    case = covidDF.DeceasedTIme
# covidDF = pd.read_sql(raw.select(), con=db.engine)

tot_caseT = Table('TotalCase', metadata, autoload=True)
tot_caseDF = defaultdict(list)
cols = []
for state in cg.STATEDICT.keys():
    query = dbs.select([tot_caseT]).where(
            tot_caseT.columns.StateName == state
        )
    result = connection.execute(query).fetchall()
    df = pd.DataFrame(result)
    if not df.empty:
        df.columns = result[0].keys()
        # case = df.DeceasedTIme
    tot_caseDF[state] = df['TotalCase'].tolist()
    cols.append(state)
cols.append('TimeStamp')
tot_caseDF['TimeStamp'] = df['TimeStamp'].tolist()

tot_caseDF = pd.DataFrame(tot_caseDF, columns = cols)
connection.close()
