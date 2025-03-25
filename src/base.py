from abc import ABC, abstractmethod
from typing import Callable
import numpy as np

class VideoSourceBase(ABC):
    def __init__(self, callback: Callable[[np.ndarray], None]):
        self.callback = callback
    @abstractmethod
    def start(self):
        pass
    @abstractmethod
    def stop(self):
        pass

class DataProcessorBase(ABC):
    pass

class StorageBase(ABC):
    pass

class UIBase(ABC):
    pass