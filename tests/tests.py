"""
    Tests for this project
"""
from __future__ import absolute_import, print_function, nested_scopes, generators, with_statement

__author__ = 'Roland'

import unittest
import nose


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


import main_script


class YoutubeApiProceduresTestCases(unittest.TestCase):
    """
    Tests for the youtube-graph script
    """

    TESTING_CHANNEL_ID = 'UC3XTzVzaHQEd30rQbuvCtTQ'

    API_KEY = 'AIzaSyBAnZnN1O9DyBf1btAtOaGxm3Wgf3znBb0'

    INVALID_CODE = '________________________'

    def test_collect_associations(self):
        """
        test an expected set of associations is created,
        given a particular user with known related channels.
        :return:
        """

        testing_target_urls = []

        # sort the target_list
        testing_target_urls.sort()

        results = main_script.get_association_list(self.TESTING_CHANNEL_ID, self.API_KEY)

        # sort the results
        results.sort()

        # result and target should be comparable by index

        self.assertEqual(len(results), len(testing_target_urls))

        for i in range(len(results)):
            self.assertEqual(results[i], testing_target_urls[i])

        self.assertRaises(ValueError, main_script.get_association_list, None, self.API_KEY)
        self.assertRaises(ValueError, main_script.get_association_list, self.TESTING_CHANNEL_ID, None)
        self.assertRaises(ValueError, main_script.get_association_list, None, None)
        self.assertRaises(ValueError, main_script.get_association_list, self.INVALID_CODE, self.API_KEY)
        self.assertRaises(ValueError, main_script.get_association_list, self.TESTING_CHANNEL_ID, self.INVALID_CODE)

    def test_extract_user_name(self):

        testing_target_username = "LastWeekTonight"

        name = main_script.extract_user_name(self.TESTING_CHANNEL_ID, self.API_KEY)

        self.assertEqual(testing_target_username, name)

        self.assertRaises(ValueError, main_script.extract_user_name, None, self.API_KEY)
        self.assertRaises(ValueError, main_script.extract_user_name, self.TESTING_CHANNEL_ID, None)
        self.assertRaises(ValueError, main_script.extract_user_name, None, None)
        self.assertRaises(ValueError, main_script.extract_user_name, self.INVALID_CODE, self.API_KEY)
        self.assertRaises(ValueError, main_script.extract_user_name, self.TESTING_CHANNEL_ID, self.INVALID_CODE)


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

        self.assertRaises(Exception, parser.parse_args, [self.TESTING_CHANNEL_ARG, None])
        self.assertRaises(Exception, parser.parse_args, [None, self.TESTING_API_KEY])
        self.assertRaises(Exception, parser.parse_args, [None, None])
        # TODO: may cause script closure. consider using subprocesses
        self.assertRaises(Exception, parser.parse_args, [self.TESTING_CHANNEL_ARG])
        self.assertRaises(Exception, parser.parse_args, [])

    # Do not test verifying the Channel Arg, as this will retest extract_user_name.

    def test_args_degrees(self):
        parser = main_script.setup_arg_parser()
        testing_degrees = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        for test_degree in testing_degrees:
            response = parser.parse_args([self.TESTING_CHANNEL_ARG, self.TESTING_API_KEY, '-d', test_degree])
            self.assertTrue(response.degree, int(test_degree))

        # TODO: may cause script closure. consider using subprocesses
        testing_degrees = ['0', '-1', 'a', '!']
        for test_degree in testing_degrees:
            self.assertRaises(Exception, parser.parse_args,
                              [self.TESTING_CHANNEL_ARG, self.TESTING_API_KEY, '-d', test_degree])

    def test_args_filename(self):
        filename = 'mock_filename'
        parser = main_script.setup_arg_parser()
        response = parser.parse_args([self.TESTING_CHANNEL_ARG, self.TESTING_API_KEY, '-f', filename])

        self.assertEqual(response.filename, filename)

        # No null case - as default is null to indicate no recording to file.

    def test_args_output(self):
        testing_outputs = ['text', 'graphml','gexf','json','yaml']
        parser = main_script.setup_arg_parser()
        for option in testing_outputs:
            response = parser.parse_args([self.TESTING_CHANNEL_ARG,
                                          self.TESTING_API_KEY, '-o', option])
            self.assertEqual(response.output, option)

        # TODO: may cause script closure. consider using subprocesses
        for bad_option in [None, 'false_output']:
            self.assertRaises(Exception, parser.parse_args, [self.TESTING_CHANNEL_ARG,
                                          self.TESTING_API_KEY, '-o', bad_option])

    def test_args_verbose(self):
        testing_verbosity = [1,2,3,4]
        parser = main_script.setup_arg_parser()
        for option in testing_verbosity:
            response = parser.parse_args([self.TESTING_CHANNEL_ARG,
                                          self.TESTING_API_KEY, '-v', option])
            self.assertEqual(response.verbose, option)

        # TODO: may cause script closure. consider using subprocesses
        testing_verbosity = [0, -1, 5]
        for bad_verbose in testing_verbosity:
            self.assertRaises(Exception, parser.parse_args, [self.TESTING_CHANNEL_ARG,
                              self.TESTING_API_KEY, '-v', bad_verbose])


from networkx import Graph

class DataOutputTestCases(unittest.TestCase):

    MOCK_GRAPH = Graph()
    MOCK_GRAPH.add_edge('1','2')
    MOCK_GRAPH.add_edge('2','3')

    MOCK_OUTPUT = "This is mock output."

    def test_graph_conversion_to_text(self):
        self.fail()

    def test_graph_conversion_to_graphml(self):
        self.fail()

    def test_graph_conversion_to_json(self):
        self.fail()

    def test_graph_conversion_to_gefx(self):
        self.fail()

    def test_graph_conversion_to_yaml(self):
        self.fail()

    def test_data_outputting(self):
        self.fail()

if __name__ == '__main__':
    nose.run()
