# coding: utf-8
from dataclasses import dataclass, field
from doctest import UnexpectedException
from typing import List
from anytree import Node, RenderTree, PreOrderIter
from collections import defaultdict

class CustomizedException(Exception):
  pass
  
class Ambito():
  '''Clase auxiliar para determinar 
  el tipo de elemento.
  '''

  def __init__(self):
    ''' Instancia un ámbito.'''
    # Referencia al ambito que estamos analizando
    self.ambito_actual = None
    # Referencia a la clase
    self.clase = None
    # Diccionario que guarda donde se han declarado los metodos y atributos y su tipo
    self.dict = defaultdict(str)
    self.dict_metodos = defaultdict(list)
    # Registro de las clases y herencias
    self.arbol_ambito = Node("Object")

    # Registramos clases basicas
    Node("IO", self.arbol_ambito)
    Node("Int", self.arbol_ambito)
    Node("Bool", self.arbol_ambito)
    Node("String", self.arbol_ambito)

    # Registramos algunas funciones basicas
    self.dict[("Object", "abort")] = 'Object'
    self.dict_metodos[("Object", "abort")] = ["abort"]
    self.dict[("Object", "type_name")] = 'String'
    self.dict_metodos[("Object", "type_name")] = ["type_name"]
    self.dict[("Object", "copy")] = 'SELF_TYPE'
    self.dict_metodos[("Object", "copy")] = ["copy"]
    self.dict[("String", "length")] = 'Int'
    self.dict_metodos[("String", "length")] = ["length"]

    self.dict[("IO", "out_string")] = 'SELF_TYPE'
    self.dict_metodos[("IO", "out_string")] = ['out_string'] + [Formal(linea=0, nombre_variable='x', tipo='String')]

    self.dict[("String", "concat")] = 'String'
    self.dict_metodos[("String", "concat")] = ['concat'] + [Formal(linea=0, nombre_variable='s', tipo='String')]

    self.dict[("String", "substr")] = 'String'
    self.dict_metodos[("String", "substr")] = ['substr'] + [Formal(linea=0, nombre_variable='i', tipo='Int'), Formal(linea=0, nombre_variable='l', tipo='Int')]
    
  def anhadeAmbito(self, ambito:str, padre:str='Object'):
    ''' Anhade un elemento al ambito. '''
    # Encontramos el nodo padre 
    nodo_padre = [node 
                for node in PreOrderIter(self.arbol_ambito)
                if node.name == padre][0]
    # Creamos la dependencia en el arbol
    Node(ambito, nodo_padre)
    # Creamos el ámbito en el diccionario
    self.dict[(padre, ambito)] = ambito

  def busca(self, nombre:str, ambito:str=''):
    ''' Encuentra el tipo de nombre. Si no esta asignado retorna _no_encontrado.
    '''
    # En caso de no especificar la clase desde la que buscar, usamos la clase actual
    if (ambito == ''): 
      ambito = self.ambito_actual
    # Nodo correspondiente al ambito desde la que buscamos
    nodo_actual = [nodo
                  for nodo in PreOrderIter(self.arbol_ambito) # Todos los nodos del arbol
                  if nodo.name == ambito]                     # Solo aquel cuyo nombre coincide
    
    # Evitamos errores en caso de que no haya ambitos con este nombre
    if (len(nodo_actual) == 0):
      return 'no_encontrado'
    else:
      nodo_actual = nodo_actual[0]

    # Consigo todas las tuplas de (ambito, atributo) para el ambito y sus padres
    tuplas = []
    while (nodo_actual is not None):
      tuplas.append((nodo_actual.name, nombre)) # Anhado la tupla (clase, caracteristica)
      nodo_actual = nodo_actual.parent          # Buscamos en el padre
    # Compruebo en todas las entradas para las tuplas generadas
    for tupla in tuplas:
      # Si la entrada es distinta de la default ('') retorna lo que ha encontrado
      if self.dict[tupla] != '':
        return self.dict[tupla]
    # Si no encontramos nada, retorna '_no_encontrado'
    return '_no_encontrado'
      
  def buscaMetodo(self, metodo:str, ambito:str=''):
    '''Busca un método en una clase o sus padres.'''
    # En caso de no especificar el ambito usamos el ambito actual
    if (ambito == ''): ambito = self.ambito_actual
    print(f"Busca {metodo} desde {ambito}")
    # Encuentra correspondiente al ambito
    nodo = [nodo
            for nodo in PreOrderIter(self.arbol_ambito)
            if nodo.name == ambito]

    # Evitamos errores en caso de que no haya ambitos con este nombre
    if (len(nodo) == 0):
      return ['_no_encontrado']
    else:
      nodo = nodo[0]
    
    # Generamos las entradas del diccinoario para todos los ambitos por encima del arbol
    tuplas = []
    while (nodo is not None):
      tuplas.append((nodo.name, metodo)) # Anhado la tupla (clase, caracteristica)
      nodo = nodo.parent                 # Buscamos en el padre
    print(tuplas)
    # Compruebo en todas las entradas para las tuplas generadas
    for tupla in tuplas:
      # Si el metodo existe retorna lo que ha encontrado
      if len(self.dict_metodos[tupla]) != 0:
        return self.dict_metodos[tupla]
    # Si no encontramos nada, retorna la lista vacía
    return ["_no_encontrado"]

  def claseInAmbito(self, clase:str):
    '''Retorna True si la clase está registrada en el ambito.'''
    nodo = [nodo
            for nodo in PreOrderIter(self.arbol_ambito)
            if nodo.name == clase]
    if len(nodo) != 0: return True
    return False

@dataclass
class Nodo:
    linea: int = 0

    def str(self, n):
        return f'{n*" "}#{self.linea}\n'


@dataclass
class Formal(Nodo):
    nombre_variable: str = '_no_set'
    tipo: str = '_no_type'
    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_formal\n'
        resultado += f'{(n+2)*" "}{self.nombre_variable}\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        return resultado

    def Tipo(self, ambito):
      # Hemos de comprobar que los tipos de los objetos de clases no basicas estén declaradas
      if self.tipo not in ['Int', 'Bool', 'String']:
        # Comprobamos que tenemos la clase en el arbol de clases
        clase = [clase 
                for clase in PreOrderIter(ambito.arbol_ambito)
                if clase.name == self.tipo]
        # Si la longitud de la lista es 0, es que no ha encontrado la clase
        if len(clase) == 0:
          # Lanzar Error
          pass
        # Si hemos encontrado la clase
        clase = clase[0]
        # El formal declarado con el mismo tipo que la clase actual es de tipo SELF_TYPE
        if (self.tipo == clase.name): self.tipo = 'SELF_TYPE'

      

class Expresion(Nodo):
    cast: str = '_no_type'


@dataclass
class Asignacion(Expresion):
    nombre: str = '_no_set'
    cuerpo: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_assign\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, ambito):
      # Comprobamos el cuerpo
      self.cuerpo.Tipo(ambito)
      
      # Comprobamos que son el mismo tipo
      tipo_nombre = ambito.busca(self.nombre)
      # Tenemos que tener en cuenta la herencia TODO:
      if (self.cuerpo.cast != tipo_nombre):
        raise CustomizedException(f"{self.linea}: Type {self.cuerpo.cast} of assigned expression does not conform to declared type {tipo_nombre} of identifier {self.nombre}.")
      # Cambiamos el cast de la asignación
      self.cast = tipo_nombre
      
      

@dataclass
class LlamadaMetodoEstatico(Expresion):
    cuerpo: Expresion = None
    clase: str = '_no_type'
    nombre_metodo: str = '_no_set'
    argumentos: List[Expresion] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_static_dispatch\n'
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n+2)*" "}{self.clase}\n'
        resultado += f'{(n+2)*" "}{self.nombre_metodo}\n'
        resultado += f'{(n+2)*" "}(\n'
        resultado += ''.join([c.str(n+2) for c in self.argumentos])
        resultado += f'{(n+2)*" "})\n'
        resultado += f'{(n)*" "}: _no_type\n'
        return resultado

    def Tipo(self, ambito):
      # Falta por implementar
      pass


@dataclass
class LlamadaMetodo(Expresion):
    cuerpo: Expresion = None
    nombre_metodo: str = '_no_set'
    argumentos: List[Expresion] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_dispatch\n'
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n+2)*" "}{self.nombre_metodo}\n'
        resultado += f'{(n+2)*" "}(\n'
        resultado += ''.join([c.str(n+2) for c in self.argumentos])
        resultado += f'{(n+2)*" "})\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, ambito):
      # Comprobamos el cuerpo
      self.cuerpo.Tipo(ambito)

      # Comprobamos que tenga un cuerpo desde donde se llama
      if(self.cuerpo.cast == 'SELF_TYPE'): ambito_base = ambito.clase
      else: ambito_base = self.cuerpo.cast

      # Buscamos el tipo del método
      tipo_metodo = ambito.busca(self.nombre_metodo, ambito_base)
      
      # Si no lo encuentra tira un error
      if (tipo_metodo == '_no_encontrado'):
        raise CustomizedException(f'{self.linea}: Dispatch to undefined method {self.nombre_metodo}.')
      # Si encuentra el tipo como SELF_TYPE, el tipo es como el del cuerpo
      if (tipo_metodo == 'SELF_TYPE'):
        tipo_metodo = self.cuerpo.cast

      # Comprobamos los parametros
      parametros = ambito.buscaMetodo(self.nombre_metodo, ambito_base)
      print(parametros)
      # Si no lo encuentra tira un error
      if parametros[0] == '_no_encontrado':
        raise CustomizedException(f'{self.linea}: Dispatch to undefined method {self.nombre_metodo}.')
      # Si lo encuentra quitamos el primer elemento para ahorrarnos problemas
      parametros = parametros[1::]
      # Mismo numero de parametros
      if len(self.argumentos) != len(parametros):
        raise CustomizedException(f"Error por determinar b")
      # Comprobamos los tipos de los argumentos
      for argumento in self.argumentos:
        argumento.Tipo(ambito)
      # Mismo tipo estático
      for i, formal in enumerate(parametros):
        if (self.argumentos[i].cast != formal.tipo):
          raise CustomizedException(f"{self.linea}: In call of method {self.nombre_metodo}, type {self.argumentos[i].cast} of parameter {formal.nombre_variable} does not conform to declared type {formal.tipo}.")
      # Establecemos el cast de la llamada
      self.cast = tipo_metodo

@dataclass
class Condicional(Expresion):
    condicion: Expresion = None
    verdadero: Expresion = None
    falso: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_cond\n'
        resultado += self.condicion.str(n+2)
        resultado += self.verdadero.str(n+2)
        resultado += self.falso.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, ambito):
      # Falta implementar
      pass


@dataclass
class Bucle(Expresion):
    condicion: Expresion = None
    cuerpo: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_loop\n'
        resultado += self.condicion.str(n+2)
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, ambito):
      # Comprobamos la condicion
      self.condicion.Tipo(ambito)

      if self.condicion.cast != 'Bool':
        raise CustomizedException(f"{self.linea}: Loop condition does not have type Bool.")

      # Comprobamos el cuerpo
      self.cuerpo.Tipo(ambito)

      # El cast de un loop es Object
      self.cast = 'Object'


@dataclass
class Let(Expresion):
    nombre: str = '_no_set'
    tipo: str = '_no_set'
    inicializacion: Expresion = None
    cuerpo: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_let\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += self.inicializacion.str(n+2)
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, ambito):
      # Anhadimos el ambito del let al arbol de ambitos
      ambito.anhadeAmbito(self.nombre, ambito.ambito_actual)

      # Cambiamos el ambito actual al ambito del let
      ambito.ambito_actual = self.nombre

      # Anhadimos al ambito lo declarado en el Let
      ambito.dict[(ambito.ambito_actual, self.nombre)] = self.tipo

      # Comprobamos la inicialización
      self.inicializacion.Tipo(ambito)

      # Simulamos una asignacion


      # Comprobamos primero el cuerpo
      self.cuerpo.Tipo(ambito)
      
       


@dataclass
class Bloque(Expresion):
    expresiones: List[Expresion] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado = f'{n*" "}_block\n'
        resultado += ''.join([e.str(n+2) for e in self.expresiones])
        resultado += f'{(n)*" "}: {self.cast}\n'
        resultado += '\n'
        return resultado

    def Tipo(self, ambito):
      # Comprobamos las expresiones
      for expr in self.expresiones:
        expr.Tipo(ambito)
      # Establecemos el cast del bloque como el resultado de la ultima expresion
      self.cast = self.expresiones[-1].cast

@dataclass
class RamaCase(Expresion):
    nombre_variable: str = '_no_set'
    tipo: str = '_no_set'
    cuerpo: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_branch\n'
        resultado += f'{(n+2)*" "}{self.nombre_variable}\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, ambito):
      # Anhadimos este case al arbol de ambitos
      ambito.anhadeAmbito("case" + self.nombre_variable, ambito.ambito_actual)
      # Cambio el ambito actual a case
      ambito.ambito_actual = "case" + self.nombre_variable
      # Anhadimos la variable declarada
      ambito.dict[(ambito.ambito_actual, self.nombre_variable)] = self.tipo
      # Comprobamos el cuerpo
      self.cuerpo.Tipo(ambito)
      # Establecemos el cast del caso
      self.cast = self.tipo

@dataclass
class Swicht(Expresion):
    expr: Expresion = None
    casos: List[RamaCase] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_typcase\n'
        resultado += self.expr.str(n+2)
        resultado += ''.join([c.str(n+2) for c in self.casos])
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, ambito):
      tipos = []
      # Comprobamos los case
      for caso in self.casos:
        caso.Tipo(ambito)
        if caso.cast in tipos:
          raise CustomizedException(f'{self.linea}: Duplicate branch {caso.cast} in case statement.')
        tipos.append(caso.cast)

@dataclass
class Nueva(Expresion):
    tipo: str = '_no_set'
  
    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_new\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, ambito):
      # Comprobamos que tenemos el tipo en el ambito
      clase = [clase for clase in PreOrderIter(ambito.arbol_ambito)
              if clase.name == self.tipo][0]
      if not clase:
        # Lanzar Error
        pass
      else:
        self.cast = clase.name

@dataclass
class OperacionBinaria(Expresion):
    izquierda: Expresion = None
    derecha: Expresion = None


@dataclass
class Suma(OperacionBinaria):
    operando: str = '+'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_plus\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, ambito):
      # Comprobamos que los dos lados estén bien
      self.izquierda.Tipo(ambito)
      self.derecha.Tipo(ambito)
      
      # Comprobamos solo integers
      if self.izquierda.cast != 'Int' or self.derecha.cast != 'Int':
        # Lanzar Error
        raise CustomizedException(f"{self.linea}: non-Int arguments: {self.izquierda.cast} + {self.derecha.cast}")
        
      # Establecemos el cast
      self.cast = 'Int'


@dataclass
class Resta(OperacionBinaria):
    operando: str = '-'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_sub\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, ambito):
      # Comprobamos que los dos lados estén bien
      self.izquierda.Tipo(ambito)
      self.derecha.Tipo(ambito)
      
      # Comprobamos solo integers
      if self.izquierda.cast != 'Int' or self.derecha.cast != 'Int':
        raise CustomizedException(f"{self.linea}: non-Int arguments: {self.izquierda.cast} - {self.derecha.cast}")

      # Establecemos el cast
      self.cast = 'Int'


@dataclass
class Multiplicacion(OperacionBinaria):
    operando: str = '*'
    
    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_mul\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, ambito):
      # Comprobamos que los dos lados estén bien
      self.izquierda.Tipo(ambito)
      self.derecha.Tipo(ambito)
      
      # Comprobamos solo integers
      if self.izquierda.cast != 'Int' or self.derecha.cast != 'Int':
        # Lanzar Error
        pass

      # Establecemos el cast
      self.cast = 'Int'


@dataclass
class Division(OperacionBinaria):
    operando: str = '/'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_divide\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, ambito):
      # Comprobamos que los dos lados estén bien
      self.izquierda.Tipo(ambito)
      self.derecha.Tipo(ambito)
      
      # Comprobamos solo integers
      if self.izquierda.cast != 'Int' or self.derecha.cast != 'Int':
        # Lanzar Error
        pass

      # Establecemos el cast
      self.cast = 'Int'


@dataclass
class Menor(OperacionBinaria):
    operando: str = '<'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_lt\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    
    def Tipo(self, ambito):
      # Comprobamos que los dos lados estén bien
      self.izquierda.Tipo(ambito)
      self.derecha.Tipo(ambito)
      
      # Comprobamos solo integers
      if self.izquierda.cast != 'Int' or self.derecha.cast != 'Int':
        # Lanzar Error
        pass

      # Establecemos el cast
      self.cast = 'Bool'
    

@dataclass
class LeIgual(OperacionBinaria):
    operando: str = '<='

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_leq\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, ambito):
      # Comprobamos que esten bien los hijos
      self.izquierda.Tipo(ambito)
      self.derecha.Tipo(ambito)

      # Comprobamos solo integers
      if self.izquierda.cast != 'Int' or self.derecha.cast != 'Int':
        # Lanzar Error
        pass

      # Establecemos el cast
      self.cast = 'Bool'

@dataclass
class Igual(OperacionBinaria):
    operando: str = '='

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_eq\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, ambito):
      # Comprobamos el cast de cada lado
      self.izquierda.Tipo(ambito)
      self.derecha.Tipo(ambito)

      # Comprobamos que sean del mismo tipo
      if self.izquierda.cast in ['Int', 'String', 'Bool']:
        if (self.izquierda.cast != self.derecha.cast):
          # Lanzar Error
          raise CustomizedException(f'{self.linea}: Illegal comparison with a basic type.')
      
      self.cast = 'Bool'
      



@dataclass
class Neg(Expresion):
    expr: Expresion = None
    operador: str = '~'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_neg\n'
        resultado += self.expr.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def Tipo(self, ambito):
        # Determinamos el tipo de la expresion
        self.expr.Tipo(ambito)
        # Establecemos el tipo de la negación
        self.cast = 'Bool'



@dataclass
class Not(Expresion):
    expr: Expresion = None
    operador: str = 'NOT'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_comp\n'
        resultado += self.expr.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, ambito):
        # Comprobamos que la expresion es correcta
        self.expr.Tipo(ambito)

        # Una expresión not es un booleano
        self.cast = 'Bool'


@dataclass
class EsNulo(Expresion):
    expr: Expresion = None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_isvoid\n'
        resultado += self.expr.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, ambito):
        # Determinamos el tipo de la expresion
        self.expr.Tipo(ambito)

        # EsNulo siempre es de tipo booleano
        self.cast = 'Bool'

@dataclass
class Objeto(Expresion):
    nombre: str = '_no_set'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_object\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, ambito):
        # Comprobamos el nombre
        if (self.nombre == 'self'):
          self.cast = 'SELF_TYPE'
        else:
          # Buscamos este objeto en el ambito
          tipo = ambito.busca(self.nombre)

          # Si no lo encuentra levantamos una excepción
          if (tipo == '_no_encontrado'):
            raise CustomizedException(f"{self.linea}: Undeclared identifier {self.nombre}.")

          # Si lo encuentra, establecemos el cast
          self.cast = tipo
        


@dataclass
class NoExpr(Expresion):
    nombre: str = ''

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_no_expr\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado
    
    def Tipo(self, ambito):
        pass


@dataclass
class Entero(Expresion):
    valor: int = 0

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_int\n'
        resultado += f'{(n+2)*" "}{self.valor}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, ambito):
      self.cast = 'Int'


@dataclass
class String(Expresion):
    valor: str = '_no_set'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_string\n'
        resultado += f'{(n+2)*" "}{self.valor}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, ambito):
      self.cast = 'String'
  
@dataclass
class Booleano(Expresion):
    valor: bool = False

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_bool\n'
        resultado += f'{(n+2)*" "}{1 if self.valor else 0}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

    def Tipo(self, ambito):
      self.cast = 'Bool'

@dataclass
class IterableNodo(Nodo):
    secuencia: List = field(default_factory=List)


class Programa(IterableNodo):
    
    def Tipo(self):
      # Creamos el ambito
      ambito = Ambito()
      
      # Construimos el arbol de ambitos
      for clase in self.secuencia:
        # Utilizar un arbol para registrar las dependencias de ambitos
        if(clase.padre in ['Int', 'Bool', 'String', 'SELF_TYPE']):
          raise CustomizedException(f"{self.linea}: Class {clase.nombre} cannot inherit class {clase.padre}.")
        if(clase.padre != 'Object' and not ambito.claseInAmbito(clase.padre)):
          raise CustomizedException(f'{self.linea}: Expression type SELF_TYPE does not conform to declared static dispatch type {clase.nombre}.')
        ambito.anhadeAmbito(clase.nombre, clase.padre)
        
      # Registramos las caracteristicas de la clase
      for clase in self.secuencia:
        # Establecemos la referencia a la clase que estamos comprobando
        ambito.ambito_actual = clase.nombre
        ambito.clase = clase.nombre
        clase.RegistraCaracteristicas(ambito)
      
      # Comprobamos que los tipos están bien
      for clase in self.secuencia:
        # Comprobamos los tipos
        ambito.ambito_actual = clase.nombre
        ambito.clase = clase.nombre
        clase.Tipo(ambito)
      
  
    def str(self, n):
        resultado = super().str(n)
        resultado += f'{" "*n}_program\n'
        resultado += ''.join([c.str(n+2) for c in self.secuencia])
        return resultado

@dataclass
class Caracteristica(Nodo):
    nombre: str = '_no_set'
    tipo: str = '_no_set'
    cuerpo: Expresion = None


@dataclass
class Clase(Nodo):
    nombre: str = '_no_set'
    padre: str = '_no_set'
    nombre_fichero: str = '_no_set'
    caracteristicas: List[Caracteristica] = field(default_factory=list)

    def RegistraCaracteristicas(self, ambito):
      ''' Registra las declaraciones de cada clase.'''
      # Registramos los atributos y metodos conocidos y la clase en la que se definen
      for caracteristica in self.caracteristicas:
        # Anhadimos al ambito la declaración de la característica en la clase
        # dict: key(nombre clase, nombre caracteristica) : value (tipo de la caracteristica)
        
        # Atributos
        if (isinstance(caracteristica, Atributo)):
          # Comprobamos que el atributo no se llame 'self'
          if caracteristica.nombre == "self":
            raise CustomizedException(f"{caracteristica.linea}: 'self' cannot be the name of an attribute.")

          # Comprobamos que el atributo no este ya definido
          tipo_nombre = ambito.busca(caracteristica.nombre, self.nombre)
          if (tipo_nombre != '_no_encontrado'):
            raise CustomizedException(str(caracteristica.linea) + f": Attribute {caracteristica.nombre} is an attribute of an inherited class.")
          # Registra el atributo en la clase
          ambito.dict[(self.nombre, caracteristica.nombre)] = caracteristica.tipo
          
        # Metodos
        if (isinstance(caracteristica, Metodo)):
          # Anhadimos el ambito al arbol de ambitos
          ambito.anhadeAmbito(caracteristica.nombre, self.nombre)
          # Anhadimos el metodo al ambito
          ambito.dict[(self.nombre, caracteristica.nombre)] = caracteristica.tipo
          ambito.dict_metodos[(self.nombre, caracteristica.nombre)] = [caracteristica.nombre] + caracteristica.formales

    def Tipo(self, ambito):
      ''' Comprueba que los tipos estén bien.'''
      # Comprobamos el nombre de la clase
      if (self.nombre in ['Int', 'Bool', 'String']):
        raise CustomizedException(f'{self.linea + 1}: Redefinition of basic class {self.nombre}.')
      
      # Comprobarmos que no hereda de clases basicas
      if (self.padre in ['Int', 'Bool', 'String']):
        raise CustomizedException(f'{self.linea}: Class {self.nombre} cannot inherit class {self.padre}.')

      for caracteristica in self.caracteristicas:
        # Comprobamos que la característica es correcta
        ambito.ambito_actual = self.nombre
        caracteristica.Tipo(ambito)


    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_class\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += f'{(n+2)*" "}{self.padre}\n'
        resultado += f'{(n+2)*" "}"{self.nombre_fichero}"\n'
        resultado += f'{(n+2)*" "}(\n'
        resultado += ''.join([c.str(n+2) for c in self.caracteristicas])
        resultado += '\n'
        resultado += f'{(n+2)*" "})\n'
        return resultado

@dataclass
class Metodo(Caracteristica):
    formales: List[Formal] = field(default_factory=list)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_method\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += ''.join([c.str(n+2) for c in self.formales])
        resultado += f'{(n + 2) * " "}{self.tipo}\n'
        resultado += self.cuerpo.str(n+2)
        return resultado

    def Tipo(self, ambito):
      # Establecemos el nombre del ambito como el nombre del metodo
      ambito.ambito_actual = self.nombre

      # Comprobamos los tipos de los formales
      for formal in self.formales:
        ambito.dict[(self.nombre, formal.nombre_variable)] = formal.tipo

      # comprobamos los formales
      for formal in self.formales:
        formal.Tipo(ambito)

      # Comprobamos el cuerpo
      self.cuerpo.Tipo(ambito)
      
class Atributo(Caracteristica):

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_attr\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += self.cuerpo.str(n+2)
        return resultado

    def Tipo(self, ambito):
        # Establecemos el tipo del cuerpo
        self.cuerpo.Tipo(ambito)