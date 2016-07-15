import unittest
from coconut import convenience

class Test_convenience(unittest.TestCase):
    
    def test_version(self):
        version = convenience.version()
        self.assertIsInstance(version,str)

    def test_exec(self):
        expr = 'a = 1 + 1'

        code = convenience.parse(expr)
        exec(code)

        self.assert_(a == 2)

        

if __name__ == '__main__':
    unittest.main()
