"""
Test for the `loaders` module.

TODO:
    Need to add tests for IniLoader.
"""

from unittest import TestCase, mock
import loaders


class TestLoaders(TestCase):

    def setUp(self):
        self.factory = loaders.LoaderFactory
        self.target_file_extensions = ['.yml', '.yaml', '.ini']

    # Factory tests
    def test_target_file_exts_is_converted_to_array_if_string(self):
        """
        Test the `target_file_exts` argument is converted to a list if it's a string.
        """
        factory = self.factory('.yml')
        self.assertEqual(factory.target_file_exts, ['.yml'])

    def test_NoTargetFileExtensionsException(self):
        """
        Test a `NoTargetFileExtensionsException` is thrown if the `target_file_exts` argument is empty.
        """
        with self.assertRaises(loaders.NoTargetFileExtensionsError):
            factory = self.factory([])
            factory.get_loader('.yml')

    def test_get_loader_returns_instance_of_YamlLoader(self):
        """
        Test `Factory.get_loader()` correctly returns an instance of YamlLoader.
        """
        factory = self.factory(self.target_file_extensions)
        loader = factory.get_loader('.yml')
        self.assertIsInstance(loader, loaders.YamlLoader)

    def test_get_loader_returns_instance_of_IniLoader(self):
        """
        Test `Factory.get_loader()` correctly returns an instance of IniLoader.
        """
        factory = self.factory(self.target_file_extensions)
        loader = factory.get_loader('.ini')
        self.assertIsInstance(loader, loaders.IniLoader)

    def test_get_loader_returns_None_if_file_extension_is_not_targeted(self):
        """
        Test `Factory.get_loader()` correctly returns `None` if the file extension provided is not targeted..
        """
        factory = self.factory(self.target_file_extensions)
        loader = factory.get_loader('.invalid')
        self.assertEqual(loader, None)

    def test_get_loader_throws_NoLoaderFoundException(self):
        """
        Test `Factory.get_loader()` throws a `NoLoaderFoundException` if no loader is found for a targeted
        file extension.
        """
        with self.assertRaises(loaders.NoLoaderFoundError):
            factory = self.factory('.noloader')
            factory.get_loader('.noloader')

    # Loader tests
    def test_YamlLoader_load_opens_path_correctly(self):
        """
        Test `YamlLoader.load()` opens path correctly.
        """
        path = 'path/to/file.yml'
        mock_open = mock.mock_open(read_data=yaml_test_data())
        with mock.patch('loaders.loaders.open', mock_open):
            yaml_loader = loaders.YamlLoader()
            yaml_loader.load(path)
        mock_open.assert_called_once_with(path)

    def test_YamlLoader_load_returns_correct_data(self):
        """
        Test `YamlLoader.load()` returns the correct data.
        """
        mock_open = mock.mock_open(read_data=yaml_test_data())
        with mock.patch('loaders.loaders.open', mock_open):
            yaml_loader = loaders.YamlLoader()
            result = yaml_loader.load('path/to/file.yml')
        self.assertEqual(result, yaml_as_dict())

# Test fixtures.
def yaml_as_dict():
    """
    The yaml test data formatted as a dictionary.

    :return: Yaml test data in dict form.
    """
    return {
        'First': 'one',
        'Second': 'two',
        'Third': [
            'Alpha',
            'Bravo',
            {'Charlie': ['Delta', 'Echo', 'Foxtrot']}
        ],
        'Fourth': 'four'
    }


def yaml_test_data():
    """
    The yaml data to test with.

    :return: The test data in yaml format.
    """
    return '''
        First: one
        Second: two
        Third:
            - Alpha
            - Bravo
            - Charlie:
                - Delta
                - Echo
                - Foxtrot
        Fourth: four
    '''
