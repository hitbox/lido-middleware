import types
import unittest

from pathlib import Path

import lido
import amazon_lsh.extract

datadir = Path(__file__).parent / 'data'

def from_pyfile(filename):
    d = types.ModuleType("config")
    d.__file__ = filename
    with open(filename, mode="rb") as file:
        exec(compile(file.read(), filename, "exec"), d.__dict__)
    return d

class TestAmazonLSH(unittest.TestCase):

    def test_amazon_lsh_extract(self):
        email_text_path = datadir / 'amazon_lsh.py'
        expect_path = datadir / 'amazon_lsh.py.extract-expect.py'
        source = from_pyfile(email_text_path)
        expect = from_pyfile(expect_path)
        result = amazon_lsh.extract.from_text(source.data)
        self.maxDiff = None
        self.assertEqual(result, expect.data)


if __name__ == '__main__':
    unittest.main()
