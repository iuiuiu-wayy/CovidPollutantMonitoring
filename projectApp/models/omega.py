from sqlalchemy import Table, MetaData
from . import db
import pandas as pd



metadata = MetaData(bind=db.engine)

raw = Table('Omega', metadata, autoload=True)

omegaDF = pd.read_sql(raw.select(), con=db.engine)