# this config stuff is where i spent more time than anywhere else when transforming
# the project from my hacky prototype to a somewhat less hacky first version i would
# actually let the world see


import argparse
import json
import jsonschema
import os


# treating these basically as singletons
SCHEMA = None
DEFAULTS = None


def load_schema():
    global SCHEMA
    if SCHEMA == None:
        with open(os.path.join("configs", "__schema__.json"), "r") as f:
            SCHEMA = json.load(f)
    return SCHEMA


def validate_config(config, description):
    schema = load_schema()
    try:
        jsonschema.validate(config, schema)
    except jsonschema.ValidationError as e:
        print("")
        print(f"Validation description: {description}\n")
        print(f"Validation error in the configuration file:\n{e.message}\n")
        print(f"Error path: {' -> '.join(map(str, e.path))}\n")
        print("Please fix the configuration file and try again.")
        print("")
        exit(1)
    return config


def load_config(filepath):
    with open(filepath, "r") as f:
        return validate_config(json.load(f), filepath)


def load_defaults():
    global DEFAULTS
    if DEFAULTS == None:
        DEFAULTS = load_config(os.path.join("configs", "__defaults__.json"))

    return DEFAULTS


def handle_argparse(schema, defaults):
    # Create the ArgumentParser
    parser = argparse.ArgumentParser(
        prog=schema["title"], description=schema["description"]
    )

    # Add the optional gui mode argument, sends the application down a different path
    parser.add_argument(
        "--gui",
        action="store_true",
        help=(
            "Optional. This launches the gradio web app server instead of just "
            "processing. It will use all config info and overrides as the initial "
            "state of the web app. You can create multiple shortcuts to launch the "
            "web app pre-configured in different ways."
        ),
    )

    # Add the optional config file argument
    parser.add_argument(
        "--config-file",
        type=str,
        help=(
            "Optional. Path to the configuration file to use instead of the defaults, "
            "other parameters will still override this configuration file"
        ),
    )

    # Add arguments based on the schema properties
    for prop, details in schema["properties"].items():
        if prop == "$schema":
            continue

        type_translation = {
            "string": str,
            "integer": int,
            "number": float,
        }
        arg_type = None
        nargs = None

        # for an array, set nargs and use the array item type as a basic type lookup
        if details["type"] == "array":
            arg_type = type_translation[details["items"]["type"]]
            nargs = "+"

        # we need to pick one for compound types, these might need manually expanded
        if details["type"] == ["string", "integer", "number"]:
            arg_type = str
        if details["type"] == ["number", "integer"]:
            arg_type = float
        if details["type"] == ["integer", "number"]:
            arg_type = float

        # translate the basic types to the python types we need, this isn't everything
        if arg_type is None:
            arg_type = type_translation[details["type"]]

        # make sure we aren't skipping or missing anything accidentally
        if arg_type is None:
            raise ValueError(
                f"Unsupported type defined in the config schema file: {details['type']}"
            )
        if details["description"] is None:
            raise ValueError(
                f"Missing description for property {prop} in the config schema file"
            )

        # generate the (default: ) info for the help descriptions, based on the defaults
        if defaults != None:
            default_info = defaults.get(prop) if defaults.get(prop) else '""'
            default_info = f" (default: {default_info})"
        else:
            default_info = ""

        parser.add_argument(
            f"--{prop}",
            nargs=nargs,
            type=arg_type,
            help=f"{details['description']}{default_info}",
        )

    # Return the parsed arguments
    return parser.parse_args()


def interpret_config(defaults, args):
    # build the actual config object
    config = defaults
    if args.config_file != None:
        custom = load_config(args.config_file)
        validate_config(custom, "CLI Specified Configuration File")
        config.update(custom)
        validate_config(config, "After Merging With Defaults")

    # apply the command line parameter overrides to the config if there are any
    for prop, value in vars(args).items():
        prop = prop.replace("_", "-")
        if prop == "gui" or prop == "config-file" or value is None:
            continue
        else:
            config[prop] = value

    # validate then return the final config object
    return validate_config(config, "After Applying CLI Overrides")
