"""
    Tests for this project
"""

__author__ = 'Roland'

import unittest

import nose

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


class YoutubeGraphTestCases(unittest.TestCase):
    """
    Tests for the youtube-graph script
    """

    def test_collect_associations(self):
        """
        test an expected set of associations is created,
        given a particular user with known related channels.
        :return:
        """

        testing_origin = u'https://www.youtube.com/channel/UCu2yrDg7wROzElRGoLQH82A/channels'
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

    def test_graph_view(self):
        """
        test the showing of the graph works without exceptions.
        :return:
        """
        try:
            main_script.show_graph()
            # TODO use more specific exception catching.
        except Exception as exp:
            self.fail('main_script.show_graph raised an Exception. Message is:\n' +
                      e.message)

    def test_graph_generation(self):
        """
        test the creation of the graph nodes and edges.
        :return:
        """

        testing_first_user = (u'Markiplier',
                              u'https://www.youtube.com/user/markiplierGAME/channels')
        testing_degrees = 2

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
             'Kiwo', 'ZeRoyalViking', 'RitzPlays', 'Smarticus',
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

        # final preparation
        main_script.DEFAULT_MAX_DEGREES_OF_SEPARATION = testing_degrees
        main_script.DEFAULT_FIRST_USER = testing_first_user

        # the function to test
        main_script.generate_graph()

        # comparisons
        for user_list in test_data:
            source = user_list[0]
            associates = user_list[1:]
            # some duplicate comparisons may occur.
            self.assertTrue(main_script.graph_nodes.has_node(source),
                            'Error: Expected to find (' + source +
                            ') in Nodes but did not.')

            for assoc in associates:
                self.assertTrue(main_script.graph_nodes.has_node(assoc),
                                "Error: Expected to find (" + assoc + ") " +
                                "in Nodes but did not.\n" +
                                "Current User_list=\n" + str(user_list))
                self.assertTrue(main_script.graph_nodes.has_edge(source, assoc) or
                                main_script.graph_nodes.has_edge(assoc, source),
                                'Error: expected to find edge (' + assoc + ', '
                                + source + ') but did not.\n' +
                                "Current User_list=\n" + str(user_list))


if __name__ == '__main__':
    nose.run()
