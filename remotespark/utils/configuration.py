"""Utility to read configs for spark magic.
"""
# Copyright (c) 2015  aggftw@gmail.com
# Distributed under the terms of the Modified BSD License.

import json
import copy

from remotespark.utils.constants import CONFIG_JSON
from remotespark.utils.utils import join_paths, get_magics_home_path, get_livy_kind
from remotespark.utils.filesystemreaderwriter import FileSystemReaderWriter

_overrides = None


def initialize(fsrw_class=None):
    """Checks if the configuration is initialized. If so, initializes the
    global configuration object by reading from the configuration
    file, overwriting the current set of overrides if there is one"""
    global _overrides
    if _overrides is None:
        load(fsrw_class)


def load(fsrw_class=None):
    """Initializes the global configuration by reading from the configuration
    file, overwriting the current set of overrides if there is one"""
    if fsrw_class is None:
        fsrw_class = FileSystemReaderWriter
    home_path = fsrw_class(get_magics_home_path())
    home_path.ensure_path_exists()
    config_file = fsrw_class(join_paths(home_path.path, CONFIG_JSON))
    config_file.ensure_file_exists()
    config_text = config_file.read_lines()
    line = "".join(config_text).strip()
    if line == "":
        overrides = {}
    else:
        overrides = json.loads(line)
    override_all(overrides)


def override_all(obj):
    """Given a dictionary representing the overrided defaults for this
    configuration, initialize the global configuration."""
    global _overrides
    _overrides = obj


def override(config, value):
    """Given a string representing a configuration and a value for that configuration,
    override the configuration. Initialize the overrided configuration beforehand."""
    initialize()
    _overrides[config] = value


def _override(f):
    """A decorator which first initializes the overrided configurations,
    then checks the global overrided defaults for the given configuration,
    calling the function to get the default result otherwise."""
    def ret():
        global _overrides
        initialize()
        name = f.__name__
        if name in _overrides:
            return _overrides[name]
        else:
            return f()
    # Hack! We do this so that we can query the .__name__ of the function
    # later to get the name of the configuration dynamically, e.g. for unit tests
    ret.__name__ = f.__name__
    return ret


def get_session_properties(language):
    properties = copy.deepcopy(session_configs())
    properties["kind"] = get_livy_kind(language)
    return properties


# All of the functions below return the values of configurations. They are
# all marked with the _override decorator, which returns the overridden
# value of that configuration if there is any such configuration. Otherwise,
# these functions return the default values described in their bodies.


@_override
def session_configs():
    return {}


@_override
def kernel_python_credentials():
    return {'username': '', 'password': '', 'url': 'http://localhost:8998'}


@_override
def kernel_scala_credentials():
    return {'username': '', 'password': '', 'url': 'http://localhost:8998'}


@_override
def logging_config():
    return {
        "version": 1,
        "formatters": {
            "magicsFormatter": {
                "format": "%(asctime)s\t%(levelname)s\t%(message)s",
                "datefmt": ""
            }
        },
        "handlers": {
            "magicsHandler": {
                "class": "remotespark.utils.filehandler.MagicsFileHandler",
                "formatter": "magicsFormatter"
            }
        },
        "loggers": {
            "magicsLogger": {
                "handlers": ["magicsHandler"],
                "level": "DEBUG",
                "propagate": 0
            }
        }
    }

@_override
def events_handler_class():
    return "remotespark.utils.eventshandler.EventsHandler"


@_override
def status_sleep_seconds():
    return 2


@_override
def statement_sleep_seconds():
    return 2


@_override
def wait_for_idle_timeout_seconds():
    return 15


@_override
def livy_session_startup_timeout_seconds():
    return 60


@_override
def fatal_error_suggestion():
    return """The code failed because of a fatal error:
\t{}.

Some things to try:
a) Make sure Spark has enough available resources for Jupyter to create a Spark context.
b) Contact your Jupyter administrator to make sure the Spark magics library is configured correctly.
c) Restart the kernel."""


@_override
def ignore_ssl_errors():
    return False


@_override
def use_auto_viz():
    return True


@_override
def default_maxrows():
    return 2500


@_override
def default_samplemethod():
    return "take"


@_override
def default_samplefraction():
    return 0.1


@_override
def max_slices_pie_graph():
    return 100
