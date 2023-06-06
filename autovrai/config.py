import argparse
import json
import jsonschema
import os


# treating these as a singletons
SCHEMA = None
DEFAULTS = None


def load_schema():
    global SCHEMA
    if SCHEMA == None:
        with open(os.path.join('configs', '__schema__.json'), 'r') as f:
            SCHEMA = json.load(f)
    return SCHEMA


def validate_config(config):
    jsonschema.validate(config, load_schema())
    return config


def load_config(filepath):
    with open(filepath, 'r') as f:
        return validate_config(json.load(f))


def load_defaults():
    global DEFAULTS
    if DEFAULTS == None:
        DEFAULTS = load_config(os.path.join('configs', '__defaults__.json'))
    return DEFAULTS


def handle_argparse(schema, defaults):
    # Create the ArgumentParser
    parser = argparse.ArgumentParser(
        prog=schema['title'],
        description=schema['description']
    )

    # Add the optional config file argument
    parser.add_argument('--config-file', type=str, help='Optional. Path to the configuration file to use instead of the defaults, other parameters will still override this configuration file')

    # Add arguments based on the schema properties
    for prop, details in schema['properties'].items():
        if prop == '$schema':
            continue

        # if it is an array, set nargs and assign the array type to the base type, simplifies things
        if details['type'] == 'array':
            details['type'] = details['items']['type']
            nargs = '+'
        else:
            nargs = None

        # translate the basic types to the python types we need
        arg_type = str if details['type'] == 'string' else int if details['type'] == 'integer' else float if details['type'] == 'number' else None

        # we can just bring these in as a float because it can represent either type
        if arg_type is None and details['type'] == ['number', 'integer']:
            arg_type = float

        # make sure we aren't skipping or missing anything accidentally (these should never happen)
        if arg_type is None:
            raise ValueError(f"Unsupported type defined in the configuration schema file: {details['type']}")
        if details['description'] is None:
            raise ValueError(f"Missing description for property {prop} in the configuration schema file")

        # generate the default info for the end of the help info if a set of defaults were passed in
        if defaults != None:
            default_info = defaults.get(prop) if defaults.get(prop) else '""'
            default_info = f" (default: {default_info})"
        else:
            default_info = ""

        parser.add_argument(
            f'--{prop}',
            nargs=nargs,
            type=arg_type,
            help=f"{details['description']}{default_info}"
        )

    # Return the parsed arguments
    return parser.parse_args()


def interpret_config(defaults, args):
    # build the actual config object
    config = defaults
    if args.config_file != None:
        custom = load_config(args.config_file)
        validate_config(custom)
        config.update(custom)
        validate_config(config)

    # apply the command line parameter overrides to the config if there are any
    for prop, value in vars(args).items():
        if prop == 'config_file' or value is None:
            continue
        else:
            config[prop] = value

    # validate then return the final config object
    return validate_config(config)
