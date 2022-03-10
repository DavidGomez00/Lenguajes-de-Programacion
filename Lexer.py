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

    cuenta = 1

    # Otro comentario
    @_(r'[^\\]\(\*')
    def COMENTARIO_ANIDADO(self, t):
      self.cuenta += 1

    # Función para terminar el comentario
    @_(r'[^\\]\*\)')
    def VOLVER(self, t):
        self.cuenta -= 1
        if (self.cuenta == 0):
          self.cuenta = 1
          # Retorna el flujo al CoolLexer
          self.begin(CoolLexer)

    # Función para ignorar
    @_(r'.')
    def PASAR(self, t):
        pass
    
    # Salto de línea
    @_(r'\n')
    def SALTO(self, t):
        self.lineno += 1





class ComentarioSingular(Lexer):
    ''' Clase para interpretar comentarios
    '''

    # Tokens
    tokens = {}
    
    # Función para ignorar
    @_(r'.')
    def PASAR(self, t):
        pass

    # Función para ignorar
    @_(r'(.+|["]+)')
    def PASAR(self, t):
        pass

    @_(r'\n')
    def VOLVER(self, t):
        # Retorna el flujo al CoolLexer
        self.lineno += 1
        self.begin(CoolLexer)




class StringLexer(Lexer):
    ''' Lexer para interpretar Strings.
    '''
    _string = ""
  
    tokens = {STR_CONST, ERROR}
    
    
    @_(r'\\\n$')
    def ERRORT(self, t):
      print('Error detectado')
      t.value = '"' + "EOF in string constant" + '"'
      t.type = 'ERROR'
      self._string = ""
      self.begin(CoolLexer)
      return t
    

      
    @_(r'\\\t')
    def TABULACION(self, t):
      # Tabulación
      self._string += "\\t"

    @_(r'\\\n')
    def SALTO(self, t):
      # Salto de linea
      # print("salto")
      self._string += "\\n"
      self.lineno += 1

    @_(r'\\[nbft"]')
    def BARRAENE(self, t):
      # Literal '\n'
      self._string += "\\" + t.value[1:]

    @_(r'\\\\')
    def BARRABARRA(self, t):
      # Dos \\ seguidas
      self._string += "\\\\"
    
    @_(r'\\[^\\]')
    def BACKLASH(self, t):
      self._string += t.value[1:]

    @_(r'"')
    def STR_CONST(self, t):
      # Retornamos el String
      t.value = '"' + self._string + '"'
      self._string = ""
      # Usamos al lexer de COOL
      self.begin(CoolLexer)
      return t

    @_(r'\n')
    def ERROR(self, t):
      t.value = '"' + "Unterminated string constant" + '"'
      self._string = ""
      # Return to Cool Lexer
      self.begin(CoolLexer)
      return t

    '''
        @_(r'.$')
    def ERROREOF(self, t):
      t.value = '"' + "EOF in string constant" + '"'
      self._string = ""
      # Return to Cool Lexer
      self.begin(CoolLexer)
      return t
    
    '''

  
    

    
        
    @_(r'[^"\\]')
    def ACUMULA(self, t):
      # La coincidencia es parte del String
      self._string += t.value
    

class CoolLexer(Lexer):
    ''' Lexer para interpretar el lenguaje COOL
    '''

    # Tipos de tokens
    tokens = {OBJECTID, INT_CONST, BOOL_CONST, TYPEID,
              ELSE, IF, FI, THEN, NOT, IN, CASE, ESAC, CLASS,
              INHERITS, ISVOID, LET, LOOP, NEW, OF,
              POOL, THEN, WHILE, STR_CONST, LE, DARROW, ASSIGN, ERROR}

    # Caracteres especiales
    ignore = '\t '

    # Definimos las regex para los distintos tokens
    ELSE = r'\b[eE][lL][sS][eE]\b'
    WHILE = r'\b[Ww][Hh][Ii][Ll][Ee]\b'
    INT_CONST = r'[0-9]+'
    THEN = r'\b[Tt][Hh][Ee][Nn]\b'
    POOL = r'\b[Pp][Oo][Oo][Ll]\b'    
    IF = r'\b[Ii][Ff]\b'
    FI = r'\b[Ff][Ii]\b'
    NOT = r'\b[Nn][Oo][Tt]\b'
    IN = r'\b[Ii][Nn]\b'
    CASE = r'\b[Cc][Aa][Ss][Ee]\b'
    ESAC = r'[Ee][Ss][Aa][Cc]'
    CLASS = r'\b[Cc][Ll][Aa][Ss][Ss]\b'
    DARROW = r'=>'
    LE = r'<='
    INHERITS = r'\b[iI][nN][hH][eE][rR][iI][tT][sS]\b'
    ISVOID = r'\b[iI][sS][vV][oO][iI][dD]\b'
    LET = r'\b[lL][eE][tT]\b'
    LOOP = r'\b[lL][oO][oO][pP]\b'
    NEW = r'\b[nN][eE][wW]\b'
    OF = r'\b[oO][fF]\b'
    ASSIGN = r'<-'

    # Literales
    literals = {';', ':', '{', '}', '(', ')', '~',
               '.', ',', '+', '/', '=', '@', '<', '>', '-', '*'}

    # Definimos las funciones para interpretar los tokens con valor

    # Salto de línea
    @_(r'\n')
    def SALTO(self, t):
        self.lineno += 1

    # Comentario de una sola línea
    @_(r'--')
    def COMENTARIO2(self, t):
        # Cambia el Lexer a Comentario
        self.begin(ComentarioSingular)

    @_(r'"')
    def STRING(self, t):
      # Analizamos lo siguiente con el lexer de Strings.
      self.begin(StringLexer)

    # Bool True
    @_(r'\b(t[Rr][Uu][Ee]|f[Aa][Ll][Ss][Ee])\b')
    def BOOL_CONST(self, t):
        if t.value[0] == "t":
            t.value = True
        else:
            t.value = False
        return t

    # Type Identifier
    @_(r'\b[A-Z][a-zA-Z0-9_]*\b')
    def TYPEID(self, t):
        t.value = (t.value)
        return t

    # Object Identifier
    @_(r'[a-z][a-zA-Z0-9_]*')
    def OBJECTID(self, t):
        t.value = (t.value)
        return t

    # Comment
    @_(r'\(\*')
    def COMENTARIO(self, t):
        # Cambia el Lexer a Comentario
        self.begin(Comentario)

    # Error
    @_(r'_')
    def ERROR(self, t):
        # Change value
        t.value = '"' + t.value + '"'
        # Return error
        return t
      
    @_(r'(\*\)|_)')
    def ERROR(self, t):
        if (t.value == "*)"):
          t.value = '"' + "Unmatched *)" + '"'
        else:
          t.value = '"' + t.value + '"'
        return t

    def error(self, t):
        # 
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
                result = f'#{token.lineno} \'{token.type}\''
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