#!/usr/bin/env python

import argparse
import config_manager
import importlib
import logging
import signal
from workers.manager.persistence import PersistenceManager
from queue_managers import send_message


def _get_backend_class(config):
    """
    :param config: worker configuration
    :return: worker backend class
    """
    class_data = config['backend'].split(".")
    module_path = ".".join(class_data[:-1])
    module = importlib.import_module(module_path)
    class_str = class_data[-1]
    return getattr(module, class_str)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug",
                        help="get debug output",
                        action="store_true")
    parser.add_argument("--logstash",
                        help="log everything (in addition) to logstash "
                             ", give host:port")
    parser.add_argument("--envfile",
                        help="provide a file that tells which not-default "
                        "environment variables to use")
    parser.add_argument("--config",
                        help="provide a config file")
    args = parser.parse_args()
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    if args.config:
        config_manager._CONFIG_FILE = args.config
    if args.logstash:
        import logstash
        host, port = args.logstash.split(':')
        logger.addHandler(logstash.TCPLogstashHandler(host=host,
                                                      port=int(port)))

    local_persistence = PersistenceManager(
        config=config_manager.get_configuration('local_persistence'),
        send_method=send_message)

    worker_config = config_manager.get_configuration('worker')
    worker_env = config_manager.get_configuration('configurable_env')
    worker_class = _get_backend_class(worker_config)
    worker = worker_class(worker_config,
                          worker_env,
                          local_persistence,
                          send_message)

    signal.signal(signal.SIGTERM, worker.stop)
    signal.signal(signal.SIGHUP, worker.stop)
    signal.signal(signal.SIGINT, worker.stop)
    worker.start()

if __name__ == "__main__":
    run()
