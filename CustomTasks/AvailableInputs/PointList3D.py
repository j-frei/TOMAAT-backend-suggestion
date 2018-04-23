from CustomTasks.AvailableInputs.AbstractBaseInput import AbstractBaseInput, Destination
import json, os

class PointList3DInput(AbstractBaseInput):
    def __init__(self, number_entries = -1, default="",**kw):
        super().__init__(**kw)
        self.default = default
        self.number_entries = -1
        self.type="pointlist"
        self.destination = Destination.mainjson


    def definition(self):
        df = super().definition()
        df.update({
            'default': self.default,
            'number_entries': self.number_entries,
        })
        return df

    def check(self,in_path):
        mainfile = os.path.join(in_path,"main.json")
        if os.path.exists(mainfile):
            try:
                jsoninput = json.load(open(mainfile))
                try:
                    svalue = str(jsoninput['inputs'][self.id])
                    pointlist = [ tuple([ float(c) for c in coords.split(",")]) for coords in svalue.split(";")]

                    if self.number_entries != -1 and len(pointlist) != self.number_entries:
                        raise Exception("Length of point list is {} but {} expected!".format(len(pointlist),self.number_entries))

                    return pointlist
                except:
                    raise Exception("No value/input entry or no valid point list structure.")
            except:
                raise Exception("Error parsing main.json.")
        else:
            raise Exception("main.json does not exists.")