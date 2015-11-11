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

    def test_collect_associations(self):
        """
        test an expected set of associations is created,
        given a particular user with known related channels.
        :return:
        """

        testing_target_ids = ['HBO','Cinemax','HBOBoxing','HBODocs',
                              'Real Time with Bill Maher','GameofThrones','trueblood',
                              'HBOLatino']

        # sort the target_list
        testing_target_ids.sort()

        try:
            api = self._youtube_api()
            non_api = discovery.RawModel()      # object that is not actually an api.
            results = main_script.get_association_list(self.TESTING_CHANNEL_ID, api)
        except (HttpError, ValueError):
            self.fail()

        # sort the results
        results.sort()

        # result and target should be comparable by index
        self.assertEqual(len(results), len(testing_target_ids))

        for i in range(len(results)):
            self.assertEqual(results[i][0], testing_target_ids[i])

        self.assertRaises(AttributeError, main_script.get_association_list, None, api)
        self.assertRaises(AttributeError, main_script.get_association_list,
                          self.TESTING_CHANNEL_ID, None)
        self.assertRaises(AttributeError, main_script.get_association_list, None, None)
        self.assertRaises(AttributeError, main_script.get_association_list, self.INVALID_CODE, api)
        self.assertRaises(AttributeError, main_script.get_association_list,
                          self.TESTING_CHANNEL_ID, non_api)

    def test_extract_user_name(self):
        """
        test that extract_user_name collects the user_name from a channel id with an api object.
        """
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
            response = parser.parse_args([self.TESTING_CHANNEL_ARG, self.TESTING_API_KEY, '-d', test_degree])
            self.assertTrue(response.degree, int(test_degree))

        # Do not check degrees of 0 or less (non-sensical) - verify_arguments will do this.

    def test_args_filename(self):
        filename = 'mock_filename'
        parser = main_script.setup_arg_parser()
        response = parser.parse_args([self.TESTING_CHANNEL_ARG, self.TESTING_API_KEY, '-f', filename])

        self.assertEqual(response.filename, filename)

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
                                          self.TESTING_API_KEY, '-v', str(option)])
            self.assertEqual(int(response.verbose), option)


class ArgsVerificationTestCases(unittest.TestCase):

    TESTING_CHANNEL_ID = 'UC3XTzVzaHQEd30rQbuvCtTQ'

    API_KEY = 'AIzaSyBAnZnN1O9DyBf1btAtOaGxm3Wgf3znBb0'
    BAD_KEY = '_______________________________________'

    TESTING_FILENAME = 'graph'
    TESTING_EXT = 'out'
    BAD_CHARS = """^&*[]{};:\'\"?/\\><,"""

    def test_verify_args_general(self):
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
        except AssertionError as e:
            self.fail(str(e.message))

        self.assertRaises(AttributeError, main_script.verify_arguments, parser, [self.TESTING_CHANNEL_ID, self.API_KEY,
                                                  '-d', '0', '-f', self.TESTING_FILENAME])
        self.assertRaises(AttributeError, main_script.verify_arguments, parser, [self.TESTING_CHANNEL_ID, self.API_KEY,
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

    MOCK_FILE_OUTPUT = 'mockfile.out'

    STDOUT_REDIRECTION = 'output_std_file'

    # TODO: gneerate_output will output text to console if no output format specified. otherwise it will output to file in the format specified, default filename if no filename given.

    def setUp(self):
        self.old_stdout = sys.stdout
        sys.stdout = open(self.STDOUT_REDIRECTION, 'w')

    def tearDown(self):
        if os.path.exists(self.MOCK_FILE_OUTPUT):
            os.remove(self.MOCK_FILE_OUTPUT)
        sys.stdout = self.old_stdout

    def test_graph_conversion_to_text(self):
        main_script.convert_graph_to_text(self.MOCK_GRAPH, self.MOCK_FILE_OUTPUT)
        with open(self.MOCK_FILE_OUTPUT) as f:
            output = f.read()
        expected = "1 2\n2 3\n"
        for index in range(len(output)):
            self.assertEqual(output[index], expected[index])

    def test_graph_conversion_to_graphml(self):
        main_script.convert_graph_to_graphml(self.MOCK_GRAPH, self.MOCK_FILE_OUTPUT)
        result_graph = nx.read_graphml(self.MOCK_FILE_OUTPUT)
        self.assertEqual(self.MOCK_GRAPH.nodes(), result_graph.nodes())
        self.assertEqual(self.MOCK_GRAPH.edges(), result_graph.edges())

    def test_graph_conversion_to_gml(self):
        main_script.convert_graph_to_gml(self.MOCK_GRAPH, self.MOCK_FILE_OUTPUT)
        result_graph = nx.read_gml(self.MOCK_FILE_OUTPUT)
        self.assertEqual(self.MOCK_GRAPH.nodes(), result_graph.nodes())
        self.assertEqual(self.MOCK_GRAPH.edges(), result_graph.edges())

    def test_graph_conversion_to_json(self):
        main_script.convert_graph_to_json(self.MOCK_GRAPH, self.MOCK_FILE_OUTPUT)
        with open(self.MOCK_FILE_OUTPUT) as f:
            json_data = json.load(f.read())
            result_graph = json_graph.tree_graph(json_data)
        self.assertEqual(self.MOCK_GRAPH.nodes(), result_graph.nodes())
        self.assertEqual(self.MOCK_GRAPH.edges(), result_graph.edges())

    def test_graph_conversion_to_gexf(self):
        main_script.convert_graph_to_gexf(self.MOCK_GRAPH, self.MOCK_FILE_OUTPUT)
        result_graph = nx.read_gexf(self.MOCK_FILE_OUTPUT)
        self.assertEqual(self.MOCK_GRAPH.nodes(), result_graph.nodes())
        self.assertEqual(self.MOCK_GRAPH.edges(), result_graph.edges())

    def test_graph_conversion_to_yaml(self):
        main_script.convert_graph_to_yaml(self.MOCK_GRAPH, self.MOCK_FILE_OUTPUT)
        result_graph = nx.read_yaml(self.MOCK_FILE_OUTPUT)
        self.assertEqual(self.MOCK_GRAPH.nodes(), result_graph.nodes())
        self.assertEqual(self.MOCK_GRAPH.edges(), result_graph.edges())

    def test_output(self):
        main_script.generate_output(self.MOCK_FILE_OUTPUT, self.MOCK_OUTPUT)
        self.assertTrue(os.path.exists(self.MOCK_FILE_OUTPUT))
        with open(self.MOCK_FILE_OUTPUT) as f:
            self.assertEqual(f.read(), self.MOCK_OUTPUT)

        main_script.generate_output(None, self.MOCK_OUTPUT)
        sys.stdout.flush()
        with open(self.STDOUT_REDIRECTION) as f:
            self.assertEqual(f.read(), self.MOCK_OUTPUT)

    # def test_


if __name__ == '__main__':
    nose.run()
