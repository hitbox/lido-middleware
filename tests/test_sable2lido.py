import unittest

import sable.extract

from lido import LIDOWeightBalanceMessage
from sable.schema import LoadPlanSchema

class TestLIDO(unittest.TestCase):

    @unittest.skip('unfinished')
    def test_sable_message_to_lido_string(self):
        loadplan_schema = LoadPlanSchema()
        with open('tests/sable_message.txt') as sable_file:
            text = sable_file.read()
            loadplan_data = sable.extract.from_text(text)
            loadplan = loadplan_schema.load(loadplan_data)
            wbmsg = LIDOWeightBalanceMessage(loadplan)
            s = str(wbmsg)
            print(s)
            #e = ('WAB09NOV2017002500COM  123 09NOV2017MIA  NGU  04100'
            #     '      000000NNN 24.121487521783520000L     017986  '
            #     '                            ')
            #self.assertEqual(s, e)


if __name__ == '__main__':
    unittest.main()
