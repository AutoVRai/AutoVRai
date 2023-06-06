import os
from PIL import Image

def modify_images(input_folder, output_folder, width, height, background_color=(0, 0, 0)):
    file_count = sum([len(files) for r, d, files in os.walk(input_folder)])
    print(f'Total number of files: {file_count} (might be doubled or tripled?)')

    processed = 0
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(('left-right.png', 'left-right.jpg', 'left-right.jpeg')):
                image_path = os.path.join(root, file)
                image = Image.open(image_path)
                new_image = Image.new("RGB", (2 * width, height), background_color)

                left_image = image.crop((0, 0, image.width // 2, image.height))
                right_image = image.crop((image.width // 2, 0, image.width, image.height))

                new_image.paste(left_image, (width//2 - left_image.width//2, height//2 - left_image.height//2))
                new_image.paste(right_image, (width + width//2 - right_image.width//2, height//2 - right_image.height//2))

                new_image.save(os.path.join(output_folder, file))

                processed += 1
                if processed % 25 == 0:
                    print(f'Processed {processed} files.')

    print('Done processing all files.')


input_folder = 'output2'
output_folder = 'final2'
width = 1920
height = 1920
background_color = (0, 0, 0)  # RGB for white

modify_images(input_folder, output_folder, width, height, background_color)
