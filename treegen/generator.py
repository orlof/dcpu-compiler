
class Creator(object):
    def __init__(self, tokens):
        super(Creator, self).__init__()
        self.stmts = tokens
        self.output = ''

    def longest_stmt(self):
        return max([len(x) for x in self.stmts.keys()])

    def create_stmts_by_len(self, stmts):
        stmts_by_len = {}

        for stmt, label in stmts.items():
            l = len(stmt)
            if l not in stmts_by_len:
                stmts_by_len[l] = {}
            stmts_by_len[l][stmt] = label

        return stmts_by_len

    def create_tree(self, label, default_value):
        stmts_by_len = self.create_stmts_by_len(self.stmts)

        self.output += ":%s\n" % label
        self.output += "    set c, %s\n" % (default_value,)
        if len(stmts_by_len) < 3:
            for l in stmts_by_len.keys():
                self.output += "    ife b, %i\n" % (l,)
                self.output += "        set pc, %s_%i\n\n" % (label, l)

        else:
            self.output += "    ifg b, %i\n" % (self.longest_stmt())
            self.output += "        set pc, pop\n\n"
            self.output += "    set pc, [%s_table + b - 1]\n\n" % (label,)

            self.output += ":%s_table\n" % (label,)
            for l in range(1, self.longest_stmt()+1):
                self.output += "    dat %s_%i\n" % (label, l)

            self.output += "\n"

            for l in range(1, self.longest_stmt()+1):
                if l not in stmts_by_len:
                    self.output += ":%s_%i\n" % (label, l)

        self.output += "    set pc, pop\n\n"

        for length, stmts in stmts_by_len.items():
            self.output += "\n:%s_%i\n" % (label, length)
            self.output += self.process("%s_%i_" % (label, length), stmts)

    def write_to_file(self, filename):
        with open(filename, 'w') as f:
            f.write(self.output)

    def get_choices(self, keywords):
        heads, head_keywords = [], {}

        for stmt, label in keywords.items():
            head = stmt[0]
            if head not in head_keywords:
                heads.append(head)
                head_keywords[head] = {}
            head_keywords[head][stmt] = label

        return sorted(heads), head_keywords

    def advance(self, label_prefix, tokens, prefix, use_label=True, depth=0):
        return self.process(label_prefix, {key[1:]: label for key, label in tokens.items()}, prefix, use_label=use_label, depth=depth)

    def process(self, label_prefix, keywords, prefix='', preprefix='', use_label=True, depth=0):
        output = ''

        if use_label and (preprefix or prefix):
            output += "\n:%s%s\n" % (label_prefix, preprefix if preprefix else prefix)

        if '' in keywords:
            output += "%s    set c, %s\n" % (depth * 4 * ' ', keywords[''])
            output += "    set pc, pop\n"
            return output

        heads, head_keywords = self.get_choices(keywords)

        if len(heads) == 0:
            output += "    set pc, pop\n"

        elif len(heads) == 1:
            if len(head_keywords[heads[0]]) == 1:
                output += "%s    ife [a + %i], '%s'\n" % (depth * 4 * ' ', len(prefix), heads[0],)
                output += self.advance(label_prefix, head_keywords[heads[0]], prefix + heads[0], use_label=False, depth=depth + 1)

            else:
                output += "    ifn [a + %i], '%s'\n" % (len(prefix), heads[0],)
                output += "        set pc, pop\n"

                output += self.advance(label_prefix, head_keywords[heads[0]], prefix + heads[0], use_label=False)

        elif len(heads) == 2:
            output += "    ife [a + %i], '%s'\n" % (len(prefix), heads[0],)
            output += "        set pc, %s%s\n" % (label_prefix, prefix + heads[0])
            output += "    ifn [a + %i], '%s'\n" % (len(prefix), heads[1],)
            output += "        set pc, pop\n"

            output += self.advance(label_prefix, head_keywords[heads[1]], prefix + heads[1], use_label=False)

            output += self.advance(label_prefix, head_keywords[heads[0]], prefix + heads[0])

        elif len(heads) == 3:
            output += "    ife [a + %i], '%s'\n" % (len(prefix), heads[0],)
            output += "        set pc, %s%s\n" % (label_prefix, prefix + heads[0])
            output += "    ife [a + %i], '%s'\n" % (len(prefix), heads[1],)
            output += "        set pc, %s%s\n" % (label_prefix, prefix + heads[1])
            output += "    ifn [a + %i], '%s'\n" % (len(prefix), heads[2],)
            output += "        set pc, pop\n"

            output += self.advance(label_prefix, head_keywords[heads[2]], prefix + heads[2], use_label=False)

            output += self.advance(label_prefix, head_keywords[heads[0]], prefix + heads[0])

            output += self.advance(label_prefix, head_keywords[heads[1]], prefix + heads[1])

        else:
            middle = len(heads) // 2
            left = {}
            for key in heads[:middle]:
                for stmt, label in head_keywords[key].items():
                    left[stmt] = label

            right = {}
            for key in heads[middle:]:
                for stmt, label in head_keywords[key].items():
                    right[stmt] = label

            output += "    ifl [a + %i], '%s'\n" % (len(prefix), heads[middle])
            output += "        set pc, %s%s_to_%s\n" % (label_prefix, prefix + heads[0], prefix + heads[middle-1])

            output += self.process(label_prefix, right, prefix, "%s_to_%s" % (prefix + heads[middle], prefix + heads[-1]))

            output += self.process(label_prefix, left, prefix, "%s_to_%s" % (prefix + heads[0], prefix + heads[middle-1]))

        return output


generator = Creator({
    "if": "token_if",
    "or": "token_or",
    "is": "token_is",
    "in": "token_in",
    "and": "token_and",
    "not": "token_not",
    "for": "token_for",
    "cls": "token_cls",
    "del": "token_del",
    "inf": "token_float",
    "nan": "token_float",
    "run": "token_run",
    "try": "token_try",
    "elif": "token_elif",
    "else": "token_else",
    "true": "token_true",
    "none": "token_none",
    "pass": "token_pass",
    "false": "token_false",
    "print": "token_print",
    "while": "token_while",
    "reset": "token_reset",
    "break": "token_break",
    "raise": "token_raise",
    "return": "token_return",
    "except": "token_except",
    "continue": "token_continue",
})

generator.create_tree("stmt", "token_name")
generator.write_to_file("tree_stmt.dasm16")

generator = Creator({
    "id": "built_in_id",
    "rm": "built_in_rm",
    "dir": "built_in_dir",
    "hex": "built_in_hex",
    "hwi": "built_in_hwi",
    "hwn": "built_in_hwn",
    "hwq": "built_in_hwq",
    "mem": "built_in_mem",
    "rnd": "built_in_rnd",
    "int": "built_in_int",
    "str": "built_in_str",
    "len": "built_in_len",
    "abs": "built_in_abs",
    "ord": "built_in_ord",
    "chr": "built_in_chr",
    "cmp": "built_in_cmp",
    "key": "built_in_key",
    "bool": "built_in_bool",
    "call": "built_in_call",
    "getc": "built_in_getchar",
    "plot": "built_in_plot",
    "line": "built_in_line",
    "load": "built_in_load",
    "peek": "built_in_peek",
    "poke": "built_in_poke",
    "show": "built_in_show",
    "read": "built_in_read",
    "repr": "built_in_repr",
    "hsel": "built_in_hsel",
    "save": "built_in_save",
    "sort": "built_in_sort",
    "type": "built_in_type",
    "wget": "built_in_win_get",
    "wset": "built_in_win_set",
    "edit": "built_in_edit",
    "exit": "built_in_exit",
    "range": "built_in_range",
    "float": "built_in_float",
    "point": "built_in_point",
    "input": "built_in_input",
    "write": "built_in_write",
    "hrecv": "built_in_hrecv",
    "hsend": "built_in_hsend",
    "hinfo": "built_in_hinfo",
    "rrecv": "built_in_rrecv",
    "rsend": "built_in_rsend",
    "rinfo": "built_in_rinfo",
    "rconf": "built_in_rconf",
    "hires": "built_in_hires",
    "cursor": "built_in_cursor",
    "format": "built_in_format",
    "locals": "built_in_locals",
    "scroll": "built_in_scroll",
    "circle": "built_in_circle",
    "globals": "built_in_globals",
})

generator.create_tree("glob_func", "led_lparen_user_defined")
generator.write_to_file("tree_gfunc.dasm16")

generator = Creator({
    "append": "built_in__list_append",
    "insert": "built_in__list_insert",
})

generator.create_tree("list_func", "led_lparen_user_defined")
generator.write_to_file("tree_list.dasm16")

generator = Creator({
    "create": "built_in__dict_create",
})

generator.create_tree("dict_func", "led_lparen_user_defined")
generator.write_to_file("tree_dict.dasm16")

generator = Creator({
    "decrypt": "built_in__str_decrypt",
    "encrypt": "built_in__str_encrypt",
    "lower": "built_in__str_lower",
    "upper": "built_in__str_upper",
    "find": "built_in__str_find",
    "replace": "built_in__str_replace",
    "split": "built_in__str_split",
    "endswith": "built_in__str_endswith",
    "startswith": "built_in__str_startswith",
    "isalpha": "built_in__str_isalpha",
    "isdigit": "built_in__str_isdigit",
})

generator.create_tree("str_func", "led_lparen_user_defined")
generator.write_to_file("tree_str.dasm16")

