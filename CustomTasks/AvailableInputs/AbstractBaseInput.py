from abc import ABC, abstractmethod
from enum import Enum

class Destination(Enum):
    # data is stored inside main.json -> "inputs" -> <id>
    mainjson = 0
    # data is stored as a file with name file-<id>.*
    file = 1

class AbstractBaseInput(ABC):
    def __init__(self, id, pretty_name, description=""):
        self.id = id
        self.name = pretty_name
        self.description = description
        self.destination = Destination.mainjson
        self.type = ""

    @abstractmethod
    def check(self, in_path):
        pass

    def definition(self):
        return {
            'id':self.id,
            'name':self.name,
            'description':self.description,
            'type': self.type,
            'store':self.destination.name
        }

    @staticmethod
    def getFilePatternByID(in_path,id):
        import os
        return os.path.join(in_path,"file-"+str(id)+".*")

