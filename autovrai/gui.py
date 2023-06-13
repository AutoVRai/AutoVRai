import gradio as gr

import autovrai


CONFIG = None
PROPS = None
INPUTS = None


# this is a simplified way to build out some of the base components, but won't be used
# for the more complex or non-conforming ones
def component(name, kind=None):
    global CONFIG, PROPS, INPUTS

    # try to get all of the common attributes based on the name of our property
    type = PROPS[name].get("type", None)
    enums = PROPS[name].get("enum", None)
    min = PROPS[name].get("minimum", None)
    max = PROPS[name].get("maximum", None)
    step = PROPS[name].get("multipleOf", None)
    item = PROPS[name].get("items.type", None)
    info = PROPS[name].get("description", None)
    default = CONFIG.get(name, None)

    input = None

    if kind == None:
        if enums != None:
            kind = "Radio"
        elif type == "string" or type == "array":
            kind = "Textbox"
        elif type == "integer" or type == "number":
            kind = "Slider"
        elif type == "boolean":
            kind = "Checkbox"
        else:
            raise ValueError(f"Property: {name} - Unsupported component type: {type}")

    if kind == "Dropdown":
        input = gr.Dropdown(label=name, choices=enums, info=info, value=default)
    elif kind == "Radio":
        input = gr.Radio(label=name, choices=enums, info=info, value=default)
    elif kind == "Textbox":
        input = gr.Textbox(label=name, info=info, value=default)
    elif kind == "Directory":
        input = gr.File(label=name, info=info, file_count="directory")
    elif kind == "Slider":
        input = gr.Slider(
            label=name,
            minimum=min,
            maximum=max,
            step=step,
            info=info,
            value=default,
        )
    elif kind == "Checkbox":
        input = gr.Checkbox(label=name, info=info, value=default)
    elif kind == "ColorPicker":
        input = gr.ColorPicker(label=name, info=info, value=default)
    else:
        raise ValueError(f"Property: {name} - Unknown kind: {kind}")

    INPUTS.add(input)
    return input


def handle_inputs(inputs):
    # clearing our config definition and rebuilding it from the inputs
    global CONFIG
    CONFIG = {}
    for input, value in inputs.items():
        if value == None or value == "":
            continue
        CONFIG[input.label] = value

    print("")
    print("CONFIG: ", CONFIG)
    print("")


def launch_gui(config, schema):
    global CONFIG, PROPS, INPUTS
    CONFIG = config
    PROPS = schema["properties"]
    INPUTS = {0}
    INPUTS.clear()

    with gr.Blocks() as gui:
        with gr.Tab("Image Directory") as tab:
            with gr.Row():
                component("model-name")
                component("device-name")
            with gr.Row():
                component("precision-mode")

            with gr.Row():
                component("precision-factor")
            with gr.Row():
                component("precision-width")
            with gr.Row():
                component("precision-height")
            with gr.Row():
                component("input-type")
            with gr.Row():
                component("input-patterns")
            with gr.Row():
                component("input-source", "Directory")
            with gr.Row():
                component("input-depthmap")
            with gr.Row():
                component("input-depthraw")
            with gr.Row():
                component("output-stereo")
            with gr.Row():
                component("output-padded")
            with gr.Row():
                component("output-anaglyph")
            with gr.Row():
                component("output-depthmap")
            with gr.Row():
                component("output-depthraw")
            with gr.Row():
                component("padded-color", "ColorPicker")
            with gr.Row():
                component("padded-factor")
            with gr.Row():
                component("padded-width")
            with gr.Row():
                component("padded-height")
            with gr.Row():
                component("stereo-intensity")

            submit_directory = gr.Button("Submit Directory")
            submit_directory.click(fn=handle_inputs, inputs=INPUTS, outputs=[])

    gui.queue().launch(server_name="0.0.0.0")
