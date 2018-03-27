from AbstractComputeSource import AbstractComputeSource
from CustomTasks.DummyTask import DummyTask
from CustomTasks.InnerEarTasks.InnerEarSegmentationTask import InnerEarSegmentationTask

class GPU0ComputeSource(AbstractComputeSource):
    supported_tasks = [DummyTask, InnerEarSegmentationTask]

    @classmethod
    def initialize(cls):
        print("GPU0ComputeSource: Masking CUDA Devices, using Device 0.")
        import os
        os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
        os.environ["CUDA_VISIBLE_DEVICES"]="0"

