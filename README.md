# Suggested TOMAAT backend
Hi Fausto! :)
# About

## Architecture
see Architecture.txt
No explicit locks are used.
Due to the usage of a "ticketing" system, the progress of the requested operation must be polled.

## Terminology
Unfortunately, I use the terms "Task" and "Service" as a synonym.
Task is meant to be an explicit instantiation of a service operation.

## Workflow

- Client sends a POST request to http://localhost:5000/request with attached form data like this:
-- service : "InnerEarSegmentation"
-- payload : data.tar.gz
and receives
-- task id
-- access token
to query the task's status/result.
- Server extracts the data and puts the request to the shortest queue
- Server performs operation and stores result
- Client queries http://host:5000/result/id&token and receives the result as a tar.gz file.
The client can query the current status at http://host:5000/status/id&token
The client can query the host capabilities including their interfaces at http://host:5000/supportedservices

## Data Transfer

The data is transfered via a single .tar.gz file during upload and download.
The actual data is stored inside the .tar.gz file as
-a file, probably with the following pattern: file-dataid.*
-inside the main.json inside root/inputs/dataid
The input data can be composed by defined input classes which perform a lot of simple error handling and extract the actual data. Currently implemented input classes are:
- VolumeInput
- FloatInput
- StringInput
- IntInput
- SingleChoiceInput
These input classes also render the interfaces at http://host:5000/supportedservices.

## Multiple GPU Setup

The TaskScheduler takes care of assigning incoming tasks to different compute sources (GPUs).
You can assign a set of possible tasks to each compute source individually.

## Tasks/Services
Services can be defined easily. (e.g. see CustomTasks/FloatComputationTask.py)
The given task_identifier has to match to the "service" parameter of the form of the initial POST request.

## Settings
see all options in TOMAATSettings.py

## Get It Running
Make sure the folder BASE_STORAGE_DIR defined in TOMAATSettings exists.
Get a PostgreSQL database running with
 - username: tomaat-user
 - password: tomaat-password
 - database: tomaat
 then...
- Run...
`python3 QueueManager.py`
`python3 WebService.py`
`python3 TaskScheduling.py`

## Example Usage
After Get It Running, using Chrome postman, you can perform a POST request to http://localhost:5000/request
with body -> form-data and
form entries:
- service: FloatComputation
- payload: payload_float_add.tar.gz

Get the result at http://host:5000/result/id&token

## What about these messy (non-JSON) text responses
Yes, we should reorganize that.
