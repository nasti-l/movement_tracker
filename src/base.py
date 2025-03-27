import threading
from abc import ABC, abstractmethod
from typing import Callable
import queue
import numpy as np

class VideoSourceBase(ABC):
    def __init__(self, callback: Callable[[np.ndarray], None]):
        self._callback = callback

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

class DataProcessorBase(ABC):
    def __init__(self, output_queue: queue.Queue):
        self._output_queue = output_queue

    @abstractmethod
    def process_frame(self, frame: np.ndarray):
        pass

class ThreadedComponentBase(ABC):
    def __init__(self):
        self.running = False
        self._thread = threading.Thread(target=self._run_loop, daemon=True)

    def start(self):
        self.running = True
        self._thread.start()

    def stop(self):
        self.running = False
        self._thread.join()

    @abstractmethod
    def _run_loop(self):
        pass

class StorageBase(ABC):
    pass

class UIBase(ABC):
    pass