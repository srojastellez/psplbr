# -*- coding: UTF-8 -*-
import re
import requests
from datetime import date
from bs4 import BeautifulSoup
from basededatos import chvEnBD
from dataRosco import diccidRosco, roscoDesdeDiccid
from time import sleep

colordict={ 'color:#0000ff;':'azul', 'color:#ff6600;':'naranjo'}
mesdict={'Enero':1, 'Febrero':2, 'Marzo':3, 'Abril':4, 'Mayo':5, 'Junio':6, 'Julio':7, 'Agosto':8, 'Septiembre':9, 'Octubre':10, 'Noviembre':11, 'Diciembre':12}

def getInfo(capitulo,informacion,titulo,colores):
    datos = re.sub('[\(\[{]',';',informacion)
    datos = re.sub('[\)\]}]','',datos)
    datos = datos.split(';')
    numero = int(titulo[0].strip()[1:])
    fecha = titulo[1].strip().split('[')[0].split(' ')
    capitulo['capitulo'] = numero
    capitulo['fecha'] = date(int(fecha[4]), mesdict[fecha[2]], int(fecha[0]))
    n = int(datos[0].split(' ')[1])
    capitulo['equipo'] = colordict[colores[n-1].attrs['style']]
    capitulo['roscoid'] = (numero-1)*2+n
    capitulo['jugador'] = datos[1].strip()
    capitulo['tiempoinicial'] = int(datos[2])
    puntaje = datos[3].split('/')
    capitulo['buenas'] = int(puntaje[0])
    capitulo['malas'] = int(puntaje[1])
    return capitulo

def scraperCapituloCHV(prerosco,pagina):
    corchetes = re.compile('(\ \[|\])|\)')
    parentesis = re.compile(' \(')
    asterisco = re.compile(' \*')
    page = requests.get(pagina)
    print("Leyendo página "+pagina+"\n")
    soup = BeautifulSoup(page.content,'html.parser')
    titulo = soup.find(class_='entry-title').get_text().split('–')
    contenido = soup.find(class_='entry-content')
    colores = contenido.find_all('span')
    texto = contenido.get_text()
    lista = texto.split('\n')
    capitulo={}
    informacion = lista[1]
    capitulo = getInfo(capitulo,informacion,titulo,colores)
    rosco1 = []
    for i in range(2,27):
      rosco1.append(lista[i].rstrip().split(':')[1].split(';'))
    rosco1 = [list(map(lambda x: x.strip() , subRosco)) for subRosco in rosco1]
    rosco1 = [list(map(lambda x: re.sub('\xa0',' ',x), subRosco)) for subRosco in rosco1]
    rosco1 = [list(map(lambda x: re.sub(asterisco,'*',x) , subRosco)) for subRosco in rosco1]
    rosco1 = [list(map(lambda x: re.sub(corchetes,'',x) , subRosco)) for subRosco in rosco1]
    rosco1 = [list(map(lambda x: re.sub(parentesis,'_',x) , subRosco)) for subRosco in rosco1]
    rosco1 = [list(map(lambda x: x if x[-2] == '_' else x+"_1" , subRosco)) for subRosco in rosco1]

    equipoRosco1 = (capitulo, rosco1)
    prerosco.append(equipoRosco1)

    capitulo={}
    informacion = lista[27]
    capitulo = getInfo(capitulo,informacion,titulo,colores)
    rosco2 = []
    for i in range(28,53):
      rosco2.append(lista[i].rstrip().split(':')[1].split(';'))
    rosco2 = [list(map(lambda x: x.strip() , subRosco)) for subRosco in rosco2]
    rosco2 = [list(map(lambda x: re.sub('\xa0',' ',x), subRosco)) for subRosco in rosco2]
    rosco2 = [list(map(lambda x: re.sub(asterisco,'*',x) , subRosco)) for subRosco in rosco2]
    rosco2 = [list(map(lambda x: re.sub(corchetes,'',x) , subRosco)) for subRosco in rosco2]
    rosco2 = [list(map(lambda x: re.sub(parentesis,'_',x) , subRosco)) for subRosco in rosco2]
    rosco2 = [list(map(lambda x: x if x[-2] == '_' or x[-3] == '_' else x+"_1" , subRosco)) for subRosco in rosco2]

    equipoRosco2 = (capitulo, rosco2)
    prerosco.append(equipoRosco2)


    return prerosco

def scraperSitioPSPLBR(rip=False):
    lista = []
    if rip:
        page = requests.get("https://psplbr.wordpress.com/")
        soup = BeautifulSoup(page.content,'html.parser')
        archives = soup.find(class_='widget widget_archive')
        for link in archives.find_all('li'):
            largo = int(link.getText().split('(')[1].split(')')[0])
            pagina = link.a.get("href")
            if largo > 14:
                lista.append(pagina+"page/3")
            if largo > 7:
                lista.append(pagina+"page/2")
            lista.append(pagina)
        print(lista)
    else:
        lista=['https://psplbr.wordpress.com/2018/08/page/3', 'https://psplbr.wordpress.com/2018/08/page/2', 'https://psplbr.wordpress.com/2018/08/']

    capitulos = []
    while len(lista)>0:
        print(str(len(lista)))
        pagina = lista.pop()
        page = requests.get(pagina)
        soup = BeautifulSoup(page.content,'html.parser')
        titulos = soup.find_all(class_='entry-title')
        for link in titulos:
            sleep(2)
            if '#' in link.getText():
                capitulos.append(link.a.get('href'))
    bd = chvEnBD()
    for capitulo in capitulos:
        prerosco = []
        sleep(2)
        prerosco = scraperCapituloCHV(prerosco,capitulo)
        prerosco = diccidRosco(prerosco)
        #bd.guardarCapitulo(prerosco)

def testScraperSitioPSPLBR():
    scraperSitioPSPLBR()

def testScraperCapituloCHV():
    pagina = "https://psplbr.wordpress.com/2018/08/30/73-30-de-agosto-de-2018-solucion-repechajes/"
    pagina = "https://psplbr.wordpress.com/2018/05/20/23-20-de-mayo-de-2018-solucion/"
    pagina = "https://psplbr.wordpress.com/2018/08/19/66-19-de-agosto-de-2018-solucion/"
    prerosco=[]
    prerosco = scraperCapituloCHV(prerosco,pagina)
    equipo1 = prerosco[0][0]
    equipo2 = prerosco[1][0]
    prerosco1 = prerosco[0][1]
    prerosco2 = prerosco[1][1]
    prerosco1 = diccidRosco(prerosco1)
    prerosco2 = diccidRosco(prerosco2)
    bd = chvEnBD()
    #bd.guardarCapitulo([(equipo1,prerosco1),(equipo2,prerosco2)])
    prerosco = roscoDesdeDiccid(prerosco1)
    print("Rosco del primer equipo")
    print(prerosco)
    sleep(10)
    prerosco = roscoDesdeDiccid(prerosco2)
    print("Rosco del segundo equipo")
    print(prerosco)

if __name__ == '__main__':
    #testScraperSitioPSPLBR()
    testScraperCapituloCHV()
