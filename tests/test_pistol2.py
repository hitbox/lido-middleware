import os
import pickle
import unittest

from pistol2 import extract

# download the inbox messages and save in a pickle as an unnamed list
PSTLMESSAGES = os.environ.get('PSTLMESSAGES')

@unittest.skipIf(
    PSTLMESSAGES is None,
    'Environment variable PSTLMESSAGES not set.'
)
class TestExtract(unittest.TestCase):

    def setUp(self):
        with open(PSTLMESSAGES, 'rb') as fp:
            self.pstlmessages = pickle.load(fp)

    def test_run(self):
        # simply testing that only our internal errors are thrown.
        # would like to make better.
        for msg in self.pstlmessages:
            try:
                loadplan_data = extract.loadplan_from_message(msg)
            except extract.PistolExtractError as e:
                print(f'pistol2.extract:accepting:{e!r}')


if __name__ == '__main__':
    unittest.main()
