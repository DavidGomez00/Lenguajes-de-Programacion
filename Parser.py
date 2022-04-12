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
      ('left', 'LE', '<', '='),
      ('left', '+', '-'),
      ('left', 'ISVOID'),
      ('left', '~'),
      ('left', '@'),
      ('left', '.')
    )


    # Program
    @_('_class ";"')
    def _program(self, p):
      return Programa(secuencia=[p._class])

    @_('_class ";" _program')
    def _program(self, p):
      return Programa(secuencia=[p._class]+p._program.secuencia)

    # Class
    @_('CLASS TYPEID "{" _feature_list "}"')
    def _class(self, p):
      return Clase(nombre=p.TYPEID,
                   padre="Object",
                   nombre_fichero=self.nombre_fichero,
                   caracteristicas=p[3])

    @_('CLASS TYPEID INHERITS TYPEID "{" _feature_list "}"')
    def _class(self, p):
      return Clase(nombre=p[1],
                   padre=p[3],
                   nombre_fichero=self.nombre_fichero,
                   caracteristicas=p[5])

    # Feature_list
    @_('_feature ";" _feature_list')
    def _feature_list(self, p):
      return p._feature

    @_('')
    def _feature_list(self, p):
      return []

    # Feature
    @_('OBJECTID "(" _formal_list ")" ":" TYPEID "{" _expr "}"')
    def _feature(self, p):
      return Metodo(nombre=p[0], tipo=p[5], cuerpo=p[7], formales=p[2])
    
    @_('OBJECTID ":" TYPEID ASSIGN _expr')
    def _feature(self, p):
      return Atributo(nombre=p[0], tipo=p[2], cuerpo=p[4])
    
    @_('OBJECTID ":" TYPEID')
    def _feature(self, p):
      return Atributo(nombre=p[0], tipo=p[2])

    # Formal_list
    @_('_formal "," _formal_list')
    def _formal_list(self, p):
      return p._formal

    @_('_formal')
    def _formal_list(self, p):
      return p._formal

    @_('')
    def _formal_list(self, p):
      return []

    #Formal 
    @_('OBJECTID ":" TYPEID')  
    def _formal(self, p):
      return Formal(nombre_variable=p[0], tipo=p[2])
    
    # Expresiones
    ## Expresion list
    @_('_expr "," _expr_list')
    def _expr_list(self, p):
      return p._expr

    @_('_expr')
    def _expr_list(self, p):
      return p._expr

    @_('')
    def _expr_list(self, p):
      return []

    ## Nueva
    @_('NEW OBJECTID')
    def _expr(self, p):
      return Nueva(tipo=p[1])

      
    ## Switch
    @_('CASE _expr OF _lista_case "+" ESAC')
    def _expr(self, p):
      return Switch(
        expr=p[1],
        casos=p[3])
  
    ##  RamaCase
    @_('OBJECTID ":" TYPEID DARROW _expr')
    def _rama_case(self, p):
      return RamaCase(
        nombre_variable=p[0],
        tipo=p[2],
        cuerpo=p[4])
      
    ## ListaCase
    @_('_rama_case ";" _lista_case')
    def _lista_case(self, p):
      return [p[0]]+p[2]

    @_('')
    def _lista_case(self, p):
      return []

    ## Asignacion
    @_('_expr ASSIGN _expr')
    def _expr(self, p):
      return Asignacion(nombre=p[0], cuerpo=p[1])

    ## Llamada a método estático
    @_('_expr "@" TYPEID "." OBJECTID "(" _expr_list ")"')
    def _expr(self, p):
      return LlamadaMetodoEstatico(
        clase=p[1],
        nombre_metodo=p[3],
        argumentos=p[5])
      
    ## Llamada a método
    @_('_expr "." OBJECTID "(" _expr_list ")"')
    def _expr(self, p):
        return LlamadaMetodo(
          cuerpo=p[0],
          nombre_metodo=p[2],
          argumentos=p[4])

    ## Condicional
    @_('IF _expr THEN _expr ELSE _expr FI')
    def _expr(self, p):
      return Condicional(condicion=p[1], verdadero=p[3], falso=p[5])
      
    ## Bucle
    @_('WHILE _expr LOOP _expr POOL')
    def _expr(self, p):
      return Bucle(condicion=p[1], cuerpo=p[3])

    ## Let
    @_('LET OBJECTID ":" TYPEID ASSIGN _expr IN _expr')
    def _expr(self, p):
      return Let(nombre=p[1], tipo=p[3], inicializacion=[(p[1], p[3], p[5])], cuerpo=p[7])
    
    @_('LET OBJECTID ":" TYPEID IN _expr')
    def _expr(self, p):
      return Let(nombre=p[1], tipo=p[3], inicializacion=[(p[1], p[3], NoExpr(nombre=p[1]))], cuerpo=p[5])

    @_('LET OBJECTID ":" TYPEID ASSIGN _expr "," _listalet')
    def _expr(self, p):
      return Let(nombre=p[1], tipo=p[3], inicializacion=[(p[1], p[3], p[5])], cuerpo=p[7])

    @_('LET OBJECTID ":" TYPEID "," _listalet')
    def _expr(self, p):
      return Let(nombre=p[1], tipo=p[3], inicializacion=[(p[1], p[3], NoExpr(nombre=p[1]))], cuerpo=p[5])

    @_('OBJECTID ":" TYPEID ASSIGN _expr "," _listalet')
    def _listalet(self, p):
      return Let(nombre=p[0], tipo=p[2], inicializacion=[(p[0], p[2], p[4])], cuerpo=p[6])

    @_('OBJECTID ":" TYPEID "," _listalet')
    def _listalet(self, p):
      return Let(nombre=p[0], tipo=p[2], inicializacion=[(p[0], p[2], NoExpr(nombre=p[0]))], cuerpo=p[6])

    @_('OBJECTID ":" TYPEID ASSIGN _expr IN _expr')
    def _listalet(self, p):
      return Let(nombre=p[0], tipo=p[2], inicializacion=[(p[0], p[2], p[4])], cuerpo=p[6])

    @_('OBJECTID ":" TYPEID IN _expr')
    def _listalet(self, p):
      return Let(nombre=p[0], tipo=p[2], inicializacion=[(p[0], p[2], NoExpr(nombre=p[0]))], cuerpo=p[6])
      
    ## Bloque
    @_('"{" _expr ";" _expr ";" "}"')
    def _expr(self, p):
      return Bloque(expresiones=[p[1], p[3]])
      
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
      return Objeto(nombre=p[0])
      
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
      return Suma(operando="+")

    ### Resta
    @_('_expr "-" _expr')
    def _expr(self, p):
      return Resta(operando="-")

    ### Multiplicación
    @_('_expr "*" _expr')
    def _expr(self, p):
      return Multiplicacion(operando="*")
      
    ### División
    @_('_expr "/" _expr')
    def _expr(self, p):
      return Division(operando="/")

    ### Menor
    @_('_expr "<" _expr')
    def _expr(self, p):
      return Menor(operando="<")
      
    ### LeIgual
    @_('_expr LE _expr')
    def _expr(self, p):
      return LeIgual(operando="<=")

    ### Igual
    @_('_expr "=" _expr')
    def _expr(self, p):
      return Igual(operando="=")

    @_('"(" _expr ")"')
    def _expr(self, p):
      return p[1]    

    