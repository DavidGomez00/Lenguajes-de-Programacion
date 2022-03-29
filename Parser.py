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

    '''
    precedence = (
      ('left', '+', '-'),
      ('left', '*', '/'),
    )
    '''

    # Program
    @_('_class')
    def _program(self, p):
      return p._class

    @_('_program _class')
    def _program(self, p):
      return [p._program, p._class]

    # Class
    @_('CLASS TYPEID "{" _feature "}" ";"')
    def _class(self, p):
      return p

    @_('CLASS')
    def _class(self, p):
      return p.CLASS
      
    # Feature
    @_('_attribute _feature')
    def _feature(self, p):
      return p

    @_('_method _feature')
    def _feature(self, p):
      return p
      
    @_('_attribute')
    def _feature(self, p):
      return p._attribute

    @_('_method')
    def _feature(self, p):
      return p._method

    # Attribute
    @_('OBJECTID')
    def _attribute(self, p):
      return p.OBJECTID

    # Method
    @_('OBJECTID "(" _arg ")" ":" TYPEID "{" _expr "}"')
    def _method(self, p):
      return p

    @_('OBJECTID "(" ")" ":" TYPEID "{" _expr "}"')
    def _method(self, p):
      return p

    # Argument
    @_('_arg "," _arg')
    def _arg(self, p):
      return p

    @_('OBJECTID ":" TYPEID')
    def _arg(self, p):
      return p
      
    # Expresion
    @_('OBJECTID')
    def _expr(self, p):
      return p
      



  
   

    
    '''
      # Grammar rules and actions
    @_('expr "+" term')
    def expr(self, p):
        return p.expr + p.term

    @_('expr "+" expr')
    def expr(self, p):
      return p.expr0 + p.expr1

    @_('expr "-" term')
    def expr(self, p):
        return p.expr - p.term

    @_('term')
    def expr(self, p):
        return p.term

    @_('term "*" factor')
    def term(self, p):
        return p.term * p.factor

    @_('term "/" factor')
    def term(self, p):
        return p.term / p.factor

    @_('factor')
    def term(self, p):
        return p.factor

    @_('INT_CONST')
    def factor(self, p):
        return p.INT_CONST

    @_('"(" expr ")"')
    def factor(self, p):
        return p.expr
  
    '''


    @_('')
    def empty(self, p):
      pass