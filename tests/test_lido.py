import unittest

from lido import LIDOWeightBalanceMessage
from pistol import LoadPlanSchema
from pistol.parse import loadplan_from_text

class TestLIDO(unittest.TestCase):

    def test_(self):
        loadplan_schema = LoadPlanSchema()
        with open('tests/pistol_message.txt') as pstlfile:
            text = pstlfile.read()
            loadplan_data = loadplan_from_text(text)
            loadplan = loadplan_schema.load(loadplan_data)
            wbmsg = LIDOWeightBalanceMessage(loadplan)
            s = str(wbmsg)
            e = ('WAB2017-11-09 00:25:00123     _09Nov2017KMIA TODO'
                 'TODO_TODOTODO00TODOTODOTODOTODOTODO0TODO00TODO00TODOTODOTODOTODOTODO'
                 'TODOTODOTODOTODO')
            print(s)


if __name__ == '__main__':
    unittest.main()
