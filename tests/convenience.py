import unittest
from coconut import convenience

exec(convenience.parse(""))

class Test_convenience(unittest.TestCase):
    
    def test_version(self):
        version = convenience.version()
        self.assertIsInstance(version,str)

    def test_eval(self):
        expr = '1'

        result_globals = {}
        result_locals = {}

        code = convenience.parse(expr,"block")
        res = eval(code)

        self.assert_(res == 1)

        

if __name__ == '__main__':
    unittest.main()
