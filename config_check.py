from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from configparser import ConfigParser
import os

color = '\033[91m'
reset = '\033[0m'
bold = '\033[1m'
def print_config_err(file: str, section: str, option=None):
    if option is not None:
        output = f"Missing option {bold}{option}{reset}{color} in section {bold}{section}{reset}{color}"
    else:
        output = f"Missing section {bold}{section}{reset}{color}"
    print(f"{color}CONFIG_ERROR: {output} in {bold}{file}{reset}{color}")

def config_check(config: ConfigParser):
    example = ConfigParser()
    example.read('config-example.ini')
    failed = False
    for section in config.sections():
        if not example.has_section(section):
            failed = True
            print_config_err("config-example.ini", section)
        else:
            for option in config.options(section):
                if not example.has_option(section, option):
                    failed = True
                    print_config_err("config-example.ini", section, option)

    for section in example.sections():
        if not config.has_section(section):
            failed = True
            print_config_err("config.ini", section)
        else:
            for option in example.options(section):
                if not config.has_option(section, option):
                    failed = True
                    print_config_err("config.ini", section, option)
    if failed:
        print(reset)
    return not failed

config = ConfigParser()

if not os.path.exists("./config.ini"):
    raise Exception("Config.ini does not exist. Try copying config-example.ini as config.ini")

def get_config():
    return config

def load_config():
    global config
    config = ConfigParser()
    config.read('config.ini')
    if not config_check(config):
        print("There were errors while reading the config file. Please make sure all properties are in both config.ini and config-example.ini.")
        os._exit(0)
    print("Loaded config")

# Hot reload configuration
class ConfigLoader(FileSystemEventHandler):
    def on_modified(self, event: FileSystemEvent) -> None:
        if (event.src_path == ".\config.ini"):
            load_config()

def start_observer():
    global observer
    observer = Observer()
    observer.schedule(ConfigLoader(), ".", recursive=False)
    observer.start()