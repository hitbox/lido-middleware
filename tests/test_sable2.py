import os
import pickle
import unittest

from sable2 import extract

# download the inbox messages and save in a pickle as an unnamed list
SABLEMESSAGES = os.environ.get('SABLEMESSAGES')
SABLEMESSAGES_PRINT = os.environ.get('SABLEMESSAGES_PRINT')

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
        nerr = 0
        for msg in self.sablemessages:
            try:
                loadplan_data = extract.loadplan_from_message(msg)
            except extract.SableExtractError as e:
                if SABLEMESSAGES_PRINT:
                    print(f'sable2.extract:accepting:{e!r}')
                nerr += 1
        if nerr > 0 and SABLEMESSAGES_PRINT:
            print('Should only see SableExtractError error messages.')


if __name__ == '__main__':
    unittest.main()
