# -*- coding: utf-8 -*-
import colorama
from colorama import Fore, Style
import speech_recognition as sr
import threading
from mytimer import MyTimer
import contextlib
import signal
with contextlib.redirect_stdout(None):
    from pygame import time
    from pygame import mixer
from dataRosco import generaRosco

# Clase Vueltas
# Está pensado para simular la version de chv del programa, esto es:
# - Primera vuelta se leen las definiciones completas antes de responder
# - De la segunda en adelante se pueden responder rapidamente
# - Al fallar o decir "PASAPALABRA" se hace una pausa antes de continuar
# TODO:
# - Migrar el reconocimiento de voz de internet a una version local
#   porque la latencia es grande. Existen comportamientos raros como
#   intentar reconocer audios vacíos.
# - ¿Cambiar el algoritmo? Actualmente es imposible hacer una metralleta
# - Actualmente se compara solo la primera solución.
# - En algunas ocasiones el programa se cuelga durante el stop_listening()
#   la razón la desconozco
class Vueltas(threading.Thread):
    def __init__(self):
        super().__init__()
        self.score = { "buenas" : 0 , "malas" : 0 }
        self.detencion = threading.Event()
        self.jugadorDijo = ""
        self.pausa = 10000

    def rcg_callback(self,rcg,audio):
            try:
                self.jugadorDijo = rcg.recognize_google(audio,language='es-CL')
            except sr.UnknownValueError:
                if self.jugadorDijo:
                    mixer.music.stop()
                    print(Fore.MAGENTA + "ERROR!" + Fore.RESET + "Problema al registrar la palabra escuchada: "+ self.jugadorDijo)

    def run(self,rosco,cronometro,rcg,mic):

        def signal_handler(sig, frame):
            print("~ ~ ~ ~ CTRL-C:   Terminando ~ ~ ~ ~")
            self.stop()
            try:
                stop_listening()
            except NameError:
                pass

        signal.signal(signal.SIGINT, signal_handler)
        esPrimeraVuelta=True
        self.score["pendientes"] = list(rosco.keys())
        while len(self.score["pendientes"]) > 0:
            if self.detencion.is_set():
                break
            print("\nLista de Pendientes: " + Fore.YELLOW + str(self.score["pendientes"]) + Fore.RESET + "\n")
            cronometro.pause()
            time.wait(4000)
            cronometro.resume()
            for letra in self.score["pendientes"][:]:
                if not self.detencion.is_set():
                    self.jugadorDijo = ""
                    restante = cronometro.remaining()
                    print("[" + str(restante)+ "] " + Fore.GREEN + letra+ Fore.RESET + " -   ",end="")
                    mixer.music.load(rosco[letra]["audio"])
                    mixer.music.play()
                    if esPrimeraVuelta:
                        while mixer.music.get_busy():
                            time.Clock().tick(10)
                    stop_listening = rcg.listen_in_background(mic, self.rcg_callback)
                    while not self.jugadorDijo:
                        time.wait(50)
                        if self.detencion.is_set():
                            stop_listening()
                            return self.score
                    stop_listening(wait_for_stop=True)
                    mixer.music.stop()
                    if self.jugadorDijo == rosco[letra]["solucion"][0].lower():
                        self.score["buenas"]+=1
                        self.score["pendientes"].remove(letra)
                        print(Fore.CYAN + "BUENA!" + Fore.RESET + " La palabra es "+self.jugadorDijo)
                    else:
                        if self.jugadorDijo == "pasapalabra":
                            print(Fore.YELLOW + "PASAPALABRA" + Fore.RESET)
                            cronometro.pause()
                            time.wait(self.pausa)
                        else:
                            print(Fore.RED + "MALA!" + Fore.RESET + " La palabra es "+rosco[letra]["solucion"][0]+" pero el jugador dijo "+self.jugadorDijo)
                            self.score["malas"]+=1
                            self.score["pendientes"].remove(letra)
                            cronometro.pause()
                            time.wait(self.pausa)
                        cronometro.resume()
                else:
                    break
            esPrimeraVuelta=False
        return self.score

    def stop(self):
        print("\n\n¡¡SE TERMINÓ EL TIEMPO!!\n\n")
        self.detencion.set()
        mixer.music.stop()



def juegaRosco(rosco,tiempo=120):


    mixer.init(24000)
    rcg = sr.Recognizer()
    mic = sr.Microphone()
    #set threhold level
    with mic as source: rcg.adjust_for_ambient_noise(source)
    print("Set minimum energy threshold to {}".format(rcg.energy_threshold))
    rcg.pause_threshold = 0.5
    print(Fore.RED + Style.BRIGHT + "\nINICIO ROSCO " + Style.RESET_ALL + Fore.CYAN + "["+ str(tiempo) +"seg.]" + Style.RESET_ALL)
    vueltas = Vueltas()
    cronometro=MyTimer(tiempo,vueltas.stop)
    score=vueltas.run(rosco,cronometro,rcg,mic)

    cronometro.cancel()

    print("\nResultados: ")
    print(Fore.CYAN   + "    BUENAS     " + str(score["buenas"]))
    print(Fore.RED    + "    MALAS      " + str(score["malas"]))
    print(Fore.YELLOW + "    PENDIENTES " + str(len(score["pendientes"])))
    print(Fore.RESET  + "    TIEMPO RESTANTE "+str(cronometro.deadline-cronometro.acumTime))
    mixer.quit()

def pasapalabra():
    colorama.init()
    rosco = generaRosco()
    juegaRosco(rosco)

if __name__ == '__main__':
    pasapalabra()
