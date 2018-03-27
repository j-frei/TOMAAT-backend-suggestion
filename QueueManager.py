from multiprocessing.managers import BaseManager
from multiprocessing import Queue
import TOMAATSettings

# The QueueManager hosts the shared Queue between the WebService worker(s) and the TaskScheduler
# It's necessary because in production mode the WebService worker(s) are usually
# launched by a WSGI application so we cannot use a simple fork call with a shared pipe.

m = BaseManager(address=('127.0.0.1',TOMAATSettings.web2scheduler_IPC_port),
                               authkey=TOMAATSettings.web2scheduler_IPC_authkey)
server = m.get_server()
requestQueue = Queue()
m.register('tasks',callable=lambda:requestQueue)

print("QueueMgr started.")
server.serve_forever()