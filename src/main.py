from video_source import GStreamerVideoSource

if __name__ == "__main__":
    def dummy_callback(frame):
        print(f"Frame shape: {frame.shape}")
    video = GStreamerVideoSource(dummy_callback)
    try:
        video.start()
    except KeyboardInterrupt:
        video.stop()