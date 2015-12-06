"""
    Tests for this project
"""
from __future__ import absolute_import, print_function, nested_scopes, generators, with_statement

__author__ = 'Roland'

import unittest
import nose
import os
import json
import sys

import networkx as nx
from networkx import Graph
from networkx.readwrite import json_graph

from googleapiclient import discovery
from googleapiclient.errors import HttpError

from scripts import main_script


class YoutubeApiProceduresTestCases(unittest.TestCase):
    """
    Tests for the youtube-graph script
    """

    TESTING_CHANNEL_ID = 'UC3XTzVzaHQEd30rQbuvCtTQ'
    # remove key from developer console when released
    API_KEY = 'AIzaSyBAnZnN1O9DyBf1btAtOaGxm3Wgf3znBb0'
    INVALID_CODE = '________________________'

    def _youtube_api(self):
        return discovery.build(developerKey=self.API_KEY, serviceName='youtube', version='v3')

    def test_collect_associations(self):
        """
        test an expected set of associations is created,
        given a particular user with known related channels.
        :return:
        """

        testing_target_ids = ['UCVTQuK2CaWaTgSsoNkn5AiQ', 'UCYbinjMxWwjRpp4WqgDqEDA',
                              'UCWPQB43yGKEum3eW0P9N_nQ', 'UCbKo3HsaBOPhdRpgzqtRnqA',
                              'UCy6kyFxaMqGtpE3pQTflK8A', 'UCQzdMyuz0Lf4zo4uGcEujFw',
                              'UCPnlBOg4_NU9wdhRN-vzECQ', 'UCeKum6mhlVAjUFIW15mVBPg']

        # sort the target_list
        testing_target_ids.sort()

        try:
            api = self._youtube_api()
            non_api = discovery.RawModel()      # object that is not actually an api.
            results = main_script.get_association_list(self.TESTING_CHANNEL_ID, api)
        except (HttpError, AttributeError):
            self.fail()

        # sort the results
        results.sort()

        # result and target should be comparable by index
        self.assertEqual(len(results), len(testing_target_ids))

        for i in range(len(results)):
            self.assertEqual(results[i], testing_target_ids[i])

        result = main_script.get_association_list(self.INVALID_CODE, api)
        self.assertEqual(result, [])

        self.assertRaises(RuntimeError, main_script.get_association_list, None, api)
        self.assertRaises(RuntimeError, main_script.get_association_list,
                          self.TESTING_CHANNEL_ID, None)
        self.assertRaises(RuntimeError, main_script.get_association_list, None, None)
        self.assertRaises(RuntimeError, main_script.get_association_list,
                          self.TESTING_CHANNEL_ID, non_api)

    def test_extract_user_name(self):
        """
        test that extract_user_name collects the user_name from a channel id with an api object.
        """
        testing_target_username = "LastWeekTonight"
        try:
            api = self._youtube_api()
            non_api = discovery.RawModel()      # object that is not actually an api.
            name = main_script.extract_user_name(self.TESTING_CHANNEL_ID, api=api)
        except (HttpError, AttributeError):
            self.fail()

        self.assertEqual(testing_target_username, name)

        result = main_script.extract_user_name(self.INVALID_CODE, api)
        self.assertIsNone(result)

        self.assertRaises(RuntimeError, main_script.extract_user_name,
                          None, api)
        self.assertRaises(RuntimeError, main_script.extract_user_name,
                          self.TESTING_CHANNEL_ID, None)
        self.assertRaises(RuntimeError, main_script.extract_user_name,
                          None, None)
        self.assertRaises(RuntimeError, main_script.extract_user_name,
                          self.TESTING_CHANNEL_ID, non_api)


class ArgsParserTestCases(unittest.TestCase):

    TESTING_CHANNEL_ARG = 'mock_channel'
    TESTING_API_KEY = 'mock_api_key'

    def test_args_defaults(self):

        expected_defaults = "Namespace(api_key=" + repr(self.TESTING_API_KEY) + \
                            ", degree=1, filename=" + repr(main_script.DEFAULT_OUTPUT_FILENAME) \
                            + ", id=" + repr(self.TESTING_CHANNEL_ARG) + \
                            ", output=None, show_graph=False, verbose=0)"

        parser = main_script.setup_arg_parser()
        response = parser.parse_args([self.TESTING_CHANNEL_ARG, self.TESTING_API_KEY])
        self.assertEqual(str(response), expected_defaults)

        # Do not check nulls - verify_arguments will do this.
        # Do not check incorrect number of required arguments.

    # Do not test verifying the Channel Arg, as this will retest extract_user_name.

    def test_args_degrees(self):
        parser = main_script.setup_arg_parser()
        testing_degrees = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        for test_degree in testing_degrees:
            response = parser.parse_args([self.TESTING_CHANNEL_ARG,
                                          self.TESTING_API_KEY, '-d', test_degree])
            self.assertTrue(response.degree, int(test_degree))

        # Do not check degrees of 0 or less (non-sensical) - verify_arguments will do this.

    def test_args_filename(self):
        filename = 'mock_filename'
        parser = main_script.setup_arg_parser()
        response = parser.parse_args([self.TESTING_CHANNEL_ARG,
                                      self.TESTING_API_KEY, '-f', filename])

        self.assertEqual(response.filename, filename)

    def test_args_output(self):
        testing_outputs = ['text', 'graphml', 'gml', 'gexf', 'yaml']
        parser = main_script.setup_arg_parser()
        for option in testing_outputs:
            response = parser.parse_args([self.TESTING_CHANNEL_ARG,
                                          self.TESTING_API_KEY, '-o', option])
            self.assertEqual(response.output, option)

        # Do not check bad choices - arg parser will catch this.

    def test_args_verbose(self):
        testing_verbosity = [1, 2, 3, 4]
        parser = main_script.setup_arg_parser()
        for option in testing_verbosity:
            response = parser.parse_args([self.TESTING_CHANNEL_ARG,
                                          self.TESTING_API_KEY, '-v', str(option)])
            self.assertEqual(int(response.verbose), option)


class ArgsVerificationTestCases(unittest.TestCase):

    TESTING_CHANNEL_ID = 'UC3XTzVzaHQEd30rQbuvCtTQ'

    # remove key from developer console when released
    API_KEY = 'AIzaSyBAnZnN1O9DyBf1btAtOaGxm3Wgf3znBb0'
    BAD_KEY = '_______________________________________'

    TESTING_FILENAME = 'graph'
    TESTING_EXT = 'out'
    BAD_CHARS = """^&*[]{};:\'\"?/\\><,"""

    def test_verify_args_general(self):
        parser = main_script.setup_arg_parser()

        try:
            main_script.verify_arguments(
                parser, [self.TESTING_CHANNEL_ID, self.API_KEY,
                         '-d', '1', '-f', self.TESTING_FILENAME + '.' + self.TESTING_EXT])
            main_script.verify_arguments(
                parser, [self.TESTING_CHANNEL_ID, self.API_KEY,
                         '-d', '99999', '-f', '.' + self.TESTING_FILENAME + '.' + self.TESTING_EXT])
            main_script.verify_arguments(
                parser, [self.TESTING_CHANNEL_ID, self.API_KEY,
                         '-d', '99999', '-f', self.TESTING_FILENAME + '.' + self.TESTING_EXT + '.'])
            main_script.verify_arguments(
                parser, [self.TESTING_CHANNEL_ID, self.API_KEY,
                         '-d', '99999', '-f', self.TESTING_FILENAME])
        except AssertionError as e:
            self.fail(str(e.message))

        self.assertRaises(AttributeError, main_script.verify_arguments,
                          parser, [self.TESTING_CHANNEL_ID, self.API_KEY,
                                   '-d', '0', '-f', self.TESTING_FILENAME])
        self.assertRaises(AttributeError, main_script.verify_arguments,
                          parser, [self.TESTING_CHANNEL_ID, self.API_KEY,
                                   '-d', '-1', '-f', self.TESTING_FILENAME])
        for char in self.BAD_CHARS:
            self.assertRaises(Exception, main_script.verify_arguments,
                              [self.TESTING_CHANNEL_ID, self.API_KEY,
                               '-f', self.TESTING_FILENAME + char])


class GraphGenerationTestCases(unittest.TestCase):
    MOCK_GRAPH = Graph()
    MOCK_GRAPH.add_node('A', name='Bob')
    MOCK_GRAPH.add_node('B', name='Jim')
    MOCK_GRAPH.add_node('D', name='Carey')
    MOCK_GRAPH.add_node('C', name='Hurshel')
    MOCK_GRAPH.add_node('E', name='Errol')
    MOCK_GRAPH.add_node('G', name='Carol')
    MOCK_GRAPH.add_node('H', name='Monty')
    MOCK_GRAPH.add_node('I', name='Zara')
    MOCK_GRAPH.add_node('F', name='Morgan')
    MOCK_GRAPH.add_edge('A', 'B')
    MOCK_GRAPH.add_edge('A', 'C')
    MOCK_GRAPH.add_edge('A', 'D')
    MOCK_GRAPH.add_edge('B', 'E')
    MOCK_GRAPH.add_edge('C', 'F')
    MOCK_GRAPH.add_edge('C', 'G')
    MOCK_GRAPH.add_edge('G', 'H')
    MOCK_GRAPH.add_edge('H', 'I')
    MOCK_GRAPH.add_edge('E', 'A')
    MOCK_GRAPH.add_edge('H', 'C')
    MOCK_GRAPH.add_edge('I', 'D')
    MOCK_GRAPH.add_edge('C', 'D')

    def setUp(self):
        # save the normal script api functions
        self.old_assoc = main_script.get_association_list
        self.old_names = main_script.extract_user_name

        # mock the api functions, so instead of youtube API they access the mock graph
        def _mock_get_association_list(channel_id, _):
            association_list = []
            for edge in self.MOCK_GRAPH.edges():
                if channel_id in edge:
                    a, b = edge
                    if channel_id == a:
                        association_list.append(b)
                    else:
                        association_list.append(a)
            return association_list

        def _mock_extract_user_name(channel_id, _):
            return self.MOCK_GRAPH.node[channel_id]['name']

        main_script.get_association_list = _mock_get_association_list
        main_script.extract_user_name = _mock_extract_user_name

    def tearDown(self):
        main_script.get_association_list = self.old_assoc
        main_script.extract_user_name = self.old_names

    def test_create_graph(self):
        expected_graph = nx.Graph()
        expected_graph.add_node('Bob', degree=0)
        expected_graph.add_node('Jim', degree=1)
        expected_graph.add_node('Carey', degree=1)
        expected_graph.add_node('Hurshel', degree=1)
        expected_graph.add_node('Errol', degree=2)
        expected_graph.add_node('Morgan', degree=2)
        expected_graph.add_node('Carol', degree=2)
        expected_graph.add_node('Monty', degree=3)
        expected_graph.add_node('Zara', degree=4)
        expected_graph.add_path(['Bob', 'Jim', 'Errol'])
        expected_graph.add_path(['Bob', 'Hurshel', 'Carol', 'Monty', 'Zara'])
        expected_graph.add_path(['Bob', 'Carey', 'Zara'])
        expected_graph.add_path(['Monty', 'Hurshel', 'Carey'])
        expected_graph.add_edge('Bob', 'Errol')
        expected_graph.add_edge('Hurshel', 'Morgan')

        actual_graph = nx.Graph()

        main_script.build_graph(actual_graph, None, max_depth=7, initial_channel='A')

        for node in expected_graph.nodes():
            self.assertIn(node, actual_graph.nodes())
        for edge in expected_graph.edges():
            try:
                self.assertIn(edge, actual_graph.edges())
            except AssertionError:
                edge = (edge[1], edge[0])
                self.assertIn(edge, actual_graph.edges())
                continue

    def test_no_initial_channel(self):

        actual_graph = nx.Graph()

        main_script.build_graph(actual_graph, None, max_depth=7, initial_channel=None)

        self.assertEqual(actual_graph.number_of_nodes(), 0)


class DataOutputTestCases(unittest.TestCase):
    """
    Test the functions which convert graphs to other formats and write to console or file
    """

    MOCK_GRAPH = Graph()
    MOCK_GRAPH.add_node('1', degree=0)
    MOCK_GRAPH.add_node('2', degree=1)
    MOCK_GRAPH.add_node('3', degree=2)
    MOCK_GRAPH.add_node('4', degree=1)
    MOCK_GRAPH.add_edge('1', '2')
    MOCK_GRAPH.add_edge('2', '3')
    MOCK_GRAPH.add_edge('1', '4')

    MOCK_OUTPUT = "This is mock output.\n"

    MOCK_FILE_OUTPUT = 'mockfile.out'

    STDOUT_REDIRECTION = 'output_std_file'

    def setUp(self):
        """
        change stdout to a file.
        :return:
        """
        if os.path.exists(self.MOCK_FILE_OUTPUT):
            os.remove(self.MOCK_FILE_OUTPUT)
        self.old_stdout = sys.stdout
        sys.stdout = open(self.STDOUT_REDIRECTION, 'w')

    def tearDown(self):
        """
        restore stdout and remove unneeded files
        :return:
        """
        sys.stdout.close()
        sys.stdout = self.old_stdout
        if os.path.exists(self.STDOUT_REDIRECTION):
            os.remove(self.STDOUT_REDIRECTION)
        if os.path.exists(self.MOCK_FILE_OUTPUT):
            os.remove(self.MOCK_FILE_OUTPUT)

    def test_graph_conversion_to_text(self):
        """
        convert graph to text, as adjacency list.
        :return:
        """
        main_script.convert_graph_to_text(self.MOCK_GRAPH, self.MOCK_FILE_OUTPUT)
        with open(self.MOCK_FILE_OUTPUT) as f:
            output = f.read()
            output = output.split('\n')
        result_graph = nx.parse_adjlist(output)
        for node in self.MOCK_GRAPH.nodes():
            self.assertIn(node, result_graph.nodes())
        for edge in self.MOCK_GRAPH.edges():
            try:
                self.assertIn(edge, result_graph.edges())
            except AssertionError:
                edge = (edge[1], edge[0])
                self.assertIn(edge, result_graph.edges())
                continue

    def test_graph_conversion_to_graphml(self):
        """
        convert graph to graphml xml format
        :return:
        """
        main_script.convert_graph_to_graphml(self.MOCK_GRAPH, self.MOCK_FILE_OUTPUT)
        result_graph = nx.read_graphml(self.MOCK_FILE_OUTPUT)
        for node in self.MOCK_GRAPH.nodes():
            self.assertIn(node, result_graph.nodes())
        for edge in self.MOCK_GRAPH.edges():
            try:
                self.assertIn(edge, result_graph.edges())
            except AssertionError:
                edge = (edge[1], edge[0])
                self.assertIn(edge, result_graph.edges())
                continue

    def test_graph_conversion_to_gml(self):
        """
        convert graph to gml format
        :return:
        """
        main_script.convert_graph_to_gml(self.MOCK_GRAPH, self.MOCK_FILE_OUTPUT)
        result_graph = nx.read_gml(self.MOCK_FILE_OUTPUT)
        for node in self.MOCK_GRAPH.nodes():
            self.assertIn(node, result_graph.nodes())
        for edge in self.MOCK_GRAPH.edges():
            try:
                self.assertIn(edge, result_graph.edges())
            except AssertionError:
                edge = (edge[1], edge[0])
                self.assertIn(edge, result_graph.edges())
                continue

    def test_graph_conversion_to_json(self):
        """
        convert graph to a serialised json tree format useful for js documents.
        :return:
        """
        self.skipTest('Requires directed Graphs, which are outside the scope of the project.')
        main_script.convert_graph_to_json(self.MOCK_GRAPH, self.MOCK_FILE_OUTPUT)
        with open(self.MOCK_FILE_OUTPUT) as f:
            json_data = json.load(f.read())
            result_graph = json_graph.tree_graph(json_data)
        result_nodes = result_graph.nodes()
        result_edges = result_graph.edges()
        original_nodes = self.MOCK_GRAPH.nodes()
        original_edges = self.MOCK_GRAPH.edges()
        result_edges.sort()
        result_nodes.sort()
        original_edges.sort()
        original_nodes.sort()
        self.assertEqual(original_nodes, result_nodes)
        self.assertEqual(original_edges, result_edges)

    def test_graph_conversion_to_gexf(self):
        """
        convert graph to gexf xml format
        :return:
        """
        main_script.convert_graph_to_gexf(self.MOCK_GRAPH, self.MOCK_FILE_OUTPUT)
        result_graph = nx.read_gexf(self.MOCK_FILE_OUTPUT)
        for node in self.MOCK_GRAPH.nodes():
            self.assertIn(node, result_graph.nodes())
        for edge in self.MOCK_GRAPH.edges():
            try:
                self.assertIn(edge, result_graph.edges())
            except AssertionError:
                edge = (edge[1], edge[0])
                self.assertIn(edge, result_graph.edges())
                continue

    def test_graph_conversion_to_yaml(self):
        """
        convert graph to yaml format
        :return:
        """
        main_script.convert_graph_to_yaml(self.MOCK_GRAPH, self.MOCK_FILE_OUTPUT)
        result_graph = nx.read_yaml(self.MOCK_FILE_OUTPUT)
        for node in self.MOCK_GRAPH.nodes():
            self.assertIn(node, result_graph.nodes())
        for edge in self.MOCK_GRAPH.edges():
            try:
                self.assertIn(edge, result_graph.edges())
            except AssertionError:
                edge = (edge[1], edge[0])
                self.assertIn(edge, result_graph.edges())
                continue

    def test_output(self):
        """
        test the output management function. should only output to file if an output
        format is given. otherwise output to console in adj list text.
        :return:
        """
        custom_filename = 'custom.out'

        try:
            main_script.generate_output(self.MOCK_GRAPH, None, self.MOCK_FILE_OUTPUT)
            self.assertFalse(os.path.exists(self.MOCK_FILE_OUTPUT))
        except AttributeError:
            self.fail()

        try:
            main_script.generate_output(self.MOCK_GRAPH, 'gml', self.MOCK_FILE_OUTPUT)
            result_graph = nx.read_gml(self.MOCK_FILE_OUTPUT)
            for node in self.MOCK_GRAPH.nodes():
                self.assertIn(node, result_graph.nodes())
            for edge in self.MOCK_GRAPH.edges():
                try:
                    self.assertIn(edge, result_graph.edges())
                except AssertionError:
                    edge = (edge[1], edge[0])
                    self.assertIn(edge, result_graph.edges())
                    continue
        except AttributeError:
            self.fail()

        try:
            main_script.generate_output(self.MOCK_GRAPH, 'gml', custom_filename)
            result_graph = nx.read_gml(custom_filename)
            for node in self.MOCK_GRAPH.nodes():
                self.assertIn(node, result_graph.nodes())
            for edge in self.MOCK_GRAPH.edges():
                try:
                    self.assertIn(edge, result_graph.edges())
                except AssertionError:
                    edge = (edge[1], edge[0])
                    self.assertIn(edge, result_graph.edges())
                    continue
        except AttributeError:
            self.fail()

        self.assertRaises(RuntimeError, main_script.generate_output,
                          self.MOCK_GRAPH, 'fake_format', custom_filename)

        if os.path.exists(custom_filename):
            os.remove(custom_filename)


class OtherTestCases(unittest.TestCase):

    TESTING_CHANNEL_ID = 'UC3XTzVzaHQEd30rQbuvCtTQ'

    # remove key from developer console when released
    API_KEY = 'AIzaSyBAnZnN1O9DyBf1btAtOaGxm3Wgf3znBb0'

    def setUp(self):
        self.old_verify = main_script.verify_arguments
        self.args = []
        def mock_verify(parser, args):
            arguments = parser.parse_args(self.args)
            return arguments
        main_script.verify_arguments = mock_verify

    def tearDown(self):
        main_script.verify_arguments = self.old_verify
        if os.path.exists('yaml.graph'):
            os.remove('yaml.graph')

    def test_colour_generator(self):
        colours = ['#ffffff', '#ffff22', '#ff44ff', '#22ffff', '#ffff22', '#ff44ff', '#22ffff']
        col_gen = main_script.build_colour_generator()
        for index in range(7):
            self.assertEqual(next(col_gen), colours[index])

    def test_api_creation(self):
        try:
            api = main_script.create_youtube_api(self.API_KEY)
        except Exception:
            self.fail('should not have raised an error.')

        self.assertRaises(RuntimeError, main_script.create_youtube_api)

    def test_main_runner(self):
        try:
            self.args = [self.TESTING_CHANNEL_ID, self.API_KEY, '-d', '1', '-o',
                                           'yaml', '-f', 'yaml.graph', '-v', '4']
            main_script.main_function()

            self.args = [self.TESTING_CHANNEL_ID, self.API_KEY, '-d', '1', '-o',
                                           'yaml', '-f', 'yaml.graph', '-v', '3']
            main_script.main_function()

            self.args = [self.TESTING_CHANNEL_ID, self.API_KEY, '-d', '2', '-o',
                                           'yaml', '-f', 'yaml.graph', '-v', '2']
            main_script.main_function()

            self.args = [self.TESTING_CHANNEL_ID, self.API_KEY, '-d', '1', '-o',
                                           'yaml', '-f', 'yaml.graph', '-v', '1']
            main_script.main_function()

            self.args = [self.TESTING_CHANNEL_ID, self.API_KEY, '-d', '1', '-o',
                                           'yaml', '-f', 'yaml.graph']
            main_script.main_function()

        except Exception:
            self.fail('main_runner function threw should have not thrown an Exception.')

        # bad filenames
        self.args = [self.TESTING_CHANNEL_ID, self.API_KEY, '-d', '1', '-o',
                                           'yaml', '-f', 'yaml.graph?']
        self.assertRaises(Exception, main_script.main_function)

        self.args = [self.TESTING_CHANNEL_ID, self.API_KEY, '-d', '1', '-o',
                                           'yaml', '-f', 'yaml.graph:']
        self.assertRaises(Exception, main_script.main_function)

        # invalid degree
        self.args = [self.TESTING_CHANNEL_ID, self.API_KEY, '-d', '0', '-o',
                                           'yaml', '-f', 'yaml.graph?']
        self.assertRaises(Exception, main_script.main_function)

        self.args = [self.TESTING_CHANNEL_ID, self.API_KEY, '-d', '-1', '-o',
                                           'yaml', '-f', 'yaml.graph?']
        self.assertRaises(Exception, main_script.main_function)

        # bad api keys or channel ids
        self.args = [self.TESTING_CHANNEL_ID, None, '-d', '1', '-o',
                                           'yaml', '-f', 'yaml.graph?']
        self.assertRaises(Exception, main_script.main_function)

        self.args = [self.TESTING_CHANNEL_ID, '____________', '-d', '1', '-o',
                                           'yaml', '-f', 'yaml.graph?']
        self.assertRaises(Exception, main_script.main_function)

        self.args = ['___________________', self.API_KEY, '-d', '1', '-o',
                                           'yaml', '-f', 'yaml.graph?']
        self.assertRaises(Exception, main_script.main_function)

if __name__ == '__main__':
    nose.run()
