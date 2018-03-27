from CustomTasks.AvailableInputs.AbstractBaseInput import AbstractBaseInput, Destination
import json, os

class VolumeInput(AbstractBaseInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.type="volume"
        self.destination = Destination.file


    def definition(self):
        df = super().definition()
        df.update({})
        return df

    def check(self,in_path):
        pathpattern = AbstractBaseInput.getFilePatternByID(in_path, self.id)
        from glob import glob
        # search for file
        possible_filepaths = glob(pathpattern)
        if len(possible_filepaths) != 1:
            raise Exception("Not exactly one file found.")

        filepath = possible_filepaths[0]
        # check for SimpleITK import capabilities
        import SimpleITK as sitk
        try:
            a = sitk.ReadImage(filepath)
            return a
        except:
            raise Exception("Unsupported volume filetype")