from AbstractComputeSource import AbstractComputeSource
from CustomTasks.DummyTask import DummyTask
from CustomTasks.FloatComputationTask import FloatComputationTask
from CustomTasks.InnerEarTasks.InnerEarSegmentationTask import InnerEarSegmentationTask

# define CustomComputeSources
class GPU1ComputeSource(AbstractComputeSource):
    # Imagine that GPU 1 has only 16MiB VRAM so we can only perform this supid task...
    supported_tasks = [DummyTask,FloatComputationTask]

    @classmethod
    def initialize(cls):
        print("GPU1ComputeSource: Masking CUDA Devices, using Device 1.")
        import os
        os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
        os.environ["CUDA_VISIBLE_DEVICES"]="1"

