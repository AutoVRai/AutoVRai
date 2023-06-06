import os
import numpy as np
from tqdm import trange
from PIL import Image

from autovrai import DepthModel, colorize, save_raw_16bit
from autovrai import stereo_eyes, combine_left_right, combine_anaglyph, padded_left_right
from autovrai import find_filenames, load_image


def process_single_video(model: DepthModel, config, video):
    print("This will be implemented soon in another version, but for now you can use the video shredder and video stitcher from the scripts directory.")
    pass

def process_video_directory(model: DepthModel, config):
    print("This will be implemented soon in another version, but for now you can use the video shredder and video stitcher from the scripts directory.")
    pass

def process_single_image(model: DepthModel, config, image):
#     depth = predict(model_name, model, image, depth_width, depth_height)
#     depthmap = colorize(depth, cmap='gray_r')

#     left, right = stereo_eyes(image, depth, divergence)

#     stereo = combine_left_right(left, right)
#     padded = padded_left_right(left, right, padded_width, padded_height)
#     anaglyph = combine_anaglyph(left, right)

#     return [depthmap, stereo, padded, anaglyph]
    pass

def process_image_directory(model: DepthModel, image_location, stereo_location, padded_location, anaglyph_location, depthmap_location, depthraw_location, divergence=2.5):

    # make sure all of our directories exist
    stereo_dir = make_directory(stereo_location)
    padded_dir = make_directory(padded_location)
    anaglyph_dir = make_directory(anaglyph_location)
    depthmap_dir = make_directory(depthmap_location)
    depthraw_dir = make_directory(depthraw_location)
    
    filenames, file_count = find_filenames(image_location, patterns)

    for i in trange(file_count):
        filename = filenames[i]
        filepath = os.path.basename(filename)

        image = load_image(filename)

        # if iwidth == 1024 and iheight == 1024:
        #     pwidth = 1440
        #     pheight = 1440
        #     depth = predict(model_name, model, image, 896, 896)
        # elif iwidth == 1024 and iheight == 768:
        #     dwidth = 1024
        #     dheight = 768
        #     pwidth = 2048
        #     pheight = 1440
        


        # if image_width > depth_width or image_height > depth_height:
            # depth = predict(model_name, model, image, depth_width, depth_height)
        # else:
        #     depth = predict(model_name, model, image, image_width, image_height)

        

        model.core.prep.resizer._Resize__width = image.width
        model.core.prep.resizer._Resize__height = image.height

        depth: np.ndarray = model.infer_pil(image, output_type="numpy")


        left, right = stereo_eyes(image, depth, divergence)

        if stereo_dir != '':
            stereo = combine_left_right(left, right)
            stereo.save(os.path.join(stereo_dir, filepath))
        if padded_dir != '':
            padded = padded_left_right(left, right, int(round(image.width*1.5)), int(round(image.height*1.5)))
            padded.save(os.path.join(padded_dir, filepath))
        if anaglyph_dir != '':
            anaglyph = combine_anaglyph(left, right)
            anaglyph.save(os.path.join(anaglyph_dir, filepath))
        if depthmap_dir != '':
            depthmap = Image.fromarray(colorize(depth, cmap='gray_r'))
            depthmap.save(os.path.join(depthmap_dir, filepath))
        if depthraw_dir != '':
            save_raw_16bit(depth, os.path.join(depthraw_dir, filepath))
 
    return []





# from myloader import load_ai_model_wrapper
# from something import millions_of_widgets

# def do_the_processing(model, widget):
#     # do something with model and widget, but I want
#     # these to be typed properly in this function
#     pass

# if __name__ == '__main__':
#     model = load_ai_model_wrapper()
#     for widget in millions_of_widgets:
#         do_the_processing(model, widget)
