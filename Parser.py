# coding: utf-8

from Lexer import CoolLexer
from sly import Parser
import sys
import os
from Clases import *


class CoolParser(Parser):
    nombre_fichero = ''
    tokens = CoolLexer.tokens
    debugfile = "salida.out"
    errores = []

    precedence = (
      ('left', 'ASSIGN'),
      ('left', 'NOT'),
      ('nonassoc', 'LE', '<', '='),
      ('left', '-', '+'),
      ('left', '*', '/'),
      ('left', 'ISVOID'),
      ('left', '~'),
      ('left', '@'),
      ('left', '.')
    )

    # Program
    @_('_class ";"')
    def _program(self, p):
      return Programa(secuencia=[p._class], linea=p.lineno)

    @_('_class ";" _program')
    def _program(self, p):
      return Programa(secuencia=[p._class]+p._program.secuencia, linea=p.lineno)

    # Class
    @_('CLASS TYPEID "{" _feature_list "}"')
    def _class(self, p):
      return Clase(nombre=p.TYPEID,
                   padre="Object",
                   nombre_fichero=self.nombre_fichero,
                   caracteristicas=p[3],
                   linea=p.lineno)

    # Class
    @_('CLASS TYPEID "{" error "}"')
    def _class(self, p):
      return None

    @_('CLASS TYPEID INHERITS TYPEID "{" _feature_list "}"')
    def _class(self, p):
      return Clase(nombre=p[1],
                   padre=p[3],
                   nombre_fichero=self.nombre_fichero,
                   caracteristicas=p[5],
                   linea=p.lineno)

    @_('CLASS TYPEID INHERITS TYPEID "{" error "}"')
    def _class(self, p):
      return None

    # Feature_list
    @_('_feature ";" _feature_list')
    def _feature_list(self, p):
      return [p._feature] + p._feature_list

    @_('_feature ";"')
    def _feature_list(self, p):
      return [p._feature]

    @_('')
    def _feature_list(self, p):
      return []

    @_('error ";"')
    def _feature_list(self, p):
      return []
  
      
    # Feature
    @_('OBJECTID "(" _formal_list ")" ":" TYPEID "{" _expr "}"')
    def _feature(self, p):
      return Metodo(nombre=p[0], tipo=p[5], cuerpo=p[7], formales=p[2])

    @_('OBJECTID "(" error ")" ":" TYPEID "{" _expr "}"')
    def _feature(self, p):
      return None
      
    @_('error "(" _formal_list ")" ":" TYPEID "{" _expr "}"')
    def _feature(self, p):
      return None
    
    @_('OBJECTID ":" TYPEID ASSIGN _expr')
    def _feature(self, p):
      return Atributo(nombre=p[0], tipo=p[2], cuerpo=p[4], linea=p.lineno)
    
    @_('OBJECTID ":" TYPEID')
    def _feature(self, p):
      return Atributo(nombre=p[0], tipo=p[2], cuerpo=NoExpr(), linea=p.lineno)

    @_('OBJECTID ":" error')
    def _feature(self, p):
      return None

    @_('error ":" TYPEID')
    def _feature(self, p):
      return None

    # Formal_list
    @_('_formal "," _formal_list')
    def _formal_list(self, p):
      return [p[0]] + p[2]

    @_('_formal')
    def _formal_list(self, p):
      return [p[0]]

    @_('')
    def _formal_list(self, p):
      return []

    #Formal 
    @_('OBJECTID ":" TYPEID')  
    def _formal(self, p):
      return Formal(nombre_variable=p[0], tipo=p[2])
    
    # Expresiones
    ## Bloque
    @_('"{" expresion_block "}"')
    def _expr(self, p):
      return Bloque(expresiones=p[1])
 
    @_('_expr ";"')
    def expresion_block(self, p):
      return [p[0]]
    
    @_('error ";"')
    def expresion_block(self, p):
      return []
    
    @_('expresion_block _expr ";"')
    def expresion_block(self, p):
      return p[0] + [p[1]]
    
    ## Expresion list
    @_('_expr "," _expr_list')
    def _expr_list(self, p):
      return [p[0]] + p[2]

    @_('error "," _expr_list')
    def _expr_list(self, p):
      return []

    @_('_expr "," error')
    def _expr_list(self,p):
      return[]

    @_('_expr')
    def _expr_list(self, p):
      return [p[0]]

    ## Nueva
    @_('NEW TYPEID')
    def _expr(self, p):
      return Nueva(tipo=p[1])

      
    ## Switch
    @_('CASE _expr OF _lista_case ESAC')
    def _expr(self, p):
      return Swicht(
        expr=p[1],
        casos=p[3],
        linea=p.lineno)
  
    ##  RamaCase
    @_('OBJECTID ":" TYPEID DARROW _expr')
    def _rama_case(self, p):
      return RamaCase(
        nombre_variable=p[0],
        tipo=p[2],
        cuerpo=p[4],
        linea=p.lineno)
      
    ## ListaCase
    @_('_rama_case ";" _lista_case')
    def _lista_case(self, p):
      return [p[0]]+p[2]

    @_('')
    def _lista_case(self, p):
      return []

    ## Asignacion
    @_('OBJECTID ASSIGN _expr')
    def _expr(self, p):
      return Asignacion(nombre=p[0], cuerpo=p[2], linea=p.lineno)

    ## Llamada a método estático
    @_('_expr "@" TYPEID "." OBJECTID "(" _expr_list ")"')
    def _expr(self, p):
      return LlamadaMetodoEstatico(
        clase=p[2],
        nombre_metodo=p[4],
        argumentos=p[6],
        linea=p.lineno)
    
    @_('_expr "@" TYPEID "." OBJECTID "(" ")"')
    def _expr(self, p):
      return LlamadaMetodoEstatico(
        clase=p[2],
        nombre_metodo=p[4],
        argumentos=[],
        linea=p.lineno)
      
    ## Llamada a método
    @_('_expr "." OBJECTID "(" _expr_list ")"')
    def _expr(self, p):
        return LlamadaMetodo(
          cuerpo=p[0],
          nombre_metodo=p[2],
          argumentos=p[4],
          linea=p.lineno)

    @_('OBJECTID "(" _expr_list ")"')
    def _expr(self, p):
      return LlamadaMetodo(
        cuerpo=Objeto(nombre="self"),
        nombre_metodo=p[0],
        argumentos=p[2],
        linea=p.lineno)

    @_('OBJECTID "(" error ")"')
    def _expr(self, p):
      return None
    
    @_('_expr "." OBJECTID "(" ")"')
    def _expr(self, p):
      return LlamadaMetodo(
        cuerpo=p[0],
        nombre_metodo=p[2],
        argumentos=[],
        linea=p.lineno)

    @_('OBJECTID "(" ")"')
    def _expr(self, p):
      return LlamadaMetodo(
        cuerpo=Objeto(nombre="self"),
        nombre_metodo=p[0],
        argumentos=[],
        linea=p.lineno)
    
    ## Condicional
    @_('IF _expr THEN _expr ELSE _expr FI')
    def _expr(self, p):
      return Condicional(condicion=p[1], verdadero=p[3], falso=p[5])
      
    ## Bucle
    @_('WHILE _expr LOOP _expr POOL')
    def _expr(self, p):
      return Bucle(condicion=p[1], cuerpo=p[3], linea=p.lineno)

    ## Let
    @_('LET OBJECTID ":" TYPEID ASSIGN _expr IN _expr')
    def _expr(self, p):
      return Let(nombre=p[1], tipo=p[3], inicializacion=p[5], cuerpo=p[7])
    
    @_('LET OBJECTID ":" TYPEID IN _expr')
    def _expr(self, p):
      return Let(nombre=p[1], tipo=p[3], inicializacion=NoExpr(), cuerpo=p[5])

    @_('LET OBJECTID ":" TYPEID ASSIGN _expr "," _listalet')
    def _expr(self, p):
      return Let(nombre=p[1], tipo=p[3], inicializacion=p[5], cuerpo=p[7])

    @_('LET OBJECTID ":" TYPEID ASSIGN error "," _listalet')
    def _expr(self, p):
      return None
    
    @_('LET OBJECTID ":" TYPEID "," _listalet')
    def _expr(self, p):
      return Let(nombre=p[1], tipo=p[3], inicializacion=NoExpr(), cuerpo=p[5])

    @_('OBJECTID ":" TYPEID ASSIGN _expr "," _listalet')
    def _listalet(self, p):
      return Let(nombre=p[0], tipo=p[2], inicializacion=p[4], cuerpo=p[6])

    @_('OBJECTID ":" TYPEID "," _listalet')
    def _listalet(self, p):
      return Let(nombre=p[0], tipo=p[2], inicializacion=NoExpr(), cuerpo=p[4])

    @_('OBJECTID ":" TYPEID ASSIGN _expr IN _expr')
    def _listalet(self, p):
      return Let(nombre=p[0], tipo=p[2], inicializacion=p[4], cuerpo=p[6])

    @_('OBJECTID ":" TYPEID ASSIGN error IN _expr')
    def _listalet(self, p):
      return None

    @_('OBJECTID ":" TYPEID IN _expr')
    def _listalet(self, p):
      return Let(nombre=p[0], tipo=p[2], inicializacion=NoExpr(), cuerpo=p[4])

    ## Negacion
    @_('"~" _expr')
    def _expr(self, p):
      return Neg(expr=p[1])
      
    ## Not
    @_('NOT _expr')
    def _expr(self, p):
      return Not(operador="NOT", expr=p[1]) 

    ## Es nulo
    @_('ISVOID _expr')
    def _expr(self, p):
      return EsNulo(expr=p[1])

    ## Objeto
    @_('OBJECTID')
    def _expr(self, p):
      return Objeto(nombre=p[0], linea=p.lineno)
      
    ## Entero
    @_('INT_CONST')
    def _expr(self, p):
      return Entero(valor=p[0]) 

    ## String
    @_('STR_CONST')
    def _expr(self, p):
      return String(valor=p[0])

    ## Booleano
    @_('BOOL_CONST')
    def _expr(self, p):
      return Booleano(valor=p[0])

    ## Operaciones binarias
    ### Suma
    @_('_expr "+" _expr')
    def _expr(self, p):
      return Suma(izquierda=p._expr0, derecha=p._expr1, linea=p.lineno)   

    ### Resta
    @_('_expr "-" _expr')
    def _expr(self, p):
      return Resta(izquierda=p._expr0, derecha=p._expr1, linea=p.lineno)

    ### Multiplicación
    @_('_expr "*" _expr')
    def _expr(self, p):
      return Multiplicacion(izquierda=p._expr0, derecha=p._expr1, linea=p.lineno)
      
    ### División
    @_('_expr "/" _expr')
    def _expr(self, p):
      return Division(izquierda=p._expr0, derecha=p._expr1, linea=p.lineno)

    ### Menor
    @_('_expr "<" _expr')
    def _expr(self, p):
      return Menor(izquierda=p._expr0, derecha=p._expr1, linea=p.lineno)
      
    ### LeIgual
    @_('_expr LE _expr')
    def _expr(self, p):
      return LeIgual(izquierda=p._expr0, derecha=p._expr1, linea=p.lineno)

    ### Igual
    @_('_expr "=" _expr')
    def _expr(self, p):
      return Igual(izquierda=p._expr0, derecha=p._expr1, linea=p.lineno)

    ## Paréntesis
    @_('"(" _expr ")"')
    def _expr(self, p):
      return p[1]    
      
    ## Errores
    def error(self, p):
      '''
      print(self.nombre_fichero)
      print(p)
      '''
      mensaje = ''
      if (not p):
        mensaje = f'"{self.nombre_fichero}", line 0: syntax error at or near EOF'
      elif (p.type in ('TYPEID', 'OBJECTID', 'INT_CONST')):
        mensaje = f'"{self.nombre_fichero}", line {p.lineno}: syntax error at or near {p.type} = {p.value}'
      elif (p.type in ('WHILE', 'POOL',  'OF', 'FI', 'LOOP', 'ELSE', 'LE')):
        mensaje = f'"{self.nombre_fichero}", line {p.lineno}: syntax error at or near {p.type}'
        mensaje = mensaje.replace('WHILE', 'LOOP')
      elif (p.type in ('+', ',', ';', '{', '}', ':', ')', '.', '=')):
        mensaje = f'"{self.nombre_fichero}", line {p.lineno}: syntax error at or near \'{p.type}\''

      # Anhadimos el error a los mensajes
      self.errores.append(mensaje)