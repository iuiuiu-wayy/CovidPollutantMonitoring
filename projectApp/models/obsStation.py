from sqlalchemy import Table, MetaData
from . import db
import pandas as pd

metadata = MetaData(bind=db.engine)

raw = Table('ObsStation', metadata, autoload=True)

ObsStationDF = pd.read_sql(raw.select(), con=db.engine)