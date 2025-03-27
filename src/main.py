import queue

from video_source import GStreamerVideoSource
from processor import MockDataProcessor

if __name__ == "__main__":
    q = queue.Queue()
    processor = MockDataProcessor(queue=q)
    video = GStreamerVideoSource(callback=processor.process_frame)
    try:
        video.start()
    except KeyboardInterrupt:
        video.stop()
    while not q.empty():
        print(q.get())