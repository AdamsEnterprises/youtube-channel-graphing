"""
    Tests for this project
"""
from __future__ import absolute_import, print_function, nested_scopes, generators, with_statement

__author__ = 'Roland'

import unittest
import nose
import os
import json

import networkx as nx
from networkx import Graph
from networkx.readwrite import json_graph

from apiclient import discovery

import main_script


def scrape_elements(soup, params_hierarchy):
    """
    given a beautiful_soup and a sequence of tags to parse down, send back a list of tag elements.
    e.g. say the hierarchy is:
        <div>
            <div class='333'>
                <ol>
                    <li class='222'>
                        <ul>
                            <li class="777">
                                <div>
                                    <a class="111">
                                    <a class="6666">
                            ( * 9 more such <li>s)
                    <li class="333">
            ( * 2 such <div>s)
        <div class="999">
            <a>

    and the hierarchy is:
        (['div'], {'attrs':{'class':'333'}}), (['li'], {'attrs':{'class':'777'}}),
            (['a'], {'attrs':{'class':'6666'}})

    the returned list of elements will contain:
        <a class="6666>
        ... * 10 elements

    note that if at any stage, no elements match the parse requirements set by the hierarchy, an
    empty list will be returned.

    :param soup:                the beautifulsoup to process
    :param params_hierarchy:    list of (args, keywords) to process down the soup tag hierarchy
    :return:                    list of tag elements parsed via the hierarchy.
    """
    elements = list()
    elements.append(soup)
    for params in params_hierarchy:
        results = list()
        for element in elements:
            for items in element.find_all(*params[0], **params[1]):
                for item in items:
                    if len(item) > 0:
                        results.append(item)
        elements = list(results)
    return elements


class YoutubeApiProceduresTestCases(unittest.TestCase):
    """
    Tests for the youtube-graph script
    """

    TESTING_CHANNEL_ID = 'UC3XTzVzaHQEd30rQbuvCtTQ'
    API_KEY = 'AIzaSyBAnZnN1O9DyBf1btAtOaGxm3Wgf3znBb0'
    INVALID_CODE = '________________________'

    def _youtube_api(self):
        return discovery.build(developerKey=self.API_KEY, serviceName='youtube', version='v3')

    def test_api_creation(self):
        try:
            api = main_script.create_youtube_api(developerKey=self.API_KEY)
        except Exception:
            self.fail()

        self.assertRaises(ValueError, main_script.create_youtube_api, developerKey=self.INVALID_CODE)
        self.assertRaises(ValueError, main_script.create_youtube_api, developerKey=None)

    def test_collect_associations(self):
        """
        test an expected set of associations is created,
        given a particular user with known related channels.
        :return:
        """

        # TODO: complete the list of comparison ids.
        testing_target_ids = []

        # sort the target_list
        testing_target_ids.sort()

        try:
            api = self._youtube_api()
            non_api = discovery.RawModel()      # object that is not actually an api.
            results = main_script.get_association_list(self.TESTING_CHANNEL_ID, api=api)
        except Exception:
            self.fail()

        # sort the results
        results.sort()

        # result and target should be comparable by index
        self.assertEqual(len(results), len(testing_target_ids))

        for i in range(len(results)):
            self.assertEqual(results[i], testing_target_ids[i])

        self.assertRaises(ValueError, main_script.get_association_list, None, api=api)
        self.assertRaises(ValueError, main_script.get_association_list, self.TESTING_CHANNEL_ID, api=None)
        self.assertRaises(ValueError, main_script.get_association_list, None, api=None)
        self.assertRaises(ValueError, main_script.get_association_list, self.INVALID_CODE, api=api)
        self.assertRaises(ValueError, main_script.get_association_list, self.TESTING_CHANNEL_ID, api=non_api)

    def test_extract_user_name(self):

        testing_target_username = "LastWeekTonight"
        api=self._youtube_api()
        non_api = discovery.RawModel()      # object that is not actually an api.
        name = main_script.extract_user_name(self.TESTING_CHANNEL_ID, api=api)

        self.assertEqual(testing_target_username, name)

        self.assertRaises(AttributeError, main_script.extract_user_name, None, api)
        self.assertRaises(AttributeError, main_script.extract_user_name, self.TESTING_CHANNEL_ID, None)
        self.assertRaises(AttributeError, main_script.extract_user_name, None, None)
        self.assertRaises(AttributeError, main_script.extract_user_name, self.INVALID_CODE, api)
        self.assertRaises(AttributeError, main_script.extract_user_name, self.TESTING_CHANNEL_ID, non_api)


class ArgsParserTestCases(unittest.TestCase):

    TESTING_CHANNEL_ARG = 'mock_channel'
    TESTING_API_KEY = 'mock_api_key'

    def test_args_defaults(self):

        expected_defaults = "Namespace(api_key=" + repr(self.TESTING_CHANNEL_ARG) + \
                            ", degree=1, filename=None, id=" + self.TESTING_API_KEY + \
                            ", output='text', show_graph=False, verbose=0)"

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
            response = parser.parse_args([self.TESTING_CHANNEL_ARG, self.TESTING_API_KEY, '-d', test_degree])
            self.assertTrue(response.degree, int(test_degree))

        # Do not check degrees of 0 or less (non-sensical) - verify_arguments will do this.

    def test_args_filename(self):
        filename = 'mock_filename'
        parser = main_script.setup_arg_parser()
        response = parser.parse_args([self.TESTING_CHANNEL_ARG, self.TESTING_API_KEY, '-f', filename])

        self.assertEqual(response.filename, filename)

        # No null case - as default is null to indicate no recording to file.

    def test_args_output(self):
        testing_outputs = ['text', 'graphml', 'gml','gexf','json','yaml']
        parser = main_script.setup_arg_parser()
        for option in testing_outputs:
            response = parser.parse_args([self.TESTING_CHANNEL_ARG,
                                          self.TESTING_API_KEY, '-o', option])
            self.assertEqual(response.output, option)

        # Do not check bad choices - arg parser will catch this.

    def test_args_verbose(self):
        testing_verbosity = [1,2,3,4]
        parser = main_script.setup_arg_parser()
        for option in testing_verbosity:
            response = parser.parse_args([self.TESTING_CHANNEL_ARG,
                                          self.TESTING_API_KEY, '-v', option])
            self.assertEqual(response.verbose, option)


class ArgsVerificationTestCases(unittest.TestCase):

    TESTING_CHANNEL_ID = 'UC3XTzVzaHQEd30rQbuvCtTQ'

    API_KEY = 'AIzaSyBAnZnN1O9DyBf1btAtOaGxm3Wgf3znBb0'
    BAD_KEY = '_______________________________________'

    TESTING_FILENAME = 'graph'
    TESTING_EXT = 'out'
    BAD_CHARS = """^&*[]{};:\'\"?/\\><,"""

    def test_verify_args(self):
        parser = main_script.setup_arg_parser()

        try:
            args = main_script.verify_arguments(parser, [self.TESTING_CHANNEL_ID, self.API_KEY,
                                                         '-d', '1', '-f', self.TESTING_FILENAME + '.' +
                                                         self.TESTING_EXT])
            args = main_script.verify_arguments(parser, [self.TESTING_CHANNEL_ID, self.API_KEY,
                                                         '-d', '99999', '-f', '.' + self.TESTING_FILENAME
                                                         + '.' + self.TESTING_EXT])
            args = main_script.verify_arguments(parser, [self.TESTING_CHANNEL_ID, self.API_KEY,
                                                         '-d', '99999', '-f', self.TESTING_FILENAME
                                                         + '.' + self.TESTING_EXT + '.'])
            args = main_script.verify_arguments(parser, [self.TESTING_CHANNEL_ID, self.API_KEY,
                                                         '-d', '99999', '-f', self.TESTING_FILENAME])
        except Exception:
            self.fail()

        self.assertRaises(Exception, main_script.verify_arguments, [self.TESTING_CHANNEL_ID, self.API_KEY,
                                                  '-d', '0', '-f', self.TESTING_FILENAME])
        self.assertRaises(Exception, main_script.verify_arguments, [self.TESTING_CHANNEL_ID, self.API_KEY,
                                                  '-d', '-1', '-f', self.TESTING_FILENAME])
        for char in self.BAD_CHARS:
            self.assertRaises(Exception, main_script.verify_arguments,
                              [self.TESTING_CHANNEL_ID, self.API_KEY,
                              '-f', self.TESTING_FILENAME + char])


class DataOutputTestCases(unittest.TestCase):

    MOCK_GRAPH = Graph()
    MOCK_GRAPH.add_node('1', degree=0)
    MOCK_GRAPH.add_edge('1','2')
    MOCK_GRAPH.add_edge('2','3')

    MOCK_OUTPUT = "This is mock output.\n"

    MOCK_FILE_OUTPUT = 'graph.out'

    def tearDown(self):
        if os.path.exists(self.MOCK_FILE_OUTPUT):
            os.remove(self.MOCK_FILE_OUTPUT)

    def test_graph_conversion_to_text(self):
        output = main_script.convert_graph_to_text(self.MOCK_GRAPH)
        output.sort()
        expected = "1 2\n2 3\n"
        for index in range(len(output)):
            self.assertEqual(output[index], expected[index])

    def test_graph_conversion_to_graphml(self):
        # mock convert_graph_to_graphml -> tmp file, to MOCK_FILE_OUTPUT
        output = main_script.convert_graph_to_graphml(self.MOCK_GRAPH)
        result_graph = nx.read_graphml(self.MOCK_FILE_OUTPUT)
        self.assertEqual(self.MOCK_GRAPH.nodes(), result_graph.nodes())
        self.assertEqual(self.MOCK_GRAPH.edges(), result_graph.edges())

    def test_graph_conversion_to_gml(self):
        output = main_script.convert_graph_to_gml(self.MOCK_GRAPH)
        result_graph = nx.parse_gml(output)
        self.assertEqual(self.MOCK_GRAPH.nodes(), result_graph.nodes())
        self.assertEqual(self.MOCK_GRAPH.edges(), result_graph.edges())

    def test_graph_conversion_to_json(self):
        output = main_script.convert_graph_to_json(self.MOCK_GRAPH)
        json_data = json.load(output)
        result_graph = json_graph.tree_graph(json_data)
        self.assertEqual(self.MOCK_GRAPH.nodes(), result_graph.nodes())
        self.assertEqual(self.MOCK_GRAPH.edges(), result_graph.edges())

    def test_graph_conversion_to_gexf(self):
        # mock convert_graph_to_gexf -> tmp file, to MOCK_FILE_OUTPUT
        output = main_script.convert_graph_to_gefx(self.MOCK_GRAPH)
        result_graph = nx.read_gexf(self.MOCK_FILE_OUTPUT)
        self.assertEqual(self.MOCK_GRAPH.nodes(), result_graph.nodes())
        self.assertEqual(self.MOCK_GRAPH.edges(), result_graph.edges())

    def test_graph_conversion_to_yaml(self):
        # mock convert_graph_to_yaml -> tmp file, to MOCK_FILE_OUTPUT
        output = main_script.convert_graph_to_yaml(self.MOCK_GRAPH)
        result_graph = nx.read_yaml(self.MOCK_FILE_OUTPUT)
        self.assertEqual(self.MOCK_GRAPH.nodes(), result_graph.nodes())
        self.assertEqual(self.MOCK_GRAPH.edges(), result_graph.edges())

    def test_data_outputting(self):
        filename = 'graph.out'
        main_script.generate_output(filename, self.MOCK_OUTPUT)
        self.assertTrue(os.path.exists('graph.out'))
        with open(self.MOCK_FILE_OUTPUT) as f:
            self.assertEqual(f.read(), self.MOCK_FILE_OUTPUT)

        main_script.generate_output(None, self.MOCK_OUTPUT)
        # collect console output for comparison.

        self.fail()

if __name__ == '__main__':
    nose.run()
