import sys
# Explicitly use ../ply from git submodule path
sys.path.insert(1,'../ply')
import ply.lex as plex

class MyLexer:
    tokens = (
        'NUMBER',
        'PLUS',
        'MINUS',
        'TIMES',
        'DIVIDE',
        'LPAREN',
        'RPAREN',
    )

    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'

    def t_NUMBER(self,t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_newline(self,t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    t_ignore = ' \t'

    def t_error(self,t):
        print "Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)

    def build(self,**kwargs):
        self.lexer = plex.lex(module=self, **kwargs)

    def test(self,data):
        self.lexer.input(data)
        while True:
            tok = plex.token()
            if not tok: break
            print tok


if __name__ == '__main__':
    print 'sys.path = ',sys.path
    m = MyLexer()
    m.build()
    m.test("3 + 4")


