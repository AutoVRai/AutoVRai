import gradio as gr

import autovrai


CONFIG = None
PROPS = None
INPUTS = None
PROGRESS = None

# customizing the gradio output a bit for some very opinionated reasons. the "share"
# option is not something we want to support at the moment. it doesn't really line up
# with the way we expect people to use this project. it also felt inconsistent to not
# have the `--- AutoVR.ai ---` prefix on the output, so we're adding that here as well.
gr.strings.en["RUNNING_LOCALLY_SEPARATED"] = (
    "--- AutoVR.ai --- " + "Running gradio web app on local URL:  {}://{}:{}"
)
gr.strings.en["PUBLIC_SHARE_TRUE"] = "--- AutoVR.ai --- " + "Press Ctrl+C to quit"


# this is a simplified way to build out some of the base components, but won't be used
# for the more complex or non-conforming ones
def component(name, kind=None, interactive=True):
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
        input = gr.Dropdown(
            label=name, interactive=interactive, choices=enums, info=info, value=default
        )
    elif kind == "Radio":
        input = gr.Radio(
            label=name, interactive=interactive, choices=enums, info=info, value=default
        )
    elif kind == "Textbox":
        input = gr.Textbox(
            label=name, interactive=interactive, info=info, value=default
        )
    elif kind == "Directory":
        input = gr.File(
            label=name, interactive=interactive, info=info, file_count="directory"
        )
    elif kind == "Slider":
        input = gr.Slider(
            label=name,
            interactive=interactive,
            minimum=min,
            maximum=max,
            step=step,
            info=info,
            value=default,
        )
    elif kind == "Checkbox":
        input = gr.Checkbox(
            label=name, interactive=interactive, info=info, value=default
        )
    elif kind == "ColorPicker":
        input = gr.ColorPicker(
            label=name, interactive=interactive, info=info, value=default
        )
    else:
        raise ValueError(f"Property: {name} - Unknown kind: {kind}")

    INPUTS.add(input)
    return input


def handle_submit_click(inputs):
    # clearing our config definition and rebuilding it from the inputs
    global CONFIG, PROGRESS
    CONFIG = {}
    for input, value in inputs.items():
        if value == None or value == "" or value == 0 or value == []:
            continue
        CONFIG[input.label] = value

    print("")
    print("CONFIG: ", CONFIG)
    print("")

    return autovrai.process_image_directory(CONFIG, gr.Progress())


def handle_device_name_change(device_name):
    if device_name == "cpu":
        return [gr.update(value="manual", interactive=False), gr.update(open=True)]
    else:
        return [gr.update(interactive=True), gr.update()]


def create_help_checkbox():
    help = gr.Checkbox(
        label="Show Help Info",
        value=False,
        info="Turns on/off help info (like this) for each component.",
    )
    js_to_toggle_class = "() => document.body.classList.toggle('hide-info')"
    help.input(fn=None, _js=js_to_toggle_class)
    return help


def dimension_attachments(factor, width, height):
    clear1 = lambda _: gr.update(value=0) if _ != 0 else gr.update()
    clear2 = lambda _: [clear1(_), clear1(_)]
    height.input(fn=clear1, inputs=height, outputs=[factor])
    width.input(fn=clear1, inputs=width, outputs=[factor])
    factor.input(fn=clear2, inputs=factor, outputs=[width, height])


def gui_layout():
    with gr.Box() as basics:
        with gr.Row(variant="panel"):
            with gr.Column():
                input_source = component("input-source")
                output_stereo = component("output-stereo")
            with gr.Column():
                stereo_intensity = component("stereo-intensity")
                help = create_help_checkbox()
                submit = gr.Button("Submit", variant="primary")

    with gr.Accordion("Status", open=False) as status:
        progress_output = gr.Textbox(show_label=False, placeholder="Waiting...")

    with gr.Accordion("General", open=False) as general:
        with gr.Row(variant="panel"):
            with gr.Column():
                model_name = component("model-name")
            with gr.Column():
                device_name = component("device-name")

    with gr.Accordion("Precision", open=False) as precision:
        with gr.Row(variant="panel"):
            with gr.Column():
                precision_mode = component("precision-mode")
                precision_factor = component("precision-factor")
            with gr.Column():
                precision_width = component("precision-width")
                precision_height = component("precision-height")
        dimension_attachments(precision_factor, precision_width, precision_height)

    with gr.Accordion("Padded", open=False) as padded:
        with gr.Row(variant="panel"):
            with gr.Column():
                padded_color = component("padded-color", "ColorPicker")
                padded_factor = component("padded-factor")
            with gr.Column():
                padded_width = component("padded-width")
                padded_height = component("padded-height")
        dimension_attachments(padded_factor, padded_width, padded_height)

    with gr.Accordion("Inputs", open=False) as inputs:
        with gr.Row(variant="panel"):
            with gr.Column():
                input_type = component("input-type", interactive=False)
                input_patterns = component("input-patterns", interactive=False)
            with gr.Column():
                input_depthmap = component("input-depthmap", interactive=False)
                input_depthraw = component("input-depthraw", interactive=False)

    with gr.Accordion("Outputs", open=False) as outputs:
        with gr.Row(variant="panel"):
            with gr.Column():
                output_padded = component("output-padded")
                output_anaglyph = component("output-anaglyph")
            with gr.Column():
                output_depthmap = component("output-depthmap")
                output_depthraw = component("output-depthraw")

    submit.click(fn=lambda: gr.update(open=True), outputs=status).then(
        fn=lambda: gr.update(interactive=False), outputs=submit
    ).then(fn=handle_submit_click, inputs=INPUTS, outputs=progress_output).then(
        fn=lambda: gr.update(interactive=True), outputs=submit
    )

    device_name.change(
        fn=handle_device_name_change,
        inputs=device_name,
        outputs=[precision_mode, precision],
    )

    return [basics, general, precision, padded, inputs, outputs]


def launch_gui(config, schema, browser, network):
    global CONFIG, PROPS, INPUTS
    CONFIG = config
    PROPS = schema["properties"]
    INPUTS = {None}
    INPUTS.clear()

    css = ".hide-info { --block-info-text-size: 0px; }"
    theme = gr.themes.Default(text_size="lg").set(
        checkbox_background_color_dark="*neutral_600",
        input_background_fill_dark="*neutral_600",
    )

    with gr.Blocks(theme=theme, mode="autovrai", title="AutoVR.ai", css=css) as demo:
        with gr.Box() as header:
            gr.Markdown(f"# {schema['title']}")
            gr.Markdown(f"### {schema['description']}")

        sections = gui_layout()

        js_on_load = """() => {
            document.body.classList.add('dark');
            document.body.classList.add('hide-info');
        }"""
        demo.load(None, _js=js_on_load)

    if network == True:
        raise ValueError(
            "Network mode is not supported yet, sorry! Currently all file path "
            "references are relative to the current working directory of the "
            "environment running the web app, not the user potentially accessing it "
            "from another computer. This will eventually be changed, but it requires a "
            "slightly less efficient method of 'uploading' files to the web server "
            "instead of letting AutoVR.ai handle reading in batches from local storage."
        )

    demo.queue(api_open=False).launch(
        # shows error messages as a popup window
        show_error=True,
        # the `share` option may not do what you expect and doesn't fit for our project
        share=False,
        # this could be enabled eventually, but would need a lot of testing and some dev
        show_api=False,
        # if `browser` is true, it will launch the URL in the default web browser
        inbrowser=browser,
        # if `network` is true, allow local network connections, else localhost only
        server_name="0.0.0.0" if network else "127.0.0.1",
        # may need to allow some of these to be configurable at some point
        # server_port=7860,
        # favicon_path="favicon.ico",
        # ssl_keyfile=None,
        # ssl_certfile=None,
        # ssl_keyfile_password=None,
        # ssl_verify=True,
    )
