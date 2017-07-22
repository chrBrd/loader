#!/usr/bin/env python3

"""
File loader factory

The factory uses a file's extension to find, instantiate and return a loader object that handles that file type.

TODO:
    Look into making the loader objects singletons; they probably don't need instantiated each time.
"""

from abc import ABCMeta, abstractmethod
import yaml
import configparser

__all__ = ['LoaderError', 'NoLoaderFoundError', 'NoTargetFileExtensionsError',
           'LoaderFactory', 'Loader', 'YamlLoader', 'IniLoader']


class LoaderError(Exception):
    def __init__(self, msg=''):
        """
        Base class for Loader exceptions.

        :param msg: Human readable error message describing the exception.
        """
        self.msg = msg
        print(self.msg)
        Exception.__init__(self, msg)

    def __repr__(self):
        return self.msg

    __str__ = __repr__


class NoLoaderFoundError(LoaderError):
    def __init__(self, file_extension):
        """
        Exception thrown when no loader is found for a targeted file type.

        :param file_extension: The target file extension without a loader.
        """
        self.file_extension = file_extension
        self.msg = 'No loader found for file extension `{}` in LoaderFactory.'.format(file_extension)
        super().__init__(self.msg)


class NoTargetFileExtensionsError(LoaderError, AttributeError, ValueError):
    def __init__(self):
        """
           Exception thrown when an empty `target_file_extensions` value is passed to the LoaderFactory's constructor.
        """
        self.msg = 'The LoaderFactory\'s `target_file_extensions` attribute must not be empty.'
        super().__init__(self.msg)


class LoaderFactory:
    def __init__(self, target_file_exts):
        """
        Loader factory class.

        Uses a file's extension to find, instantiate and return a loader object that handles that file type.

        :param target_file_exts: An iterable type containing the file extensions targeted by the loader factory.
            Cannot be left empty. If a single file extension is passed as a string it will be converted to a list.
        """
        self.target_file_exts = target_file_exts

    @property
    def target_file_exts(self):
        """
        Getter for the `target_file_exts` attribute.
        """
        return self._target_file_exts

    @target_file_exts.setter
    def target_file_exts(self, target_file_exts):
        """
        Setter for the `target_file_exts` attribute.

        :param target_file_exts: An iterable type containing the file extensions targeted by the loader factory.
            Cannot be left empty. If a single file extension is passed as a string it will be converted to a list.
        """
        # Raise an exception if target_file_exts is empty.
        if not target_file_exts:
            raise NoTargetFileExtensionsError()
        # Convert target_file_exts to a list if it's a string.
        elif isinstance(target_file_exts, str):
            target_file_exts = [target_file_exts]
        self._target_file_exts = target_file_exts

    def get_loader(self, file_ext):
        """
        Get the loader associated with a particular file extension.

        :param file_ext: The file extension to find a loader for.
        :return: Returns an instance of the Loader subclass associated with the file extension.
        :raise NoLoaderFoundException: Raised when no loader is found for a file extension specified
            in the factory's `target_file_exts` attribute.
        """
        if file_ext not in self.target_file_exts:
            return None
        for loader in Loader.__subclasses__():
            if loader.check_extension_supported(file_ext):
                return loader()
        # Raise an exception if no loaders were found to handle the file.
        raise NoLoaderFoundError(file_ext)


class Loader(metaclass=ABCMeta):
    """
    Base class for all file loaders.

    :var cls._SUPPORTED_EXTS: The file extensions supported by the loader.
    """
    _SUPPORTED_EXTS = None

    @abstractmethod
    def load(self, path):
        """
        Abstract load method for file loaders

        :param path: The path to the file to be loaded.
        :return: The data loaded from the file.
        """
        pass

    @classmethod
    def check_extension_supported(cls, file_ext):
        """
        Use a file's extension to check if a loader supports it.

        :param file_ext: The file extension to check against.
        :return: A boolean indicating whether the loader supports the file extension.
        """
        if file_ext in cls._SUPPORTED_EXTS:
            return True


class YamlLoader(Loader):
    """
    Loader handling Yaml files
    """
    _SUPPORTED_EXTS = ['.yml', '.yaml']

    def load(self, path):
        """
        Load .yml and .yaml files.

        :param path: The path to the file to be loaded.
        :return: A dictionary containing the data loaded from the file.
        """
        with open(path) as stream:
            return yaml.load(stream)


class IniLoader(Loader):
    """
    Loader handling config and ini files.
    """
    _SUPPORTED_EXTS = ['.ini', '.config']

    def __init__(self):
        """
        :ivar self.config: An instance of the `configparser` module's `ConfigParser` class.
        """
        self.config = configparser.ConfigParser()

    def load(self, path):
        """
        Load .config and .ini files.

        :param path: The path to the file to be loaded.
        :return: A dictionary containing the data loaded from the file.
        """
        try:
            self.config.read(path)
        # Add a section header to the file if it doesn't have one and read it again.
        except configparser.MissingSectionHeaderError:
            self._add_section_head(path)

        return {
            section: {
                option: self.config.get(section, option) for option in self.config.options(section)
            } for section in self.config.sections()
        }

    def _add_section_head(self, path):
        """
        Add a section header to the file if it doesn't have one and read it again.
        """
        with open(path, 'r') as stream:
            self.config.read_string('[__headless__]\n' + stream.read())
