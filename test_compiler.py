import unittest
from compiler import *


class TestCompiler(unittest.TestCase):
    def test_lexer_stack(self):
        lexer = Lexer("1 2 3 4")

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_DEC)
        self.assertEquals(lexer.text, "1")

        lexer.push("a b")

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_SYMBOL)
        self.assertEquals(lexer.text, "a")

        lexer.push("abc")

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_SYMBOL)
        self.assertEquals(lexer.text, "abc")

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_SYMBOL)
        self.assertEquals(lexer.text, "b")

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_DEC)
        self.assertEquals(lexer.text, "2")

        lexer.push("123")

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_DEC)
        self.assertEquals(lexer.text, "123")

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_DEC)
        self.assertEquals(lexer.text, "3")

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_DEC)
        self.assertEquals(lexer.text, "4")

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_EOT)

    def test_lexer(self):
        lexer = Lexer("  DAT 1, 'ab' \n  SET A, 0x05  \n  ; AB\n  #define A 1 X\n#define A 2 3;B\n  SET B, A")

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_SYMBOL)
        self.assertEquals(lexer.text, "DAT")

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_DEC)
        self.assertEquals(lexer.text, "1")

        lexer.next()
        self.assertEquals(lexer.token, ',')

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_LITERAL)
        self.assertEquals(lexer.text, "'ab'")

        lexer.next()
        self.assertEquals(lexer.token, '\n')

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_SYMBOL)
        self.assertEquals(lexer.text, "SET")

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_SYMBOL)
        self.assertEquals(lexer.text, "A")

        lexer.next()
        self.assertEquals(lexer.token, ',')

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_HEX)
        self.assertEquals(lexer.text, "0x05")

        lexer.next()
        self.assertEquals(lexer.token, '\n')

        lexer.next()
        self.assertEquals(lexer.token, ';')

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_SYMBOL)
        self.assertEquals(lexer.text, "AB")

        lexer.next()
        self.assertEquals(lexer.token, '\n')

        lexer.next()
        self.assertEquals(lexer.token, '#')

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_SYMBOL)
        self.assertEquals(lexer.text, "define")

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_SYMBOL)
        self.assertEquals(lexer.text, "A")

        lexer.eat_text()
        self.assertEquals(lexer.token, TOKEN_TEXT)
        self.assertEquals(lexer.text, "1 X")

        lexer.next()
        self.assertEquals(lexer.token, '\n')

        lexer.next()
        self.assertEquals(lexer.token, '#')

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_SYMBOL)
        self.assertEquals(lexer.text, "define")

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_SYMBOL)
        self.assertEquals(lexer.text, "A")

        lexer.eat_text()
        self.assertEquals(lexer.token, TOKEN_TEXT)
        self.assertEquals(lexer.text, "2 3")

        lexer.next()
        self.assertEquals(lexer.token, ';')

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_SYMBOL)
        self.assertEquals(lexer.text, "B")

        lexer.next()
        self.assertEquals(lexer.token, '\n')

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_SYMBOL)
        self.assertEquals(lexer.text, "SET")

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_SYMBOL)
        self.assertEquals(lexer.text, "B")

        lexer.next()
        self.assertEquals(lexer.token, ',')

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_SYMBOL)
        self.assertEquals(lexer.text, "A")

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_EOT)

    def test_comment(self):
        lexer = Lexer(";\n")

        lexer.next()
        self.assertEquals(lexer.token, ';')

        lexer.next()
        self.assertEquals(lexer.token, '\n')

        lexer.next()
        self.assertEquals(lexer.token, TOKEN_EOT)

    def _expr(self, val):
        parser = Compiler(val)
        parser.lexer = Lexer(val)
        parser.lexer.next()
        return parser.expr()

    def test_expr(self):
        self.assertEquals(self._expr('1'), (None, 1, True))
        self.assertEquals(self._expr('1+2'), (None, 3, True))
        self.assertEquals(self._expr('1+2+3'), (None, 6, True))
        self.assertEquals(self._expr('1+2*3'), (None, 7, True))
        self.assertEquals(self._expr('(1+2)*3'), (None, 9, True))
        self.assertEquals(self._expr('(1+2)*(3)'), (None, 9, True))
        self.assertEquals(self._expr('-(1+2)*(3)'), (None, -9, True))
        self.assertEquals(self._expr('-(1+2)*(-3)'), (None, 9, True))
        self.assertEquals(self._expr('-(1-2)*(-3)'), (None, -3, True))

        self.assertEquals(self._expr('A'), ('a', 0, True))
        self.assertEquals(self._expr('A+2'), ('a', 2, True))
        self.assertEquals(self._expr('A-2'), ('a', -2, True))
        self.assertEquals(self._expr('A-2*3'), ('a', -6, True))

        self.assertEquals(self._expr('1-A'), None)

    def _op_value(self, val, is_a=False):
        parser = Compiler(val)
        parser.lexer = Lexer(val)
        parser.defines = {}
        parser.lexer.next()
        return parser.op_value(is_a)

    def test_op_value(self):
        self.assertEquals(self._op_value('-1', True), (0x20, None))
        self.assertEquals(self._op_value('0', True), (0x21, None))
        self.assertEquals(self._op_value('1', True), (0x22, None))
        self.assertEquals(self._op_value('30', True), (0x3f, None))
        self.assertEquals(self._op_value('0x00', True), (0x21, None))
        self.assertEquals(self._op_value('0x01', True), (0x22, None))
        self.assertEquals(self._op_value('0xffff', True), (0x20, None))
        self.assertEquals(self._op_value('0x1ffff', True), (0x20, None))

        self.assertEquals(self._op_value('-1'), (0x1f, -1))
        self.assertEquals(self._op_value('0'), (0x1f, 0))
        self.assertEquals(self._op_value('1'), (0x1f, 1))
        self.assertEquals(self._op_value('30'), (0x1f, 30))
        self.assertEquals(self._op_value('0x00'), (0x1f, 0x00))
        self.assertEquals(self._op_value('0x01'), (0x1f, 0x01))
        self.assertEquals(self._op_value('0xffff'), (0x1f, 0xffff))
        self.assertEquals(self._op_value('0x1ffff'), (0x1f, 0x1ffff))

        self.assertEquals(self._op_value('[0]'), (0x1e, 0))
        self.assertEquals(self._op_value('[1]'), (0x1e, 1))
        self.assertEquals(self._op_value('[0x00]'), (0x1e, 0))
        self.assertEquals(self._op_value('[0x01]'), (0x1e, 1))
        self.assertEquals(self._op_value('[0xffff]'), (0x1e, 0xffff))
        self.assertEquals(self._op_value('[0x1ffff]'), (0x1e, 0x1ffff))

        self.assertEquals(self._op_value('a'), (0x00, None))
        self.assertEquals(self._op_value('A'), (0x00, None))
        self.assertEquals(self._op_value('b'), (0x01, None))
        self.assertEquals(self._op_value('c'), (0x02, None))
        self.assertEquals(self._op_value('x'), (0x03, None))
        self.assertEquals(self._op_value('y'), (0x04, None))
        self.assertEquals(self._op_value('z'), (0x05, None))
        self.assertEquals(self._op_value('i'), (0x06, None))
        self.assertEquals(self._op_value('j'), (0x07, None))
        self.assertEquals(self._op_value('sp'), (0x1b, None))

        self.assertEquals(self._op_value('[a]'), (0x08, None))
        self.assertEquals(self._op_value('[A]'), (0x08, None))
        self.assertEquals(self._op_value('[b]'), (0x09, None))
        self.assertEquals(self._op_value('[c]'), (0x0a, None))
        self.assertEquals(self._op_value('[x]'), (0x0b, None))
        self.assertEquals(self._op_value('[y]'), (0x0c, None))
        self.assertEquals(self._op_value('[z]'), (0x0d, None))
        self.assertEquals(self._op_value('[i]'), (0x0e, None))
        self.assertEquals(self._op_value('[j]'), (0x0f, None))
        self.assertEquals(self._op_value('[sp]'), (0x19, None))

        self.assertEquals(self._op_value('[a+5]'), (0x10, 5))
        self.assertEquals(self._op_value('[A+5]'), (0x10, 5))
        self.assertEquals(self._op_value('[b+5]'), (0x11, 5))
        self.assertEquals(self._op_value('[c+5]'), (0x12, 5))
        self.assertEquals(self._op_value('[x+5]'), (0x13, 5))
        self.assertEquals(self._op_value('[y+5]'), (0x14, 5))
        self.assertEquals(self._op_value('[z+5]'), (0x15, 5))
        self.assertEquals(self._op_value('[i+5]'), (0x16, 5))
        self.assertEquals(self._op_value('[j+5]'), (0x17, 5))
        self.assertEquals(self._op_value('[sp+5]'), (0x1a, 5))

        self.assertEquals(self._op_value('[a-5]'), (0x10, -5))
        self.assertEquals(self._op_value('[a-5+3]'), (0x10, -2))
        self.assertEquals(self._op_value('[a-(5*3)]'), (0x10, -15))

        self.assertEquals(self._op_value('pc'), (0x1c, None))
        self.assertEquals(self._op_value('ex'), (0x1d, None))
        self.assertEquals(self._op_value('push'), (0x18, None))
        self.assertEquals(self._op_value('pop'), (0x18, None))
        self.assertEquals(self._op_value('peek'), (0x19, None))
        self.assertEquals(self._op_value('pick 5'), (0x1a, 5))

    def _preprocessor(self, val):
        parser = Compiler(val)
        parser.process(PREPROCESSOR)
        return parser

    def test_preprocessor(self):
        self.assertDictEqual(self._preprocessor("#define A 1\n#define B 1 2 3;56\n\n#define C").defines, {'A': '1', 'B': '1 2 3', 'C': ''})
        self.assertListEqual(self._preprocessor('DAT l1,l2;COMMENT\nDAT l3').memory, [0, 0, 0])

    def _pass1(self, val):
        parser = Compiler(val)
        parser.process(PASS_1)
        return parser.labels

    def test_pass1(self):
        self.assertDictEqual(self._pass1('DAT 0\n:a1 DAT 1\n:a2 DAT 2'), {"a1": 1, "a2": 2})

    def _pass2(self, val):
        parser = Compiler(val)
        parser.process(PASS_2)
        return parser.memory

    def test_pass2(self):
        self.assertListEqual(self._pass2('SET C, B'), [0b0000010001000001])
        self.assertListEqual(self._pass2("DAT ,1, 2, 0x03, 'AB',"), [0, 1, 2, 3, 65, 66, 0])
        self.assertListEqual(self._pass2("JSR B"), [0b0000010000100000])
        self.assertListEqual(self._pass2('DAT 1,2;COMMENT'), [1, 2])



if __name__ == '__main__':
    unittest.main()
