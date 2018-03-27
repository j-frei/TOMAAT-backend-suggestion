from abc import ABC, abstractmethod


class AbstractValidator(ABC):
    def __init__(self,dir,**kargs):
        self.dir = dir

    # The validator checks for a specific property
    # and throws an Error if something is not fulfilled
    def clean(self):
        pass