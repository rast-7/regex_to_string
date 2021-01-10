import random
import string
import types

sr = random.SystemRandom()
randint = sr.randint
choice = sr.choice
sample = sr.sample
shuffle = sr.shuffle

class StringGenerator(object):
    """Generate a randomized string of characters using a template.
    The purpose of this class is to generate a string of characters
    according to a template.
    """

    class SyntaxError(Exception):
        """Catch syntax errors."""
        pass

    class UniquenessError(Exception):
        """Catch when template can't generate required list count."""
        pass

    meta_chars = "[]{}()|"

    allowed_chars = set(string.digits + string.ascii_lowercase + \
                    string.ascii_uppercase + string.whitespace + string.punctuation)


    class Node(object):
        """The abstract class for all nodes"""

        def render(self, **kwargs):
            raise Exception("abstract class")

    class Sequence:
        """Render a sequence of nodes from the template."""

        def __init__(self, seq):
            """seq is a list."""
            self.seq = seq  # list of Nodes

        def render(self, **kwargs):
            return "".join([x.render(**kwargs) for x in self.seq])

    class OR(Sequence):
        """Randomly choose from operands."""

        def render(self, **kwargs):
            # return just one of the items in self.seq
            return self.seq[randint(0, len(self.seq) - 1)].render(**kwargs)

    class Literal(Node):
        """Render a literal string."""

        def __init__(self, chars):
            self.literal = chars  # a literal string

        def render(self, **kwargs):
            return self.literal

        def __str__(self):
            return self.literal

    class CharacterSet(Node):
        """Render a random combination from a set of characters."""

        def __init__(self, chars, start, cnt):
            self.chars = chars
            try:
                self.start = int(start)
                self.cnt = int(cnt)
            except Exception as e:
                raise e

        def render(self, **kwargs):
            cnt = 1
            if self.start > -1:
                cnt = randint(self.start, self.cnt)
            else:
                cnt = self.cnt
            return "".join(
                self.chars[randint(0, len(self.chars) - 1)] for x in range(cnt)
            )

        def __str__(self):
            return "%s:%s:%s" % (self.start, self.cnt, self.chars)

    def __init__(self, pattern, uaf=10):
        try:
            self.pattern = pattern
        except NameError:
            self.pattern = pattern
        self.seq = None
        self.index = -1
        self.unique_attempts_factor = uaf
        self.sets_in_seq = 0
        # breakpoint()
        self.seq = self.getSequence()
        print(self.seq.render())

    def current(self):
        if self.index < len(self.pattern):
            return self.pattern[self.index]
        return None

    def peek(self):
        """Just an alias."""
        return self.current()

    def next(self):
        self.index += 1
        return self.current()

    def lookahead(self):
        if self.index + 1 < len(self.pattern):
            return self.pattern[self.index + 1]
        return None

    def last(self):
        if self.index == 0:
            return None
        return self.pattern[self.index - 1]

    def getQuantifier(self):
        start = -1
        bracket = self.next()
        # we should only be here because that was a bracket
        if not bracket == "{":
            raise Exception("parse error getting quantifier")
        d = ""
        digits = "0"
        while True:
            d = self.next()
            if not d:
                raise Exception("unexpected end of input getting quantifier")
            if d == "-" or d == ",":
                start = int(digits)
                digits = "0"
                continue
            if d == "}":
                if self.last() in ",-":
                    # this happens if the user thinks the quantifier
                    # behaves like python slice notation in allowing uppper range to be open
                    raise StringGenerator.SyntaxError("quantifier range must be closed")
                break
            if d.isnumeric():
                digits += d
            else:
                raise StringGenerator.SyntaxError("non-digit in count")
        return [start, int(digits)]

    def getCharacterRange(self, f, t):
        chars = ""
        # support z-a as a range
        if not ord(f) < ord(t):
            tmp = f
            f = t
            t = tmp
        if (ord(t) - ord(f)) > 10000:  # protect against large sets ?
            raise Exception(
                "character range too large: %s - %s: %s" % (f, t, ord(t) - ord(f))
            )
        for c in range(ord(f), ord(t) + 1):
            chars += chr(c)
        return chars

    def getCharacterSet(self):
        """Get a character set with individual members or ranges.

        Current index is on '[', the start of the character set.

        """
        # import ipdb; ipdb.set_trace()
        chars = ""
        c = None
        cnt = 1
        start = 0

        negate = False
        if self.lookahead() == "^":
            negate = True

        while True:
            c = self.next()
            if self.lookahead() == "-":
                f = c
                self.next()  # skip hyphen
                c = self.next()  # get far range
                if not c or (c in self.meta_chars):
                    raise StringGenerator.SyntaxError("unexpected end of class range")
                chars += self.getCharacterRange(f, c)
            elif c and c not in self.meta_chars:
                chars += c
            if c == "]":
                if self.lookahead() == "{":
                    [start, cnt] = self.getQuantifier()
                elif self.lookahead() == "?":
                    start = 0
                    cnt = 1
                    self.next() #skip the ?
                elif self.lookahead() == "*":
                    start = 0
                    cnt = randint(0, len(self.pattern))
                    self.next() #skip the *
                elif self.lookahead() == "+":
                    start = 1
                    cnt = randint(1, len(self.pattern))
                    self.next() # skip the +
                else:
                    start = -1
                    cnt = 1
                break

            if c and c in self.meta_chars:
                raise StringGenerator.SyntaxError(
                    "Un-escaped character in class definition: %s" % c
                )
            if not c:
                break

        if negate:
            chars_to_use = self.allowed_chars - set(chars)
            chars = ''.join(str(char) for char in chars_to_use)

        return StringGenerator.CharacterSet(chars, start, cnt)

    def getLiteral(self):
        """Get a sequence of non-special characters."""
        # we are on the first non-special character

        chars = ""
        c = self.current()
        while True:
            if not c or (c in self.meta_chars):
                break
            else:
                if self.lookahead() == "?":
                    repeat = randint(0, 1)
                    chars += (c * repeat)
                    c = self.next()
                elif self.lookahead() == "*":
                    upper_limit = randint(0, len(self.pattern))
                    repeat = randint(0, upper_limit)
                    chars += (c * repeat)
                    c = self.next()
                elif self.lookahead() == "+":
                    upper_limit = randint(1, len(self.pattern))
                    repeat = randint(1, upper_limit)
                    chars += (c * repeat)
                    c = self.next()
                else:
                    chars += c
            if self.lookahead() and self.lookahead() in self.meta_chars:
                break
            c = self.next()
        return StringGenerator.Literal(chars)

    def getSequence(self, level=0):
        """Get a sequence of nodes."""

        seq = []
        op = ""
        left_operand = None
        right_operand = None
        sequence_closed = False
        while True:
            c = self.next()
            if not c:
                break
            if c and c not in self.meta_chars:
                seq.append(self.getLiteral())
                self.sets_in_seq += 1
            elif c == "[":
                seq.append(self.getCharacterSet())
                print(seq[-1].render())
                if level:
                    self.sets_in_seq += 1
            elif c == "(":
                seq.append(self.getSequence(level + 1))
            elif c == ")":
                # end of this sequence
                if level == 0:
                    # there should be no parens here
                    raise StringGenerator.SyntaxError("Extra closing parenthesis")
                elif self.lookahead() == "{":
                    [start, cnt] = self.getQuantifier()
                    if start > -1:
                        times = randint(start, cnt)
                    else:
                        times = cnt - 1
                    print(f"{start}, {cnt}")
                    print(f"times = {times}")
                    repeat = len(seq) - self.sets_in_seq
                    elements_to_repeat = seq[repeat: len(seq)]
                    for time in range(times):
                        for element in elements_to_repeat:
                            seq.append(element)
                    self.set_in_seq = 0
                sequence_closed = True
                break
            elif c == "|":
                op = c
            else:
                if c in self.meta_chars:
                    print(c)
                    raise StringGenerator.SyntaxError(
                        "Un-escaped special character: %s" % c
                    )

            if op and not left_operand:
                if not seq or len(seq) < 1:
                    raise StringGenerator.SyntaxError(
                        "Operator: %s with no left operand" % op
                    )
                left_operand = seq.pop()
            elif op and len(seq) >= 1 and left_operand:
                right_operand = seq.pop()

                if op == "|":
                    seq.append(
                        StringGenerator.OR([left_operand, right_operand])
                    )
                op = ""
                left_operand = None
                right_operand = None

        # check for syntax errors
        if op:
            raise StringGenerator.SyntaxError("Operator: %s with no right operand" % op)
        if level > 0 and not sequence_closed:
            # it means we are finishing a non-first-level sequence without closing parens
            raise StringGenerator.SyntaxError("Missing closing parenthesis")

        return StringGenerator.Sequence(seq)

    def render(self, **kwargs):
        """Produce a randomized string that fits the template/pattern.

        Args:
            None

        Returns:
            The generated string.

        """
        return self.seq.render(**kwargs)

    def render_list(self, cnt, unique=False, **kwargs):
        """Return a list of generated strings.

        Args:
            cnt (int): length of list
            unique (bool): whether to make entries unique

        Returns:
            list.

        We keep track of total attempts because a template may
        specify something impossible to attain, like [1-9]{} with cnt==1000

        """

        rendered_list = []
        i = 0
        total_attempts = 0
        while True:
            if i >= cnt:
                break
            if total_attempts > cnt * self.unique_attempts_factor:
                raise StringGenerator.UniquenessError("couldn't satisfy uniqueness")
            s = self.render(**kwargs)
            if unique:
                if s not in rendered_list:
                    rendered_list.append(s)
                    i += 1
            else:
                rendered_list.append(s)
                i += 1
            total_attempts += 1

        return rendered_list


print(StringGenerator('(1[0-2]|0[1-9])(:[0-5][0-9]){2} (A|P)M', 10).render())
