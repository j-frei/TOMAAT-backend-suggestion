from AbstractTask import AbstractTask
from CustomTasks.AvailableInputs.SingleChoiceInput import SingleChoiceInput

# Example for a provided task implementation
class DummyTask(AbstractTask):
    task_identifier = "Dummy"
    description = "This Service does nothing but waiting for 20 secs, but expects a choice between Bayern, Real and Barcelona as an input."
    inputs = [
        SingleChoiceInput(id="dummyinput",pretty_name="Club",choices=["Bayern","Real","Barcelona"])
    ]

    def perform(self):
        import os, tarfile, time
        print("Performing a very complex task that takes 20 secs...")
        print("My data is at: {}".format(self.dir))
        print("My ID is: {}".format(self.id))
        print("My dummy input value was: {}.".format(self.cleaned_values['dummyinput']))

        time.sleep(20)

        # writing back dummy result
        achive_output_path = os.path.join(self.dir,"out","result.tar.gz")
        with tarfile.open(achive_output_path, "w:gz") as tar:
            tar.add(os.path.join(self.dir,"in","main.json"),arcname="main.json")
        print("Task performed!")