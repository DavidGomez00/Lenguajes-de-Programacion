import os
import re
import sys
from colorama import init
from termcolor import colored
init()


DIRECTORIO = os.path.expanduser(".")
sys.path.append(DIRECTORIO)

from Lexer import *
from Parser import *
from Clases import *

PRACTICA = "03" # Practica que hay que evaluar
DEBUG = True   # Decir si se lanzan mensajes de debug
NUMLINEAS = 5   # Numero de lineas que se muestran antes y después de la no coincidencia
sys.path.append(DIRECTORIO)
DIR = os.path.join(DIRECTORIO, PRACTICA, 'grading')
FICHEROS = os.listdir(DIR)
TESTS = [fich for fich in FICHEROS
         if os.path.isfile(os.path.join(DIR, fich)) and
         re.search(r"^[a-zA-Z].*\.(cool|test|cl)$",fich)]
TESTS.sort()
#TESTS = TESTS
#TESTS = ['badargs1.test']
TESTS = ['cells.cl.test']

if True:
    for fich in TESTS:
        print(fich)
        lexer = CoolLexer()
        f = open(os.path.join(DIR, fich), 'r', newline='')
        g = open(os.path.join(DIR, fich + '.out'), 'r', newline='')
        if os.path.isfile(os.path.join(DIR, fich)+'.nuestro'):
            os.remove(os.path.join(DIR, fich)+'.nuestro')
        if os.path.isfile(os.path.join(DIR, fich)+'.bien'):
            os.remove(os.path.join(DIR, fich)+'.bien')
        texto = ''
        entrada = f.read()
        f.close()
        if PRACTICA == '01':
            texto = '\n'.join(lexer.salida(entrada))
            texto = f'#name "{fich}"\n' + texto
            resultado = g.read()
            g.close()
            texto = re.sub(r'#\d+\b','',texto)
            resultado = re.sub(r'#\d+\b','',resultado)
            if texto.strip().split() != resultado.strip().split():
                print(f"Revisa el fichero {fich}")
                
                if DEBUG:
                    nuestro = [linea for linea in texto.split('\n') if linea]
                    bien = [linea for linea in resultado.split('\n') if linea]
                    linea = 0
                    while nuestro[linea:linea+NUMLINEAS] == bien[linea:linea+NUMLINEAS] and linea < len(bien):
                        linea += 1
                    print(colored('\n'.join(nuestro[linea:linea+NUMLINEAS]), 'white', 'on_red'))
                    print(colored('\n'.join(bien[linea:linea+NUMLINEAS]), 'blue', 'on_green'))
                    f = open(os.path.join(DIR, fich)+'.nuestro', 'w')
                    g = open(os.path.join(DIR, fich)+'.bien', 'w')
                    f.write(texto.strip())
                    g.write(resultado.strip())
                    f.close()
                    g.close()
        elif PRACTICA in ('02', '03'):
            #if fich != 'badargs1.test':
                parser = CoolParser()
                parser.nombre_fichero = fich
                parser.errores = []
                bien = ''.join([c for c in g.readlines() if c and '#' not in c])
                g.close()
                j = parser.parse(lexer.tokenize(entrada))
                resultado = ''
                try:
                    if j and not parser.errores:

                        if PRACTICA in ('03'):
                            # Modificar el resultado
                            j.Tipo()  # Ambito y herencias
                            resultado = '\n'.join([c for c in j.str(0).split('\n')
                                                if c and '#' not in c])
                    else:
                        resultado = '\n'.join(parser.errores)
                        resultado += '\n' + "Compilation halted due to lex and parse errors"
                # Excepciones de la practica 3
                except CustomizedException as e:
                    resultado += '\n' + fich + ':' + e.args[0]
                    resultado += '\n' + "Compilation halted due to static semantic errors."
                # Excepciones generales
                except Exception as e:
                    import traceback
                    print(traceback.format_exc())
                    pass
                
                if resultado.lower().strip().split() != bien.lower().strip().split():
                    print(f"Revisa el fichero {fich}")
                    if DEBUG:
                        nuestro = [linea for linea in resultado.split('\n') if linea]
                        bien = [linea for linea in bien.split('\n') if linea]
                        linea = 0
                        while nuestro[linea:linea+NUMLINEAS] == bien[linea:linea+NUMLINEAS] and linea < len(bien):
                            linea += 1
                        print(colored('\n'.join(nuestro[linea:linea+NUMLINEAS]), 'white', 'on_red'))
                        print(colored('\n'.join(bien[linea:linea+NUMLINEAS]), 'blue', 'on_green'))
                        f = open(os.path.join(DIR, fich)+'.nuestro', 'w')
                        g = open(os.path.join(DIR, fich)+'.bien', 'w')
                        f.write(resultado.strip())
                        g.write('\n'.join(bien).strip())
                        f.close()
                        g.close()
            
              

