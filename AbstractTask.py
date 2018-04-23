from abc import ABC, abstractmethod
import os

# Each task needs a task identifier that is publicly known
# and part of the initial POST request
class AbstractTask(ABC):
    task_identifier = ""
    description = "No description"
    inputs = []
    shared = {}

    def __init__(self,id : int,data_dir : str):
        self.id = id
        self.dir = data_dir
        self.cleaned_values = {}


    @classmethod
    def interface(cls):
        interface = {}
        for input in cls.inputs:
            interface[input.id] = input.definition()
        return interface


    # perform validator checks before task dispatch
    def validateInputData(self):
        in_path = os.path.join(self.dir,"in")
        errors = []
        for input in self.inputs:
            try:
                value = input.check(in_path)
                self.cleaned_values[input.id]=value
            except Exception as e:
                errors.append(str(e))
        if len(errors) != 0:
            raise Exception("\n".join(errors))

    @abstractmethod
    def perform(self):
        pass
