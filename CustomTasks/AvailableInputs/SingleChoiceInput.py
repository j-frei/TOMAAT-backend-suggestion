from CustomTasks.AvailableInputs.AbstractBaseInput import AbstractBaseInput, Destination
import json, os

class SingleChoiceInput(AbstractBaseInput):
    def __init__(self, choices, defaultIndex=0,**kw):
        super().__init__(**kw)
        if len(choices) == 0:
            raise ValueError("Empty choice list given.")
        self.choices = choices
        self.default = choices[defaultIndex]
        self.type="singlechoice"
        self.destination = Destination.mainjson


    def definition(self):
        df = super().definition()
        df.update({
            'default': self.default,
            'choices': self.choices
        })
        return df

    def check(self,in_path):
        mainfile = os.path.join(in_path,"main.json")
        if os.path.exists(mainfile):
            try:
                jsoninput = json.load(open(mainfile))
                choice = jsoninput['inputs'][self.id]
                if choice in self.choices:
                    return choice
                else:
                    raise Exception("Choice is not valid.")
            except:
                raise Exception("Error parsing main.json.")
        else:
            raise Exception("main.json does not exists.")