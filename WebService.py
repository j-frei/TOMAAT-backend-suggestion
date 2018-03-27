import json
import tarfile, re, os, shutil, TOMAATSettings
from multiprocessing.managers import BaseManager
from datetime import datetime

from DB import insertNewRow
from TOMAATSettings import StorageChoices as scs
from flask import Flask, request, send_from_directory, after_this_request

app = Flask(__name__)

mgr = BaseManager(address=('127.0.0.1',TOMAATSettings.web2scheduler_IPC_port),authkey=TOMAATSettings.web2scheduler_IPC_authkey)
mgr.connect()
mgr.register('tasks')

if TOMAATSettings.maxRequestSize is not None:
    app.config['MAX_CONTENT_LENGTH'] = TOMAATSettings.maxRequestSize
    print("Setting MAX content size to {} MiB.".format(TOMAATSettings.maxRequestSize/1024/1024))

print("Connected to IPC WebService <-> QueueMgr.")


def extractData(id,filestorage):
    # open compressed file
    tar_data = tarfile.open(fileobj=filestorage.stream)
    pattern = re.compile(r'[^/]+$')
    # extract only files in tar root directory
    def filterFiles(members):
        for tinfo in members:
            if tinfo.isfile() and pattern.match(tinfo.name):
                yield tinfo
    # setup target directory (input folder is 'in')
    path_extract = os.path.join(TOMAATSettings.BASE_STORAGE_DIR,str(id),"in")
    path_out = os.path.join(TOMAATSettings.BASE_STORAGE_DIR,str(id),"out")

    os.makedirs(path_extract, exist_ok=True)
    os.makedirs(path_out, exist_ok=True)

    # extract data from tarfile
    tar_data.extractall(path=path_extract,members=filterFiles(tar_data))

    tar_data.close()
    filestorage.close()

def propagateNewRequest(id):
    # put id number in queue
    global mgr
    mgr.tasks().put(id)


@app.route("/request", methods=['GET', 'POST'])
def newTask():
    service = request.form['service']
    if service in TOMAATSettings.availableServicesByName:
        new_id, token = insertNewRow(time=datetime.now(),service=service,ip=request.remote_addr)
        extractData(new_id,request.files['payload'])
        propagateNewRequest(new_id)
        return "Ask for ID: {} with token: {}".format(new_id,token)
    else:
        return "Service not available."

@app.route("/status/<id>&<token>")
def status(id,token):
    import DB
    task = DB.getRowByID(id)
    if task and task['accesstoken'] == token:
        if task['errors_occurred']:
            return "Errors occurred"
        else:
            finished = task['time_finished']
            if finished:
                return "Task has been finished!"
            elif task['time_started']:
                return "Task has been started!"
            else:
                return "Task has not been started!"
    else:
        return "No such id or wrong access token!"

@app.route("/result/<id>&<token>")
def retrieveResult(id,token):
    import DB

    # cleanup files after successful transfer or error
    def cleanup(output_dir):
        strategy = TOMAATSettings.StorageStrategy
        if strategy == scs.KEEP_ONLY_INPUT:
            # remove only .../<id>/out folder
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
        if strategy == scs.KEEP_NOTHING:
            # remove .../<id> folder
            entire_folder = os.path.dirname(output_dir)
            if os.path.exists(entire_folder):
                shutil.rmtree(entire_folder)
        DB.updateColumnsByID(id, retrieved=True)

    # find corresponding DB entry
    task = DB.getRowByID(id)
    if task and task['accesstoken'] == token:
        output_file_path = os.path.join(TOMAATSettings.BASE_STORAGE_DIR, str(id), "out", "result.tar.gz")
        output_dir,output_file = os.path.split(output_file_path)
        if task['errors_occurred']:
            @after_this_request
            def after_download(response):
                cleanup(output_dir)
                return response
            return "Errors occurred!"

        if task['time_finished']:
            # task has been finished and was successful
            if os.path.exists(output_file_path):
                try:
                    @after_this_request
                    def after_download(response):
                        cleanup(output_dir)
                        return response

                    return send_from_directory(output_dir,output_file, as_attachment=True)
                except Exception as e:
                    # Transfer of the result file was not successful
                    return "An error occurred!"
            else:
                # result.tar.gz was not found
                return "No output file!"
        else:
            # task has not been finshed yet
            return "Task pending..."
    else:
        return "No such id or wrong access token!"

@app.route("/supportedservices")
def supportedservices():
    supported = [{"name":service.task_identifier,
                   "description":service.description,
                   "interface":service.interface()
                   } for service in TOMAATSettings.availableServices]
    return json.dumps(supported)


app.run()