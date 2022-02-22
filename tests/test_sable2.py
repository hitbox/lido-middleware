import os
import pickle
import unittest

from sable2 import extract

# download the inbox messages and save in a pickle as an unnamed list
SABLEMESSAGES = os.environ.get('SABLEMESSAGES')

@unittest.skipIf(
    SABLEMESSAGES is None,
    'Environment variable SABLEMESSAGES not set.'
)
class TestExtract(unittest.TestCase):

    def setUp(self):
        with open(SABLEMESSAGES, 'rb') as fp:
            self.sablemessages = pickle.load(fp)

    def test_run(self):
        # simply testing that only our internal errors are thrown.
        # would like to make better.
        for msg in self.sablemessages:
            try:
                loadplan_data = extract.loadplan_from_message(msg)
            except extract.SableExtractError as e:
                print(f'sable2.extract:accepting:{e!r}')


if __name__ == '__main__':
    unittest.main()
