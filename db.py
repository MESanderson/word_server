import importlib


def init(config):
    db = importlib.import_module('db_interfaces.{}'.format(config['db']))
    db.init(config)
    return db


