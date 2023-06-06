import argparse
from moviepy.editor import *

def combine_video_audio(video_file, audio_file, target_file):
    video = VideoFileClip(video_file)
    audio = AudioFileClip(audio_file)
    
    if abs(video.duration - audio.duration) > 0.1:
        print("Warning: The video and audio files have different lengths.")

    final_video = video.set_audio(audio)
    final_video.write_videofile(target_file, codec="libx264", audio_codec="aac")







if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine video and audio files and convert to MP4 with H264 video codec and AAC audio codec.")
    parser.add_argument("--video", help="Input video file (MP4 or WEBM)")
    parser.add_argument("--audio", help="Input audio file (MP4 or WEBM)")
    parser.add_argument("--target", help="Output MP4 file")

    args = parser.parse_args()

    combine_video_audio(args.video_file, args.audio_file, args.target_file)
