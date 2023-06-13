# AutoVR.ai

AI-powered toolkit for converting 2D media into immersive VR using local hardware

---

## Installation

This might be a bit rough for now, but I'll try to make it easier to install in the future. Development was done with python version `3.10.11`.

```
git clone https://github.com/AutoVRai/AutoVRai.git
cd AutoVRai
python3 -m venv venv
source venv/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

### Requirements

These should be handled by `requirements.txt` or `setup.py` but I'm not sure if I'm doing it right. In the meantime, you can try:

```bash
pip install -r requirements.txt
```


## Simple Usage Examples

Launching the CLI using all default settings:
```bash
python autovrai
```

Launching the GUI starting with all default settings:
```bash
python autovrai --gui
```

Showing the CLI and GUI help information:
```bash
python autovrai --help
```

Launching the CLI with custom settings:
```bash
python autovrai --input-source 'c:\Users\Someone\Somewhere' --device-name 'cpu'
```

Launching the CLI with a custom config file (needs created by you, see below):
```bash
python autovrai --config 'configs/some-config.json'
```

## Configuration, Defaults, Parameters, and Options, Oh My!

The full set of default values can be seen in `configs/__defaults__.json`, but that file should not be changed. Instead, you can create new config files and override the values you want to change. The defaults get loaded automatically, the entire config object gets replaced if you provide a custom config file with the `--config configs/my_config.json` option. After that, any other parameters provided when launching will take priority. This behavior works the same for the CLI mode and GUI mode, but the config information at launch will just be the default initial values for the GUI.

All of the config file properties directly match the CLI options and mean the exact same thing. The only difference is that the config file properties are all lowercase and use dashes instead of underscores. For example, `--input-source` becomes `input-source` in the config file. The config file is just a `json` file, so you can use any text editor to create or edit it. The `configs/__defaults__.json` file is a good starting point for creating your own config file. I'll be using the `--option-name` and `option-name` interchangeably throughout the documentation to help drive home a key concept. The `config` object represents the singular driver and control mechanism, but there are many ways to access and change it. If you have just been using the GUI so far, there are very few differences between the labels you see in the web app versus the CLI options. Mostly just a couple things that were easier to represent in the GUI a little differently that should be documented in the `jsonschema` file (just use `--help` to see it).

Special Note: There are some mutually exclusive options, such as ones related to `--precision-*` or `--padding-*`. For example, if you provide `--precision-factor` you are not allowed to provide `--precision-height` or `--precision-width`, but if you do give one of those two, you have to give both. This is enforced by the somewhat confusing `jsonschema` rules and the IDE help information I've gotten in some tools hasn't been great. I've also added some special handling for these when provided via the CLI that might be confusing, but it was the only reasonable / reliable way I could come up with. If you provide one of the `--*-factor`, `--*-width`, or `--*-height` options, the corresponding directly incompatible options will immediately be removed from the current config object. For example,  if you had `precision-factor` defined in your custom config

The resulting `config` object is used and updated throughout the program to determine how to run. It is re-validated against the `configs/__schema__.json` file representing the AutoVR.ai specific config `jsonschema` definition. That definition also helps provide some documentation on what each parameter does, acceptable values, and other information. The CLI `--help` information and the GUI help blocks are imported from that schema dynamically. That is to ensure the usage documentation only lives in one place. Be sure to include the `$schema` element in any custom config files similar to how it appears in `__defaults__.json`. The easiest way to do that is to copy the `__defaults__.json` file and rename it to anything that doesn't start and end with `__`, the files in that directory that match the `__*__.json` pattern are reserved for future use. Any other files in the `configs` directory are ignored by git, so you can create your own config files there without worrying about accidentally having them overwritten or committing them.

In the future there will be an option to save the current config to a file or to load a config file from within the GUI. For now, the `jsonschema` gives a pretty nice interface for creating a config file manually when using something like VS Code. We could use some help improving and expanding the documentation in general, but also with centralizing some information from the `jsonschema` into a markdown web-ready format. Let me know if interested in helping with that. At that point I'd like to still have something generate the `jsonschema` from the markdown.
