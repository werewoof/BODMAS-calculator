#TOKENS

T_NEWLINE = 0
T_PLUS = 1
T_MINUS = 2
T_STAR = 3
T_SLASH = 4
T_INTLIT = 5
T_DSTAR = 6
T_BSLASH = 7
T_PERCENT = 8

#IDENTIIERS

A_ADD = 0
A_SUBTRACT = 1
A_MULTIPLY = 2
A_DIVIDE = 3
A_INTLIT = 4
A_POWER = 5
A_ROOT = 6
A_MOD = 7

#ORDER HIGHER NUMBER = HIGHER PRIORITY

OpPrec = {
    T_NEWLINE : 0,
    T_PLUS : 10,
    T_MINUS : 10,
    T_STAR : 20,
    T_SLASH : 20,
    T_PERCENT : 20,
    T_INTLIT : 0,
    T_DSTAR : 30,
    T_BSLASH : 30
}

INDEX = -1 #GLOBAL INDEX THING
_text : str = ""

class CalculatorException(Exception):
    pass

class token:
    token = 0
    intvalue = 0

da_token : token = None

class ASTnode:
    op = 0
    left = None
    right = None
    intvalue = 0

def reset():
    global INDEX
    INDEX = -1

def next():
    global INDEX
    INDEX += 1
    return _text[INDEX]

def back():
    global INDEX
    INDEX -= 1
    return _text[INDEX]

def putback():
    c = back()
    while c == ' ' or c == '\t' or c == '\r' or c == '\f':
        c = back()

def skip() -> str:
    c = next()
    while c == ' ' or c == '\t' or c == '\r' or c == '\f':
        c = next()
    return c

def scanint(c : str) -> int:
    val = 0
    while c.isdigit():
        k = int(c)
        val = val * 10 + k
        c = next()
    putback()
    return val


def scan(t : token) -> bool:
    c = skip()
    match c:
        case '\n':
            t.token = T_NEWLINE
            return False
        case '+':
            t.token = T_PLUS
        case '-':
            t.token = T_MINUS
        case '*':
            if skip() == '*':
                t.token = T_DSTAR
            else:
                putback()
                t.token = T_STAR
        case '\\':
            t.token = T_BSLASH
        case '/':
            t.token = T_SLASH
        case '%':
            t.token = T_PERCENT
        case _:
            if c.isdigit():
                t.intvalue = scanint(c)
                t.token = T_INTLIT
                return True
            raise CalculatorException(f"Unrecognised symbol: {c}")
    return True

def makeASTnode(op: int, left: ASTnode, right: ASTnode, intvalue : int) -> ASTnode:
    n = ASTnode()
    n.op = op
    n.left = left
    n.right = right
    n.intvalue = intvalue
    return n

def makeASTleaf(op: int, intvalue: int) -> ASTnode:
    return makeASTnode(op, None, None, intvalue)

def arithop(tokentype: int) -> int:
    if tokentype == T_PLUS:
        return A_ADD
    elif tokentype == T_MINUS:
        return A_SUBTRACT
    elif tokentype == T_STAR:
        return A_MULTIPLY
    elif tokentype == T_SLASH:
        return A_DIVIDE
    elif tokentype == T_DSTAR:
        return A_POWER
    elif tokentype == T_BSLASH:
        return A_ROOT
    elif tokentype == T_PERCENT:
        return A_MOD
    else:
        raise CalculatorException(f"Unknown token in arithop(): {tokentype}")


def primary() -> ASTnode:
    n = ASTnode()
    if da_token.token == T_INTLIT:
        n = makeASTleaf(A_INTLIT, da_token.intvalue)
        scan(da_token)
        return n
    else:
        raise CalculatorException(f"Syntax error: token, {da_token.token}")

def op_precedence(tokentype : int) -> int:
    prec = OpPrec[tokentype]
    if prec == 0:
        raise CalculatorException(f"Syntax error on token, {tokentype}")
    return prec

def createAST(ptp : int):
    left = primary()
    tokentype = da_token.token
    if tokentype == T_NEWLINE:
        return left
    
    while op_precedence(tokentype) > ptp:
        scan(da_token)
        right = createAST(OpPrec[tokentype])
        left = makeASTnode(arithop(tokentype), left, right, 0)
        tokentype = da_token.token
        if tokentype == T_NEWLINE:
            return left
    return left

def interpretAST(n : ASTnode) -> int:
    if n.left:
        leftval = interpretAST(n.left)
    if n.right:
        rightval = interpretAST(n.right)
    
    if n.op == A_ADD:
        return leftval + rightval
    elif n.op == A_SUBTRACT:
        return leftval - rightval
    elif n.op == A_MULTIPLY:
        return leftval * rightval
    elif n.op == A_DIVIDE:
        return leftval / rightval
    elif n.op == A_POWER:
        return leftval ** rightval
    elif n.op == A_ROOT:
        if rightval == 0:
            raise CalculatorException(f"Power of zero doesnt work")
        return leftval ** (1/rightval)
    elif n.op == A_MOD:
        return leftval % rightval
    elif n.op == A_INTLIT:
        return n.intvalue
    else:
        raise CalculatorException(f"Unknown AST operator {n.op}")

if __name__ == "__main__":
    print("calculator")
    while True:
        _text = input(">>> ")
        _text += "\n"
        try:
            da_token = token()
            scan(da_token)
            tree = createAST(0)
            ans = interpretAST(tree)
            print(ans)
        except Exception as err:
            print(err)
        reset()