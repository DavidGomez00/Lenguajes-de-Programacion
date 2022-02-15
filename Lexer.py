# coding: utf-8

from sly import Lexer
import os
import re
import sys





class CoolLexer(Lexer):
    tokens = {OBJECTID, INT_CONST, BOOL_CONST, TYPEID,
              ELSE, IF, FI, THEN, NOT, IN, CASE, ESAC, CLASS,
              INHERITS, ISVOID, LET, LOOP, NEW, OF,
              POOL, THEN, WHILE, NUMBER, STR_CONST, LE, DARROW, ASSIGN}
    ignore = '\t '
    literals = {}
    # Ejemplo
    ELSE = r'\b[eE][lL][sS][eE]\b'
    WHILE = r'\b[Ww][Hh][Ii][Ll][Ee]\b'
    INT_CONST = r'\b[0-9]+\b'

    @_(r'\bt[Rr][Uu][Ee]\b')
    def BOOL_CONST(self, t):
        t.value = (t.value).lower()
        return t
    
    @_(r'\bf[Aa][Ll][Ss][Ee]\b')
    def BOOL_CONST(self, t):
        t.value = (t.value).lower()
        return t

    @_(r'\b[A-Z]+\b')
    def TYPEID(self, t):
        t.value = (t.value)
        return t

    CARACTERES_CONTROL = [bytes.fromhex(i+hex(j)[-1]).decode('ascii')
                          for i in ['0', '1']
                          for j in range(16)] + [bytes.fromhex(hex(127)[-2:]).decode("ascii")]

    def salida(self, texto):
        lexer = CoolLexer()
        list_strings = []
        for token in lexer.tokenize(texto):
            result = f'#{token.lineno} {token.type} '
            if token.type == 'OBJECTID':
                result += f"{token.value}"
            elif token.type == 'BOOL_CONST':
                result += "true" if token.value else "false"
            elif token.type == 'TYPEID':
                result += f"{str(token.value)}"
            elif token.type in self.literals:
                result = f'#{token.lineno} \'{token.type}\' '
            elif token.type == 'STR_CONST':
                result += token.value
            elif token.type == 'INT_CONST':
                result += str(token.value)
            elif token.type == 'ERROR':
                result = f'#{token.lineno} {token.type} {token.value}'
            else:
                result = f'#{token.lineno} {token.type}'
            
            list_strings.append(result)
        return list_strings