__author__ = 'Roland'

import unittest
import nose
import itertools

import networkx
import main_script



class YoutubeGraphTestCases(unittest.TestCase):

    def test_collect_associations(self):
        testing_origin = u'https://www.youtube.com/channel/UCu2yrDg7wROzElRGoLQH82A/channels'
        testing_targets = [
            (u'videooven', u'https://www.youtube.com/channel/UCR0_w50kjTiqQFE6J76l_mw/channels'),
            (u'wowcrendor', u'https://www.youtube.com/channel/UCy4earvTTlP5OUpNRvPI7TQ/channels'),
            (u'Traggey', u'https://www.youtube.com/channel/UC6Bz9OXlcmtO0dAFEPOjACA/channels'),
            (u'PewDiePie', u'https://www.youtube.com/channel/UC-lHJZR3Gqxm24_Vd_AJ5Yw/channels'),
            (u'PressHeartToContinue', u'https://www.youtube.com/channel/UC_ufxdQbKBrrMOiZ4LzrUyA/channels'),
            (u'Northernlion', u'https://www.youtube.com/channel/UC3tNpTOHsTnkmbwztCs30sA/channels'),
            (u'DamnNoHtml', u'https://www.youtube.com/channel/UCk9gPdY4fbH0BRhyTio9XIg/channels'),
            (u'Jesse Cox', u'https://www.youtube.com/channel/UCCbfB3cQtkEAiKfdRQnfQvw/channels'),
            (u'Russ Money', u'https://www.youtube.com/channel/UCp_jLG-XA4LP-nqep-rjkLQ/channels'),
            (u'TheRPGMinx', u'https://www.youtube.com/channel/UCTcc3KiX3RYXhi96vI_jJPA/channels'),
            (u'Sp00nerism', u'https://www.youtube.com/channel/UCICngZf7CfJ84sQzAQ1OiUg/channels'),
            (u'CinnamonToastKen', u'https://www.youtube.com/channel/UCepq9z9ovYGxhNrvf6VMSjg/channels'),
            (u'Markiplier', u'https://www.youtube.com/channel/UC7_YxT-KID8kRbqZo7MyscQ/channels'),
            (u'Gamerbomb', u'https://www.youtube.com/channel/UC73Fbzm7QAYKGiDZMR50oVA/channels'),
            (u'Tasty', u'https://www.youtube.com/channel/UC0n9yiP-AD2DpuuYCDwlNxQ/channels')
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
        return  tuple(ret_list)




if __name__ == '__main__':
    nose.run()

