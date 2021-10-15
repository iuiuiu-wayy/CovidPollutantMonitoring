from sqlalchemy import Table, MetaData
from . import db
import pandas as pd

metadata = MetaData(bind=db.engine)

raw = Table('Pollutant', metadata, autoload=True)

pollutantDF = pd.read_sql(raw.select(), con=db.engine)