from CustomComputeSources.GPU0ComputeSource import GPU0ComputeSource
from CustomComputeSources.GPU1ComputeSource import GPU1ComputeSource
from enum import Enum

# What do we do after the data was
# retrieved by a client?
class StorageChoices(Enum):
    KEEP_ALL = 1
    KEEP_ONLY_INPUT = 2
    KEEP_NOTHING = 3

# used Compute Sources
registeredComputeSources = [
    GPU0ComputeSource,
    GPU1ComputeSource
]


# Database username, password, used database name
# The given example uses PostgreSQL with the user "tomaat-user" with password "tomaat-password"
# running on port 5432 (postgres default) with a database "tomaat"
sqlDBString = 'postgres://tomaat-user:tomaat-password@localhost:5432/tomaat'

# Storage setup
BASE_STORAGE_DIR = '/home/jfrei/test'
StorageStrategy = StorageChoices.KEEP_NOTHING


# IPC setup (ignore it as long as you don't ran into port conflicts)
web2scheduler_IPC_authkey = b'TOMAAT'
web2scheduler_IPC_port = 4999

# max content size in bytes for a request
# example max size: 400MiB -> 400 * 1024 * 1024
maxRequestSize = 400 * 1024 * 1024

# determine all tasks provided by registered compute sources
availableServices = list(set([ task for cs in registeredComputeSources for task in cs.supported_tasks]))
availableServicesByName = [task.task_identifier for task in availableServices]