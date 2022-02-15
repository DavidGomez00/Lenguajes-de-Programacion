# coding: utf-8

from sly import Lexer
import os
import re
import sys

class Comentario(Lexer):
    ''' Clase para interpretar comentarios
    '''

    # Tokens
    tokens = {}
    
    # Función para ignorar
    @_(r'.')
    def PASAR(self, t):
        pass

    # Función para terminar el comentario
    @_(r'\*\)')
    def VOLVER(self, t):
        # Retorna el flujo al CoolLexer
        self.begin(CoolLexer)
pass

class CoolLexer(Lexer):
    ''' Lexer para interpretar el lenguaje COOL
    '''

    # Tipos de tokens
    tokens = {OBJECTID, INT_CONST, BOOL_CONST, TYPEID,
              ELSE, IF, FI, THEN, NOT, IN, CASE, ESAC, CLASS,
              INHERITS, ISVOID, LET, LOOP, NEW, OF,
              POOL, THEN, WHILE, NUMBER, STR_CONST, LE, DARROW, ASSIGN}

    # Caracteres especiales
    ignore = '\t '
    
    # Literales
    literals = {}

    # Definimos las regex para los distintos tokens
    ELSE = r'\b[eE][lL][sS][eE]\b'
    WHILE = r'\b[Ww][Hh][Ii][Ll][Ee]\b'
    INT_CONST = r'\b[0-9]+\b'
    STR_CONST = r'\b".*"\b'
    
    # Definimos las funciones para interpretar los tokens con valor

    # Salto de línea
    @_(r'\n|\r')
    def SALTO(self, t):
        self.lineno += 1

    # Bool True
    @_(r'\bt[Rr][Uu][Ee]\b')
    def BOOL_CONST(self, t):
        t.value = True
        return t
    
    # Bool False
    @_(r'\bf[Aa][Ll][Ss][Ee]\b')
    def BOOL_CONST(self, t):
        t.value = (t.value).lower()
        return t

    # Type Identifiers
    @_(r'\b[A-Z][a-zA-Z0-9_]*\b')
    def TYPEID(self, t):
        t.value = (t.value)
        return t

    # Object Identifiers
    @_(r'[a-z][a-zA-Z0-9_]*')
    def OBJECTID(self, t):
        t.value = (t.value)
        return t

    # Comment
    @_(r'\(\*')
    def COMENTARIO(self, t):
        # Cambia el Lexer a Comentario
        self.begin(Comentario)

    def error(self, t):
        self.index += 1

    

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