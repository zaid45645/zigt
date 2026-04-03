
DIGITS = '0123456789'

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'

class error:
    def __init__(self, error_name, details):
        self.error_name = error_name
        self.details = details 

    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        return result
    
class illegal_char_error(error):
    def __init__(self, details):
        super().__init__('illegal charcater', details)

class position:
    def __init__(self, idx, ln, coln):
        self.idx = idx
        self.ln = ln
        self.coln = coln
    
    def advance(self, current_char):
        self.idx += 1
        self.col += 1

        if current_char == "\n":
            self.ln += 1
            self.col = 0

        

class token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
    
    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'
    
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = -1
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
    
    def make_tokens(self):
        tokens = []
        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_numbers())
            elif self.current_char == "+":
                tokens.append(token(TT_PLUS))
                self.advance()
            elif self.current_char == "-":
                tokens.append(token(TT_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(token(TT_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(token(TT_DIV))
                self.advance()
            elif self.current_char == '(':
                tokens.append(token(TT_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(token(TT_RPAREN))
                self.advance()
            else:
                char = self.current_char
                self.advance()
                return [], illegal_char_error("'" + char + "'")
            
        return tokens, None

    def make_numbers(self):
        num_str = ''
        dot_count = 0
        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return token(TT_INT, int(num_str))
        else:
            return token(TT_FLOAT, float(num_str))
        

def run(text):
    lexer = Lexer(text)
    tokens, error = lexer.make_tokens()
    return tokens, error