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


# this is a custom argparse action that ensures an argument is only provided once, i'm
# not sure if there's a better way to do this, but it works for now. also, how is this
# not a built in argparse action? it kinda seems like it should be...
class SingleUseAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest) is not None:
            parser.error(f"{option_string} can only be provided once.")
        setattr(namespace, self.dest, values)


# this does all the heavy lifting of building the argparse parser based on the schema
def handle_argparse(schema, defaults):
    # Create the actual ArgumentParser
    parser = argparse.ArgumentParser(
        prog=schema["title"], description=schema["description"]
    )

    # separation of adding additional special arguments that don't come from the schema
    parser = add_special_arguments(parser)

    # Add arguments based on the schema properties
    for prop, details in schema["properties"].items():
        if prop == "$schema":
            continue

        prop_type = details["type"]

        # our basic types, boolean is special cased below
        type_translation = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
        }
        arg_type = None
        nargs = None

        # for an array, set nargs and use the array item type as a basic type lookup
        if prop_type == "array":
            arg_type = type_translation.get(details["items"]["type"])
            nargs = "+"

        # we need to pick one for compound types, these might need manually expanded
        if prop_type == ["string", "integer", "number"]:
            arg_type = str
        if prop_type == ["number", "integer"]:
            arg_type = float
        if prop_type == ["integer", "number"]:
            arg_type = float

        # translate the basic types to the python types we need, this isn't everything
        if arg_type is None:
            arg_type = type_translation.get(prop_type)

        # make sure we aren't skipping or missing anything accidentally
        if arg_type is None:
            raise ValueError(
                f"Unsupported type defined in the config schema file: {prop_type}"
            )
        if details["description"] is None:
            raise ValueError(
                f"Missing description for property {prop} in the config schema file"
            )

        # generate the (default: ) info for the help descriptions, based on the defaults
        if defaults != None:
            default_info = defaults.get(prop, "")
            default_info = f" (default: {default_info})"
        else:
            default_info = ""

        # bring it all together and add the argument to the parser
        if prop_type == "boolean":
            parser.add_argument(
                f"--{prop}",
                help=f"{details['description']}{default_info}",
                action="store_true",
            )
        else:
            parser.add_argument(
                f"--{prop}",
                nargs=nargs,
                type=arg_type,
                help=f"{details['description']}{default_info}",
                action=SingleUseAction,
            )

    return special_error_checking(parser)


def special_error_checking(parser):
    # making sure there are no unknown arguments, they would almost certainly be a typo
    args, unknowns = parser.parse_known_args()
    if unknowns:
        parser.error(f"Unknown arguments: {' '.join(unknowns)}")

    # check for options that must be provided as a pair such as: --*-width or --*-height
    if (args.precision_width is None) != (args.precision_height is None):
        parser.error("--precision-width and --precision-height must both be provided.")
    if (args.padded_width is None) != (args.padded_height is None):
        parser.error("--padded-width and --padded-height must both be provided.")

    # Check for bad combinations of `--*-width`, `--*-height`, and `--*-factor` options
    incomplete = (args.precision_width is None) != (args.precision_height is None)
    multiple = args.precision_factor is not None and (
        args.precision_width is not None or args.precision_height is not None
    )
    if incomplete or multiple:
        parser.error(
            "Provide either --precision-factor or "
            "both --precision-width and --precision-height"
        )
    incomplete = (args.padded_width is None) != (args.padded_height is None)
    multiple = args.padded_factor is not None and (
        args.padded_width is not None or args.padded_height is not None
    )
    if incomplete or multiple:
        parser.error(
            "Provide either --padded-factor or "
            "both --padded-width and --padded-height"
        )

    # Return the parsed and known arguments
    return args


def interpret_config(defaults, args):
    # build the actual config object
    if args.config != None:
        # load the custom config file if there is one
        config = load_config(args.config)
        validate_config(config, f"Loaded custom config file: {args.config}")
    else:
        # otherwise just use the defaults
        config = defaults

    # remove the `--*-factor` if `--*-width` or `--*-height` are set
    if args.precision_width is not None or args.precision_height is not None:
        config.pop("precision-factor", None)
    if args.padded_width is not None or args.padded_height is not None:
        config.pop("padded-factor", None)

    # remove the `--*-width` and `--*-height` if the `--*-factor` is set
    if args.precision_factor is not None:
        config.pop("precision-width", None)
        config.pop("precision-height", None)
    if args.padded_factor is not None:
        config.pop("padded-width", None)
        config.pop("padded-height", None)

    # apply the command line parameter overrides to the config if there are any
    for prop, value in vars(args).items():
        prop = prop.replace("_", "-")
        if value is None or prop in ["config", "gui", "browser", "network"]:
            continue
        else:
            config[prop] = value

    # validate then return the final config object
    return validate_config(config, "After Applying CLI Overrides")


def add_special_arguments(parser):
    # Add the optional config file argument, this will replace the defaults
    parser.add_argument(
        "--config",
        type=str,
        help=(
            "Optional. Path to the configuration file to use instead of the defaults. "
            "Other parameters will still override this configuration file."
        ),
        action=SingleUseAction,
    )

    # Add the optional gui mode argument, sends the application down a different path
    parser.add_argument(
        "--gui",
        action="store_true",
        help=(
            "Optional. This launches the gradio app web server instead of just "
            "processing. It will use all config info and overrides as the initial "
            "state of the web app. You can create multiple shortcuts to launch the "
            "web app to be pre-configured in different ways."
        ),
    )

    # Add the optional gui mode argument, sends the application down a different path
    parser.add_argument(
        "--browser",
        action="store_true",
        help=(
            "Optional. Only used with --gui option. "
            "This will launch the web app in your default browser when it is ready."
        ),
    )

    # Add the optional gui mode argument, sends the application down a different path
    parser.add_argument(
        "--network",
        action="store_true",
        help=(
            "Optional. Only used with --gui option. "
            "This will make the web app accessible from your local network. "
            "Otherwise, it will only be accessible from your local machine."
        ),
    )

    return parser
