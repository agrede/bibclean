import importlib
import regex
import os


class PluginMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.register_plugin(cls)

    def register_plugin(cls, plugin):
        instance = plugin
        cls.plugins.append(instance)


class Plugin(metaclass=PluginMount):
    pass


rePC = regex.compile(r'^(?!__init|test).*.py$')


def imp_plugins(path):
    for f in os.listdir(path):
        if rePC.search(f):
            importlib.import_module('.'.join([path, f[:-3]]))
