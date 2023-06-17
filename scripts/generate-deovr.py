import cv2
import os
import glob
import json
import socket
import argparse
from PIL import Image


def generate_image_thumbnail(image_file, thumb_path):
    image = Image.open(image_file)
    # just use the left half of the image for the thumbnail (assuming it is stereo)
    image = image.crop((0, 0, image.width // 2, image.height))
    image.thumbnail((256, 256))
    image.save(thumb_path)


def generate_video_thumbnail(video_file, thumb_path):
    cap = cv2.VideoCapture(video_file)
    cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_FRAME_COUNT) // 2)
    ret, frame = cap.read()
    # just use the left half of the image for the thumbnail (assuming it is stereo)
    frame = frame[:, : frame.shape[1] // 2]
    # turn the frame into a thumbnail version similar to PIL.Image.thumbnail
    frame = cv2.resize(frame, (256, 256), interpolation=cv2.INTER_AREA)
    if ret:
        cv2.imwrite(thumb_path + ".png", frame)
    cap.release()


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


def build_config(url, path, crawl, thumbs, patterns):
    if not os.path.exists(path):
        raise ValueError(f"The specified path {path} does not exist.")

    if not url:
        url = f"http://{get_local_ip()}:8000/"

    if not patterns:
        patterns = ["*.jpg", "*.jpeg", "*.png", "*.mp4"]

    thumbs = thumbs if thumbs else "thumbs/"
    thumbs_path = os.path.join(path, thumbs)
    if not os.path.exists(thumbs_path):
        os.makedirs(thumbs_path)

    scenes = {"scenes": []}

    if crawl:
        for root, dirs, files in os.walk(path):
            video_scene = {"name": f"Videos ({root})", "list": []}
            image_scene = {"name": f"Images ({root})", "list": []}
            scenes["scenes"].extend([image_scene, video_scene])
            for pattern in patterns:
                for filename in glob.glob(os.path.join(root, pattern)):
                    if pattern == "*.mp4":
                        add_video(video_scene, url, root, filename, thumbs)
                    else:
                        add_image(image_scene, url, root, filename, thumbs)
    else:
        video_scene = {"name": "Videos", "list": []}
        image_scene = {"name": "Images", "list": []}
        scenes["scenes"].extend([image_scene, video_scene])
        for pattern in patterns:
            for filename in glob.glob(os.path.join(path, pattern)):
                if pattern == "*.mp4":
                    add_video(video_scene, url, path, filename, thumbs)
                else:
                    add_image(image_scene, url, path, filename, thumbs)

    with open(os.path.join(path, "deovr"), "w") as f:
        json.dump(scenes, f)

    print("--- AutoVR.ai ---", f"DeoVR config file written to {path}/deovr.")
    print(
        "--- AutoVR.ai ---",
        f"To start a local web server:  python -m http.server --directory {path}",
    )
    print(
        "--- AutoVR.ai ---",
        f"Once that is started, you can open this URL in the DeoVR browser:  {url}",
    )


def add_image(scene, url, base_path, image_file, thumbs):
    relative_path = os.path.relpath(image_file, base_path)
    thumb_file = os.path.join(thumbs, os.path.basename(image_file))
    thumb_path = os.path.join(base_path, thumb_file)
    if not os.path.exists(thumb_path):
        generate_image_thumbnail(image_file, thumb_path)
    image_id = int(os.path.getmtime(image_file))  # unix timestamp
    image = {
        "path": f"{url}{relative_path}",
        "thumbnailUrl": f"{url}{thumb_file}",
        "title": os.path.basename(image_file),
        "screenType": "flat",
        "stereoMode": "sbs",
        "is3d": True,
        "id": image_id,
    }
    scene["list"].append(image)


def add_video(scene, url, base_path, video_file, thumbs):
    relative_path = os.path.relpath(video_file, base_path)
    thumb_file = os.path.join(thumbs, os.path.basename(video_file)) + ".png"
    thumb_path = os.path.join(base_path, thumb_file)
    if not os.path.exists(thumb_path):
        generate_video_thumbnail(video_file, thumb_path)
    video_id = int(os.path.getmtime(video_file))  # unix timestamp
    video = {
        "encodings": [
            {"name": "h264", "videoSources": [{"url": f"{url}{relative_path}"}]}
        ],
        "thumbnailUrl": f"{url}{thumb_file}",
        "title": os.path.basename(video_file),
        "screenType": "flat",
        "stereoMode": "sbs",
        "is3d": True,
        "id": video_id,
    }
    scene["list"].append(video)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Builds the DeoVR json configuration file."
    )
    parser.add_argument(
        "--url",
        help="The base url to use for everything. If not provided, the script will attempt to generate it.",
    )
    parser.add_argument(
        "--path",
        default="output",
        help="The location where the script should start looking for media files.",
    )
    parser.add_argument(
        "--crawl",
        action="store_true",
        help="If provided, the script will also check each sub directory under the path and will generate a new scene for each directory that has files.",
    )
    parser.add_argument(
        "--thumbs",
        help="The location to find the associated thumbnail images. If not provided, the default `thumbs/` will be used.",
    )
    parser.add_argument(
        "--patterns",
        nargs="+",
        help='The set of file patterns to find, such as "*.png", "*.mp4", or "*.jpg".',
    )
    args = parser.parse_args()

    build_config(args.url, args.path, args.crawl, args.thumbs, args.patterns)
