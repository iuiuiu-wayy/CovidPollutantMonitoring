from sqlalchemy import Table, MetaData
from . import db
import pandas as pd
from datetime import datetime
from .pollutant import pollutantDF
from .state import stateDF

metadata = MetaData(bind=db.engine)

raw = Table('Record', metadata, autoload=True)

# pollDict = {}

# for poll in pollutantDF.PollutantID:
#     for state in stateDF.StateName:
#         tmpDF = pd.read_sql(raw.select().where(raw.c.PollutantID == poll).where(raw.c.StateName == state), con=db.engine)
#         pollDict[(state, poll)] = tmpDF

pollDF = pd.read_sql(raw.select(), con=db.engine)