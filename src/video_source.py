from typing import Callable
import numpy as np
from base import VideoSourceBase
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib, GObject
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GStreamerVideoSource(VideoSourceBase):
    def __init__(self, callback: Callable[[np.ndarray], None]):
        super().__init__(callback)
        logger.info("Initializing GStreamer...")
        Gst.init(None)
        logger.info("Creating pipeline...")
        self.__pipeline: Gst.Pipeline = self.__pipeline_init()
        logger.info("Creating main loop...")
        self.__main_loop: GLib.MainLoop = self.__loop_init()
        bus = self.__pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.__on_bus_message)
        logger.info("Initialization complete")

    def __pipeline_init(self, source: str = "v4l2src",
                        device: str = "/dev/video0",
                        sink: str = "autovideosink") -> Gst.Pipeline:
        pipeline = Gst.Pipeline()
        src = Gst.ElementFactory.make(source, "source")
        if not src:
            logger.error("Failed to create source element")
            raise RuntimeError("Failed to create source")
        src.set_property("device", device)
        sink = Gst.ElementFactory.make(sink, "sink")
        if not sink:
            logger.error("Failed to create sink element")
            raise RuntimeError("Failed to create sink")
        pipeline.add(src)
        pipeline.add(sink)
        if not src.link(sink):
            logger.error("Failed to link source to sink")
            raise RuntimeError("Failed to link elements")
        logger.debug("Pipeline initialized successfully")
        return pipeline

    def __loop_init(self):
        logger.debug("Initializing GLib MainLoop")
        return GLib.MainLoop()

    def __on_bus_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            logger.error(f"Pipeline error: {err}, Debug info: {debug}")
            self.stop()
        elif t == Gst.MessageType.EOS:
            logger.info("End of stream reached")
            self.stop()

    def start(self):
        logger.info("Starting pipeline...")
        ret = self.__pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            logger.error("Failed to start pipeline")
            return
        logger.info("Running main loop...")
        self.__main_loop.run()
        logger.info("Main loop exited")

    def stop(self):
        logger.info("Stopping pipeline...")
        if self.__pipeline:
            self.__pipeline.set_state(Gst.State.NULL)
        logger.info("Quitting main loop...")
        self.__main_loop.quit()

if __name__ == "__main__":
    video = GStreamerVideoSource(callback=lambda _: None)
    try:
        video.start()
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt, stopping video...")
        video.stop()