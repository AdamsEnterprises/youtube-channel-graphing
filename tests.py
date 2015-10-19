__author__ = 'Roland'

import unittest

import nose

import main_script


class YoutubeGraphTestCases(unittest.TestCase):

    def test_collect_associations(self):
        testing_origin = u'https://www.youtube.com/channel/UCu2yrDg7wROzElRGoLQH82A/channels'
        testing_targets = [
            (u'videooven', u'https://www.youtube.com/channel/UCR0_w50kjTiqQFE6J76l_mw/channels?view=60'),
            (u'wowcrendor', u'https://www.youtube.com/channel/UCy4earvTTlP5OUpNRvPI7TQ/channels?view=60'),
            (u'Traggey', u'https://www.youtube.com/channel/UC6Bz9OXlcmtO0dAFEPOjACA/channels?view=60'),
            (u'PewDiePie', u'https://www.youtube.com/channel/UC-lHJZR3Gqxm24_Vd_AJ5Yw/channels?view=60'),
            (u'PressHeartToContinue', u'https://www.youtube.com/channel/UC_ufxdQbKBrrMOiZ4LzrUyA/channels?view=60'),
            (u'Northernlion', u'https://www.youtube.com/channel/UC3tNpTOHsTnkmbwztCs30sA/channels?view=60'),
            (u'DamnNoHtml', u'https://www.youtube.com/channel/UCk9gPdY4fbH0BRhyTio9XIg/channels?view=60'),
            (u'Jesse Cox', u'https://www.youtube.com/channel/UCCbfB3cQtkEAiKfdRQnfQvw/channels?view=60'),
            (u'Russ Money', u'https://www.youtube.com/channel/UCp_jLG-XA4LP-nqep-rjkLQ/channels?view=60'),
            (u'TheRPGMinx', u'https://www.youtube.com/channel/UCTcc3KiX3RYXhi96vI_jJPA/channels?view=60'),
            (u'Sp00nerism', u'https://www.youtube.com/channel/UCICngZf7CfJ84sQzAQ1OiUg/channels?view=60'),
            (u'CinnamonToastKen', u'https://www.youtube.com/channel/UCepq9z9ovYGxhNrvf6VMSjg/channels?view=60'),
            (u'Markiplier', u'https://www.youtube.com/channel/UC7_YxT-KID8kRbqZo7MyscQ/channels?view=60'),
            (u'Gamerbomb', u'https://www.youtube.com/channel/UC73Fbzm7QAYKGiDZMR50oVA/channels?view=60'),
            (u'Tasty', u'https://www.youtube.com/channel/UC0n9yiP-AD2DpuuYCDwlNxQ/channels?view=60')
        ]

        # sort the target_list
        testing_targets.sort(key=lambda x:x[0])

        results = main_script.get_association_list(testing_origin)

        # sort the results
        results.sort(key=lambda x:x[0])

        # result and target should be comparable by index

        self.assertEqual(len(results), len(testing_targets))

        for i in range(len(results)):
            self.assertEqual(results[i], testing_targets[i])

    def _create_testing_users(self, *target_set):
        ret_list = list()
        for t in target_set:
            ret_list.append( (t, main_script.URL_YOUTUBE_USER + t) )
        return tuple(ret_list)

    def test_colour_generation(self):
        degrees_to_test = (2, 4, 12, 20)
        for degree in degrees_to_test:
            colours = main_script.generate_colours(degree)
            self.assertEqual(len(colours), degree, "Failure: expected {} colours but received {}".format(
                degree, len(colours)
            ))
            self.assertTrue((0, 0, 0) not in colours)
            self.assertTrue((255, 255, 255) not in colours)
        self.assertRaises(ValueError, main_script.generate_colours, 0)
        self.assertRaises(ValueError, main_script.generate_colours, -3)
        self.assertRaises(TypeError, main_script.generate_colours, 4.4)
        self.assertRaises(TypeError, main_script.generate_colours, '7')
        self.assertRaises(TypeError, main_script.generate_colours, None)

    def test_graph_generation(self):
        self.fail("Test is incomplete.")
        main_script.DEFAULT_MAX_DEGREES_OF_SEPARATION = 2
        main_script.DEFAULT_FIRST_USER = 'Markiplier'
        nodes = set()
        edges = set()

        test_data = (
            ('Markiplier', 'muyskerm', 'LordMinion777', 'yamimash', 'LixianTV', 'GameGrumps', 'EgoRaptor',
             'Ninja Sex Party',
             'RubberNinja', 'Cyndago', 'Matthias', 'TheRPGMinx', 'jacksepticeye', 'CinnamonToastKen', 'Cryaotic'),
            ('Cryaotic', 'videooven', 'wowcrendor', 'Traggey', 'PewDiePie', 'PressHeartToContinue', 'Northernlion',
             'DamnNoHtml', 'Jesse Cox', 'Russ Money', 'TheRPGMinx', 'Sp00nerism', 'CinnamonToastKen',
             'Markiplier', 'Gamerbomb', 'Tasty'),

        )

        for x in test_data:
            for n in x:
                nodes.add(n)
            for n in x[1:]:
                edges.add((x[0], n))

        main_script.generate_graph()

        for node in nodes:
            self.assertTrue(main_script.graph_nodes.has_nodes(node))
        for edge in edges:
            self.assertTrue(main_script.graph_nodes.has_edge(edge[0], edge[1]))


if __name__ == '__main__':
    nose.run()

