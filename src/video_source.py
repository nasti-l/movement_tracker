from typing import Callable
import numpy as np
from src.base import VideoSourceBase
import gi

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib, GObject
import logging

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

    def _on_new_sample(self, sink):
        sample = sink.emit("pull-sample")
        buf = sample.get_buffer()
        caps = sample.get_caps()
        struct = caps.get_structure(0)
        height = caps.get_structure(0).get_value("height")
        width = caps.get_structure(0).get_value("width")
        format = struct.get_value("format")
        logger.debug(f"Caps: width={width}, height={height}, format={format}, buffer_size={buf.get_size()}")
        data = buf.extract_dup(0, buf.get_size())
        if format == "YUY2":
            frame = np.frombuffer(data, dtype=np.uint8).reshape(height, width, 2)
        else:
            frame = np.frombuffer(data, dtype=np.uint8).reshape(height, width, 3) # RGB
        self._callback(frame)
        return Gst.FlowReturn.OK

    def __pipeline_init(self, source: str = "v4l2src",
                        device: str = "/dev/video0",
                        sink: str = "appsink") -> Gst.Pipeline:
        pipeline = Gst.Pipeline()

        # Create elements
        src = Gst.ElementFactory.make(source, "source")
        if not src:
            logger.error("Failed to create source element")
            raise RuntimeError("Failed to create source")
        src.set_property("device", device)

        # Add videoconvert to handle format conversion
        convert = Gst.ElementFactory.make("videoconvert", "convert")
        if not convert:
            logger.error("Failed to create videoconvert element")
            raise RuntimeError("Failed to create videoconvert")

        sink = Gst.ElementFactory.make(sink, "sink")
        if not sink:
            logger.error("Failed to create sink element")
            raise RuntimeError("Failed to create sink")
        sink.set_property("emit-signals", True) # actively notify via signals when a frame is ready
        sink.connect("new-sample", self._on_new_sample)

        # Add elements to pipeline
        pipeline.add(src)
        pipeline.add(convert)
        pipeline.add(sink)

        # Link elements
        if not src.link(convert):
            logger.error("Failed to link source to videoconvert")
            raise RuntimeError("Failed to link source to videoconvert")
        if not convert.link(sink):
            logger.error("Failed to link videoconvert to sink")
            raise RuntimeError("Failed to link videoconvert to sink")

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