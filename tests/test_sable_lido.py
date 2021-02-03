import unittest

from pathlib import Path

import sable.extract

from lido import LIDOWeightBalanceMessage
from sable.schema import LoadPlanSchema

class TestLIDO(unittest.TestCase):

    @unittest.skip('schema load and a/c reg. to airline is unfinished')
    def test_sable_message_to_lido_string(self):
        loadplan_schema = LoadPlanSchema()
        datadir = Path(__file__).parent / 'data'
        loadplan_path = datadir / 'sable_message.txt.schema-load-expect.py'
        with open(loadplan_path) as loadplan_file:
            loadplan = eval(loadplan_file.read())
            wbmsg = LIDOWeightBalanceMessage(loadplan)
            s = str(wbmsg)
            print(s)
            #e = ('WAB09NOV2017002500COM  123 09NOV2017MIA  NGU  04100'
            #     '      000000NNN 24.121487521783520000L     017986  '
            #     '                            ')
            #self.assertEqual(s, e)


if __name__ == '__main__':
    unittest.main()
