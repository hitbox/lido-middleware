import unittest

from lido import LIDOWeightBalanceMessage
from pistol import LoadPlanSchema
from pistol.parse import loadplan_from_text

class TestLIDO(unittest.TestCase):

    def test_pistol_message_to_lido_string(self):
        loadplan_schema = LoadPlanSchema()
        with open('tests/pistol_message.txt') as pistol_file:
            text = pistol_file.read()
            loadplan_data = loadplan_from_text(text)
            loadplan = loadplan_schema.load(loadplan_data)
            wbmsg = LIDOWeightBalanceMessage(loadplan)
            s = str(wbmsg)
            e = ('WAB09NOV2017002500COM  123 09NOV2017MIA  NGU  04100'
                 '      000000NNN 24.121487521783520000L     017986  '
                 '                            ')
            self.assertEqual(s, e)


if __name__ == '__main__':
    unittest.main()
