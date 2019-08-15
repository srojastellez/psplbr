# -*- coding: utf-8 -*-
import time
import re
import argparse
import datetime
import ortografia
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FOptions
from selenium.webdriver.chrome.options import Options as ChrOptions
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

abreviaciones = ["etc.","etc.,","U.","p. ej.,", "P. ej.,"
        "cm","cm.","mm","mm.","l","°C","kg","kg.","gr","gr."]
adaptaciones = ["f.","m.","pl.","U. m. en pl.","U. t. en pl."
        "prnl.","U. t. c. prnl."]

# TODO:
# - Mirgrar del parser de selenium a bs4
def getPulpa(diccionario,drae,entry,acep,saveExample=False,saveOrigen=False):
    REabetc=re.compile('<abbr class="d" title="etcétera">etc\.,?</abbr>')
    REabext=re.compile('<abbr class="d" title="por extensión,">por ext\.,</abbr>')
    REabErU=re.compile('<abbr class="d" title="Era usado o usada">Era u\.</abbr>')
    REabreU=re.compile('<abbr class="d" title="[Uu]sad.*?>[Uu]\.</abbr>')
    REabpej=re.compile('<abbr class="d" title="[Pp]or ejemplo">[Pp]\. ej\.,</abbr>')

    REnacep=re.compile('<span class="n_acep">.*?</span>')
    REabrev=re.compile('<abbr.*?>.*?</abbr>')
    REmarca=re.compile('<.?mar.*?>')
    RElink1=re.compile('<a class.*?>')
    RElink2=re.compile('</a>')
    REejemp=re.compile('<span class="h">.*</span>')
    REspan1=re.compile('<span class=".*?>')
    REspan2=re.compile('</span>')
    REcursi=re.compile('<.?i>')
    REsuper=re.compile('<.?sup>')

    REabsim=re.compile('<abbr class="d" title="Símbolo">Símb\.</abbr>')
    REUmm=re.compile('<abbr class="d" title="milímetro\(s\)">mm\.?</abbr>')
    REUcm=re.compile('<abbr class="d" title="centímetro\(s\)">cm\</abbr>')
    REUms=re.compile('<abbr class="d" title="metro\(s\)">m\.?</abbr>')
    REUm2=re.compile('<abbr title="metro(s) cuadrado\(s\)">m<sup>2</sup>\.?</abbr>')
    REUm3=re.compile('<abbr (class="d")? title="metro\(s\) cúbico(s)">m<sup>3</sup>\.?</abbr>')
    REUms=re.compile('<abbr class="d" title="metro\(s\) por segundo">m/s\.?</abbr>')
    REUms2=re.compile('<abbr title="metro\(s\) por segundo cada segundo">m/s<sup>2</sup>\.?</abbr>')
    REUgrs=re.compile('<abbr class="d" title="gramo\(s\)">gr\.?</abbr>')
    REUkgs=re.compile('<abbr class="d" title="kilogramo\(s\)">kg\.?</abbr>')
    REUlts=re.compile('<abbr class="d" title="litro\(s\)">l\.?</abbr>')
    REUcls=re.compile('<abbr class="d" title="grado\(s\) centígrado\(s\)">°C\.?</abbr>')
    #REUfhr=re.compile('<abbr class="d" title="grado\(s\) Fahrenheit">°F\.?</abbr>')

    allArticles = drae.find_elements_by_xpath(".//article")
    allArticlesId = drae.find_elements_by_xpath(".//*[contains(@class,'article')]")

    for article in allArticles:
        articleID = article.get_property("id")
        header = article.find_element_by_xpath(".//header")
        palabra = header.text
        alternativo = article.find_elements_by_class_name("n1")
        acepciones = article.find_elements_by_xpath(".//*[contains(@class,'j')]")
        superindice = header.find_elements_by_xpath(".//sup")
        if entry > 0 and not(len(superindice) != 0 and int(superindice[0].text) == entry):
            continue

        entrada={}
        entrada["palabra"] = re.sub('[0-9]','',palabra)
        superind = lambda x: x[0].text if len(x)>0 else None
        entrada["entrada"] = superind(superindice)
        entrada["lookupID"] = articleID
        entrada["alt"] = None
        entrada["origen"] = None
        entrada["acepciones"] = []
        entrada["pronominal"] = None
        entrada["singularf"] = None
        entrada["singularm"] = None
        entrada["pluralm"] = None
        entrada["pluralf"] = None
        sf = 0
        sm = 0
        pf = 0
        pm = 0

        # OJO, hay un caso particular: "vídeo" que es una forma
        #   alternativa para escribir video pero en algunas acepciones,
        #   no en todas. Sin tener acceso al diccionario completo es
        #   difícil elegir la  manera adecuada de extraer y guardar
        #   esta información.
        if alternativo and len(alternativo[0].text.split('~'))<2:
            entrada["alt"] = alternativo[0].text.split('.')[1].split(',')[0].strip()
            print(entrada["alt"])

        if saveOrigen:
            origen = article.find_elements_by_class_name("n2")
            if origen:
                entrada["origen"] = origen[0].text
            else:
                origen = article.find_elements_by_class_name("n3")
                if origen:
                    entrada["origen"] = origen[0].text
            print("Origen de la palabra: "+str(entrada["origen"]))

        for acepcion in acepciones:
            acepcionID = acepcion.get_property("id")
            numero = acepcion.find_element_by_class_name("n_acep").text
            if acep != 0 and acep != int(numero[:-1]):
                continue

            informaciones = acepcion.find_elements_by_xpath(".//abbr")
            info = ""

            for informacion in informaciones:
                if informacion.text not in abreviaciones:
                    info = info + informacion.get_attribute("title") + " ; "
            if "pronominal" in info:
                entrada["pronominal"] = ortografia.pronominal(entrada["palabra"])
            if "adjetivo" in info or "femenino" in info:
                if "en plural" in info:
                    pf = 1
                    sf = 1
                    entrada["singularf"] = ortografia.femenino(entrada["palabra"])
                elif "plural" in info:
                    pf = 1
                else:
                    sf = 1
                    entrada["singularf"] = ortografia.femenino(entrada["palabra"])
            if "adjetivo" in info or "masculino" in info:
                if "en plural" in info:
                    pm = 1
                    sm = 1
                    entrada["singularm"] = ortografia.masculino(entrada["palabra"])
                elif "plural" in info:
                    pm = 1
                else:
                    sm = 1
                    entrada["singularm"] = ortografia.masculino(entrada["palabra"])

            subentrada={}
            subentrada["diccID"] = acepcionID
            subentrada["acepcion"] = numero
            subentrada["info"] = info
            subentrada["enlaza"] = None

            enlace = acepcion.find_elements_by_tag_name("a")
            if len(enlace)>0:
                subentrada["enlaza"] = enlace[0].get_attribute("href").split("=")[1]

            pulpa = acepcion.get_attribute('innerHTML')
            definicion=re.sub(REnacep,'',pulpa)
            definicion=re.sub(REabpej,'por ejemplo,',definicion)
            definicion=re.sub(REabext,'por extensión,',definicion)
            definicion=re.sub(REabetc,'etcétera',definicion)
            definicion=re.sub(REabreU,'Usado',definicion)
            definicion=re.sub(REabsim,'Símbolo',definicion)
            definicion=re.sub(REUmm,'milimetros',definicion)
            definicion=re.sub(REUcm,'centímetros',definicion)
            definicion=re.sub(REUms,'metros',definicion)
            definicion=re.sub(REUm2,'metros cuadrados',definicion)
            definicion=re.sub(REUm3,'metros cúbicos',definicion)
            definicion=re.sub(REUms,'metros por segundo',definicion)
            definicion=re.sub(REUms2,'metros por segundo al cuadrado',definicion)
            definicion=re.sub(REUgrs,'gramos',definicion)
            definicion=re.sub(REUkgs,'kilogramos',definicion)
            definicion=re.sub(REUlts,'litros',definicion)
            definicion=re.sub(REUcls,'grados centígrados',definicion)
            definicion=re.sub(REabrev,'',definicion)
            definicion=re.sub(REmarca,'',definicion)
            definicion=re.sub(RElink1,'',definicion)
            definicion=re.sub(RElink2,'',definicion)
            # OJO CON REEMPLAZAR <SUP>x</SUP>.
            # Casos de estudio: "gigabyte"(1) y "caballo"(8)
            definicion=re.sub(REsuper,'',definicion)

            if saveExample:
                ejemplos = ''.join(re.findall(REejemp,definicion))

            definicion=re.sub(REejemp,'',definicion)

            if saveExample:
                ejemplos = re.sub(REspan1,'',ejemplos)
                ejemplos = re.sub(REspan2,'',ejemplos)
                subentrada["ejemplos"] = ejemplos

            definicion=re.sub(REspan1,'',definicion)
            definicion=re.sub(REspan2,'',definicion)
            definicion=re.sub(REcursi,'',definicion)
            subentrada["definicion"] = definicion.lstrip()

            entrada["acepciones"].append(subentrada)

        if pf == 1:
            if sf == 1:
                entrada["pluralf"] = ortografia.plural(entrada["singularf"])
            else:
                entrada["pluralf"] = ortografia.femenino(entrada["palabra"])
        if pm == 1:
            if sm == 1:
                entrada["pluralm"] = ortografia.plural(entrada["singularm"])
            else:
                entrada["pluralm"] = ortografia.masculino(entrada["palabra"])

        diccionario.append(entrada)
    print(diccionario)

def showPalabra(diccionario):
    for palabra in diccionario:
        print(palabra["palabra"]+" ["+str(palabra["entrada"])+"] : ")
        for acepcion in palabra["acepciones"]:
            print(acepcion["acepcion"]+" "+acepcion["info"]+acepcion["definicion"])


def scraperRaeID(id):

    dt=datetime.datetime
    t1=dt.now()

    chrome_options = ChrOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('log-level=3')
    chrome_options.add_argument("--mute-audio")
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(options=chrome_options)

    wait = WebDriverWait(browser, timeout=12)

    diccionario=[]

    intentos=4
    while intentos > 0:
        try:
            browser.get("http://dle.rae.es/?id="+id)
            print("\n\nBuscando la definición de: "+id)
            wait.until(expected.visibility_of_element_located((By.ID, 'resultados')))
            drae = browser.find_element_by_id("resultados")
            t3=dt.now()
            entry = 0
            acepcion = 0
            getPulpa(diccionario,drae,entry,acepcion)
            intentos = 0
        except TimeoutException:
            intentos=intentos-1

    t2=dt.now()
    print("Tiempo total: "+str(t2-t1))
    print("Tiempo para cargar la página: "+str(t3-t1))
    print("Tiempo de procesamiento de datos:"+str(t2-t3))
    showPalabra(diccionario)
    browser.quit()
    return diccionario


# Se asume que el número de la acepcion existe.
# Recibe una lista de listas del par palabra-#acepcion a buscar en la RAE,
# por ejemplo: [ [baya,1] , [vaya2,3] , [valla,0] ]
# Retorna una lista de diccionarios
#OJO, salta atrapar:
#  - "this site can¿t be reached"
#  - MaxRetryError
#  - WebDriverException: unknown error (tab crashed)
def scraperRae(listadoABuscar, saveAll=False):
    #navegador="Firefox"
    #navegador="Firefox-headless"
    #navegador="Chrome"
    navegador="Chrome-headless"
    dt=datetime.datetime
    t1=dt.now()
    if navegador=="PhantomJS":
        browser = webdriver.PhantomJS("phantomjs.exe",
                service_args=['--load-images=no'])
    elif navegador=="Firefox":
        browser = webdriver.Firefox()
    elif navegador=="Firefox-headless":
        firefox_options = FOptions()
        firefox_options.add_argument('-headless')
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference('permissions.default.image', 2)
        firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        browser = webdriver.Firefox(firefox_options=firefox_options,
                firefox_profile=firefox_profile)
    elif navegador=="Chrome":
        browser = webdriver.Chrome()
    else:
        chrome_options = ChrOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('log-level=3')
        chrome_options.add_argument("--mute-audio")
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        browser = webdriver.Chrome(options=chrome_options)

    wait = WebDriverWait(browser, timeout=12)

    diccionario=[]

    for par in listadoABuscar:
        palabra = par[0].lower()
        acepcion = int(par[1])

        # Revisa si el último caracter de la palabra es un numero,
        #  vale decir, si se pide una entrada en particular
        if palabra[-1].isnumeric():
            entry = int(palabra[-1])
            palabra=palabra[:-1]
        else:
            entry = 0

        if saveAll:
            entry = 0
            acepcion = 0

        intentos=4
        while intentos > 0:
            try:
                browser.get("http://dle.rae.es/?w="+palabra)
                print("\n\nBuscando la definición de: "+palabra+" // acepción #"+str(acepcion)+"\n\n")
                wait.until(expected.visibility_of_element_located((By.ID, 'resultados')))

                drae = browser.find_element_by_id("resultados")
                if "no está registrada" in drae.text:
                    print(drae.text)
                    intentos = 0

                elif "no está disponile" in drae.text:
                    print("Esperando por 30 segundos porque el diccionario no está disponible en estos momentos.")
                    sleep(30)
                    pass

                elif "1." in drae.text:
                    t3=dt.now()
                    getPulpa(diccionario,drae,entry,acepcion)
                    intentos = 0

                else:
                    print("DLE lanzó una lista de palabra, eligiendo la más adecuada")
                    print(drae.text)
                    # Eleccion de palabras de la lista tiene el siguiente criterio:
                    #   Prioridad 1: Que la palabra tenga superindice (len(split(';')) > 1
                    #   Prioridad 2: Que la palabra tenga masculino, femenino (len(split(',')) > 1
                    #   Prioridad 3: Que la palabra tenga masculino, femenino (len(split(',')) > 1 pero la palabra buscada sea femenina
                    #   Prioridad 4: Que la palabra tenga un superindice PALABRA1 (por ejemplo: veda)
                    #   Priodidad 5: ¿Alguna idea que falte?
                    #   Algunas palabras son todo un problema, por ejemplo: "LA"
                    # Se puede a la pagina anterior usando driver.back()
                    try:
                        nextlink=drae.find_element_by_link_text(palabra)
                    except NoSuchElementException:
                        buscando = True
                        # Prioridad 1
                        nextlinks=drae.find_elements_by_partial_link_text(palabra)
                        for nextlink in nextlinks:
                            print(nextlink.text)
                            if len(nextlink.text.split(';')) > 1:
                                buscando = False
                                print("Prioridad 1: "+nextlink.text)
                                break
                        # Prioridad 2
                        if buscando:
                            for nextlink in nextlinks:
                                if len(nextlink.text.split(',')) > 1:
                                    buscando = False
                                    print("Prioridad 2: "+nextlink.text)
                                    break
                        # Prioridad 3
                        if buscando:
                            nextlinks = drae.find_elements_by_xpath(".//a[@href]")
                            for nextlink in nextlinks:
                                if len(nextlink.text.split(',')) > 1:
                                    buscando = False
                                    print("Prioridad 3: "+nextlink.text)
                                    break
                        if buscando:
                            nextlinks=drae.find_elements_by_partial_link_text(palabra+"1")
                            for nextlink in nextlinks:
                                print(nextlink.text)
                                if len(nextlink.text.split(';')) > 1:
                                    buscando = False
                                    print("Prioridad 4: "+nextlink.text)
                                    break

                    try:
                        nextlink.click()
                    except WebDriverException:
                        # Cookie post-acuerdo UE
                        # Ojo que el sitio, hasta este momento, tiene los nombres cambiados
                        #  para la opción de aceptar vs configurar-y-rechazar
                        div = browser.find_element_by_class_name("banner_consentConfig--3URYv")
                        div.find_element_by_xpath(".//button").click()
                        nextlink.click()

                    time.sleep(1)
                    drae = browser.find_element_by_id("resultados")
                    if "1." in drae.text:
                        t3=dt.now()
                        getPulpa(diccionario,drae,entry,acepcion)
                        intentos = 0
                    else:
                        print("NO, no apareció :S \n\n")
                        # OJO, TENDRIA QUE SER UN BREAK pero desmayo requirió un segundo intento
                        intentos = intentos -1

            except TimeoutException:
                intentos=intentos-1

        t2=dt.now()
        if not t3:
            t3=dt.now()
        print("Tiempo total: "+str(t2-t1))
        print("Tiempo para cargar la página: "+str(t3-t1))
        print("Tiempo de procesamiento de datos:"+str(t2-t3))
        showPalabra(diccionario)
    browser.quit()
    return diccionario

# Buscar palabras es interesante por la variedad de respuestas que pueden surgir.
# Como ejemplo les dejo la siguiente lista:
#  - niño
#  - princesa
#  - aeronáutica
#  - cesárea
#  - sendos
#  - jaspeado
#  - reina
# En realidad el problema se presenta si luego se desea almacenar internamente
#   dichas definiciones.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scraper del DLE de la RAE')
    parser.add_argument('-p', dest='palabra', nargs=2, action='append',
                        metavar=('PALABRA','#ACEPCIÓN'), required=True,
                        help='Palabra a buscar y su acepcion (0 para buscar todas sus acepciones)')
    args = parser.parse_args()

    scraperRae(args.palabra)
