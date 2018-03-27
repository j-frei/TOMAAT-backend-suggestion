import TOMAATSettings
from multiprocessing.managers import BaseManager
import multiprocessing as mp
from multiprocessing import Queue, Process
from AbstractComputeSource import InferenceWorker


class TaskScheduler(object):
    def __init__(self):
        # setup DB and TaskQueue connections
        import DB
        self.DB = DB
        self.mgr = BaseManager(address=('127.0.0.1',TOMAATSettings.web2scheduler_IPC_port),
                               authkey=TOMAATSettings.web2scheduler_IPC_authkey)
        self.mgr.connect()
        self.mgr.register('tasks')
        self.taskQueue = self.mgr.tasks()
        print("Connected to IPC QueueMgr <-> Scheduler.")

        self.computeSources = TOMAATSettings.registeredComputeSources
        self.supportedTasksBySource = [ cs.supported_tasks for cs in self.computeSources]


        self.computeSourceIndexByTask = {}
        # Find all available ComputeSource indices for each Task
        for i,tasks in enumerate(self.supportedTasksBySource):
            for task in tasks:
                # add index of compute source to supported task name in the dictionary
                self.computeSourceIndexByTask[task.task_identifier] = \
                    self.computeSourceIndexByTask.get(task.task_identifier,[]) + [i]

        self.workers = []
        self.workerProcesses = []
        self.workerQueues = []


    def startComputeProcesses(self):
        # Setup and launch all InferenceWorkers
        self.workers = [InferenceWorker(usedComputeSourceClass=cs) for cs in self.computeSources]
        for w in self.workers:
            q = Queue()
            p = Process(target=w.start,args=(q,))
            self.workerProcesses.append(p)
            self.workerQueues.append(q)

        for wp in self.workerProcesses:
            wp.start()


    def scheduleIncomingTasks(self):
        while True:
            print("Waiting for incoming tasks...")
            task_id = self.taskQueue.get()

            print("New task incoming!")
            servicetype = self.DB.getRowByID(task_id)['servicetype']

            capableComputeSources = self.computeSourceIndexByTask.get(servicetype,[])

            # Should not happen as the check is already performed at the incoming request
            if len(capableComputeSources):
                print("No capable device available!")

            queuesOfCapableSources = [ (i,self.workerQueues[i]) for i in capableComputeSources]

            # select compute source with shorted queue
            (selectedComputeSourceIndex,_),*_ = sorted(queuesOfCapableSources, reverse=False, key=lambda obj: obj[1].qsize())

            print("Dispatch task id {} with task {} in queue of compute source index {}.".format(task_id,servicetype,selectedComputeSourceIndex))
            self.workerQueues[selectedComputeSourceIndex].put(task_id)



if __name__ == "__main__":
    mp.set_start_method('spawn')
    ts = TaskScheduler()
    ts.startComputeProcesses()
    ts.scheduleIncomingTasks()