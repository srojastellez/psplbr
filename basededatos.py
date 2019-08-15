# -*- coding: utf-8 -*-

from scraperRae import scraperRae, scraperRaeID
import psycopg2
import re
import ortografia

class postgreBD:
    def __init__(self):
        nombreArchivo="conexionbd.txt"
        archivo = open(nombreArchivo,'r')
        datos = list(archivo)
        archivo.close()
        try:
            self.conn = psycopg2.connect("dbname=DLE user="+datos[0]+" password="+datos[1])
            self.cur = self.conn.cursor()
        except psycopg2.Error as e:
            print('ERROR: '+e)
    def __enter__(self):
        return self
    def __exit__(self, exception_type, exception_value, traceback):
        self.cur.close()
        self.conn.close()



class chvEnBD:
    def __init__(self):
        self.something = 0

    def consultarRoscosDisponibles(self):
        with postgreBD() as bd:
            SQL = 'SELECT roscoid FROM programachv ORDER BY roscoid;'
            try:
                bd.cur.execute(SQL)
                print("Buscando el listado de roscos")
            except Exception as e:
                print(e)
            bd.conn.commit()
            tuplas = bd.cur.fetchall()
        return tuplas

    def consultarJugadores(self):
        with postgreBD() as bd:
            SQL = 'SELECT jugador FROM programachv GROUP BY jugador ORDER BY jugador;'
            try:
                bd.cur.execute(SQL)
                print("Buscando el listado de jugadores")
            except Exception as e:
                print(e)
            bd.conn.commit()
            tuplas = bd.cur.fetchall()
        return tuplas

    def consultarGanadores(self):
        with postgreBD() as bd:
            SQL = 'SELECT roscoid , jugador FROM programachv WHERE buenas=25;'
            try:
                bd.cur.execute(SQL)
                print("Buscando el listado de roscos ganadores")
            except Exception as e:
                print(e)
            bd.conn.commit()
            tuplas = bd.cur.fetchall()
        return tuplas

    def consultarRoscosDeJugador(self,jugador):
        with postgreBD() as bd:
            SQL = 'SELECT roscoid FROM programachv WHERE jugador=%s ORDER BY roscoid;'
            data = (jugador,)
            try:
                bd.cur.execute(SQL,data)
                print("Buscando el listado de roscos del jugador "+jugador)
            except Exception as e:
                print(e)
            bd.conn.commit()
            tuplas = bd.cur.fetchall()
        return tuplas

# TODO: Buscar datos para mostrar resultados de un capitulo
    def consultarCapitulo(self):
        with postgreBD() as bd:
            pass

# TODO: Buscar datos para generar estadisticas de un jugador
    def consultarJugador(self):
        with postgreBD() as bd:
            pass

    def consultarRosco(self,roscoid):
        with postgreBD() as bd:
            SQL = 'SELECT a,asol,b,bsol,c,csol,d,dsol,e,esol,f,fsol,g,gsol,h,hsol,i,isol,j,jsol,l,lsol,m,msol,n,nsol,ñ,ñsol,o,osol,p,psol,q,qsol,r,rsol,s,ssol,t,tsol,u,usol,v,vsol,x,xsol,y,ysol,z,zsol FROM roscochv WHERE roscoid=%s;'
            data = (roscoid,)
            try:
                bd.cur.execute(SQL,data)
                print("Buscando el rosco "+roscoid)
            except Exception as e:
                print(e)
            bd.conn.commit()
            tuplas = bd.cur.fetchall()
        return tuplas


    def guardarCapitulo(self,capitulo):
        with postgreBD() as bd:
            for i in [0,1]:
                cap = capitulo[i][0]
                print(cap)
                roscoid = cap['roscoid']
                SQL = 'INSERT INTO programachv (fecha, jugador, tiempo, equipo, buenas, malas, roscoid, capitulo, tipo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
                data = (cap['fecha'], cap['jugador'], cap['tiempoinicial'], cap['equipo'], cap['buenas'], cap['malas'], roscoid, cap['capitulo'], cap['tipo'])
                try:
                    bd.cur.execute(SQL,data)
                    print("Agregando el capitulo "+str(cap['capitulo'])+" y la info del equipo "+cap['equipo'])
                except Exception as e:
                    print(e)
                    bd.conn.rollback()
                bd.conn.commit()
                cap = capitulo[i][1]
                print(cap)
                SQL = 'INSERT INTO roscochv (roscoid, a, asol, b, bsol, c, csol, d, dsol, e, esol, f, fsol, g, gsol, h, hsol, i, isol, j, jsol, l, lsol, m, msol, n, nsol, ñ, ñsol, o, osol, p, psol, q, qsol, r, rsol, s, ssol, t, tsol, u, usol, v, vsol, x, xsol, y, ysol, z, zsol) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                #SQL = 'INSERT INTO roscochv (roscoid, a, b, c, d, e, f, g, h, i, j, l, m, n, ñ, o, p, q, r, s, t, u, v, x, y, z) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                #data = (roscoid, cap['a'], cap['b'], cap['c'], cap['d'], cap['e'], cap['f'], cap['g'], cap['h'], cap['i'], cap['j'], cap['k'], cap['l'], cap['m'], cap['n'], cap['ñ'], cap['o'], cap['p'], cap['q'], ap['r'], cap['s'], cap['t'], cap['u'], cap['v'], cap['x'], cap['y'], cap['z'])
                #data = (roscoid, cap[0], cap[1], cap[2], cap[3], cap[4], cap[5], cap[6], cap[7], cap[8], cap[9], cap[10], cap[11], cap[12], cap[13], cap[14], cap[15], cap[16], cap[17], cap[18], cap[19], cap[20], cap[21], cap[22], cap[23], cap[24])
                data = (roscoid, cap[0], cap[1], cap[2], cap[3], cap[4], cap[5], cap[6], cap[7], cap[8], cap[9], cap[10], cap[11], cap[12], cap[13], cap[14], cap[15], cap[16], cap[17], cap[18], cap[19], cap[20], cap[21], cap[22], cap[23], cap[24], cap[25], cap[26], cap[27], cap[28], cap[29], cap[30], cap[31], cap[32], cap[33], cap[34], cap[35], cap[36], cap[37], cap[38], cap[39], cap[40], cap[41], cap[42], cap[43], cap[44], cap[45], cap[46], cap[47], cap[48], cap[49])
                try:
                    bd.cur.execute(SQL,data)
                    print("Agregando rosco "+str(roscoid))
                except Exception as e:
                    print(e)
                    bd.conn.rollback()
                bd.conn.commit()

    # Definido por si acaso.
    def actualizar(self):
        pass



class diccEnBD:
    def __init__(self):
        self.something = 0

    def consultarGuardar(self,consulta):
        print("en consultarGuardar llegó la consulta: "+consulta)
        definicion = self.consultarPalabra(consulta)
        if not definicion:
            palabra = consulta.split('*')[0].split('_')
            print("Palabra no encontrada. Preguntando en el DLE para guardar")
            diccionario = scraperRae([[palabra[0], 0]])
            self.guardar(diccionario)
            print(diccionario)
            definicion = self.consultarPalabra(consulta)
            print("Despues de guardar: "+str(definicion)+" "+str(consulta))

            for acepcion in diccionario[0]["acepciones"]:
                if acepcion["enlaza"]:
                    id = acepcion["enlaza"].split('#')[0]
                    palabra = self.consultarLookupID(id)
                    if not palabra:
                        diccionario = scraperRaeID(id)
                        self.guardar(diccionario)
                        print(diccionario)
                        print("Después de guardar la palabra enlazada")
        return definicion

    def consultarGuardarEnlaza(self,consulta):
        print("en consultarGuardarEnlaza llegó la consulta: "+consulta)
        resultadoConsulta = self.consultarPalabra(consulta)
        if not resultadoConsulta:
            resultadoConsulta = self.consultarGuardar(consulta)
        diccid = resultadoConsulta[2].split('#')[1]
        if diccid:
            print(diccid)
            tupla = self.consultarDiccID(diccid)
        else:
            # TODO: Pendiente... primero tengo que encontrar un caso
            #       particular para implementarlo, donde en ENLAZA
            #       usa el lookupid y no el diccid.
            #       ¿Apunta únicamente a palabras con una sola
            #       acepción? ¿O pueden haber múltiples acepciones?
            lookupid = resultadoConsulta[2].split('#')[0]
            return None
        if not tupla:
            lookupid = resultadoConsulta[2].split('#')[0]
            diccionario = scraperRaeID(lookupid)
            self.guardar(diccionario)
            print(diccionario)
            print("Después de guardar la palabra enlazada")
            tupla = self.consultarDiccID(diccid)
        return tupla[0]

    def consultarDiccID(self,id):
        SQL = 'SELECT l.palabra, d.diccid, d.definicion FROM diccionario d JOIN lookup l ON d.lookupid=l.lookupid WHERE d.diccid = %s;'
        data = (id,)
        with postgreBD() as bd:
            try:
                bd.cur.execute(SQL,data)
                print("Consultando el diccID: "+id+" en la BD")
            except Exception as e:
                bd.conn.rollback()
            bd.conn.commit()
            tuplas = bd.cur.fetchall()
            if not tuplas:
                print("Palabra no encontrada")
                tuplas = None
        return tuplas

    def consultarLookupID(self,id):
        SQL = 'SELECT palabra FROM lookup WHERE lookupid = %s;'
        data = (id,)
        with postgreBD() as bd:
            try:
                bd.cur.execute(SQL,data)
                print("Consultando el lookupID: "+id+" en la BD")
            except Exception as e:
                bd.conn.rollback()
            bd.conn.commit()
            palabra = bd.cur.fetchall()
            if not palabra:
                print("Palabra no encontrada")
        return palabra

    def consultarPalabra(self,consultaOrig):
        consulta = consultaOrig.split('*')[0]
        palabra = consulta.split('_')
        acep = palabra[1]

        # TODO: revisar si el else incluye entrada=None y se deja el
        #       query SQL mas extenso y unico fuera del if
        if palabra[0][-1].isnumeric():
            palabraE = palabra[0].lower()
            entrada = palabra[0][-1]
            palabra = palabraE[:-1]
            SQL = 'SELECT dic.definicion, dic.diccid, dic.enlaza FROM diccionario dic JOIN lookup lu ON dic.lookupid=lu.lookupid  WHERE (lu.palabra = %s OR lu.masculino = %s OR lu.femenino = %s OR lu.pluralf = %s or lu.pluralm = %s or lu.pronominal = %s or lu.alt = %s) AND lu.entrada = %s AND dic.acepcion = %s;'
            data = (palabra,palabra,palabra,palabra,palabra,palabra,palabra,entrada,acep)
        else:
            palabra=palabra[0].lower()
            SQL = 'SELECT dic.definicion, dic.diccid, dic.enlaza FROM diccionario dic JOIN lookup lu ON dic.lookupid=lu.lookupid  WHERE (lu.palabra = %s OR lu.masculino = %s OR lu.femenino = %s OR lu.pluralf = %s OR lu.pluralm = %s OR lu.pronominal = %s OR lu.alt =%s) AND dic.acepcion = %s;'
            data = (palabra,palabra,palabra,palabra,palabra,palabra,palabra,acep)
        with postgreBD() as bd:
            try:
                bd.cur.execute(SQL,data)
                print("Consultando "+palabra+" ("+acep+") en la BD")
            except Exception as e:
                bd.conn.rollback()
            bd.conn.commit()
            definicion = bd.cur.fetchone()
            if definicion is not None:
                if len(consultaOrig.split('*')) < 2:
                    print("Definicion = "+definicion[0]+" // y el diccid = "+definicion[1])
                else:
                    codigo = definicion[2]
                    SQL = 'SELECT dic.definicion, dic.diccid, dic.enlaza FROM diccionario dic WHERE dic.diccid = %s;'
                    data = (codigo,)
                    with postgreBD() as bd:
                        try:
                            bd.cur.execute(SQL,data)
                            print("Consultando diccid o lookupid "+codigo+" en la BD")
                        except Exception as e:
                            bd.conn.rollback()
                        bd.conn.commit()
                        definicion = bd.cur.fetchone()
        return definicion

    def entregarDiccionario(self,consulta):
        palabra = consulta.split('_')
        acep = palabra[1]

        palabra=palabra[0].lower()
        SQL = 'SELECT lu.palabra, lu.entrada, lu.lookupid, lu.alt, lu.masculino, lu.femenino, lu.pluralm, lu.pluralf, lu.pronominal, dic.acepcion, dic.info, dic.definicion, dic.diccid FROM lookup lu FULL OUTER JOIN diccionario dic ON dic.lookupid=lu.lookupid  WHERE lu.palabra = %s OR lu.masculino = %s OR lu.femenino = %s OR lu.pluralf = %s or lu.pluralm = %s or lu.pronominal = %s or lu.alt = %s;'
        data = (palabra,palabra,palabra,palabra,palabra,palabra,palabra)
        with postgreBD() as bd:
            try:
                bd.cur.execute(SQL,data)
                print("Consultando __"+palabra+"__ en la BD")
            except Exception as e:
                bd.conn.rollback()
            bd.conn.commit()
            definicion = bd.cur.fetchall()
        return definicion

    def solucionesDesdeDiccid(self,id):
        SQL = 'SELECT d.info, l.palabra, l.pronominal, l.masculino, l.pluralm, l.femenino, l.pluralf, l.alt FROM diccionario d JOIN lookup l ON d.lookupid=l.lookupid WHERE d.diccid=%s;'
        data = (id,)
        with postgreBD() as bd:
            try:
                bd.cur.execute(SQL,data)
                print("Consultando diccid "+id+" en la BD")
            except Exception as e:
                print(e)
                bd.conn.rollback()
            bd.conn.commit()
            diccionario = bd.cur.fetchone()

        info = diccionario[0]
        soluciones = []
        if "masculino" in info or "adjetivo" in info:
            if "plural" in info and not "en plural" in info:
                soluciones.append(diccionario[4])
            elif "plural" in info:
                soluciones.append(diccionario[4])
                soluciones.append(diccionario[3])
            else:
                soluciones.append(diccionario[3])
        #if "femenino" in info or "adjetivo" in info:
        if "femenino" in info:
            if "plural" in info and not "en plural" in info:
                soluciones.append(diccionario[6])
            elif "plural" in info:
                soluciones.append(diccionario[6])
                soluciones.append(diccionario[5])
            else:
                soluciones.append(diccionario[5])
        if "transitivo" in info:
            if "pronominal" in info and not "como pronominal" in info:
                soluciones.append(diccionario[2])
            elif "pronominal" in info:
                soluciones.append(diccionario[2])
                soluciones.append(diccionario[1])
            else:
                soluciones.append(diccionario[1])
        if diccionario[7]:
            soluciones.append(diccionario[7])

        return soluciones

    def definicionDesdeDiccid(self,id):
        SQL = 'SELECT l.palabra, d.definicion FROM diccionario d JOIN lookup l ON d.lookupid=l.lookupid WHERE d.diccid=%s;'
        data = (id,)
        with postgreBD() as bd:
            try:
                bd.cur.execute(SQL,data)
                print("Consultando diccid "+id+" en la BD")
            except Exception as e:
                print(e)
                bd.conn.rollback()
            bd.conn.commit()
            diccionario = bd.cur.fetchone()
        return diccionario


    def actualizar(self,diccionario):
        with postgreBD() as bd:
            for entrada in diccionario:
                SQL = 'UPDATE diccionario SET definicion = %s, info = %s WHERE diccid = %s;'
                data = (entrada["acepciones"]["definicion"],entrada["info"],entrada["diccID"])
                try:
                    bd.cur.execute(SQL,data)
                    print("Actualizando diccID: "+entrada["diccID"]+" en la BD")
                except:
                    bd.conn.rollback()
            bd.conn.commit()

    def guardar(self,diccionario):
        with postgreBD() as bd:
            for entrada in diccionario:
                SQL1 = 'INSERT INTO lookup (lookupid, palabra, entrada, origen, alt, pronominal, femenino, masculino, pluralf, pluralm) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
                data1 = (entrada["lookupID"],entrada["palabra"],entrada["entrada"],entrada["origen"],entrada["alt"],entrada["pronominal"],entrada["singularf"],entrada["singularm"],entrada["pluralf"],entrada["pluralm"])
                try:
                    bd.cur.execute(SQL1,data1)
                    print("Agregando la palabra "+entrada["palabra"]+"--"+str(entrada["entrada"]))
                except Exception as e:
                    print(e)
                    bd.conn.rollback()
                    # El continue depende si al buscar una palabra se agregan todas las acepciones o solo la que se buscó.
                    #continue
                for acepcion in entrada["acepciones"]:
                    SQL2 = 'INSERT INTO diccionario (lookupid, diccid, acepcion, definicion, info, enlaza) VALUES (%s, %s, %s, %s, %s, %s);'
                    data2 = (entrada["lookupID"],acepcion["diccID"],acepcion["acepcion"].split('.')[0],acepcion["definicion"],acepcion["info"],acepcion["enlaza"])
                    try:
                        bd.cur.execute(SQL2,data2)
                        print("Agregada la acepcion "+acepcion["acepcion"])
                    except Exception as e:
                        print(e)
                        bd.conn.rollback()
            bd.conn.commit()
        return diccionario

    def guardarDefinicionesEnlaza(self):
        with postgreBD() as bd:
            SQL="SELECT substring(d.enlaza,1,7) AS link FROM diccionario d WHERE d.enlaza IS NOT NULL AND substring(d.enlaza,1,7) NOT IN (SELECT lookupid FROM lookup) GROUP BY link;"
            try:
                bd.cur.execute(SQL)
                print("Buscando enlaces en el diccionario")
            except Exception as e:
                print(e)
                bd.conn.rollback()
            bd.conn.commit()
            listado = bd.cur.fetchall()
            print(str(len(listado)))
            for tupla in listado:
                print("\n\n\n\nRevisando la siguiente tupla")
                id = tupla[0].split('#')[0]
                diccionario = scraperRaeID(id)
                self.guardar(diccionario)
                print(diccionario)



def testConsultarGuardar():
    bd = diccEnBD()
    definicion = bd.consultarGuardar("manilargo_2")
    print(definicion)

def testConsultar():
    bd = diccEnBD()
    definicion = bd.consultar("sapo, pa_13")
    print(definicion)

def testActualizar():
    bd = diccEnBD()
    palabra="sapo"
    acepcion=0
    diccionario=scraperRae(palabra,acepcion)
    bd.guardar(diccionario)

def testGuardar():
    bd = diccEnBD()
    """
    busqueda = [["sendos",0], ["insolar",0], ["príncipe",0], ["ñoqui",0], ["rey",0], ["volar",0,], ["sapo",13], ["mesón2",1], ["sapear",2], ["hoz",0], ["hoz",0], ["caballo",2], ["caballo",1], ["hoz2",1]]
    diccionario=scraperRae(busqueda)
    bd.guardar(diccionario)
    """
    palabra1="ceviche"
    acepcion1=0
    palabra2="león"
    acepcion2=1
    diccionario=scraperRae([[palabra1,acepcion1], [palabra2,acepcion2]])
    bd.guardar(diccionario)

def tryGuardarDefinicionesEnlaza():
    bd = diccEnBD()
    bd.guardarDefinicionesEnlaza()

if __name__ == '__main__':
    #testConsultarGuardar()
    #testGuardar()
    #testUpdatePalabraEntrada()
    #tryNewFem()
    #doFixFem()
    #tryGuardarDefinicionesEnlaza()
    pass
