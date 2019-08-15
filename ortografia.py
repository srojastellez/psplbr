# -*- coding: utf-8 -*-
import re

agudas = ['s','n']
vocal = ['a','e','i','o','u']
tildes = ['á','é','í','ó','ú']
vocales = ['a','á','e','é','i','í','o','ó','u','ú']
vf = ['a','á','e','é','í','o','ó','ú']
vd = ['i','u']
consonantes = ['b','c','d','f','g','h','j','k','l','m','n','ñ','p','q','r','s','t','v','w','x','y','z']
pareables = "(ll|ch|[bcdfgprt]r|[bcdfglpt]l)"
destildar = {'á':'a', 'é':'e', 'í':'i', 'ó':'o', 'ú':'u'}

# Inspirado en FON2.REG (http://elies.rediris.es/elies4/Fon2.htm)
# No considero el hiato de dos vocales débiles iguales(se-mi-in-cons-cien-te).
def quitaUltimaSilaba(palabra):
    # OJO, ¿Puedo omitir esta primera busqueda?
    ultima=re.search(str(vocales)+str(consonantes)+'+'+str(vocales)+'+'+str(consonantes)+'?$',palabra)
    if ultima:
        # Combinacion 1.- 1 vocal -- 2 consonantes pareables -- X vocales * consonantes
        opcion=re.search(str(pareables)+str(vocales)+'+'+str(consonantes)+'?$',ultima.group())
        if not opcion:
            # Combinacion 2.- 1 vocal X consonantes 1 s -- X consonantes X vocales * consonantes
            opcion=re.search('(?<=s)'+str(consonantes)+'+'+str(vocales)+'+'+str(consonantes)+'?$',ultima.group())
            if not opcion:
            # Combinacion 3.- 1 vocal -- 1 consonante X vocales * consonantes
                opcion=re.search(str(consonantes)+str(vocales)+'+'+str(consonantes)+'?$',ultima.group())
        palabra = palabra[:ultima.start()+opcion.start()]
    return palabra

def femenino(palabra):
    palabra = re.sub('[1-9]','',palabra)
    plbr = palabra.split(',')
    if len(plbr) > 1:
        fem = plbr[1].strip()
        mas = plbr[0].strip()
        # La palabra viene en formato "masculino, silaba femenina"
        if len(mas)>len(fem):
            # Reemplazo de vocal final (por ejemplo "mateo, a")
            if len(fem) == 1:
                palabra = mas[:-1] + fem
            # Casi concatenar la silaba femenina (por ejemplo "doctor, ra")
            elif mas[-1] == fem[0]:
                if mas[-2] in tildes:
                    mas = mas[:-2]+destildar[mas[-2]]+mas[-1]
                palabra = mas[:-1]+fem
            # Reemplazar la sílaba final por la femenina (por ejemplo "emperador, triz")
            else:
                mas = quitaUltimaSilaba(mas)
                palabra = mas+fem
        # La palabra viene en formato "masculino, femenino" (por ejemplo "rey, reina")
        else:
            palabra = fem
    return palabra

def masculino(palabra):
    palabra = re.sub('[1-9]','',palabra)
    return palabra.split(',')[0]

def oldFemenino(palabra):
    palabra = re.sub('[1-9]','',palabra)
    plbr = palabra.split(',')
    if len(plbr) > 1:
        if len(plbr[1])<5:
        #if len(plbr[1])<len(plbr[0]):
            if plbr[0][-1] not in vocal:
                if plbr[0][-1] in agudas:
                    if plbr[0][-2] in tildes:
                        palabra = plbr[0][:-2] + destildar[plbr[0][-2]] + plbr[1].strip()
                    else:
                        letra = plbr[1].strip()
                        palabra = plbr[0][:-len(letra)] + letra

                else:
                    palabra = plbr[0][:-1] + plbr[1].strip()
            else:
                letra = plbr[1].strip()
                palabra = plbr[0][:-len(letra)] + letra
        else:
            palabra = plbr[1].strip()
    return palabra

# Esto es una aproximación, las reglas son mucho más extensas. Ejemplos:
#  - espray /espráis        [sustantivo recien llegado al español]
#  - tos / toses            [monosílabo terminado en s/x]
#  - francés / franceses    [polisílabo agudo]
#  - crisis / crisis        [el resto no cambian]
#  - ciempiés / ciempiés    [voces compuestas que ya incluyen el plural]
#  - cáterin / cáterin      [esdrujulas terminadas en lrndzj]
# ...
# Pero muchas de esas reglas no aplican en ámbito de este programa
def plural(palabra):
    if palabra[-1] == "z":
        palabra = palabra[:-1]+"c"
    if palabra[-1] not in vocales:
        if (palabra[-2] in tildes and (palabra[-3] in vd or palabra[-3] in consonantes)):
            palabra = palabra[:-2] + destildar[palabra[-2]] + palabra[-1]
        palabra = palabra+"e"
    palabra = palabra+"s"
    return palabra

def pronominal(verbo):
    if verbo[-1].isnumeric():
        verbo = verbo[:-1]
    return verbo+"se"

def testOrtografia():
    word = "raíz"
    print(word + " -> pl. "+plural(word))
    word = "danés, sa"
    print(word + " -> f. "+femenino(word))
    print(word + " -> m. "+masculino(word))
    print(word + " -> f.pl. "+plural(femenino(word)))
    print(word + " -> m.pl. "+plural(masculino(word)))
    word = "aeronáutico, ca"
    print(word + " -> f.pl. "+plural(femenino(word)))
    word = "marqués, sa"
    print(word + " -> f. "+femenino(word))
    print(word + " -> f.pl. "+plural(femenino(word)))
    word = "papa"
    print(word + " -> f.pl. "+plural(femenino(word)))
    word = "carne"
    print(word + " -> f. "+femenino(word))
    print(word + " -> m. "+masculino(word))
    word = "príncipe, princesa"
    print(word + " -> f. "+femenino(word))
    print(word + " -> m. "+masculino(word))
    print(word + " -> f.pl. "+plural(femenino(word)))
    print(word + " -> m.pl. "+plural(masculino(word)))
    word = "insolar"
    print(word + " -> prnl. "+pronominal(word))
    word = "sendos, das"
    print(word + " -> f. "+femenino(word))
    print(word + " -> m. "+masculino(word))
    word = "bacán, na"
    print(word + " -> f. "+femenino(word))
    print(word + " -> m. "+masculino(word))
    word = "cesáreo, a"
    print(word + " -> f. "+femenino(word))
    print(word + " -> m. "+masculino(word))
    word = "emperador, triz"
    print(word + " -> f. "+femenino(word))
    print(word + " -> m. "+masculino(word))
    word = "distinto, ta"
    print(word + " -> f. "+femenino(word))
    print(word + " -> m. "+masculino(word))
    word = "fallo, lla"
    print(word + " -> f. "+femenino(word))
    print(word + " -> m. "+masculino(word))
    word = "casto, ta"
    print(word + " -> f. "+femenino(word))
    print(word + " -> m. "+masculino(word))
    word = "cabro, bra"
    print(word + " -> f. "+femenino(word))
    print(word + " -> m. "+masculino(word))
    word = "ubicuo, cua"
    print(word + " -> f. "+femenino(word))
    print(word + " -> m. "+masculino(word))
    word = "norcoreano, a"
    print(word + " -> f. "+femenino(word))
    print(word + " -> m. "+masculino(word))
    word = "mateo, a"
    print(word + " -> f. "+femenino(word))
    print(word + " -> m. "+masculino(word))
    word = "rey, reina"
    print(word + " -> f. "+femenino(word))
    print(word + " -> m. "+masculino(word))
    word = "doctor, ra"
    print(word + " -> f. "+femenino(word))
    print(word + " -> m. "+masculino(word))
    word = "opresor, ra"
    print(word + " -> f. "+femenino(word))
    print(word + " -> m. "+masculino(word))
    word = "camión"
    print(word + " -> pl. "+plural(word))
    word = "espía"
    print(word + " -> pl. "+plural(word))
    word = "botín"
    print(word + " -> pl. "+plural(word))
    word = "peón"
    print(word + " -> pl. "+plural(word))
    word = "charrúa"
    print(word + " -> pl. "+plural(word))
    word = "perdón"
    print(word + " -> pl. "+plural(word))




if __name__ == '__main__':
    testOrtografia()
