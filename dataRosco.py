# -*- coding: utf-8 -*-
import re
import os
from scraperRae import scraperRae
from sonidos import generaAudio
import basededatos

letraOrd = {0:'a', 1:'b', 2:'c', 3:'d', 4:'e', 5:'f', 6:'g', 7:'h', 8:'i', 9:'j', 10:'l', 11:'m', 12:'n', 13:'ñ', 14:'o', 15:'p', 16:'q', 17:'r', 18:'s', 19:'t', 20:'u', 21:'v', 22:'x', 23:'y', 24:'z'}

# Genera la informacion necesaria para jugar un rosco a partir de un
#   listado ordenado de diccID
def roscoDesdeDiccid(preRosco):
    bd = basededatos.diccEnBD()
    print(preRosco)
    rosco = {}
    for i in range(int(len(preRosco)/2)):
    #for i in range(25):
        if preRosco[i*2]:
            print("i = "+str(i)+" // ID = "+preRosco[i*2])
            entrada = {}
            definicion = bd.definicionDesdeDiccid(preRosco[i*2])
            letra = letraOrd[i]
            prefix = lambda x: letra+", " if x[0]==letra else "Contiene la "+letra+", "
            if letra=='y':
                letra="y griega"
            prefijo = prefix(letra)
            entrada["definicion"] = prefijo+definicion[1].split('‖')[0]
            palabra = preRosco[i*2]
            entrada["audio"] = generaAudio(palabra,entrada["definicion"])
            listaSoluciones = []
            for solucionID in preRosco[i*2+1]:
                soluciones = bd.solucionesDesdeDiccid(solucionID)
                listaSoluciones.append(soluciones)
            entrada["solucion"] = list(set([item for sublist in listaSoluciones for item in sublist]))
            print(entrada["solucion"])
            entrada["largo"] = len(entrada["definicion"])
            rosco[letra[0]] = entrada
    return rosco

# Genera el listado ordenado de diccID a partir de un listado ordenado
#  de palabra-acepcion
def diccidRosco(prerosco):
    bd = basededatos.diccEnBD()
    rosco = []
    for i in range(len(prerosco)):
        muchassoluciones = prerosco[i]
        definicionSinLeer = True
        id = None

        listaSolucionesID = []
        for unasolucion in muchassoluciones:
            solucion = unasolucion.split('*')
            if "¿?¿?¿?" not in solucion[0]:
                # OJO, paso la solucion[0], vale decir, sin el *
                if len(solucion) == 1:
                    diccid = bd.consultarGuardar(solucion[0])
                else:
                    diccid = bd.consultarGuardarEnlaza(solucion[0])

                # MANEJO DE ERROR EN LA BUSQUEDA EN LA BD
                if not diccid or not diccid[1]:
                    print("\n\n\nSe encontró un error en la búsqueda. La consulta era por: "+solucion[0]+"\n")
                    diccionario = bd.entregarDiccionario(solucion[0])
                    if not diccionario:
                        print("Resultado vacío, quizás faltó incluir la entrada en la palabra, particularmente si es verbo.\n")
                        input("Presione una tecla para continuar")
                    else:
                        print("Quizás hay error en la falta del tilde o se pidió una acepción inexistente")
                        for tupla in diccionario:
                            print(tupla)
                        input("Presione una tecla para continuar")

                if definicionSinLeer and diccid and diccid[1]:
                    id = diccid[1]
                    diccid = bd.consultarPalabra(solucion[0])

                # FALTA LEER TODAS LAS VARIANTES -- masculino, femenino, pluralf, pluralm, pronominal.
                listaSolucionesID.append(diccid[1])

            else:
                print("\nPalabra desconocida --nunca leída-- en el rosco para la letra "+letraOrd[i]+"\n")
                id = None
                listaSolucionesID = None
                break

        if listaSolucionesID:
            listaSolucionesID = list(set(listaSolucionesID))
        rosco.append(id)
        rosco.append(listaSolucionesID)
    return rosco

def opcionValidaStr(listado):
    listado.append(str(0))
    correcto = False
    while not correcto:
        try:
            opcion = input("\n... ")
            if opcion in listado:
                correcto = True
            else:
                print("Opcion errónea,escribió "+str(opcion)+" pero las opciones válidas son "+str(listado))
        except ValueError:
            print("Anotó una opción no válida. Intente nuevamente.")
    return opcion

def opcionValida(listado):
    listado.append(0)
    correcto = False
    while not correcto:
        try:
            opcion = int(input("\n... "))
            if opcion in listado:
                correcto = True
            else:
                print("Opcion errónea,escribió "+str(opcion)+" pero las opciones válidas son "+str(listado))
        except ValueError:
            print("Anotó una opción no válida. Intente nuevamente.")
    return opcion

def bdRosco():
    print("\nElija una opción:\n")
    print("1.- Cargar Rosco CHV")
    print("2.- Mostrar Jugadores")
    print("3.- Mostrar Roscos Ganadores")
    print("0.- Salir")
    opcion = opcionValida([1,2,3])

    if opcion == 1:
        bd = basededatos.chvEnBD()
        roscos = bd.consultarRoscosDisponibles()
        print("\nRoscos disponibles: "+str(roscos))
        roscoid = opcionValida([x[0] for x in roscos])
        if roscoid > 0:
            roscodiccid=bd.consultarRosco(roscoid)
            roscoDesdeDiccid([x for x in roscodiccid[0]])

    elif opcion == 2:
        bd = basededatos.chvEnBD()
        jugadores = bd.consultarJugadores()
        print("\nJugadores Disponibles: "+str(jugadores))
        jugador = opcionValidaStr([x[0] for x in jugadores])
        if jugador != 0:
            roscos=bd.consultarRoscosDeJugador(jugador)
            print("\nRoscos de "+jugador+": "+str(roscos))
            roscoid = opcionValida([x[0] for x in roscos])
            if roscoid > 0:
                roscodiccid=bd.consultarRosco(roscoid)
                roscoDesdeDiccid([x for x in roscodiccid[0]])

    elif opcion == 3:
        bd = basededatos.chvEnBD()
        ganadores = bd.consultarGanadores()
        print("\nRoscos ganadores: "+str(ganadores))
        roscoid = opcionValida([x[0] for x in ganadores])
        if opcion > 0:
            roscodiccid=bd.consultarRosco(roscoid)
            roscoDesdeDiccid([x for x in roscodiccid[0]])

    else:
        pass

def leeRosco(preRosco):
    nombreArchivo = input("Ingrese el nombre del archivo: ")
    if nombreArchivo == '':
        nombreArchivo = "rosco0.txt"
    archivo = open(nombreArchivo,'r')
    for linea in archivo:
        preRosco.append(linea.rstrip().split(':')[1].split(';'))
    preRosco = [list(map(lambda x: x.strip() , subRosco)) for subRosco in preRosco]
    corchetes = re.compile('(\ \[|\])|\)')
    parentesis = re.compile(' \(')
    asterisco = re.compile(' \*')
    preRosco = [list(map(lambda x: re.sub(asterisco,'*',x) , subRosco)) for subRosco in preRosco]
    preRosco = [list(map(lambda x: re.sub(corchetes,'',x) , subRosco)) for subRosco in preRosco]
    preRosco = [list(map(lambda x: re.sub(parentesis,'_',x) , subRosco)) for subRosco in preRosco]
    preRosco = [list(map(lambda x: x if x[-2] == '_' else x+"_1" , subRosco)) for subRosco in preRosco]

    print(preRosco)
    return preRosco

def generaRosco():
    if not os.path.exists("audio"):
        os.makedirs("audio")
    preRosco = []
    rosco = {}
    preRosco = leeRosco(preRosco)
    casiRosco = diccidRosco(preRosco)
    rosco = roscoDesdeDiccid(casiRosco)
    for letra in rosco:
        print(str(letra))
        print(str(rosco[letra]["audio"]))
        print(str(rosco[letra]["solucion"]))
        print(str(rosco[letra]["definicion"]))
    print("El numero de caracteres del rosco totaliza: "+str(sum(letra["largo"] for letra in rosco.values())))
    return rosco

if __name__ == '__main__':
    #generaRosco()
    bdRosco()
