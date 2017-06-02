import unittest
from coconut import convenience


class Test_operators(unittest.TestCase):

    def _compileAndCheck(self,expr,expected):
        """Compiles `code` using `convenience.parse` and asserts the result is in `output`"""
        code = convenience.parse(expr,'block')
        self.assertIn(expected,code)
    
    def test_pipe_forward(self):
        expr = '1 |> print'        
        self._compileAndCheck(expr,'(print)(1)')


    def test_pipe_backward(self):
        expr = 'print <| 1'
        self._compileAndCheck(expr,'(print)(1)')

    def test_pipe_multi_forward(self):
        expr = '[1,2] |*> print'
        self._compileAndCheck(expr,'(print)(*[1, 2])')

    def test_pipe_multi_backward(self):
        expr = 'print <*| [1,2]'
        self._compileAndCheck(expr,'(print)(*[1, 2])')

    def test_partial_function(self):
        expr = 'print$(1)'
        self._compileAndCheck(expr,'_coconut.functools.partial(print, 1)')

    def test_lambda(self):
        expr = '(x)->(x)'
        self._compileAndCheck(expr,'lambda x: (x)')

    def test_compose(self):
        expr = 'f..g'
        self._compileAndCheck(expr,'_coconut_compose(f, g)')

    def test_chain(self):
        expr = '[1,2]::[3,4]'
        self._compileAndCheck(expr,'_coconut.itertools.chain.from_iterable((_coconut_lazy_item() for _coconut_lazy_item in (lambda: [1, 2], lambda: [3, 4])))')

    def test_compose(self):
        expr = '[1,2]$[1]'
        self._compileAndCheck(expr,'_coconut_igetitem([1, 2], 1)')

if __name__ == '__main__':
    unittest.main()
