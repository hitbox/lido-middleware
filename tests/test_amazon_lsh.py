import types
import unittest

from pathlib import Path

import amazon_lsh.extract
import amazon_lsh.schema
import lido

datadir = Path(__file__).parent / 'data'

# copied from Flask.config
def from_pyfile(filename):
    d = types.ModuleType("config")
    d.__file__ = filename
    with open(filename, mode="rb") as file:
        exec(compile(file.read(), filename, "exec"), d.__dict__)
    return d

class TestAmazonLSH(unittest.TestCase):

    def test_amazon_lsh_expect(self):
        email_text_path = datadir / 'amazon_lsh.py'
        expect_path = datadir / 'amazon_lsh.py.extract-expect.py'
        source = from_pyfile(email_text_path)
        expect = from_pyfile(expect_path)
        result = amazon_lsh.extract.from_text(source.data)
        self.maxDiff = None
        self.assertEqual(result, expect.data)

    def test_schema(self):
        source_path = datadir / 'amazon_lsh.py.extract-expect.py'
        expect_path = datadir / 'amazon_lsh.py.schema-expect.py'
        source = from_pyfile(source_path)
        expect = from_pyfile(expect_path)
        result = amazon_lsh.schema.LoadPlanSchema().load(source.data)
        self.maxDiff = None
        self.assertEqual(result, expect.data)

    def test_amazon_lsh_lido(self):
        source_path = datadir / 'amazon_lsh.py.schema-expect.py'
        source = from_pyfile(source_path)
        result = str(lido.LIDOWeightBalanceMessage(source.data))
        expect = (
            'WAB11FEB20210000008C  3425 11FEB2021AFW  ABE  04100      000000YYY'
            ' 12.831239220190510000K13.29080612                              ')
        self.assertEqual(result, expect)


if __name__ == '__main__':
    unittest.main()
