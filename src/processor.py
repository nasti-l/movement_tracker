import queue
import random
import time
import numpy as np

from base import DataProcessorBase


class MockDataProcessor(DataProcessorBase):
    def __init__(self, queue: queue.Queue):
        super().__init__(output_queue=queue)

    def process_frame(self, frame: np.ndarray):
        head_y = np.mean(frame[0:frame.shape[0]//3, :, :]) # mock head location calculation
        accel_y = random.uniform(-10, -8)
        timestemp = time.time()
        posture = "slouching" if head_y > 0 else "normal"
        metadata = {"timestamp": timestemp,
                       "accel_y": accel_y,
                       head_y: head_y,
                       "posture": posture}
        self._output_queue.put(metadata)