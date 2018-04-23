from abc import ABC
from datetime import datetime
import os, TOMAATSettings

# Each InferenceWorker utilizes one ComputeSource
# to perform Tasks received from
# its queue shared with the TaskScheduler
class InferenceWorker():
    def __init__(self,usedComputeSourceClass):
        self.cs = usedComputeSourceClass
        self.classMapping = { t.task_identifier:t for t in self.cs.supported_tasks}
        self.working = None

    def start(self,task_queue, state):
        import DB
        self.cs.initialize()
        self.working = state

        while True:
            self.working.value = False
            id = task_queue.get()
            # set state to working
            self.working.value = True
            properties = DB.getRowByID(id)
            servicetype = properties['servicetype']

            data_dir = os.path.join(TOMAATSettings.BASE_STORAGE_DIR,str(id))

            print("Check input of Task with ID {} type: {}".format(id, servicetype))
            DB.updateColumnsByID(id,time_started=datetime.now())
            # Instanciate new Task object
            task = self.classMapping[servicetype](id,data_dir)
            try:
                # check input data
                task.validateInputData() # this can fail

                # The input validation was successful -> we can start the perform operation
                print("Task with ID {} is dispatched with Task: {}".format(id, servicetype))
                try:
                    task.perform() # this can still fail
                    DB.updateColumnsByID(id,time_finished=datetime.now())
                    print("Task with ID {} has been performed with Task: {}".format(id, servicetype))
                except Exception as e:
                    print("Task with ID {} had an error while performing.".format(id))
                    DB.updateColumnsByID(id, errors_occurred=True, errors=str(e))

            except Exception as e:
                print("Task with ID {} had an error during input validation.".format(id))
                DB.updateColumnsByID(id, errors_occurred=True, errors=str(e))


# Some ComputeSource may need perform some
# actions to be assigned to a single GPU
class AbstractComputeSource(ABC):
    supported_tasks = []

    @classmethod
    def initialize(cls):
        pass
