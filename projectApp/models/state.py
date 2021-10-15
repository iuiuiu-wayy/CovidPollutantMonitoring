from sqlalchemy import Table
from . import db
from .base import metadata
import pandas as pd
# from projectApp.models.base import metadata


from sqlalchemy import MetaData



table_reflection = Table('State', metadata, autoload=True, autoload_with=db.engine)
attrs = {'__table__': table_reflection}
# print('attrs', attrs)
state = type("table_name", (db.Model,), attrs)

state2 = pd.read_sql_table('ObsStation', db.engine)

metadata.reflect(bind=db.engine)
t1 = metadata.tables['State']

m2 = MetaData(bind=db.engine)
t2 = Table('State', m2, autoload=True)

t3 = Table('State', MetaData(), autoload_with=db.engine)

stateDF = pd.read_sql(t2.select(), con=db.engine)