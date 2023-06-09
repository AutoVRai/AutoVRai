########################################################################################
##### If anyone can explain why I needed to the portion below, PLEASE let me know. #####

import sys
import os

# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)

# Get the parent directory of the current file
parent_directory = os.path.dirname(current_file_path)

# Get the grandparent directory (one level up from the parent directory)
grandparent_directory = os.path.dirname(parent_directory)

# Add the ?uncle? directory to the Python path (this is where the ZoeDepth package is)
sys.path.insert(0, os.path.join(grandparent_directory, "ZoeDepth"))

# Add the grandparent directory to the Python path
sys.path.insert(0, grandparent_directory)

##### If anyone can explain why I needed to the portion above, PLEASE let me know. #####
########################################################################################


import autovrai


if __name__ == "__main__":
    print(
        "--- AutoVR.ai ---", "Ok, let's go. Loading configuration and building CLI..."
    )
    schema = autovrai.load_schema()
    defaults = autovrai.load_defaults()

    # builds and processes a command line argument parser based on the configuration
    # schema. the defaults passed in are only for the help information, they are not
    # actually used to set the defaults
    args = autovrai.handle_argparse(schema, defaults)

    print(
        "--- AutoVR.ai ---",
        "Configuration and CLI built successfully. Interpreting config...",
    )

    # this gives us the fully interpreted config including the defaults, the user config
    # if given, and the command line argument overrides. this is the config object that
    # should be used for the rest of the program's execution. it has been validated
    # against the configuration schema and is guaranteed to be a valid configuration.
    # it MUST be re-validated if it is modified
    config = autovrai.interpret_config(defaults, args)

    print("--- AutoVR.ai ---", "Configuration loaded successfully. Loading model...")
    print(
        "--- AutoVR.ai ---",
        "(you can ignore all the ZoeDepth output, we change things later)",
    )

    model = autovrai.model_loader(config)

    print("--- AutoVR.ai ---", "Model loaded successfully. Ready!")

    # main entry point for the program, it'll either launch the GUI or start immediately
    if args.gui:
        print("--- AutoVR.ai ---", "Launching gradio GUI...")
        autovrai.launch_gui(model, config)
    else:
        input_type = config["input-type"]
        input_source = config["input-source"]
        source_type = autovrai.determine_file_or_path(input_source, "input-source")

        print(
            "--- AutoVR.ai ---",
            f"Processing {input_type} from the {source_type}: {input_source}",
        )

        # for the CLI, if the input is a single file, we'll use the directory processing
        # functions by tweaking the config a bit, this is slightly different than how
        # the GUI works, it takes in an actual image and returns an image, but we are
        # taking in a filename and need to save a file back out. this makes it act as if
        # the user had selected a directory containing a single file using the exact
        # filename as the only pattern to match, letting everything else work as normal
        if source_type == "file":
            config["input-source"] = os.path.dirname(input_source)
            config["input-patterns"] = [os.path.basename(input_source)]

        # now we just need to call the appropriate image or video processing function
        if input_type == "videos" or input_type == "video":
            autovrai.process_video_directory(model, config)
        elif input_type == "images" or input_type == "image":
            autovrai.process_image_directory(model, config)
        else:
            raise Exception(
                "Invalid input type or source type mismatch. "
                "This should have been caught by the schema validation."
            )

    print("--- AutoVR.ai ---", "We're all done. Hope it worked!")


# this is by far the most useful, interesting, and largest open source project i've ever
# really worked on. i can be very opinionated about certain things around software dev
# at times, but i always try to welcome new thoughts, ideas, or different paradigms.
# i've had a lot of success designing and building things as a consultant that i
# honestly wasn't ever sure of until i got proper feedback from the devs and users that
# would be dealing with it long after i was gone. so, while this is new and while i
# still have time to be fully engaged working on this stuff, please reach out if you
# would like to discuss some of the approaches i've taken here and/or if you believe
# there may be other better ways. with that said, i'm only interested in things with
# more basis than "just because", "best practices", or anything just based on your
# opinion without an explanation of why. i love back and for discussions on this sort of
# thing, you should be able to find me pretty easily on our discord server. i'm always
# happy to talk about this stuff. oh and be sure to mention something if you think
# something might be wrong, broken, or could be better, i do really want to know. also,
# don't hesitate to bring something up as a suggestion or idea before you even dive into
# some big pull request. it might be easier and better for everyone to chat first
# because i probably will be really opinionated on the final code for a while, but i
# HATE the idea of rejecting a pull request that someone put a lot of time and effort
# into. collaboration is great

# oh, last thing, i'll always try to keep this as hackable as possible. i have a
# prototype of how to make it super easy to monkey patch the hell out of this thing to
# try and improve it or do whatever
