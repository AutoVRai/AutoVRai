import os
import cv2
import argparse
import datetime
from tqdm import trange


def video_shredder(filename, output):
    video = cv2.VideoCapture(filename)

    if not video.isOpened():
        print(f"Error: Could not open the video file {filename}")
        return

    # if we don't have an output folder, we will use the name of the video file
    if output is None:
        output = os.path.splitext(filename)[0]

    if not os.path.exists(output):
        os.makedirs(output)

    # make sure we have an output folder one way or another by now
    if not os.path.exists(output):
        raise Exception(f"Error: Could not find or create the output folder {output}")

    # get some basic video metadata for later
    count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    digits = len(str(count))

    for i in trange(count):
        ret, frame = video.read()

        if not ret:
            break

        filepath = os.path.join(output, f"frame_{i:0{digits}d}.png")

        cv2.imwrite(filepath, frame)

    print(f"Extracted {count} frames to {output} from {filename} successfully.")


def main():
    print("Current Timestamp:", datetime.datetime.now())

    parser = argparse.ArgumentParser(description="Extract images from a video file.")
    parser.add_argument("filename", help="The video file to be processed")
    parser.add_argument(
        "--output",
        help=(
            "The output folder for the images, it will make a folder named "
            "after the video file if a location is not provided."
        ),
    )
    args = parser.parse_args()

    video_shredder(args.filename, args.output)
    print("Current Timestamp:", datetime.datetime.now())


if __name__ == "__main__":
    main()
