from CustomTasks.AvailableInputs.AbstractBaseInput import AbstractBaseInput, Destination
import json, os

class BooleanInput(AbstractBaseInput):
    def __init__(self, default=False,**kw):
        super().__init__(**kw)
        self.default = default
        self.type="boolean"
        self.destination = Destination.mainjson


    def definition(self):
        df = super().definition()
        df.update({
            'default': self.default
        })
        return df

    def check(self,in_path):
        mainfile = os.path.join(in_path,"main.json")
        if os.path.exists(mainfile):
            try:
                jsoninput = json.load(open(mainfile))
                try:
                    svalue = str(jsoninput['inputs'][self.id])
                    bvalue = svalue.lower() == str(True).lower()
                    return bvalue
                except:
                    raise Exception("No value/input entry or no valid boolean value.")
            except:
                raise Exception("Error parsing main.json.")
        else:
            raise Exception("main.json does not exists.")