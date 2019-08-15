# -*- coding: utf-8 -*-
from gtts import gTTS

from os import remove

from pydub import AudioSegment

from audiotsm import phasevocoder
from audiotsm import wsola
from audiotsm.io.wav import WavReader, WavWriter

import datetime

import contextlib
with contextlib.redirect_stdout(None):
    from pygame import time
    from pygame import mixer



# Genera la pronunciacion de la definicion de las palabras
# usando la API de Google Text To Speech
def hablamiento(palabra,definicion):
    tts = gTTS(definicion, lang='es')
    archivo = "audio/"+palabra+'.mp3'
    try:
        tts.save(archivo)
    #AttributeError: 'NoneType' object has no attribute 'group'
    except AttributeError as e:
        print("PANIC ATTACK!!!!!!")
        print (e)
    return archivo

# Elimina la voz de Alvin (la ardilla) de los archivos de
# pronunciacion cuando se reproducen velozmente (x1.3)
def deAlvinizar(archivoi,algoritmo="wso",modif="_"):
    sound = AudioSegment.from_mp3(archivoi)
    archwi = archivoi[:-3]+"wav"
    archwf = archivoi[:-5]+".wav"
    sound.export(archwi, format="wav")
    with WavReader(archwi) as reader:
        with WavWriter(archwf, reader.channels, reader.samplerate) as writer:
            if algoritmo=="phv":
                tsm = phasevocoder(reader.channels, speed=1.5)
            else:
                tsm = wsola(reader.channels, speed=1.5)
            tsm.run(reader, writer)
    archivof = archwi[:-4]+modif+".mp3"
    sound = AudioSegment.from_wav(archwf)
    sound.export(archivof,format="mp3")
    remove(archwi)
    remove(archwf)
    return archivof

def generaAudio(palabra,definicion):
    archivo = hablamiento(palabra,definicion)
    archivo = deAlvinizar(archivo,"wso","")
    return archivo


def reproducirAudio(archivo,speed=24000):
    mixer.init(speed)
    mixer.music.load(archivo)
    mixer.music.play()
    while mixer.music.get_busy():
        time.Clock().tick(10)
    mixer.music.stop()
    mixer.quit()

def testGeneraAudio():
    archivo=generaAudio('sapear','Entre delincuentes, acusar')
    return archivo

def testYcomparar():
    dt = datetime.datetime
    archivo=testGeneraAudio()
    t1=dt.now()
    reproducirAudio(archivo)
    t2=dt.now()
    print("Audio Normal ["+archivo+"] reproducido en "+str(t2-t1))
    t3=dt.now()
    reproducirAudio(archivo,66150)
    t4=dt.now()
    print("Audio Rápido (x1.3) ["+archivo+"] reproducido en "+str(t4-t3))
    t5=dt.now()
    archiv=deAlvinizar(archivo,"phv","_p")
    t6=dt.now()
    print("Time stretching (x1.5) en "+str(t6-t5))
    t7=dt.now()
    reproducirAudio(archiv)
    t8=dt.now()
    print("Audio Rápido (x1.5) ["+archiv+"] reproducido en "+str(t8-t7))
    t5=dt.now()
    archiv=deAlvinizar(archivo,"wso","_w")
    t6=dt.now()
    print("Time stretching (x1.5) en "+str(t6-t5))
    t9=dt.now()
    reproducirAudio(archiv)
    t10=dt.now()
    print("Audio Rápido (x1.5) ["+archiv+"] reproducido en "+str(t8-t7))

if __name__ == '__main__':
    testYcomparar()
