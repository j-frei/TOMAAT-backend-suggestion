from CustomTasks.AvailableInputs.AbstractBaseInput import AbstractBaseInput, Destination
import json, os

class FloatInput(AbstractBaseInput):
    def __init__(self, default=0,**kw):
        super().__init__(**kw)
        self.default = default
        self.type="float"
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
                    fvalue = float(jsoninput['inputs'][self.id])
                    return fvalue
                except:
                    raise Exception("No value/input entry or no valid float.")
            except:
                raise Exception("Error parsing main.json.")
        else:
            raise Exception("main.json does not exists.")