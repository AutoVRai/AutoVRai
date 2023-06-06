import argparse
import json
import jsonschema
import os


if __name__ == '__main__':
    # Load the schema for our configuration definitions
    schema_file = os.path.join('configs', '__schema__.json')
    with open(schema_file, 'r') as f:
        schema = json.load(f)

    defaults_file = os.path.join('configs', '__defaults__.json')
    with open(defaults_file, 'r') as f:
        config = json.load(f)

    # Validate the default configuration against the schema
    jsonschema.validate(config, schema)

    # Create the ArgumentParser
    parser = argparse.ArgumentParser(
        prog=schema['title'],
        description=schema['description']
    )

    # Add arguments based on the schema properties
    for prop, details in schema['properties'].items():
        if prop == '$schema':
            continue

        # if it is an array, set the nargs and assign the array type to the base type for the next statement to work properly
        if details['type'] == 'array':
            details['type'] = details['items']['type']
            nargs = '+'
        else:
            nargs = None

        arg_type = str if details['type'] == 'string' else int if details['type'] == 'integer' else float if details['type'] == 'number' else None

        # we can just bring these in as a float because it can represent either type
        if arg_type is None and details['type'] == ['number', 'integer']:
            arg_type = float

        # make sure we aren't skipping anything accidentally
        if arg_type is None:
            raise ValueError(f"Unsupported type defined in the configuration schema file: {details['type']}")

        default = config.get(prop) if config.get(prop) else '""'
        parser.add_argument(
            f'--{prop}',
            nargs=nargs,
            type=arg_type,
            help=f"{details['description']} (default: {default})"
        )

    # Parse the arguments
    args = parser.parse_args()

    # Update the default configuration with provided arguments
    for prop, value in vars(args).items():
        if value is not None:
            config[prop] = value

    # Validate the updated configuration against the schema
    jsonschema.validate(config, schema)

    # Now you can use the updated and validated configuration
    print("Updated and validated configuration:", config)
