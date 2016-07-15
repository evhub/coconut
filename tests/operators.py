import unittest
from coconut import convenience

class Test_operators(unittest.TestCase):
    
    def test_pipe_forward(self):
        expr = '1 |> print'
        
        code = convenience.parse(expr)

        self.assertIn('(print)(1)',code)

    def test_pipe_backward(self):
        expr = 'print <| 1'
        
        code = convenience.parse(expr)

        self.assertIn('(print)(1)',code)

    def test_pipe_multi_forward(self):
        expr = '[1,2] |*> print'
        
        code = convenience.parse(expr)

        self.assertIn('(print)(*[1, 2])',code)

    def test_pipe_multi_backward(self):
        expr = 'print <*| [1,2]'
        
        code = convenience.parse(expr)

        self.assertIn('(print)(*[1, 2])',code)

if __name__ == '__main__':
    unittest.main()
