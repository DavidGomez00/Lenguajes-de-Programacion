# coding: utf-8
from dataclasses import dataclass, field
from typing import List
from anytree import Node, RenderTree, PreOrderIter
from collections import defaultdict

class CustomizedException(Exception):
  pass
  
class Ambito():
  '''Clase auxiliar para determinar 
  el tipo de elemento.
  '''

  # Diccionario que guarda donde se han declarado los metodos y atributos y su tipo
  dict = defaultdict(str)
  # Referencia a la clase que estamos analizando
  clase_actual = None

  def __init__(self):
    ''' Instancia un ámbito.'''
    # Registro de las clases y herencias
    self.arbol_clases = Node("ROOT")

  def anhadeClase(self, clase):
    ''' Anhade un elemento al ambito. '''
    # Buscamos el nodo que referencia a la clase padre
    nodo_padre = [node 
      for node in PreOrderIter(self.arbol_clases)
      if node.name == clase.padre]
    
    # Si no se encuentra el padre, depende de ROOT
    if (len(nodo_padre) == 0):
      # Creamos la relación de herencia
      Node(clase.nombre, parent=self.arbol_clases)
    else:
      # Creamos la relación de herencia
      Node(clase.nombre, parent=nodo_padre[0])

    # Anhadimos la clase al ambito
    self.dict[('ROOT', clase.nombre)] = clase.nombre

  def busca(self, nombre:str, clase:str=None):
    ''' Encuentra el tipo de nombre. Si no esta asignado retorna _no_encontrado.
    '''
    # En caso de no especificar la clase desde la que buscar, usamos la clase actual
    if (clase is None): 
      clase = self.clase_actual.nombre
    
    # Nodo correspondiente a la clase desde la que buscamos
    nodo_actual = [nodo 
                  for nodo in PreOrderIter(self.arbol_clases) # Todos los nodos del arbol
                  if nodo.name == clase][0]                   # Solo aquel cuyo nombre coincide
    
    # Consigo todas las tuplas de (clase, atributo) para la clase y sus padres
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
                for clase in PreOrderIter(ambito.arbol_clases)
                if clase.name == self.tipo]
        # Si la longitud de la lista es 0, es que no ha encontrado la clase
        if len(clase) == 0:
          # Lanzar Error
          pass
      

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

      # Buscamos el tipo del método
      tipo_metodo = ambito.busca(self.nombre_metodo, self.cuerpo.cast)

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
      # Falta por implementar
      pass


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
      # Falta por implementar
      pass


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
class RamaCase(Nodo):
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
      # Falta implementar
      pass

@dataclass
class Swicht(Nodo):
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
      # Falta implementar
      pass

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
      clase = [clase for clase in PreOrderIter(ambito.arbol_clases)
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
      self.cast = 'Bool'


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
      self.cast = 'Bool'


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
      self.cast = 'Bool'


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
          pass
      
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
        # Buscamos este objeto en el ambito
        tipo = ambito.busca(self.nombre)
        if (tipo == '_no_encontrado'):
          raise CustomizedException(f'{self.linea}: Undeclared identifier {self.nombre}.')


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
      
      # Construimos el arbol de herencias
      for clase in self.secuencia:
        # Utilizar un arbol para registrar la herencia
        ambito.anhadeClase(clase)
   
      # Comprobamos con la funcion Tipo que los tipos de dato son correctos
      for clase in self.secuencia:
        # Establecemos la referencia a la clase que estamos comprobando
        ambito.clase_actual = clase
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

    def Tipo(self, ambito):
      # Registramos los atributos y metodos conocidos y la clase en la que se definen
      for caracteristica in self.caracteristicas:
        # Comprobamos que la característica es correcta
        caracteristica.Tipo(ambito)
  
        # Anhadimos al ambito la declaración de la característica en la clase
        # dict: key(nombre clase, nombre caracteristica) : value (tipo de la caracteristica)
        ambito.dict[(self.nombre, caracteristica.nombre)] = caracteristica.tipo


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
        # Comprobamos que tenga un error válido
        if self.nombre == "self":
          raise CustomizedException(str(self.linea) + ": 'self' cannot be the name of an attribute.")

        # Comprobar que el nombre del atributo no exista ya
        tipo_nombre = ambito.busca(self.nombre)

        # El atributo ya esta declarado
        if (tipo_nombre != '_no_encontrado'):
          raise CustomizedException(str(self.linea) + f": Attribute {self.nombre} is an attribute of an inherited class.")
      
        # Establecemos el tipo del cuerpo
        self.cuerpo.Tipo(ambito)