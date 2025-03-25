from video_source import GStreamerVideoSource

if __name__ == "__main__":
    video = GStreamerVideoSource(callback=lambda _: None)
    try:
        video.start()
    except KeyboardInterrupt:
        video.stop()