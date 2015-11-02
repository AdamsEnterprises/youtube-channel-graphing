"""
    Tests for this project
"""
from __future__ import absolute_import, print_function, nested_scopes, generators, with_statement

__author__ = 'Roland'

import unittest
import nose

import os
import networkx


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


class YoutubeGraphTestCases(unittest.TestCase):
    """
    Tests for the youtube-graph script
    """

    TESTING_DEFAULT_URL_ARG = 'https://www.youtube.com/user/LastWeekTonight/channels'


    def test_collect_associations(self):
        """
        test an expected set of associations is created,
        given a particular user with known related channels.
        :return:
        """

        testing_origin = u'https://www.youtube.com/user/ChaoticMonki/channels'
        testing_targets = [
            (u'videooven',
             u'https://www.youtube.com/channel/UCR0_w50kjTiqQFE6J76l_mw/channels?view=60'),
            (u'wowcrendor',
             u'https://www.youtube.com/channel/UCy4earvTTlP5OUpNRvPI7TQ/channels?view=60'),
            (u'Traggey',
             u'https://www.youtube.com/channel/UC6Bz9OXlcmtO0dAFEPOjACA/channels?view=60'),
            (u'PewDiePie',
             u'https://www.youtube.com/channel/UC-lHJZR3Gqxm24_Vd_AJ5Yw/channels?view=60'),
            (u'PressHeartToContinue',
             u'https://www.youtube.com/channel/UC_ufxdQbKBrrMOiZ4LzrUyA/channels?view=60'),
            (u'Northernlion',
             u'https://www.youtube.com/channel/UC3tNpTOHsTnkmbwztCs30sA/channels?view=60'),
            (u'DamnNoHtml',
             u'https://www.youtube.com/channel/UCk9gPdY4fbH0BRhyTio9XIg/channels?view=60'),
            (u'Jesse Cox',
             u'https://www.youtube.com/channel/UCCbfB3cQtkEAiKfdRQnfQvw/channels?view=60'),
            (u'Russ Money',
             u'https://www.youtube.com/channel/UCp_jLG-XA4LP-nqep-rjkLQ/channels?view=60'),
            (u'TheRPGMinx',
             u'https://www.youtube.com/channel/UCTcc3KiX3RYXhi96vI_jJPA/channels?view=60'),
            (u'Sp00nerism',
             u'https://www.youtube.com/channel/UCICngZf7CfJ84sQzAQ1OiUg/channels?view=60'),
            (u'CinnamonToastKen',
             u'https://www.youtube.com/channel/UCepq9z9ovYGxhNrvf6VMSjg/channels?view=60'),
            (u'Markiplier',
             u'https://www.youtube.com/channel/UC7_YxT-KID8kRbqZo7MyscQ/channels?view=60'),
            (u'Gamerbomb',
             u'https://www.youtube.com/channel/UC73Fbzm7QAYKGiDZMR50oVA/channels?view=60'),
            (u'Tasty',
             u'https://www.youtube.com/channel/UC0n9yiP-AD2DpuuYCDwlNxQ/channels?view=60')
        ]

        # sort the target_list
        testing_targets.sort(key=lambda x: x[0])

        results = main_script.get_association_list(testing_origin)

        # sort the results
        results.sort(key=lambda x: x[0])

        # result and target should be comparable by index

        self.assertEqual(len(results), len(testing_targets))

        for i in range(len(results)):
            self.assertEqual(results[i], testing_targets[i])

    def test_colour_generation(self):
        """
        test that an expected number of random colours is produced.
        :return:
        """
        degrees_to_test = (2, 4, 12, 20)

        for degree in degrees_to_test:

            colours = main_script.generate_colours(degree)

            # number of degrees is (0, ..., x) i.e. x + 1,
            # thus number of colours should be x + 1.
            self.assertEqual(len(colours), degree + 1,
                             "Failure: expected {} colours but received {}".format(
                                 degree, len(colours)
                             ))
            self.assertTrue((0, 0, 0) not in colours)
            self.assertTrue((255, 255, 255) not in colours)

        self.assertRaises(ValueError, main_script.generate_colours, 0)
        self.assertRaises(ValueError, main_script.generate_colours, -3)
        self.assertRaises(TypeError, main_script.generate_colours, 4.4)
        self.assertRaises(TypeError, main_script.generate_colours, '7')
        self.assertRaises(TypeError, main_script.generate_colours, None)

    def test_args_url(self):
        parser = main_script.setup_arg_parser()
        response = parser.parse_args([self.TESTING_DEFAULT_URL_ARG +
                                      main_script.SUBURL_CHANNEL_PARAMS])

        test_name = 'LastWeekTonight'
        test_user_colleagues = ['HBO', 'Cinemax', 'HBOBoxing',
                                'HBODocs', 'Real Time with Bill Maher', 'GameofThrones',
                                'trueblood', 'HBOLatino']

        name = main_script.extract_first_user_name(response.url)
        self.assertEqual(name, test_name)

        associations = main_script.get_association_list(response.url)
        # for easier comparison
        associations.sort()
        test_user_colleagues.sort()
        self.assertEqual(len(associations), len(test_user_colleagues))
        for index in range(len(associations)):
            self.assertEqual(str(associations[index][0]), test_user_colleagues[index])

    def test_args_url_verified(self):
        parser = main_script.setup_arg_parser()
        test_name = 'LastWeekTonight'
        test_user_colleagues = ['HBO', 'Cinemax', 'HBOBoxing',
                                'HBODocs', 'Real Time with Bill Maher', 'GameofThrones',
                                'trueblood', 'HBOLatino']
        test_user_colleagues.sort()

        # test with ?view=60 params appended
        try:
            arguments = main_script.verify_arguments(parser,
                                [self.TESTING_DEFAULT_URL_ARG + main_script.SUBURL_CHANNEL_PARAMS])
            extracted_name = main_script.extract_first_user_name(arguments.url)
            self.assertEqual(test_name, extracted_name)
            associates = main_script.get_association_list(arguments.url)
            associates.sort()
            for index in range(len(associates)):
                self.assertEqual(str(associates[index][0]), test_user_colleagues[index])
        except ValueError:
            self.fail()

        # test with no params appended
        arguments = main_script.verify_arguments(parser,
                            [self.TESTING_DEFAULT_URL_ARG])
        try:
            index = arguments.url.index(main_script.SUBURL_CHANNEL_PARAMS)
            substring_url = arguments.url[:index]
            substring_appended_params = arguments.url[index:]
            self.assertEqual(substring_url, self.TESTING_DEFAULT_URL_ARG)
            self.assertEqual(substring_appended_params, main_script.SUBURL_CHANNEL_PARAMS)
            extracted_name = main_script.extract_first_user_name(arguments.url)
            self.assertEqual(test_name, extracted_name)
            associates = main_script.get_association_list(arguments.url)
            associates.sort()
            for index in range(len(associates)):
                self.assertEqual(str(associates[index][0]), test_user_colleagues[index])
        except (IndexError, ValueError):
            # the correct params should be present.
            self.fail()

        # test with invalid params appended
        arguments = main_script.verify_arguments(parser,
                            [self.TESTING_DEFAULT_URL_ARG + '?vxsfdegfv=nmjk'])
        try:
            index = arguments.url.index(main_script.SUBURL_CHANNEL_PARAMS)
            substring_url = arguments.url[:index]
            substring_appended_params = arguments.url[index:]
            self.assertEqual(substring_url, self.TESTING_DEFAULT_URL_ARG)
            self.assertEqual(substring_appended_params, main_script.SUBURL_CHANNEL_PARAMS)
            extracted_name = main_script.extract_first_user_name(arguments.url)
            self.assertEqual(test_name, extracted_name)
            associates = main_script.get_association_list(arguments.url)
            associates.sort()
            for index in range(len(associates)):
                self.assertEqual(str(associates[index][0]), test_user_colleagues[index])
        except (IndexError, ValueError):
            # the correct params should be present.
            self.fail()

        # test incorrect url with good params
        self.assertRaises(ValueError, main_script.verify_arguments,
                          *[parser,
                            ['https://www.youtube.com/user/LastWeekTonight/videos?view=60']])

        # test incorrect url
        self.assertRaises(ValueError, main_script.verify_arguments,
                          *[parser, ['https://www.youtube.com/user/LastWeekTonight/videos']])
        # Test with None
        self.assertRaises(ValueError, main_script.verify_arguments,
                          *[parser, [None]])

    def test_args_degrees(self):
        parser = main_script.setup_arg_parser()

        test_default_degree = 1
        response = parser.parse_args([self.TESTING_DEFAULT_URL_ARG])
        self.assertTrue(response.degree, test_default_degree)

        testing_degrees = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        for test_degree in testing_degrees:
            response = parser.parse_args([self.TESTING_DEFAULT_URL_ARG, '-d', test_degree])
            self.assertTrue(response.degree, int(test_degree))

        # testing_degrees = ['0', '-1', 'a', '!']
        # for test_degree in testing_degrees:
        #     self.assertRaises(Exception, parser.parse_args,
        #                       *[self.TESTING_DEFAULT_URL_ARG, '-d', test_degree])

    def test_args_filename(self):
        parser = main_script.setup_arg_parser()

        test_default_filename = None
        response = parser.parse_args([self.TESTING_DEFAULT_URL_ARG])
        self.assertEqual(response.filename, test_default_filename)

        test_filename = 'graph.out'
        response = parser.parse_args([self.TESTING_DEFAULT_URL_ARG,
                                     '-f', test_filename])
        self.assertEqual(response.filename, test_filename)

    def test_args_verify_filename(self):
        parser = main_script.setup_arg_parser()
        test_filename = ['graph.out', 'graph', '!graph$#']
        test_bad_filename = ['%.out', '^.out', '&.out', '*.out', '{}.out', '[].out',
                             ':,;.out', "'\".out", '<>.out', '?/\\|.out']

        for good_name in test_filename:
            arguments = main_script.verify_arguments(parser,
                            [self.TESTING_DEFAULT_URL_ARG, '-f', good_name])
            self.assertEqual(arguments.filename, good_name)

        for bad_name in test_bad_filename:
            self.assertRaises(ValueError, main_script.verify_arguments,
                              *[parser, [self.TESTING_DEFAULT_URL_ARG, '-f', bad_name]])

    def test_args_verbose(self):
        testing_verbosity = [1,2,3,4]
        parser = main_script.setup_arg_parser()

        test_verbose = 0
        response = parser.parse_args([self.TESTING_DEFAULT_URL_ARG])
        self.assertEqual(response.verbose, test_verbose)

        for test_verbose in testing_verbosity:
            response = parser.parse_args([self.TESTING_DEFAULT_URL_ARG,
                                         '-v', str(test_verbose)])
            self.assertEqual(response.verbose, test_verbose)

        # testing_verbosity = [0, -1, 5]
        # for test_verbose in testing_verbosity:
        #     self.assertRaises(Exception, parser.parse_args,
        #                       *[self.TESTING_DEFAULT_URL_ARG, '-v', test_verbose])

    def test_args_show_graph(self):
        parser = main_script.setup_arg_parser()

        response = parser.parse_args([self.TESTING_DEFAULT_URL_ARG, '-s'])
        self.assertTrue(response.show_graph)

        response = parser.parse_args([self.TESTING_DEFAULT_URL_ARG])
        self.assertFalse(response.show_graph)

    def test_graph_conversion_to_text(self):

        test_output = "LastWeekTonight, HBO\nLastWeekTonight, Cinemax\n" + \
                      "LastWeekTonight, HBOBoxing\nLastWeekTonight, HBODocs\n" + \
                      "LastWeekTonight, Real Time with Bill Maher\nLastWeekTonight, GameofThrones\n" + \
                      "LastWeekTonight, trueblood\nLastWeekTonight, HBOLatino\n"

        graph = networkx.Graph()
        graph.clear()

        # produce a mock graph.
        for pair in test_output.split('\n'):
            try:
                source, dest = pair.split(',')
                graph.add_edge(source.strip(), dest.strip())
            except ValueError:
                continue

        text = main_script.convert_graph_to_text(graph)
        # check the output, and number of lines, matches
        self.assertEqual(len(text), len(test_output))
        test_output = test_output.split('\n')
        text = text.split('\n')
        self.assertEqual(len(text), len(test_output))
        # check for correct nodes and edges in text.
        # may have different order of lines or
        for line in text:
            if len(line) == 0:
                alt_line = ""
            else:
                alt_line = line.split(',')
                alt_line = alt_line[1].strip() + ', ' + alt_line[0].strip()
            self.assertTrue(line in test_output or alt_line in test_output)

    def test_graph_conversion_to_graphml(self):

        # TODO: build an Element Tree with what is expected. parse the resultant xml into a tree and compare

        test_output = [u'<?xml version="1.0" ?>',
                       u'<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns',
                       u'http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">',
                       u'\t<graph edgedefault="undirected" id="submodules.graphml">',
                       u'\t\t<node id="n0"/>',
                       u'\t\t<node id="n1"/>',
                       u'\t\t<node id="n2"/>',
                       u'\t\t<edge source="n0" target="n1"/>',
                       u'\t\t<edge source="n1" target="n2"/>',
                       u'\t</graph>',
                       u'</graphml>',
                       u'']

        graph = networkx.Graph()
        graph.clear()
        graph.add_node("n0")
        graph.add_node("n1")
        graph.add_node("n2")
        graph.add_edge("n0","n1")
        graph.add_edge("n1","n2")

        xml_string = main_script.convert_graph_to_xml(graph)
        xml_data = xml_string.split('\n')

        self.assertEqual(len(xml_data), len(test_output))
        # expect first 4 lines to matchup
        for index in range(4):
            self.assertEqual(xml_data[index], test_output[index])
        # expect last 3 lines to matchup
        for index in range(9, len(test_output)):
            self.assertEqual(xml_data[index], test_output[index])
        # organise node and edge lines, then compare
        node_lines = []
        edge_lines = []
        for line in xml_data[4:9]:
            if 'node' in line or 'id' in line:
                node_lines.append(line)
            elif 'edge' in line or 'source' in line or 'target' in line:
                edge_lines.append(line)
        # compare for expected node lines
        for node in test_output[4:7]:
            self.assertIn(node, node_lines)
        # compare for expected edge lines
        for edge in test_output[7:9]:
            try:
                self.assertIn(edge, edge_lines)
            except AssertionError:
                # the nodes may be the other way around - swap them.
                alt_edge = edge.split('/>')[0]      # dump end of tag
                alt_edge = alt_edge.split(" ")
                first_node = alt_edge[1].split("=")[1]  # grab names of nodes
                last_node = alt_edge[2].split("=")[1]
                # rearrange
                alt_edge = u'\t\t<edge source=' + last_node + u' target=' + first_node + u'/>'
                self.assertIn(alt_edge, edge_lines)

    def test_graph_conversion_to_json(self):
        self.skipTest("test not complete")

    def test_file_creation(self):

        def _compare_from_file(filename, expected_text):
            with open(filename) as f:
                file_lines = f.read().split('\n')
                file_lines.sort()
            expected_lines = expected_text.split('\n')
            for index in range(len(file_lines)):
                try:
                    self.assertTrue(file_lines[index] in expected_lines)
                except AssertionError:
                    alt_line = file_lines[index].split(', ')
                    alt_line = alt_line[1] + ', ' + alt_line[0]
                    self.assertTrue(alt_line in expected_lines)

        test_text = "LastWeekTonight, HBO\nLastWeekTonight, Cinemax\n" + \
                    "LastWeekTonight, HBOBoxing\nLastWeekTonight, HBODocs\n" + \
                    "LastWeekTonight, Real Time with Bill Maher\nLastWeekTonight, GameofThrones\n" + \
                    "LastWeekTonight, trueblood\nLastWeekTonight, HBOLatino\n"

        filename = 'graph.out'

        graph = networkx.Graph()
        graph.clear()
        for pair in test_text.split('\n'):
            try:
                source, dest = pair.split(',')
                graph.add_edge(source.strip(), dest.strip())
            except ValueError:
                continue

        main_script.generate_file(filename, main_script.convert_graph_to_text(graph))

        self.assertTrue(os.path.exists(filename))
        # check the written file contents are as expected.
        _compare_from_file(filename, test_text)
        os.remove(filename)

        # main_script.generate_file(filename, main_script.convert_graph_to_xml(graph))
        # self.assertTrue(os.path.exists(filename))
        # # check the written file contents are as expected.
        # _compare_from_file(filename, test_xml)

        # main_script.generate_file(filename, main_script.convert_graph_to_json(graph))
        # self.assertTrue(os.path.exists(filename))
        # # check the written file contents are as expected.
        # _compare_from_file(filename, test_json)


    # TODO: check verbosity output - collect from stdout and see if it matches expected format.

    def test_graph_generation(self):
        """
        test the creation of the graph nodes and edges.
        :return:
        """

        test_data = (
            ('Markiplier', 'muyskerm', 'LordMinion777', 'yamimash',
             'LixianTV', 'GameGrumps', 'Egoraptor',
             'Ninja Sex Party', 'RubberNinja', 'Cyndago', 'Matthias',
             'TheRPGMinx', 'jacksepticeye',
             'CinnamonToastKen', 'Cryaotic'),

            ('Cryaotic', 'videooven', 'wowcrendor', 'Traggey', 'PewDiePie',
             'PressHeartToContinue', 'Northernlion',
             'DamnNoHtml', 'Jesse Cox', 'Russ Money', 'TheRPGMinx',
             'Sp00nerism', 'CinnamonToastKen',
             'Markiplier', 'Gamerbomb', 'Tasty'),

            ('CinnamonToastKen', 'Cryaotic', 'Markiplier',
             'PressHeartToContinue', 'YOGSCAST Strippin', 'TheRPGMinx',
             'jacksepticeye', 'Ken&Mary', 'SuperMaryFace',
             'PewDiePie', 'YOGSCAST Martyn', 'UberHaxorNova'),

            ('TheRPGMinx', 'Boyinaband', 'Zer0Doxy', 'Bryce Games',
             'Kiwo', 'ZeRoyalViking', 'RitzPlays', 'ManlyBadassHero',
             'GirlGamerGaB', 'KrismPro', 'Ohmwrecker / Maskedgamer',
             'Sinow', 'CriousGamers',),

            ('Matthias', 'Matt & Amanda', 'Team Edge', 'Amanda Faye',
             'M-Tech', 'J-Fred', 'The Crazie Crew'),

            ('muyskerm', 'Markiplier', 'Matthias', 'Cyndago',
             'LordMinion777', 'jacksepticeye',
             'Aliens On Toast', 'The Cincy Brass', 'GamingNutz'),

            ('LordMinion777', 'muyskerm', 'Markiplier', 'TheRPGMinx',
             'jacksepticeye', 'yamimash', 'dlive22891',
             'EntoanThePack', 'Jpw03', 'StevRayBro', 'BaronVonGamez',
             'PatrckStatic', 'Zombiemold', 'LatinGoddessGame',
             'TheTeshTube'),

            ('yamimash', 'Yugioh Masters', 'AaroInTheKnee',
             'Katyllaria', 'Markiplier', 'LordMinion777',
             'jacksepticeye', 'RaedwulfGamer', 'muyskerm',
             'dlive22891', 'TheRPGMinx', '8-BitGaming', 'EntoanThePack',
             'lTheMasterOfDooMl', 'Ohmwrecker / Maskedgamer',
             'LANDAN2006', 'LiKe BuTTeR', 'Girbeagly',
             'Randymash', 'Poro IV'),

            ('LixianTV', 'LixianVG', 'Animonster', 'Markiplier',
             'MrEVOLVF', 'Hot Pepper Gaming', 'TheOfficialEdge',
             'Cyndago', 'TheToxicDoctor', 'MrRayhonda', 'MrCreepyPasta',
             'VigorousVisuals', 'Sam Joy', 'yamimash'),

            ('GameGrumps', 'GrumpOut', 'Egoraptor', 'KittyKatGaming',
             'Ninja Sex Party', 'RubberNinja',
             'SoloTravelBlog', 'Mortem3r', 'Cinemassacre', 'Markiplier',
             'Polaris', 'JonTronShow'),

            ('Egoraptor', 'GameGrumps', 'StamperTV', 'Cinemassacre',
             'El Cid', 'Ninja Sex Party', 'newgrounds',
             'OneyNG', 'Nathan Barnatt', 'Cartoon Drive-Thru', 'Mortem3r',
             'RubberNinja', 'psychicpebbles',
             'Markiplier'),

            ('Ninja Sex Party', 'Egoraptor', 'GameGrumps', 'RubberNinja',
             'Hot Pepper Gaming', 'OneyNG',
             'psychicpebbles', 'Mortem3r', 'comicbookgirl19'),

            ('RubberNinja', 'GameGrumps', 'DidYouKnowGaming?', 'Egoraptor',
             'PeanutButterGamer', 'Ninja Sex Party',
             'Commander Holly', 'OneyNG', 'Ockeroid', 'Ricepirate',
             'psychicpebbles', 'ProJared', 'Smooth McGroove',
             'high5toons', 'That One Video Gamer', 'StamperTV',
             'Polaris', 'Spazkidin3D'),

            ('Cyndago', 'RubberNinja', 'Markiplier', 'LixianTV',
             'muyskerm', 'LixianTV', 'Kids w/ Problems',
             'whoismaxwell', 'Ninja Sex Party'),

            ('jacksepticeye', 'TheGamingLemon', 'Daithi De Nogla',
             'yamimash', 'GameGrumps', 'muyskerm', 'Markiplier',
             'PewDiePie', 'CinnamonToastKen', 'LordMinion777')
        )

        degrees = 2
        origin = (u'Markiplier', u'https://www.youtube.com/user/markiplierGAME/channels')

        # final preparation
        graph_nodes = networkx.Graph()
        graph_nodes.add_node(origin[0],
                             degree=0)

        # the function to test
        main_script.DEBUG = False
        main_script.generate_relationship_graph(graph_nodes,
                                                degrees,
                                                origin, 0)
        main_script.DEBUG = True

        # comparisons
        for user_list in test_data:
            source = user_list[0]
            associates = user_list[1:]
            # some duplicate comparisons may occur.
            self.assertTrue(graph_nodes.has_node(source),
                            'Error: Expected to find (' + source +
                            ') in Nodes but did not.')

            for assoc in associates:
                self.assertTrue(graph_nodes.has_node(assoc),
                                "Error: Expected to find (" + assoc + ") " +
                                "in Nodes but did not.\n" +
                                "Current User_list=\n" + str(user_list))
                self.assertTrue(graph_nodes.has_edge(source, assoc) or
                                graph_nodes.has_edge(assoc, source),
                                'Error: expected to find edge (' + assoc + ', '
                                + source + ') but did not.\n' +
                                "Current User_list=\n" + str(user_list))

    def test_script(self):
        """
        run the main_script as a script and make sure there are no errors.
        :return:
        """

        DEFAULT_FIRST_USER = 'https://www.youtube.com/user/ChaoticMonki/channels'
        import subprocess

        try:
            status = subprocess.call(['python', 'main_script.py', DEFAULT_FIRST_USER])
            self.assertEqual(status, 0)
        except Exception:
            self.fail()


import xml.etree.ElementTree as ET

from submodules import graphml


class GraphMLModule(unittest.TestCase):
    """
    Tests for the GraphML Module
    """

    def setUp(self):
        self.TESTING_EROOT = ET.Element(graphml.GRAPHML_TAG)
        self.TESTING_EROOT.set("xmlns", "http://graphml.graphdrawing.org/xmlns")
        self.TESTING_EROOT.set("xmlns" + ":" + graphml.XSI, "http://www.w3.org/2001/XMLSchema-instance")
        self.TESTING_EROOT.set(graphml.XSI + ":" +
                          graphml.SCHEMA_LOCATION, "http://graphml.graphdrawing.org/xmlns\n" +
                         "http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd")
        self.TESTING_EDOC = ET.SubElement(self.TESTING_EROOT, graphml.GRAPH_TAG)
        self.TESTING_EDOC.set("id", __name__)
        self.TESTING_EDOC.set("edgedefault", "undirected")

        self.TESTING_NODE_A = ET.SubElement(self.TESTING_EDOC, 'node')
        self.TESTING_NODE_A.set('id', 'A')
        self.TESTING_NODE_A.set('attrib_a', 'one')
        self.TESTING_NODE_A.set('attrib_b', 'two')
        self.TESTING_NODE_B = ET.SubElement(self.TESTING_EDOC, 'node')
        self.TESTING_NODE_B.set('id', 'B')
        self.TESTING_NODE_B.set('attrib_c', 'three')
        self.TESTING_NODE_C = ET.SubElement(self.TESTING_EDOC, 'node')
        self.TESTING_NODE_C.set('id', 'C')

        self.TESTING_EDGE_D = ET.SubElement(self.TESTING_EDOC, 'edge')
        self.TESTING_EDGE_D.set('source', 'A')
        self.TESTING_EDGE_D.set('target', 'B')
        self.TESTING_EDGE_E = ET.SubElement(self.TESTING_EDOC, 'edge')
        self.TESTING_EDGE_E.set('source', 'C')
        self.TESTING_EDGE_E.set('target', 'A')
        self.TESTING_EDGE_E.set('attrib_d', 'four')

        self.TESTING_ETREE = ET.ElementTree(self.TESTING_EROOT)

    def test_base_xml(self):
        test_tree = graphml.make_base_xml('test')
        self.assertIsInstance(test_tree, ET.ElementTree)
        test_root = test_tree.getroot()
        self.assertIsInstance(test_root, ET.Element)
        test_doc = test_root.findall('./graph')
        self.assertTrue(len(test_doc) == 1)
        test_doc = test_doc[0]
        self.assertIsInstance(test_doc, ET.Element)
        # check root and doc are what they should be:
        self.assertEqual(self.TESTING_EROOT.tag, test_root.tag)
        self.assertEqual(self.TESTING_EROOT.get("xmlns"), test_root.get("xmlns"))
        self.assertEqual(self.TESTING_EROOT.get("xmlns:xls"), test_root.get("xmlns:xls"))
        self.assertEqual(self.TESTING_EROOT.get("xls:schemaLocation"),
                         test_root.get("xls:schemaLocation"))

        self.assertEqual(self.TESTING_EDOC.tag, test_doc.tag)
        self.assertEqual(self.TESTING_EDOC.get('id'), test_doc.get('id'))
        self.assertEqual(self.TESTING_EDOC.get("edgedefault"),
                         test_doc.get("edgedefault"))

    def test_make_node(self):
        test_tree = graphml.make_base_xml('test')

        node = graphml.make_node(test_tree, 'A', attrib_a='one', attrib_b='two')
        self.assertEqual(self.TESTING_NODE_A.tag, node.tag)
        self.assertEqual(self.TESTING_NODE_A.get('attrib_a'), node.get('attrib_a'))
        self.assertEqual(self.TESTING_NODE_A.get('attrib_b'), node.get('attrib_b'))

        node = graphml.make_node(test_tree, 'B', attrib_c='three')
        self.assertEqual(self.TESTING_NODE_B.tag, node.tag)
        self.assertEqual(self.TESTING_NODE_B.get('attrib_c'), node.get('attrib_c'))

        node = graphml.make_node(test_tree, 'C')
        self.assertEqual(self.TESTING_NODE_B.tag, node.tag)

        self.assertRaises(AttributeError, graphml.make_node, test_tree, None)
        self.assertRaises(AttributeError, graphml.make_node, None, 'D')

    def test_make_edge(self):
        test_tree = graphml.make_base_xml('test')

        node_A = graphml.make_node(test_tree, 'A')
        node_B = graphml.make_node(test_tree, 'B')
        node_C = graphml.make_node(test_tree, 'C')

        edge_D = graphml.make_edge(test_tree, 'A', 'B')
        self.assertEqual(self.TESTING_EDGE_D.tag, edge_D.tag)
        self.assertEqual(self.TESTING_EDGE_D.get('source'), edge_D.get('source'))
        self.assertEqual(self.TESTING_EDGE_D.get('dest'), edge_D.get('dest'))

        edge_E = graphml.make_edge(test_tree, 'C', 'A', attrib_d='four')
        self.assertEqual(self.TESTING_EDGE_E.tag, edge_E.tag)
        self.assertEqual(self.TESTING_EDGE_E.get('source'), edge_E.get('source'))
        self.assertEqual(self.TESTING_EDGE_E.get('dest'), edge_E.get('dest'))
        self.assertEqual(self.TESTING_EDGE_E.get('attrib_d'), edge_E.get('attrib_d'))

        self.assertRaises(AttributeError, graphml.make_edge, None, None, None)
        self.assertRaises(AttributeError, graphml.make_edge, test_tree, None, None)
        self.assertRaises(AttributeError, graphml.make_edge, test_tree, 'A', None)
        self.assertRaises(AttributeError, graphml.make_edge, test_tree, None, 'A')

        # No node D - should raise Error.
        self.assertRaises(AttributeError, graphml.make_edge, test_tree, 'D', 'A')
        self.assertRaises(AttributeError, graphml.make_edge, test_tree, 'A', 'E')

    def test_remove_node(self):
        # check node and linked edges do exist
        nodes = self.TESTING_ETREE.findall('./graph/node')
        self.assertEqual(len(nodes), 3)
        self.assertIn(self.TESTING_NODE_C, nodes)
        edges = self.TESTING_ETREE.findall('./graph/edge')
        self.assertEqual(len(edges), 2)
        self.assertIn(self.TESTING_EDGE_E, edges)

        graphml.remove_node_and_linked_edges(self.TESTING_ETREE, 'C')

        # check node and linked edges have been removed
        nodes = self.TESTING_ETREE.findall('./graph/node')
        self.assertEqual(len(nodes), 2)
        self.assertNotIn(self.TESTING_NODE_C, nodes)
        edges = self.TESTING_ETREE.findall('./graph/edge')
        self.assertEqual(len(edges), 1)
        self.assertNotIn(self.TESTING_EDGE_E, edges)

        self.assertRaises(AttributeError, graphml.remove_node_and_linked_edges, None, None)
        self.assertRaises(AttributeError,
                          graphml.remove_node_and_linked_edges, self.TESTING_ETREE, None)

    def test_remove_edge(self):
        # check node and linked edges do exist
        nodes = self.TESTING_ETREE.findall('./graph/node')
        self.assertEqual(len(nodes), 3)
        edges = self.TESTING_ETREE.findall('./graph/edge')
        self.assertEqual(len(edges), 2)
        self.assertIn(self.TESTING_EDGE_E, edges)

        graphml.remove_edge(self.TESTING_ETREE, 'C', 'A')

        # check node and linked edges have been removed
        nodes = self.TESTING_ETREE.findall('./graph/node')
        self.assertEqual(len(nodes), 3)
        edges = self.TESTING_ETREE.findall('./graph/edge')
        self.assertEqual(len(edges), 1)
        self.assertNotIn(self.TESTING_EDGE_E, edges)

        self.assertRaises(AttributeError, graphml.remove_edge, None, None, None)
        self.assertRaises(AttributeError, graphml.remove_edge,
                          self.TESTING_ETREE, None, None)
        self.assertRaises(AttributeError, graphml.remove_edge,
                          self.TESTING_ETREE, 'A', None)
        self.assertRaises(AttributeError, graphml.remove_edge,
                          self.TESTING_ETREE, None, 'A')

    def test_remove_all_edges(self):
        # check node and linked edges do exist
        nodes = self.TESTING_ETREE.findall('./graph/node')
        self.assertEqual(len(nodes), 3)
        edges = self.TESTING_ETREE.findall('./graph/edge')
        self.assertEqual(len(edges), 2)

        graphml.remove_all_edges(self.TESTING_ETREE)

        nodes = self.TESTING_ETREE.findall('./graph/node')
        self.assertEqual(len(nodes), 3)
        edges = self.TESTING_ETREE.findall('./graph/edge')
        self.assertEqual(len(edges), 0)

        self.assertRaises(AttributeError, graphml.remove_all_edges, None)

    def test_remove_all(self):
        # check node and linked edges do exist
        nodes = self.TESTING_ETREE.findall('./graph/node')
        self.assertEqual(len(nodes), 3)
        edges = self.TESTING_ETREE.findall('./graph/edge')
        self.assertEqual(len(edges), 2)

        graphml.remove_all_nodes_and_edges(self.TESTING_ETREE)

        nodes = self.TESTING_ETREE.findall('./graph/node')
        self.assertEqual(len(nodes), 0)
        edges = self.TESTING_ETREE.findall('./graph/edge')
        self.assertEqual(len(edges), 0)

        self.assertRaises(AttributeError, graphml.remove_all_nodes_and_edges, None)

    def test_tostring(self):
        root = self.TESTING_ETREE.getroot()
        test_xml = '<?xml version="1.0" ?>' + ET.tostring(root, 'utf-8').decode('utf-8')
        # adjust spacing in test_xml near ends of self-ending tags.
        tmp = test_xml.split(" />")
        test_xml = ""
        for string in tmp[:-1]:
            test_xml += string + "/>"
        test_xml += tmp[-1]

        # test_xml is unprettified. Unprettify result_xml before doing comparison.
        result_xml = graphml.build_xml_string(self.TESTING_ETREE)
        tmp = result_xml.split('\n')
        tmp[1] += '&#10;'
        result_xml = ""
        for string in tmp:
            result_xml += string.strip()

        self.maxDiff = None

        # output xml first line will be xml statement. expect rest to match comparison string
        self.assertTrue('<?xml' in result_xml[:5])

        for index in range(len(test_xml)):
            self.assertEqual(test_xml, result_xml)

        self.maxDiff = 500

    def test_parse_string(self):
        self.skipTest("test not complete")
        test_string = """<?xml version="1.0" ?>
        <!DOCTYPE xmlbomb [
        <!ENTITY a "1234567890" >
        <!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;">
        <!ENTITY c "&b;&b;&b;&b;&b;&b;&b;&b;">
        <!ENTITY d "&c;&c;&c;&c;&c;&c;&c;&c;">
        ]>
        <graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
        http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
            <graph edgedefault="undirected" id="testing_parse">
                <node id="A" attrib_a="one" attrib_b="two" />
                <node id="B" attrib_c="three" />
                <node id="C"/>
                <edge source="C" target="A" attrib_d="four"/>
                <edge source="A" target="B"/>
            </graph>
        </graphml>"""

        comparison_attrs_nodes = {
            'A':{'attrib_a': 'one',
                 'attrib_b': 'two'},
            'B':{'attrib_c': 'three'},
            'C':{}
        }

        comparison_attrs_edges = {
            'C-A':{'attrib_d': 'four'},
            'A-B':{}
        }

        tree = graphml.parse_xml_to_element_tree(test_string)

        # should be elementtree
        self.assertIsInstance(tree, ET.ElementTree)
        # should have <graphlm> root
        root = tree.getroot()
        self.assertIsInstance(root, ET.Element)
        self.assertEqual(root.tag, graphml.GRAPHML_TAG)
        # check graphml namespace

        # should have <graph> element
        doc = root.findall('./' + graphml.GRAPH_TAG)
        self.assertIsInstance(doc, ET.Element)
        self.assertEqual(doc.tag, graphml.GRAPH_TAG)
        self.assertEqual(doc.get(graphml.ATTR_ID), "testing_parse")
        self.assertEqual(doc.get(graphml.ATTR_DIR), "undirected")
        # should have nodes with appropriate tags and elements
        nodes = root.findall('./' + graphml.GRAPH_TAG + '/' + graphml.NODE_TAG)
        for node in nodes:
            self.assertIsInstance(node, ET.Element)
            self.assertEqual(node.tag, graphml.NODE_TAG)
            self.assertIsNot(node.get(graphml.ATTR_ID), None)
            self.assertIn(node.get(graphml.ATTR_ID), comparison_attrs_nodes.keys())
            # compare all attributes in the node to expected values
            cmp_attribs = comparison_attrs_nodes[node.get(graphml.ATTR_ID)]
            for attr in node.attrib:
                if attr != graphml.ATTR_ID:
                    self.assertIn(attr, cmp_attribs.keys())
                    self.assertEqual(node.get(attr), cmp_attribs[attr])
        edges = root.findall('./' + graphml.GRAPH_TAG + '/' + graphml.EDGE_TAG)
        for edge in edges:
            self.assertIsInstance(edge, ET.Element)
            self.assertEqual(edge.tag, graphml.EDGE_TAG)
            self.assertIsNot(edge.get(graphml.ATTR_ID), None)
            self.assertIsNot(edge.get(graphml.EDGE_SOURCE), None)
            self.assertIsNot(edge.get(graphml.EDGE_DEST), None)
            # construct a key to retrieve appropriate comparison attributes
            # TODO: check for ordering issues with key construction
            edge_key = edge.get(graphml.EDGE_SOURCE) + '-' + edge.get(graphml.EDGE_DEST)
            self.assertIn(edge_key, comparison_attrs_nodes.keys())
            # compare all attributes in the node to expected values
            cmp_attribs = comparison_attrs_edges[edge_key]
            for attr in edge.attrib:
                if attr != graphml.EDGE_SOURCE and attr != graphml.EDGE_DEST:
                    self.assertIn(attr, cmp_attribs.keys())
                    self.assertEqual(edge.get(attr), cmp_attribs[attr])

        # TODO: Test with malformed nodes or edges. These should raise a Parsing Exception.

if __name__ == '__main__':
    nose.run()
