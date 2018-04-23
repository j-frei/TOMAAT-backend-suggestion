import SimpleITK as sitk
import tarfile, re, os, shutil, json, base64, requests, sys
from datetime import datetime
from tempfile import mkdtemp
from time import sleep
from io import BytesIO
from flask import Flask, request

from CustomTasks.AvailableInputs.BooleanInput import BooleanInput
from CustomTasks.AvailableInputs.FloatInput import FloatInput
from CustomTasks.AvailableInputs.IntInput import IntInput
from CustomTasks.AvailableInputs.PointList3D import PointList3DInput
from CustomTasks.AvailableInputs.StringInput import StringInput
from CustomTasks.AvailableInputs.VolumeInput import VolumeInput
from CustomTasks.InnerEarTasks.InnerEarSegmentationTask import InnerEarSegmentationTask

app = Flask(__name__)
taskClass = InnerEarSegmentationTask
targetHost = ("http://127.0.0.1", 5000)

# definition <-> interface
key_mapping = {
    "type": "type",
    "id": "destination",
    "name": "text",
}
type_mapping = {
    "float": "slider",
    "boolean": "checkbox",
    "pointlist": "fiducials",
}


@app.route("/predict", methods=['POST'])
def predict():
    # data needs to be filled
    mainJson = {"inputs": {}}
    files = {}

    # receive data
    for input in taskClass.inputs:
        if type(input) == VolumeInput:
            vol = BytesIO()
            request.files[input.id].save(vol)
            vol.seek(0)

            files["file-" + input.id + ".mha"] = vol
        elif type(input) in [StringInput,FloatInput,BooleanInput,IntInput, PointList3DInput]:
            data = request.form[input.id]
            mainJson['inputs'][input.id] = str(data)
        else:
            print("Unknown type found.")

    # create main file
    main = BytesIO()
    main.write(json.dumps(mainJson).encode("utf-8"))
    main.seek(0)
    files['main.json'] = main

    # generate output tarfile
    output = BytesIO()

    of = tarfile.open(fileobj=output, mode="w:gz")
    for name, f in files.items():
        tarinfo = tarfile.TarInfo(name)
        tarinfo.size = f.getbuffer().nbytes
        of.addfile(tarinfo=tarinfo, fileobj=f)
    of.close()

    # reset output
    output.seek(0)

    # send post request
    data = {"service": taskClass.task_identifier}
    files = {"payload": output}

    time_start = datetime.now()
    print("Sending request to backend.")
    response = requests.post("{}:{}/request".format(targetHost[0], targetHost[1]), data=data, files=files)
    pattern = re.compile(rb"Ask for ID: (?P<id>[0-9]+) with token: (?P<token>[0-9a-f]+)")
    print("Waiting for result...")

    m = pattern.match(response.content)
    id, token = m.group("id").decode(), m.group("token").decode()
    done = False

    while not done:
        sleep(0.5)
        response = requests.get("{}:{}/status/{}&{}".format(targetHost[0], targetHost[1], id, token))
        if response.content == b"Task has been finished!":
            print("done!")
            done = True
        else:
            print(".", end="", flush=True)

    response = requests.get("{}:{}/result/{}&{}".format(targetHost[0], targetHost[1], id, token))
    result = BytesIO()
    result.write(response.content)
    result.seek(0)

    time_end = datetime.now()

    tmpdir = mkdtemp()

    # open result files
    tf = tarfile.open(fileobj=result, mode="r:gz")

    pattern = re.compile(r'[^/]+$')

    # extract only files in tar root directory
    def filterFiles(members):
        for tinfo in members:
            if tinfo.isfile() and pattern.match(tinfo.name):
                yield tinfo

    json_answer = []
    for member in filterFiles(tf.members):
        # we are assuming that only volumes are in the result
        mpath = os.path.join(tmpdir, member.name)
        tf.extract(member, tmpdir)
        mpathNoExt, _ = os.path.splitext(mpath)
        mhaPath = mpathNoExt + ".mha"
        sitk.WriteImage(sitk.ReadImage(mpath), mhaPath)

        with open(mhaPath, 'rb') as f:
            vol_string = base64.encodebytes(f.read()).decode("utf-8")

        os.remove(mpath)
        os.remove(mhaPath)
        json_answer.append({'type': 'LabelVolume', 'content': vol_string, 'label': ''})

    tf.close()
    shutil.rmtree(tmpdir)
    # time passed
    json_answer.append(
        {'type': 'PlainText', 'content': str('process took {} seconds'.format((time_end - time_start).seconds)),
         'label': ''}
    )
    print("Returning result.")
    return json.dumps(json_answer)


@app.route("/interface")
def interface():
    interfaces = []
    for input in taskClass.inputs:
        i_dict = input.definition()
        i_dict_out = {}
        for k, v in i_dict.items():
            if k in key_mapping.keys():
                if k == "type" and v in type_mapping.keys():
                    _v = type_mapping[v]
                else:
                    _v = v

                i_dict_out[key_mapping[k]] = _v
            else:
                i_dict_out[k] = v
        interfaces.append(i_dict_out)

    return json.dumps(interfaces)


app.run(host="0.0.0.0",port=int(sys.argv[1]) if len(sys.argv) == 2 and str(sys.argv[1]).isnumeric() else 5001)
