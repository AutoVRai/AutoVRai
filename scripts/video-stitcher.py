import os
import glob
import argparse
import datetime
from moviepy.editor import ImageSequenceClip, VideoFileClip, AudioFileClip


def find_filenames(location, patterns):
    # Check if directory exists
    if not os.path.exists(location):
        return "Directory does not exist."

    # List to store image file names
    filenames = []

    # Iterate over patterns and append matching files to the list
    for pattern in patterns:
        filenames.extend(glob.glob(os.path.join(location, pattern)))

    # Return the sorted list of image files
    return sorted(filenames), len(filenames)


def create_video_from_images(input_dir, output_file, video_file, audio_file, fps):
    patterns = ["*.png", "*.jpg", "*.jpeg"]

    # Get the list of file names
    filenames, file_count = find_filenames(input_dir, patterns)

    if not filenames:
        print(f"No images found in the input folder: {input}")
        return

    # try to load the video file, set the frame rate if it wasn't provided explicitly
    video = VideoFileClip(video_file) if video_file else None
    if not video and video_file:
        print(f"Failed to load the video file: {video_file}")
        return
    elif not fps:
        fps = video.fps

    # we need a frame rate one way or another
    if not fps:
        print("Failed to determine the frame rate.")
        return

    # try to load the audio file, otherwise try to use the audio from the video
    audio = AudioFileClip(audio_file) if audio_file else None
    if not audio:
        if audio_file:
            print(f"Failed to load the audio file: {audio_file}")
            return
        elif video:
            audio = video.audio

    # give a soft warning if we don't have any audio, but continue anyway
    if not audio:
        print("Warning: No audio was found.")

    # create the actual video clip from the images and add the audio
    final = ImageSequenceClip(filenames, fps=fps)
    final.set_audio(audio)

    # save the final results
    final.write_videofile(output_file, codec="libx264", audio_codec="aac")

    print(f"Created video file {output_file} from {file_count} images.")


def main():
    print("Current Timestamp:", datetime.datetime.now())

    parser = argparse.ArgumentParser(description="Stich a video from a set of images.")

    parser.add_argument("input", help="Path to the input folder containing the images.")
    parser.add_argument("output", help="Path to use for the output video file.")

    parser.add_argument(
        "--video",
        help="Path to the original video file. Used for the audio and frame rate.",
    )
    parser.add_argument(
        "--audio",
        help="Path to the audio portion to use. Must also provide --fps.",
    )
    parser.add_argument(
        "--fps",
        type=int,
        help=(
            "Specific frame rate to use. This will override what was found in the "
            "original video and typically shouldn't be used with --video, but --fps "
            "is required if --video isn't provided."
        ),
    )

    args = parser.parse_args()

    if not args.video and not args.fps:
        print("You must provide --video or --fps so we have the right frame rate.")
        return

    create_video_from_images(args.input, args.output, args.video, args.audio, args.fps)

    print("Current Timestamp:", datetime.datetime.now())


if __name__ == "__main__":
    main()
