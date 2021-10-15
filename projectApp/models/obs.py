from sqlalchemy import Table, MetaData
from . import db
import pandas as pd
# from .obsStation import ObsStationDF

metadata = MetaData(bind=db.engine)

raw = Table('Obs', metadata, autoload=True)

obsDF = pd.read_sql(raw.select(), con=db.engine)