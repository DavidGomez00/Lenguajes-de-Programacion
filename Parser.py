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

    # Program
    @_('_class')
    def _program(self, p):
      return Programa(secuencia=[p._class])

    @_('_class _program')
    def _program(self, p):
      return Programa(secuencia=[p._class]+p._program.secuencia)

    # Class
    @_('CLASS TYPEID "{" _feature_list "}"')
    def _class(self, p):
      return Clase(nombre=p.TYPEID,
                   padre="Object",
                   nombre_fichero=self.nombre_fichero,
                   caracteristicas=p[3])

    @_('CLASS TYPEID inherits TYPEID "{" _feature_list "}"')
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

    
    # Expr
    @_('BOOL_CONST')
    def _expr(self, p):
      return Expresion(valor=self.valor)

    @_('STR_CONST')
    def _expr(self, p):
      return String(valor=self.valor)

    @_('INT_CONST')
    def _expr(self, p):
      return Integer(valor=self.valor) 

    @_('OBJECTID')
    def _expr(self, p):
      return NoExpr(nombre=self.valor)

    @_('"(" _expr ")"')
    def _expr(self, p):
      return Expresion(cast='(' + p.[1] + ')')

    @_('_expr "=" _expr')
    def _expr(self, p):
      return Expresion()

    @_('_expr "<" _expr')
    def _expr(self, p):
      return Expresion()

    @_('NOT _expr')
    def _expr(self, p):
      return Neg(expresion=p.[1])