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

    # Comentario vacío
    @_(r'\n?\(\*\*\)')
    def SIMPLECOMMENT(self, t):
        pass
      
    # Otro comentario
    @_(r'[^\\]\(\*')
    def COMENTARIO_ANIDADO(self, t):
      self.cuenta += 1

    # Otro comentario
    @_(r'\n\(\*')
    def COMENTARIO_ANIDADO2(self, t):
      self.lineno += 1
      self.cuenta += 1

    # Función para terminar el comentario
    @_(r'[^\\]\*\)')
    def VOLVER(self, t):
      self.cuenta -= 1
      if (self.cuenta == 0):
        self.cuenta = 1
        # Retorna el flujo al CoolLexer
        self.begin(CoolLexer)

    # Función para terminar el comentario
    @_(r'\n\*\)')
    def VOLVER2(self, t):
      self.lineno += 1
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
    # Parameters
    _string = ""
    _tooLong = False
    contador = 0
  
    tokens = {STR_CONST, ERROR}
    
    @_(r'"')
    def STR_CONST(self, t):

      # Check lenght
      if self.contador > 1024:
        t.type = 'ERROR'
        t.value = '"' + "String constant too long" + '"'
        # Reseteamos los parámetros
        self._string = ""
        self.contador = 0
        # Usamos el CoolLexer
        self.begin(CoolLexer)
        return t
      
      # Retornamos el String
      t.value = '"' + self._string + '"'
      # Reseteamos los parámetros
      self._string = ""
      self.contador = 0
      # Usamos al lexer de COOL
      self.begin(CoolLexer)
      return t
    
    @_(r'(\\\n|[^\n]|\\")$')
    def ERROREOF(self, t):
      #print("ERROREOF")
      t.value = '"' + "EOF in string constant" + '"'
      t.type = 'ERROR'
      
      # Reseteamos parámetros
      self._string = ""
      self.contador = 0

      # Usamos el CoolLexer
      self.begin(CoolLexer)
      return t

    @_(r'(\\)?\x00(")?')
    def ERRORNULL (self, t):
      #print("ERRORNULL")
      t.value = '"' + "String contains escaped null character." + '"'
      t.type = 'ERROR'

      # Reseteamos parámetros
      self._string = ""
      self.contador = 0

      # Usamos el CoolLexer
      self.begin(CoolLexer)
      return t

    @_(r'\\\t')
    def TABULACION(self, t):
      #print("TABULACION")
      # Tabulación
      self._string += "\\t"
        
    @_(r'\\\n')
    def SALTO(self, t):
      #print("SALTO")
      # Salto de linea
      self._string += "\\n"
      self.lineno += 1
      self.contador += 1

      
    @_(r'\\[\b]')
    def BACKSPACE(self, t):
      #print("BACKSPACE")
      # Salto de b
      self._string += "\\b"

      
    @_(r'\\[\f]')
    def FORMFEED(self, t):
      #print("FORMFEED")
      # Salto de b
      self._string += "\\f"

    @_(r'\r')
    def CARRIAGERETURN(self, t):
      #print("CARRIAGERETURN")
      # Salto de b
      self._string += "\\015"


    @_(r'\033')
    def ESCAPEKEY(self, t):
      #print("ESCAPEKEY")
      # Salto de b
      self._string += "\\033"

    
    @_(r'\\[nbft"]')
    def BARRAENE(self, t):
      #print("BARRAENE")
      # Literal '\n'
      self._string += "\\" + t.value[1:]
      self.contador += 2


    @_(r'\\\\')
    def BARRABARRA(self, t):
      #print("BARRABARRA")
      # Dos \\ seguidas
      self._string += "\\\\"
      self.contador += 1

    
    @_(r'\\[^\\]')
    def BACKLASH(self, t):
      #print("BACKLASH")
      self._string += t.value[1:]
      self.contador += 2


    @_(r'\n')
    def ERROR(self, t):
      #print("ERROR")
      t.value = '"' + "Unterminated string constant" + '"'
      
      # Reseteamos los parámetros
      self._string = ""
      self.contador = 0
      
      # Usammos el CoolLexer
      self.begin(CoolLexer)
      return t

    @_(r'[^"\\]')
    def ACUMULA(self, t):
      #print("ACUMULA")
      # La coincidencia es parte del String
      self._string += t.value
      self.contador += 1
    

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
               '.', ',', '+', '/', '=', '@', '<', '-', '*'}

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

    # Comentario vacío
    @_(r'\(\*\*\)')
    def SIMPLECOMMENT(self, t):
        pass

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
    @_(r'[!#$%^&_>?`\[\]|]')
    def ERRORINVALIDCHAR(self, t):
        # Change value
        t.value = '"' + t.value + '"'
        t.type = "ERROR"
        # Return error
        return t

    @_(r'\\')
    def ERRORINVALIDCHABARRA(self, t):
        # Change value
        t.value = '"' + "\\\\" + '"'
        t.type = "ERROR"
        # Return error
        return t

    @_(r'(\001|\002|\003|\004)')
    def ERRORINVISIBLECHAR(self, t):
        # Change value
        if t.value == '\001':
          t.value = '"' + "\\001" + '"'
        elif t.value == '\002':
          t.value = '"' + "\\002" + '"'
        elif t.value == '\003':
          t.value = '"' + "\\003" + '"'
        elif t.value == '\004':
          t.value = '"' + "\\004" + '"'
        
        t.type = "ERROR"
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