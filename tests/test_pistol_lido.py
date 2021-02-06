import unittest

from datetime import datetime
from pathlib import Path

import lido

class TestLIDO(unittest.TestCase):

    def test_pistol_message_to_lido_string(self):
        datadir = Path(__file__).parent / 'data'
        pistol_loadplan_path = datadir / 'pistol_message.txt.schema-load-expect.py'
        with open(pistol_loadplan_path) as loadplan_file:
            loadplan = eval(loadplan_file.read(), {'datetime': datetime})
            wbmsg = lido.LIDOWeightBalanceMessage(loadplan)
            wbmsg_string = str(wbmsg)
            expects = (
                'WAB09NOV20170025008C   123 09NOV2017MIA  NGU  04100'
                '      000000YYY 24.121487521783520000L     017986  '
                '                            ')
            self.assertEqual(wbmsg_string, expects)


if __name__ == '__main__':
    unittest.main()
