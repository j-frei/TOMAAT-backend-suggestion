from AbstractTask import AbstractTask
from CustomTasks.AvailableInputs.FloatInput import FloatInput
from CustomTasks.AvailableInputs.SingleChoiceInput import SingleChoiceInput

# Example for a provided task implementation
class FloatComputationTask(AbstractTask):
    task_identifier = "FloatComputation"
    description = "This Service performs a multiplication or addition of two floats"
    inputs = [
        FloatInput(id="f1",pretty_name="first float"),
        FloatInput(id="f2", pretty_name="second float"),
        SingleChoiceInput(id="op", choices=["add","multiply"],defaultIndex=1,pretty_name="float operation")
    ]

    def perform(self):
        import os, tarfile, time
        print("Performing a Float Computation Task")
        f1 = self.cleaned_values['f1']
        f2 = self.cleaned_values['f2']
        op = self.cleaned_values['op']

        if op == "add":
            symbol = "+"
            computationResult = f1 + f2
        else:
            symbol = "*"
            computationResult = f1 * f2

        outfile_path = os.path.join(self.dir,"out","result.txt")
        outfile = open(outfile_path,"w",encoding="utf-8")
        outfile.write("{} {} {} = {}".format(str(f1),symbol,str(f2),str(computationResult)))
        outfile.close()


        # writing back dummy result
        achive_output_path = os.path.join(self.dir,"out","result.tar.gz")
        with tarfile.open(achive_output_path, "w:gz") as tar:
            tar.add(outfile_path,arcname=os.path.basename(outfile_path))
        print("Task performed!")