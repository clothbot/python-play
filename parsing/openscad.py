# Python PLY based OpenSCAD parser experiment
import sys
import os
import re
sys.path.insert(1,'../ply')
#import ply.lex as plex
#import ply.yacc as pyacc
import ply

class OpenSCADLexer(object):
    """ OpenSCAD Lexical Analyzer """
    def __init__(self, error_func):
        self.filename = ''
        self.error_func = error_func
        self.directives = []
    
    def build(self, **kwargs):
        self.lexer = ply.lex.lex(object=self, **kwargs)
    def input(self, data):
        self.lexer.input(data)

    def reset_lineno(self):
        self.lexer.lineno = 1

    def get_directives(self):
        return tuples(self.directives)

    def token(self):
        return self.lexer.token()

    keywords = (
        'MODULE','FUNCTION','IMPORT','USE',
        'UNION','DIFFERENCE','INTERSECTION',
        'HULL','MINKOWSKI',
        'ROTATE','TRANSLATE','MIRROR','MULTMATRIX',
        'IF','ELSE','LET','FOR','EACH',
        'POW','LEN',
        'CUBE','SPHERE','CYLINDER','POLYHEDRON','SURFACE',
        'SQUARE','CIRCLE','POLYGON',
        'CHILDREN','RENDER',
        'TRUE','FALSE','UNDEF',
    )

    reserved = {}
    for keyword in keywords:
        reserved[keyword.lower()] = keyword

    operators = (
        'PLUS','MINUS','POWER','TIMES','DIVIDE','MOD',
        'NOT','OR','AND',
        'LOR','LAND','LNOT',
        'LT','GT','LE','GE','EQ','NE','EQL','NEL',
        'COND',
        'EQUALS',
        )

    tokens = keywords + operators + (
        'ID',
        'COMMA','COLON','SEMICOLON','DOT',
        'FLOATNUMBER','STRING_LITERAL',
        'INTNUMBER_DEC','SIGNED_INTNUMBER_DEC',
        'INTNUMBER_HEX','SIGNED_INTNUMBER_HEX',
        'INTNUMBER_OCT','SIGNED_INTNUMBER_OCT',
        'INTNUMBER_BIN','SIGNED_INTNUMBER_BIN',
        'LPAREN','RPAREN',
        'LBRACKET','RBRACKET',
        'LBRACE','RBRACE',
        'HASH',
        'DOLLAR',
        )

    skipped = (
        'COMMENTOUT','LINECOMMENT',
        )

    # Ignore
    t_ignore = ' \t'

    # Comment
    linecomment = r"""//.*?\n"""
    commentout = r"""/\*(.|\n)*?\*/"""

    @TOKEN(linecomment)
    def t_LINECOMMENT(self,t):
        t.lexer.lineno += t.value.count("\n")
        pass

    @TOKEN(commentout)
    def t_COMMENTOUT(self,t):
        t.lexer.lineno += t.value.count("\n")
        pass

    # Operator
    t_LOR = r'\|\|'
    t_LAND = r'\&\&'
    t_LNOT = r'!'

    t_EQ = r'=='
    t_NE = r'!='

    t_LE = r'<='
    t_GE = r'>='
    t_LT = r'<'
    t_GT = r'>'

    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_MOD = r'%'

    t_COND = r'\?'
    t_EQUALS = r'='

    t_COMMA = r','
    t_SEMICOLON = r';'
    t_COLON = r':'
    t_DOT = r'\.'

    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'

    t_HASH = r'\#'
    t_DOLLAR = r'\$'

    bin_number = '[0-9]*\'[bB][0-1xXzZ?][0-1xXzZ?_]*'
    signed_bin_number = '[0-9]*\'[sS][bB][0-1xZzZ?][0-1xXzZ?_]*'
    octal_number = '[0-9]*\'[oO][0-7xXzZ?][0-7xXzZ?_]*'
    signed_octal_number = '[0-9]*\'[sS][oO][0-7xXzZ?][0-7xXzZ?_]*'
    hex_number = '[0-9]*\'[hH][0-9a-fA-FxXzZ?][0-9a-fA-FxXzZ?_]*'
    signed_hex_number = '[0-9]*\'[sS][hH][0-9a-fA-FxXzZ?][0-9a-fA-FxXzZ?_]*'

    decimal_number = '([0-9]*\'[dD][0-9xXzZ?][0-9xXzZ?_]*)|([0-9][0-9_]*)'
    signed_decimal_number = '[0-9]*\'[sS][dD][0-9xXzZ?][0-9xXzZ?_]*'

    exponent_part = r"""([eE][-+]?[0-9]+)"""
    fractional_constant = r"""([0-9]*\.[0-9]+)|([0-9]+\.)"""
    float_number = '(((('+fractional_constant+')'+exponent_part+'?)|([0-9]+'+exponent_part+')))'

    simple_escape = r"""([a-zA-Z\\?'"])"""
    octal_escape = r"""([0-7]{1,3})"""
    hex_escape = r"""(x[0-9a-fA-F]+)"""
    escape_sequence = r"""(\\("""+simple_escape+'|'+octal_escape+'|'+hex_escape+'))'
    string_char = r"""([^"\\\n]|"""+escape_sequence+')'
    string_literal = '"'+string_char+'*"'

    identifier = r"""(([a-zA-Z_])([a-zA-Z_0-9$])*)|((\\\S)(\S)*)"""

    @TOKEN(string_literal)
    def t_STRING_LITERAL(self, t):
        return t

    @TOKEN(float_number)
    def t_FLOATNUMBER(self, t):
        return t

    # add more stuff here

    @TOKEN(identifier)
    def t_ID(self, t):
        t.type = self.reserved.get(t.value, 'ID')
        return t

    def t_NEWLINE(self, t):
        r'\n+'



