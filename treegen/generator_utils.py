def get_choices(keywords):
    heads, head_keywords = [], {}

    for stmt, label in keywords.items():
        head = stmt[0]
        if head not in head_keywords:
            heads.append(head)
            head_keywords[head] = {}
        head_keywords[head][stmt] = label

    return sorted(heads), head_keywords


def advance(label_prefix, tokens, prefix, use_label=True, depth=0):
    process(label_prefix, {key[1:]: label for key, label in tokens.items()}, prefix, use_label=use_label, depth=depth)


def process(label_prefix, keywords, prefix='', preprefix='', use_label=True, depth=0):
    if use_label and (preprefix or prefix):
        print
        print ":%s%s%s" % (label_prefix, preprefix, prefix)

    if '' in keywords:
        print "%s    set x, %s" % (depth * 4 * ' ', keywords[''])
        print "    set pc, pop"
        return

    heads, head_keywords = get_choices(keywords)

    if len(heads) == 0:
        print "    set pc, pop"

    elif len(heads) == 1:
        if len(head_keywords[heads[0]]) == 1:
            print "%s    ife [i + %i], '%s'" % (depth * 4 * ' ', len(prefix), heads[0],)
            advance(label_prefix, head_keywords[heads[0]], prefix + heads[0], use_label=False, depth=depth + 1)

        else:
            print "    ifn [i + %i], '%s'" % (len(prefix), heads[0],)
            print "        set pc, pop"

            advance(label_prefix, head_keywords[heads[0]], prefix + heads[0], use_label=False)

    elif len(heads) == 2:
        print "    ife [i + %i], '%s'" % (len(prefix), heads[0],)
        print "        set pc, %s%s" % (label_prefix, prefix + heads[0])
        print "    ifn [i + %i], '%s'" % (len(prefix), heads[1],)
        print "        set pc, pop"

        advance(label_prefix, head_keywords[heads[1]], prefix + heads[1], use_label=False)

        advance(label_prefix, head_keywords[heads[0]], prefix + heads[0])

    elif len(heads) == 3:
        print "    ife [i + %i], '%s'" % (len(prefix), heads[0],)
        print "        set pc, %s%s" % (label_prefix, prefix + heads[0])
        print "    ife [i + %i], '%s'" % (len(prefix), heads[1],)
        print "        set pc, %s%s" % (label_prefix, prefix + heads[1])
        print "    ifn [i + %i], '%s'" % (len(prefix), heads[2],)
        print "        set pc, pop"

        advance(label_prefix, head_keywords[heads[2]], prefix + heads[2], use_label=False)

        advance(label_prefix, head_keywords[heads[0]], prefix + heads[0])

        advance(label_prefix, head_keywords[heads[1]], prefix + heads[1])

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

        print "    ifl [i + %i], '%s'" % (len(prefix), heads[middle],)
        print "        set pc, %s%s_to_%s" % (label_prefix, prefix + heads[0], prefix + heads[middle-1])

        process(label_prefix, right, prefix, "%s_to_%s" % (prefix + heads[middle], prefix + heads[-1]))

        process(label_prefix, left, prefix, "%s_to_%s" % (prefix + heads[0], prefix + heads[middle-1]))

