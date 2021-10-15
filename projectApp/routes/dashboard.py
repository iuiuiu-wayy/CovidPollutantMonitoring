from flask import Blueprint
from sqlalchemy import Table
from ..models import db
import pandas as pd
# from . import app
dashboard = Blueprint('dashboard', __name__)
# from  import state

# @dashboard.context_processor
# @dashboard.route("/")
# def fun():
#     from ..models.state import state, state2, t1, t2, t3
#     # from sqlalchemy import MetaData
#     # meta = MetaData()
#     # table_reflection = Table('ObsStation', meta, autoload=True, autoload_with=db.engine)
#     # attrs = {'__table__': table_reflection}

#     # state = type("ObsStation", (db.Model,), attrs)
#     # print(str(state.query.get(1)))
#     # a = state.query()
#     # print(dir(state2))
#     # df = pd.read_sql_table(a, con=db.engine)
#     # print(type(a.StateName))
#     b = pd.read_sql(t2.select(), con=db.engine)
#     return str(b)
    


def dashboardfunct():
    return str(fun())