import uuid
from sqlalchemy import *
import logging
import TOMAATSettings

engine = create_engine(TOMAATSettings.sqlDBString, echo=False)
metadata = MetaData()

# define DB table structure
inferenceTask = Table('inference',metadata,
    Column('task_id',Integer, autoincrement=True,primary_key=True),
    Column('servicetype',String),
    Column('time_request',DateTime),
    Column('time_started',DateTime),
    Column('time_finished',DateTime),
    Column('retrieved',Boolean, nullable=False, default=False),
    Column('request_ip',String, nullable=False, default="not tracked"),
    Column('accesstoken',CHAR(32),nullable=False,default=lambda:uuid.uuid4().hex),
    Column('errors_occurred',Boolean,default=False),
    Column('errors',String)
)
metadata.bind = engine
metadata.create_all()

logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

def getRowByID(id):
    stmd = inferenceTask.select(whereclause=(inferenceTask.c.task_id == id)).compile()
    result = engine.connect().execute(stmd).fetchone()
    return dict(result)

def insertNewRow(time,service,ip):
    global inferenceTask
    global engine
    # prepare new entry
    stmd = inferenceTask.insert().\
        values(time_request=time,servicetype=service,request_ip=ip). \
        returning(inferenceTask.c.task_id,
                  inferenceTask.c.accesstoken).compile()
    # execute statement
    return engine.execute(stmd).fetchone()

def updateColumnsByID(id,**valueset):
    global inferenceTask
    global engine
    stmd = inferenceTask.update().\
        where(inferenceTask.c.task_id == id).\
        values(valueset).compile()
    engine.execute(stmd)
