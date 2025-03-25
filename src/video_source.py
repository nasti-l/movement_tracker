from typing import Callable
import numpy as np
from base import VideoSourceBase
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib, GObject

'''
A video source that uses GStreamer to capture webcam video with a simple pipeline
from v4l2src (webcam input) to fakesink (a dummy output that discards frames). 
This is a starting point to get video flowing, which will later expand to process frames.
'''
class GStreamerVideoSource(VideoSourceBase):
    def __init__(self, callback: Callable[[np.ndarray], None]):
        super().__init__(callback)
        Gst.init(None)
        self.__pipeline: Gst.Pipeline = self.__pipeline_init()
        self.__main_loop: GLib.MainLoop = self.__loop_init()

#TODO: make configurable
    def __pipeline_init(self, source: str = "v4l2src",
                        device: str = "/dev/video0",
                        sink: str = "autovideosink") -> Gst.Pipeline:
        pipeline = Gst.Pipeline()
        src = Gst.ElementFactory.make(source, "source")
        src.set_property("device", device)
        sink = Gst.ElementFactory.make(sink, "sink")
        pipeline.add(src)
        pipeline.add(sink)
        src.link(sink)
        return pipeline

    def __loop_init(self):
        return GLib.MainLoop()

    def start(self):
        self.__pipeline.set_state(Gst.State.PLAYING)
        self.__main_loop.run()

    def stop(self):
        if self.__pipeline:
            self.__pipeline.set_state(Gst.State.NULL)
        self.__main_loop.quit()
