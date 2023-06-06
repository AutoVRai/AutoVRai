import gradio as gr


def launch_gui(config, model):
    print("--- AutoVR.ai ---", "oops, didn't finish building this yet")


# with gr.Blocks() as demo:

#     with gr.Tab("Single Image"):
#         with gr.Row():
#             input_image = gr.Image(label="Input Image", type='pil', elem_id='img-display-input').style(height="auto")
#             depth_image = gr.Image(label="Depth Map", elem_id='img-display-depthmap')
#         with gr.Row():
#             stereo_image = gr.Image(label="Stereo Image", elem_id='img-display-stereo')
#             padded_image = gr.Image(label="Padded Image", elem_id='img-display-padded')
#         with gr.Row():
#             anaglyph_image = gr.Image(label="Anaglyph Image", elem_id='img-display-anaglyph')
#         submit_single = gr.Button("Submit Single")
#         submit_single.click(run_single_image, inputs=[input_image], outputs=[depth_image, stereo_image, padded_image, anaglyph_image])


#     with gr.Tab("Image Directory"):
#         with gr.Row():
#             image_location = gr.Textbox(label="Source Image Location", placeholder="Path to source image directory")
#         with gr.Row():
#             stereo_location = gr.Textbox(label="Output Stereo Location", placeholder="Path to output stereo image directory, leave blank to skip")
#         with gr.Row():
#             padded_location = gr.Textbox(label="Output Padded Location", placeholder="Path to output padded image directory, leave blank to skip")
#         with gr.Row():
#             anaglyph_location = gr.Textbox(label="Output Anaglyph Location", placeholder="Path to output anaglyph image directory, leave blank to skip")
#         with gr.Row():
#             depthmap_location = gr.Textbox(label="Output Depthmap Location", placeholder="Path to output depthmap image directory, leave blank to skip")
#         submit_directory = gr.Button("Submit Directory")
#         submit_directory.click(run_image_directory, inputs=[image_location, stereo_location, padded_location, anaglyph_location, depthmap_location], outputs=[])


# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description='WEB - AutoVR.ai - an AI-powered toolkit for converting 2D media into immersive VR using local hardware')

#     parser.add_argument('images', type=str, help='Path to image directory')


#     demo.queue().launch()
