#!/usr/bin/env python
import StringIO
import sys
import os
import argparse

basic_ops = {
    "set": 0x01, "add": 0x02, "sub": 0x03,
    "mul": 0x04, "mli": 0x05,
    "div": 0x06, "dvi": 0x07,
    "mod": 0x08, "mdi": 0x09,
    "and": 0x0a, "bor": 0x0b, "xor": 0x0c,
    "shr": 0x0d, "asr": 0x0e, "shl": 0x0f,
    "ifb": 0x10, "ifc": 0x11,
    "ife": 0x12, "ifn": 0x13,
    "ifg": 0x14, "ifa": 0x15,
    "ifl": 0x16, "ifu": 0x17,
    "adx": 0x1a, "sbx": 0x1b,
    "sti": 0x1e, "std": 0x1f,
}

special_ops = {
    "jsr": 0x01,
    "int": 0x08, "iag": 0x09, "ias": 0x0a, "rfi": 0x0b, "iaq": 0x0c,
    "hwn": 0x10, "hwq": 0x11, "hwi": 0x12,
}

regs = {
    "a": (0x00, 0x08, 0x10), "b": (0x01, 0x09, 0x11), "c": (0x02, 0x0a, 0x12),
    "x": (0x03, 0x0b, 0x13), "y": (0x04, 0x0c, 0x14), "z": (0x05, 0x0d, 0x15),
    "i": (0x06, 0x0e, 0x16), "j": (0x07, 0x0f, 0x17),
    "sp": (0x1b, 0x19, 0x1a),
    "push": (0x18, None, None), "pop": (0x18, None, None), "peek": (0x19, None, None), "pick": (0x1a, None, None),
    "pc": (0x1c, None, None), "ex": (0x1d, None, None),
}

boot_loader = [
    0x03, 0x01, 0x84, 0x01, 0x87, 0x01, 0x7d, 0x00, 0x47, 0x43, 0x60, 0x21,
    0x44, 0xe1, 0x00, 0x01, 0x7c, 0xe3, 0x00, 0x96, 0xd8, 0xc1, 0x1c, 0xa1,
    0x7c, 0x01, 0x00, 0x96, 0x88, 0x03, 0x39, 0xfe, 0x84, 0x13, 0xbf, 0x81,
    0x7c, 0xa2, 0x00, 0x0b, 0x17, 0x81, 0x70, 0xe1, 0x87, 0x61, 0x1f, 0x01,
    0x7f, 0x22, 0x00, 0x75, 0x1c, 0xc1, 0x7c, 0xc2, 0x00, 0x3d, 0x18, 0x20,
    0x8b, 0x62, 0x8b, 0x83, 0x70, 0xe1, 0x60, 0x21, 0x1f, 0x01, 0x7f, 0x22,
    0x00, 0x5a, 0x1c, 0xc1, 0x7c, 0xc2, 0x00, 0x32, 0x18, 0x20, 0x8b, 0x62,
    0x7c, 0x01, 0x20, 0x03, 0x78, 0x41, 0x01, 0xfd, 0x84, 0x61, 0x78, 0xa1,
    0x01, 0xfe, 0x84, 0xb2, 0x7f, 0x82, 0x00, 0x1a, 0x0b, 0x01, 0x0f, 0x01,
    0x07, 0x01, 0x7d, 0x00, 0x47, 0x43, 0x60, 0x81, 0x8f, 0x62, 0x84, 0x92,
    0x7f, 0x82, 0x00, 0x06, 0x88, 0xa3, 0x88, 0x42, 0x7c, 0x62, 0x02, 0x00,
    0x7f, 0x82, 0xff, 0xed, 0x1f, 0x01, 0x7f, 0x22, 0x00, 0x46, 0x1c, 0xc1,
    0x7c, 0xc2, 0x00, 0x32, 0x18, 0x20, 0x8b, 0x62, 0x7f, 0x82, 0x00, 0x03,
    0x04, 0x01, 0x87, 0x61, 0x87, 0x81, 0x7f, 0x81, 0x00, 0x51, 0x03, 0x01,
    0x7c, 0x01, 0x10, 0x00, 0x8b, 0x63, 0x7d, 0x00, 0x47, 0x43, 0x60, 0x01,
    0x84, 0x12, 0x7f, 0x81, 0x00, 0x65, 0x7c, 0x01, 0x10, 0x04, 0x6b, 0x01,
    0x00, 0x02, 0x8b, 0x01, 0x7d, 0x00, 0x47, 0x43, 0x8f, 0x62, 0x60, 0x01,
    0x63, 0x81, 0x00, 0x45, 0x00, 0x72, 0x00, 0x72, 0x00, 0x6f, 0x00, 0x72,
    0x00, 0x20, 0x00, 0x77, 0x00, 0x68, 0x00, 0x69, 0x00, 0x6c, 0x00, 0x65,
    0x00, 0x20, 0x00, 0x72, 0x00, 0x65, 0x00, 0x61, 0x00, 0x64, 0x00, 0x69,
    0x00, 0x6e, 0x00, 0x67, 0x00, 0x00, 0x00, 0x42, 0x00, 0x6f, 0x00, 0x6f,
    0x00, 0x74, 0x00, 0x4c, 0x00, 0x6f, 0x00, 0x61, 0x00, 0x64, 0x00, 0x65,
    0x00, 0x72, 0x00, 0x20, 0x00, 0x76, 0x00, 0x30, 0x00, 0x2e, 0x00, 0x31,
    0x00, 0x00, 0x00, 0x43, 0x00, 0x61, 0x00, 0x75, 0x00, 0x67, 0x00, 0x68,
    0x00, 0x74, 0x00, 0x20, 0x00, 0x73, 0x00, 0x74, 0x00, 0x72, 0x00, 0x61,
    0x00, 0x79, 0x00, 0x20, 0x00, 0x65, 0x00, 0x78, 0x00, 0x65, 0x00, 0x63,
    0x00, 0x75, 0x00, 0x74, 0x00, 0x69, 0x00, 0x6f, 0x00, 0x6e, 0x00, 0x3a,
    0x00, 0x20, 0x00, 0x68, 0x00, 0x61, 0x00, 0x6c, 0x00, 0x74, 0x00, 0x69,
    0x00, 0x6e, 0x00, 0x67, 0x00, 0x00
]


SYMBOLS = '_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
DIGITS = '0123456789'
HEXES = '0123456789abcdefABCDEF'


class Buffer(object):
    def __init__(self, name, text):
        self.name = name
        self.text = text
        self.pos = 0

        self.lines = [[get_addr(), None, '']]

    @property
    def current(self):
        return self.text[self.pos] if self.pos < len(self.text) else chr(0)

    def advance(self):
        if args.verbose:
            sys.stdout.write(self.current)

        if self.current not in '\n\0':
            self.lines[-1][2] += self.current

        self.pos += 1

    def finish_row(self):
        if self.lines[-1][0] == get_addr():
            self.lines[-1][0] = None
        else:
            self.lines[-1][1] = get_addr() - 1
        self.lines.append([get_addr(), None, ''])

    def finish_buf(self):
        if self.name and args.debug:
            for line_num, line in enumerate(self.lines[:-1]):
                io_buf.write("%s,%s,%s" % (
                    self.name, line_num, (line[1] - line[0] + 1) if line[0] is not None else 0
                ))
                if line[0] is not None:
                    for address in range(line[0], line[1] + 1):
                        io_buf.write(",%s:%s" % (format(address, '04x'), format(memory[address], '04x')))
                io_buf.write("\n%s\n" % (line[2]))


class BufferStream(object):
    def __init__(self, phase):
        self.phase = phase
        self.stack = []

    def push(self, name, text):
        self.stack.append(Buffer(name, text))

    @property
    def buf(self):
        if self.stack:
            return self.stack[-1]
        return None

    @property
    def char(self):
        return self.buf.current if self.stack else chr(0)

    def advance(self, prev_token):
        if prev_token == '\n':
            self.buf.finish_row()

        if self.char == '\0':
            while self.stack and self.char == '\0':
                if self.phase == PASS_2:
                    self.buf.finish_buf()
                self.stack.pop()
        else:
            self.buf.advance()

class Lexer:
    def __init__(self, name, text, phase, defines):
        self.phase = phase
        self.stack = BufferStream(phase)
        self.stack.push(name, text)
        self.defines = defines

        self.token = 'b'
        self._token_buf = None
        self._token_start = 0
        self._token_end = 0

    @property
    def buf(self):
        return self.stack.buf

    @property
    def _current_char(self):
        return self.stack.char

    def _mark_start(self):
        if self.buf:
            self._token_buf = self.buf
            self._token_start = self._token_buf.pos
        else:
            self._token_buf = None
            self._token_start = None

    def _mark_end(self):
        if self.buf:
            self._token_end = self._token_buf.pos
        else:
            self._token_end = None

    def _advance(self):
        self.stack.advance(self.token)
        self.token = '\0'

    def _skip_white(self):
        while self._current_char in ' \t':
            self._advance()

    def skip_comment(self):
        while self._current_char not in '\n\0':
            self._advance()

    def _eat_number(self):
        if self._current_char == '0':
            self._advance()
            if self._current_char == 'x':
                self._advance()
                while self._current_char in HEXES:
                    self._advance()

                self.token = 'x'
                return

        while self._current_char in DIGITS:
            self._advance()

        self.token = 'd'

    def _eat_symbol(self):
        while self._current_char in SYMBOLS:
            self._advance()

        self.token = 's'

    def _eat_literal(self):
        mark = self._current_char

        while True:
            self._advance()
            if self._current_char == '\\':
                self._advance()
                if self._current_char == mark:
                    continue

            if self._current_char == mark:
                self._advance()
                self.token = 'l'
                return
            if self._current_char == '\0':
                self.token = 'r'
                return

    def eat_text(self):
        self._skip_white()
        self._mark_start()

        while self._current_char not in ';\n\0':
            self._advance()

        self.token = 't'
        self._mark_end()

    def eat_multi_line_text(self):
        self._skip_white()
        self._mark_start()

        mlt = ''
        while self._current_char not in ';\n\0':
            if self._current_char == '%':
                mlt += "\n"
            else:
                mlt += self._current_char
            self._advance()

        self.token = 't'
        self._mark_end()

        return mlt

    def push(self, name, text):
        self.stack.push(name, text)

    @property
    def text(self):
        return self._token_buf.text[self._token_start: self._token_end]

    def next(self, replace=True):
        self._skip_white()
        c = self._current_char

        if c == '\0':
            self._advance()

            self._skip_white()
            c = self._current_char

        self._mark_start()

        if c in DIGITS:
            self._eat_number()
        elif c in SYMBOLS:
            self._eat_symbol()
        elif c == '"' or c == "'":
            self._eat_literal()
        elif c in "#.+-*/&|^()[]:;,\n":
            self._advance()
            self.token = c
        else:
            # TOKEN_EOF TOKEN_ERROR
            self.token = self._current_char

        self._mark_end()

        if replace and self.token == 's' and self.text in self.defines:
            self.push(None, self.defines[self.text])
            self.next()


PREPROCESSOR = 0
PASS_1 = 1
PASS_2 = 2

io_buf = None
doc_buf = None
memory = []
org = 0

path = None
args = None

def file_reader(src):
    print "  Loading %s" % src
    with open(os.path.join(path, src), 'r') as in_file:
        stuff = in_file.read()
        if stuff[-1] != '\n':
            stuff += '\n'
        return stuff

def debug_writer(line):
    if args.debug:
        with open("%s.dbg" % args.output, 'a') as out_file:
            out_file.write(line)


def get_addr():
    return len(memory) + org


def remove_escape(literal):
    literal = literal.replace('\\\\', '\\')
    literal = literal.replace('\\b', chr(0x10))
    literal = literal.replace('\\t', '\t')
    literal = literal.replace('\\r', chr(0x11))
    literal = literal.replace('\\n', chr(0x11))
    literal = literal.replace('\\0', '\0')
    literal = literal.replace('\\"', '\"')
    literal = literal.replace("\\'", "\'")
    while '\\x' in literal:
        pos = literal.find('\\x')
        if pos + 4 > len(literal):
            break
        literal = literal[:pos] + chr(int(literal[pos+2:pos+4], 16)) + literal[pos+4:]

    return literal

class Compiler(object):
    def __init__(self, name):
        self.name = name
        self.source = file_reader(name)

        self.included = set()
        self.lexer = None
        self.defines = {}
        self.labels = {}
        self.optimization = True

    def append(self, value):
        memory.append(value & 0xffff)

    def compile(self):
        global io_buf, doc_buf

        print "PASS 1 - Preprocessor directives"
        if self.process(PREPROCESSOR):
            print "PASS 2 - Address calculation"
            if self.process(PASS_1):

                print "PASS 3 - Compilation"
                count = 0
                while self.optimization:
                    io_buf = StringIO.StringIO()
                    doc_buf = StringIO.StringIO()
                    self.optimization = False
                    print "Optimization pass:", count
                    count += 1
                    if not self.process(PASS_2):
                        return None

                if args.doc:
                    doc_name = "%s.%s" % (os.path.splitext(args.output)[0], "txt")
                    with open(doc_name, 'w') as out_file:
                        out_file.write(doc_buf.getvalue())

                if args.debug:
                    debug_name = "%s.%s" % (os.path.splitext(args.output)[0], "dbg")
                    with open(debug_name, 'w') as out_file:
                        out_file.write("%s\n" % (len(self.defines)))
                        for k, v in sorted(self.defines.items()):
                            out_file.write("%s\n%s\n" % (k, v))

                        out_file.write("%s\n" % (len(self.labels)))
                        for k, v in sorted(self.labels.items()):
                            out_file.write("%s\n%s\n" % (k, v))

                        out_file.write(io_buf.getvalue())

                words = ''.join(chr((x >> 8) & 0xFF) + chr(x & 0xFF) for x in memory)
                return words

        return None

    def process(self, phase):
        global memory
        memory = []

        self.lexer = Lexer(self.name, self.source, phase, self.defines)
        self.included = set()

        self.lexer.next()
        while True:
            if self.lexer.token == '\0':
                return True
            elif self.lexer.token == 'r':
                return False
            elif self.lexer.token == '\n':
                self.lexer.next()
            elif self.lexer.token in '#.':
                self.lexer.next()
                if self.lexer.token == 's':
                    if self.lexer.text.lower() == "define":
                        self.lexer.next(replace=False)
                        if self.lexer.token != 's':
                            return False

                        name = self.lexer.text

                        mlt = self.lexer.eat_multi_line_text()

                        if phase == PREPROCESSOR:
                            if name in self.defines:
                                print "Warning: #define %s overrides previous value"
                            self.defines[name] = mlt
                            #print "%s: %s" % (name, self.lexer.text)

                        self.lexer.next()

                    elif self.lexer.text.lower() == "include":
                        self.lexer.eat_text()
                        #self.lexer.next()
                        #if self.lexer.token != 'l':
                        #    return False
                        name = self.lexer.text
                        if name.startswith("'") or name.startswith('"'):
                            name = name[1: -1]
                        if name not in self.included:
                            self.lexer.push(name, file_reader(name))
                        self.lexer.next()

                    elif self.lexer.text.lower() == "fill":
                        self.lexer.next()

                        value = self.logic()
                        if value is None:
                            return False
                        if value[0] is not None:
                            return False
                        if phase == PASS_2 and not value[2]:
                            return False

#                        self.lexer.next()

                        amount = self.logic()
                        if amount is None:
                            return False
                        if amount[0] is not None:
                            return False
                        if phase == PASS_2 and not amount[2]:
                            return False

                        loop = amount[1]
                        while loop:
                            self.append(value[1])
                            loop -= 1

                        self.lexer.next()

                    elif self.lexer.text.lower() == "doc":
                        self.lexer.eat_text()

                        if phase == PASS_2:
                            doc_buf.write("%s: %s\n" % (format(get_addr(), '04x'), self.lexer.text))

                        self.lexer.next()

                    else:
                        return False

            elif self.lexer.token == ';':
                self.lexer.skip_comment()
                self.lexer.next()

            elif self.lexer.token == ':':
                self.lexer.next()
                if self.lexer.token != 's':
                    return False

                name = self.lexer.text
                if name in self.labels:
                    if self.labels[self.lexer.text] != get_addr():
                        # print "\nOptimizing %s by %d" % (name, self.labels[self.lexer.text] - get_addr())
                        self.labels[self.lexer.text] = get_addr()
                        self.optimization = True
                elif phase == PASS_1:
                    self.labels[self.lexer.text] = get_addr()

                self.lexer.next()

            elif self.lexer.token == 's':
                symbol = self.lexer.text.lower()

                if symbol == 'dat':
                    self.lexer.next()
                    defined = False

                    while True:
                        if self.lexer.token in '\0\n;':
                            if not defined:
                                self.append(0)
                            break
                        elif self.lexer.token == ',':
                            if not defined:
                                self.append(0)
                            defined = False
                            self.lexer.next()
                        elif self.lexer.token == 'l':
                            no_escape = remove_escape(self.lexer.text[1:-1])
                            for c in no_escape:
                                defined = True
                                self.append(ord(c))
                            self.lexer.next()
                        else:
                            value = self.logic()
                            if value is None:
                                return False
                            if value[0] is not None:
                                return False
                            if phase == PASS_2 and not value[2]:
                                return False

                            self.append(value[1])
                            defined = True

                elif symbol in basic_ops:
                    self.lexer.next()
                    b = self.op_value(False)
                    if not b or (phase == PASS_2 and not b[2]):
                        return False

                    if self.lexer.token != ',':
                        return False
                    self.lexer.next()

                    a = self.op_value(True)
                    if not a or (phase == PASS_2 and not a[2]):
                        return False

                    if symbol in ('ife', 'ifn', 'ifb', 'ifc') and phase == PASS_2 and b[0] == 0x1f and a[0] != 0x18 and ((b[1] & 0xffff == 0xffff) or 0 <= b[1] <= 30):
                        a, b = ((0x21 + b[1]) & 0xffff, None, True), a

                    if args.optimize:
                        # if phase == PASS_2 and symbol == "mul" and
                        if phase == PASS_2 and symbol == "set" and a[0] == 0x1f and b[0] == 0x1c:
                            opt_done = False
                            if (get_addr() + 1) & 0xffe0 == a[1] & 0xffe0:
                                addr0 = a[1]
                                xor = (get_addr() + 1) ^ a[1]
                                if xor != 0b11111:
                                    symbol = "xor"
                                    a = 0x20 | (xor+1), None, True
                                    addr1 = (get_addr() + 1) ^ ((a[0] & 0x1f) - 1)
                                    # print "optimize PC %s XOR %s -> %s" % (format(get_addr(), '04x'), format(addr0, '04x'), format(addr1, '04x'))
                                    opt_done = True

                            if not opt_done:
                                jump = a[1] - (get_addr() + 1)
                                if 0 < jump < 31:
                                    symbol = "add"
                                    a = 0x20 | (jump + 1), None, True
                                    # print "optimize PC %s ADD" % (format(get_addr(), '04x'))
                                if 0 > jump > -31:
                                    symbol = "sub"
                                    a = 0x20 | (-jump + 1), None, True
                                    # print "optimize PC %s SUB" % (format(get_addr(), '04x'))

                    self.append(a[0] << 10 | b[0] << 5 | basic_ops[symbol])

                    if a[1] is not None:
                        self.append(a[1])

                    if b[1] is not None:
                        self.append(b[1])

                elif symbol in special_ops:
                    self.lexer.next()
                    a = self.op_value(True)
                    if not a or (phase == PASS_2 and not a[2]):
                        return False

                    self.append(a[0] << 10 | special_ops[symbol] << 5)

                    if a[1] is not None:
                        self.append(a[1])

                elif symbol == 'jmp':
                    symbol = "set"
                    self.lexer.next()

                    b = (0x1c, None, True)

                    a = self.op_value(True)
                    if not a or (phase == PASS_2 and not a[2]):
                        return False

                    if phase == PASS_2 and a[0] == 0x1f:
                        opt_done = False
                        if (get_addr() + 1) & 0xffe0 == a[1] & 0xffe0:
                            xor = (get_addr() + 1) ^ a[1]
                            if xor != 0b11111:
                                symbol = "xor"
                                a = 0x20 | (xor+1), None, True
                                opt_done = True

                        if not opt_done:
                            jump = a[1] - (get_addr() + 1)
                            if 0 < jump < 31:
                                symbol = "add"
                                a = 0x20 | (jump + 1), None, True
                            if 0 > jump > -31:
                                symbol = "sub"
                                a = 0x20 | (-jump + 1), None, True

                    self.append(a[0] << 10 | b[0] << 5 | basic_ops[symbol])

                    if a[1] is not None:
                        self.append(a[1])

                else:
                    return False
            else:
                return False

    def op_value(self, is_a):
        if self.lexer.token == '[':
            self.lexer.next()
            node = self.logic()
            if node is None:
                return False
            if self.lexer.token != ']':
                return False

            self.lexer.next()
            if node[0] is not None and (node[1] or not node[2]):
                if regs[node[0]][2] is None:
                    return False
                return regs[node[0]][2], node[1], node[2]
            elif node[0] is not None:
                if regs[node[0]][1] is None:
                    return False
                return regs[node[0]][1], None, node[2]
            else:
                return 0x1e, node[1], node[2]
        else:
            node = self.logic()
            if node is None:
                return False
            if node[0] is not None and (node[1] or not node[2]):
                return False

            if node[0] is not None:
                if node[0] == 'pick':
                    node = self.logic()
                    if node is None:
                        return False
                    if node[0] is not None:
                        return False
                    return regs["pick"][0], node[1], node[2]
                return regs[node[0]][0], None, node[2]
            else:
                if is_a and node[2] and ((node[1] & 0xffff == 0xffff) or 0 <= node[1] <= 30):
                    return (0x21 + node[1]) & 0xffff, None, node[2]
                return 0x1f, node[1], node[2]

    def expr(self):
        left = self.term()
        if left is None:
            return None

        while True:
            if self.lexer.token == '+':
                self.lexer.next()
                right = self.term()
                if right is None:
                    return None

                if left[0] and right[0]:
                    return None

                left = left[0] or right[0], left[1] + right[1], left[2] and right[2]

            elif self.lexer.token == '-':
                self.lexer.next()
                right = self.term()
                if right is None:
                    return None

                if right[0]:
                    return None

                left = left[0], left[1] - right[1], left[2] and right[2]

            else:
                return left

    def logic(self):
        left = self.expr()
        if left is None:
            return None

        while True:
            if self.lexer.token == '&':
                self.lexer.next()
                right = self.expr()
                if right is None:
                    return None

                if left[0] or right[0]:
                    return None

                left = None, left[1] & right[1], left[2] and right[2]

            elif self.lexer.token == '|':
                self.lexer.next()
                right = self.expr()
                if right is None:
                    return None

                if left[0] or right[0]:
                    return None

                left = None, left[1] | right[1], left[2] and right[2]

            elif self.lexer.token == '^':
                self.lexer.next()
                right = self.expr()
                if right is None:
                    return None

                if left[0] or right[0]:
                    return None

                left = None, left[1] ^ right[1], left[2] and right[2]

            else:
                return left

    def term(self):
        left = self.factor()
        if left is None:
            return None

        while True:
            if self.lexer.token == '*':
                self.lexer.next()
                right = self.factor()
                if right is None:
                    return None

                if left[0] or right[0]:
                    return None

                left = None, left[1] * right[1], left[2] and right[2]

            elif self.lexer.token == '/':
                self.lexer.next()
                right = self.factor()
                if right is None:
                    return None

                if left[0] or right[0]:
                    return None

                left = None, left[1] / right[1], left[2] and right[2]

            else:
                return left

    def factor(self):
        while True:
            if self.lexer.token == '(':
                self.lexer.next()
                node = self.logic()

                if self.lexer.token != ')':
                    return None

                self.lexer.next()
                return node

            elif self.lexer.token == '-':
                self.lexer.next()
                node = self.factor()
                if node[0]:
                    return None

                return None, -node[1], node[2]

            elif self.lexer.token == '~':
                self.lexer.next()
                node = self.factor()
                if node[0]:
                    return None

                return None, ~node[1], node[2]

            elif self.lexer.token == 'd':
                val = None, int(self.lexer.text), True
                self.lexer.next()
                return val
            elif self.lexer.token == 'x':
                val = None, int(self.lexer.text, 16), True
                self.lexer.next()
                return val
            elif self.lexer.token == 'l':
                val = None, ord(remove_escape(self.lexer.text[1:-1])), True
                self.lexer.next()
                return val
            elif self.lexer.token == 's':
                symbol = self.lexer.text
                if symbol in self.defines:
                    raise Exception("TERRIBLE!!!")
                    # print "%s" % (self.defines[symbol])
                    self.lexer.push(None, self.defines[symbol])
                    self.lexer.next()
                    continue
                elif symbol in self.labels:
                    val = None, self.labels[symbol], True
                    self.lexer.next()
                    return val
                elif symbol.lower() in regs:
                    val = symbol.lower(), 0, True
                    self.lexer.next()
                    return val
                else:
                    self.lexer.next()
                    return None, 0, False
            else:
                return None

EX_OK = getattr(os, "EX_OK", 0)
EX_USAGE = getattr(os, "EX_USAGE", 64)

class UsageError(Exception):
    def __init__(self, msg):
        self.msg = msg

def main():
    parser = argparse.ArgumentParser(description='compiler for DCPU assembler')
    parser.add_argument('input', help='source code (.dasm16)')
    parser.add_argument('output', nargs='?', default=None, help='binary file (.bin)')
    parser.add_argument('--doc', action='store_true', help='create documentation from doc directives')
    parser.add_argument('--debug', action='store_true', help='create debugger info *.dbg\nsee http://github.com/orlof/dcpu-debugger')
    parser.add_argument('--optimize', action='store_true', help='optimize local jumps with xor, add and sub - may clear EX')
    parser.add_argument('--boot', action='store_true', help='create also TC *.boot disk')
    parser.add_argument('--verbose', action='store_true', help='print every character from lexer')
    parser.add_argument('--org', default=0, type=int, help='destination address')

    global args, path
    args = parser.parse_args()
    path, main_src = os.path.split(os.path.abspath(args.input))

    if not args.output:
        args.output = "%s.%s" % (os.path.splitext(main_src)[0], "bin")

    doc_name = "%s.%s" % (os.path.splitext(args.output)[0], "txt")
    debug_name = "%s.%s" % (os.path.splitext(args.output)[0], "dbg")
    boot_name = "%s.%s" % (os.path.splitext(args.output)[0], "boot")

    try:
        print "Base directory for source: %s" % path
        print "Main compilation unit: %s" % main_src
        print "Target address space start at : %s" % get_addr()
        print "Output .bin : %s" % args.output
        if args.doc:
            print "Output .txt: %s" % doc_name
        if args.debug:
            print "Output .dbg: %s" % debug_name
        if args.boot:
            print "Output .boot: %s" % boot_name

        if args.debug and os.path.exists("%s.dbg" % args.output):
            os.remove("%s.dbg" % args.output)

        compiler = Compiler(main_src)
        code = compiler.compile()

        if code:
            with open(args.output, 'w') as out_file:
                out_file.write(code)
            print "Wrote %s words to %s" % (len(code) / 2, args.output)

            if args.boot:
                with open(boot_name, 'w') as out_file:
                    for index in range(1024):
                        if index < len(boot_loader):
                            out_file.write(chr(boot_loader[index]))
                        elif index == 1018:
                            out_file.write(chr(0x00))
                        elif index == 1019:
                            out_file.write(chr(0x01))
                        elif index == 1020:
                            msb = ((len(code)-1) / 1024 + 1) >> 8
                            out_file.write(chr(msb))
                        elif index == 1021:
                            lsb = ((len(code)-1) / 1024 + 1) & 0xff
                            out_file.write(chr(lsb))
                        elif index == 1022:
                            out_file.write(chr(0x55))
                        elif index == 1023:
                            out_file.write(chr(0xaa))
                        else:
                            out_file.write(chr(0))
                    out_file.write(code)
                print "Wrote %s words to %s" % (512 + len(code) / 2, boot_name)
        else:
            print "Error occurred"

        return EX_OK

    except UsageError, err:
        print >>sys.stderr, err.msg
        return EX_USAGE


if __name__ == "__main__":
    sys.exit(main())


