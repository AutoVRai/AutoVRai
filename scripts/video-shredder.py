import cv2
import os
import argparse
import math


def extract_images_from_video(video_file, start_time, end_time, batch_size):
    # Open the video file
    video = cv2.VideoCapture(video_file)

    if not video.isOpened():
        print(f"Error: Could not open the video file {video_file}")
        return

    # Calculate the total number of frames in the video
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    
    if start_time is None:
        start_time = 0
    if end_time is None:
        end_time = math.ceil(total_frames / fps)

    start_frame = int(start_time * fps)
    end_frame = int(math.ceil(end_time * fps))
    num_frames = end_frame - start_frame

    num_batches = math.ceil(num_frames / batch_size)
    output_base = os.path.splitext(video_file)[0]

    print(f"Total frames: {total_frames}")
    print(f"Extracting from frame {start_frame} to frame {end_frame}")
    print(f"Number of frames to be extracted: {num_frames}")
    print(f"Number of batches: {num_batches}")

    video.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    os.makedirs(output_base, exist_ok=True)
    for batch in range(num_batches):
        output_folder = f"{output_base}/{batch+1:0{len(str(num_batches))}d}"
        os.makedirs(output_folder, exist_ok=True)

        for i in range(batch_size):
            frame_number = start_frame + batch * batch_size + i
            if frame_number >= end_frame:
                break

            # Read a frame from the video
            ret, frame = video.read()

            # Break the loop if we reached the end of the video
            if not ret:
                break

            # Save the frame as an image
            output_image_file = os.path.join(output_folder, f"frame_{frame_number:04d}.png")
            cv2.imwrite(output_image_file, frame)
        
        print(f"Batch {batch+1}/{num_batches} ({(batch+1)/num_batches*100:.2f}% complete)")

    # Release the video file
    video.release()


def main():
    parser = argparse.ArgumentParser(description="Extract images from a video file.")
    parser.add_argument("video_file", help="The path to the input video file.")
    parser.add_argument("--start_time", type=float, help="Start time (in seconds) to extract frames from (default: start of the video).")
    parser.add_argument("--end_time", type=float, help="End time (in seconds) to extract frames until (default: end of the video).")
    parser.add_argument("--batch_size", type=int, default=100, help="Number of frames per output folder (default: 100).")

    args = parser.parse_args()

    extract_images_from_video(args.video_file, args.start_time, args.end_time, args.batch_size)


if __name__ == "__main__":
    main()
