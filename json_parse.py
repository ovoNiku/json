from enum import Enum, auto


def get_num(json_str, begin, end):
    numbers = '1234567890'
    while json_str[end] in numbers:
        end += 1
    token = int(json_str[begin: end])
    return end, token


def get_str(json_str, begin, end):
    end += 1
    sym_map = {
        "t": "\t",
        "n": "\n",
        "\\": "\\",
    }
    token = ''
    while True:
        if json_str[end] == '\\':
            token += sym_map[json_str[end]]
            end += 2
        elif json_str[end] == '"':
            break
        else:
            token += json_str[end]
            end += 1
    # while json_str[end] in str:
    #     end += 1
    # token = json_str[begin + 1: end]
    return end, token


def get_bool(json_str, begin, end):
    bools = ['true', 'false', 'null']
    if json_str[begin: begin + 4] in bools:
        token = bool(json_str[begin: begin + 4])
        end += 4
    elif json_str[begin: begin + 5] in bools:
        token = bool(json_str[begin: begin + 5])
        end += 5
    else:
        return False
    return end, token


def json_tokens(json_str):
    token_list = []
    span = ' \n\t\r'
    bools = 'tfn'
    numbers = '1234567890'
    i = 0
    symbol_map = {
        "{": Type.braceLeft,
        "}": Type.braceRight,
        ":": Type.colon,
        ",": Type.comma,
        "[": Type.backetLeft,
        "]": Type.backetRight,
    }
    while i < len(json_str):
        begin = end = i
        n = json_str[i]
        if n in symbol_map:
            token_list.append(Token(n, symbol_map[n]))
        elif n in numbers:
            end, token = get_num(json_str, begin, end)
            token_list.append(Token(token, Type.number))
            i = end - 1
        elif n == '"':
            end, token = get_str(json_str, begin, end)
            token_list.append(Token(token, Type.string))
            i = end
        elif n in bools:
            end, token = get_bool(json_str, begin, end)
            token_list.append(Token(token, Type.token))
            i = end - 1
        elif n in span:
            pass
        else:
            return 'Error'
        i += 1
    return token_list


class Type(Enum):
    braceLeft = auto()  # {
    braceRight = auto()  # }
    comma = auto()  # ,
    colon = auto()  # :
    number = auto()  # 123
    string = auto()  # "hello"
    backetLeft = auto()  # [
    backetRight = auto()  # ]
    token = auto()  # true false null


class TokenList(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def read_token(self):
        self.index += 1
        return self.tokens[self.index - 1]


class Token(object):

    def __init__(self, value, type):
        self.value = value
        self.type = type

    def __repr__(self):
        return "<'{}', {}>".format(self.type, self.value)


def parse(token_list):
    ts = token_list
    t = ts.read_token()
    if t.type == Type.braceLeft:
        obj = {}
        key = ts.read_token()
        while key.type != Type.braceRight:
            colon = ts.read_token()
            assert key.type == Type.string
            assert colon.type == Type.colon
            v = parse(ts)
            obj[key.value] = v
            comma = ts.read_token()
            assert comma.type == Type.comma
            key = ts.read_token()
        return obj
    elif t.type == Type.backetLeft:
        array = []
        while t.type != Type.backetRight:
            t = parse(ts)
            if t == ']':
                break
            array.append(t)
            t = ts.read_token()
        return array
    else:
        return t.value


def json_object(tokens):
    token_list = TokenList(tokens)
    obj = parse(token_list)
    return obj


def test1():
    s = """
    {
        "name": "niku",
        "height": {
            "unit": {
                "name": "cm",
            },
            "value": 163,
        },
    }
    """
    e = {
        "name": "niku",
        "height": {
            "unit": {
                "name": "cm",
            },
            "value": 163,
        }
    }

    ts = json_tokens(s)
    r = json_object(ts)
    assert str(e) == str(r), 'test 1 \nR:{}\nE:{}'.format(r, e)


def test2():
    s = """
    {
        "name": "niku",
        "height": {
            "unit": {
                "name": ["cm\\\\", "km",],
            },
            "value": 163,
            "cool": true,
        },
    }
    """
    e = {
        "name": "niku",
        "height": {
            "unit": {
                "name": ["cm\\", "km"],
            },
            "value": 163,
            "cool": True,
        }
    }
    ts = json_tokens(s)
    r = json_object(ts)
    assert str(e) == str(r), 'test 2 \nR:{}\nE:{}'.format(r, e)


if __name__ == '__main__':
    test1()
    test2()
