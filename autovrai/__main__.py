import sys
import os

# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)

# Get the parent directory of the current file
parent_directory = os.path.dirname(current_file_path)

# Get the grandparent directory (one level up from the parent directory)
grandparent_directory = os.path.dirname(parent_directory)

# Add the grandparent directory to the Python path
sys.path.insert(0, grandparent_directory)

### If anyone can explain to me why I needed to the portion above, PLEASE let me know. ###
##########################################################################################


import autovrai


if __name__ == '__main__':
    schema = autovrai.load_schema()
    defaults = autovrai.load_defaults()

    # builds and processes a command line argument parser based on the configuration schema. the
    # defaults passed in are only for the help information, they are not used to set the defaults
    args = autovrai.handle_argparse(schema, defaults)

    # this gives us the fully interpreted config including the defaults, the user config if given,
    # and the command line argument overrides. this is the config object that should be used for
    # the rest of the program's execution. it has been validated against the configuration schema
    # and is guaranteed to be a valid configuration. it MUST be re-validated if it is modified
    config = autovrai.interpret_config(defaults, args)

    print(config)
