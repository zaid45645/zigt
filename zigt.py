
DIGITS = '0123456789'

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOL = "EOL"

class error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details 

    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        result += f'\nfile {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        return result
    
class illegal_char_error(error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'illegal charcater', details)

class invalid_syntax_error(error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'invalid syntax', details)

class rt_error(error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Runtime Error', details)

class position:
    def __init__(self, idx, ln, col, fn, ftext):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftext = ftext
    
    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == "\n":
            self.ln += 1
            self.col = 0
        
        return self
    
    def copy(self):
        return position(self.idx, self.ln, self.col, self.fn, self.ftext)

        

class token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end.copy()
    
    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'
    
class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
    
    def make_tokens(self):
        tokens = []
        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_numbers())
            elif self.current_char == "+":
                tokens.append(token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == "-":
                tokens.append(token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], illegal_char_error(pos_start, self.pos, "'" + char + "'")
        tokens.append(token(TT_EOL, pos_start=self.pos))
        return tokens, None

    def make_numbers(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()
        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return token(TT_FLOAT, float(num_str), pos_start, self.pos)
        

class number_node:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end
    
    def __repr__(self):
        return f'{self.tok}'

class bin0p_node:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class unary0p_node:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end
    def __repr__(self):
        return f'({self.op_tok}, {self.node})'
    

class parser_result:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, result):
        if isinstance(result, parser_result):
            if result.error:
                self.error = result.error
            return result.node
        return result
        
    def success(self, node):
        self.node = node
        return self
    
    def failure(self, error):
        self.error = error
        return self
    

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.current_tok = None
        self.advance()
    
    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok
    
    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TT_EOL:
            return res.failure(invalid_syntax_error(self.current_tok.pos_start, self.current_tok.pos_end, "expected +, -, * or /"))
        return res
    
    def factor(self):
        res = parser_result()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(unary0p_node(tok, factor))

        elif tok.type in (TT_INT, TT_FLOAT):
            res.register(self.advance())
            return res.success(number_node(tok))
        
        elif tok.type == TT_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_tok.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(invalid_syntax_error(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')'"
                ))
        
        return res.failure(invalid_syntax_error(
            tok.pos_start, tok.pos_end,
            "expected int or float"
        ))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))
    
    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def bin_op(self, func, ops):
        res = parser_result()
        left = res.register(func())
        if res.error:
            return res
        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error:
                return res
            left = bin0p_node(left, op_tok, right)

        return res.success(left)
    

class Number:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value) 
    
    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value) 
        
    def multi_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value)
         
    def divided_by(self, other):
        if isinstance(other, Number):
            return Number(self.value / other.value) 
        
    

class Interpreter():
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)
    
    def no_visit_method(self, node):
        raise Exception(f'No visit_{type(node).__name__} method defined')
    

    def visit_number_node(self, node):
        return Number(node.tok.value).set_pos(node.pos_start, node.pos_end)

    def visit_bin0p_node(self, node):
        left =  self.visit(node.left_node)
        right = self.visit(node.right_node)

        if node.op_tok.type == TT_PLUS:
            result = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result = left.subbed_by(right)
        elif node.op_tok.type == TT_MUL:
            result = left.multi_by(right) 
        elif node.op_tok.type == TT_DIV:
            result = left.divided_by(right)   

        return result.set_pos(node.pos_start, node.pos_end)

        
    
    def visit_unary0p_node(self, node):
        number = self.visit(node.node)
        if node.op_tok.type == TT_MINUS:
            number = number.multi_by(Number(-1))

        return number.set_pos(node.pos_start, node.pos_end)




def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error

    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error

    interpreter = Interpreter()
    result = interpreter.visit(ast.node)

    return result, None

