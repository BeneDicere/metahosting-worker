#!/usr/bin/env python

import argparse
import ConfigParser
import importlib
import logging
from workers.common.instance_management import LocalInstanceManagement


def _get_cfg_as_dict(config):
    """
    Converts a ConfigParser object into a dictionary.

    The resulting dictionary has sections as keys which point to a dict of the
    sections options as key => value pairs.
    """
    config_dict = {}
    for section in config.sections():
        config_dict[section] = {}
        for key, val in config.items(section):
            config_dict[section][key] = val
    return config_dict


def _get_backend_class(config):
    """
    :param config: worker configuration (inifile parsed to dict)
    :return: worker backend class
    """
    class_data = config['worker']['backend'].split(".")
    module_path = ".".join(class_data[:-1])
    module = importlib.import_module(module_path)
    class_str = class_data[-1]
    return getattr(module, class_str)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="get debug output",
                        action="store_true")
    parser.add_argument("--envfile",
                        help="provide a file that tells which not-default "
                             "environment variables to use")
    parser.add_argument("--config", help="provide a config file")
    args = parser.parse_args()
    if args.debug:
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
    if args.config:
        config = ConfigParser.SafeConfigParser()
        config.readfp(open(args.config))
    else:
        config = ConfigParser.SafeConfigParser()
        config.readfp(open('config.ini'))
    config = _get_cfg_as_dict(config)

    instances = LocalInstanceManagement(config)
    worker_class = _get_backend_class(config)
    worker = worker_class(config, instances)

    worker.start()

if __name__ == "__main__":
    run()