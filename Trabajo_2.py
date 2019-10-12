'''
Version: 2
    + Warm up
    + Warm up testing
    + Multi-usuario
    + Multi-sistema
    + Graphical
'''

import matplotlib.pyplot as plt
from Distribucions import *

MOSTRES = 100  # Nombre de mostres/sistemes
USERS = 50  # Nombre d'usuaris
WARMUP = 100  # Temps de warm up (hores)
DELTA = 1  # Temps de mostra (minuts)

ESCRIURE_U = 0  # Mostra estat de l'usuari (1:SI, 0:NO)
ESCRIURE_S = 0  # Mostra estat del sistema (1:SI, 0:NO)
ESCRIURE_M = 1  # Mostra estat de la simulacio (1:SI, 0:NO)
GRAFICAR = 1  # Veure grafica final (1:SI, 0:NO)
BINS = 0  # Nombre de barres de la grafica (>=10:ON, <10:OFF)

WARMUP_testing = 0  # Calcul de warm up (1:SI, 0:NO)


# Simula MOSTRES xarxes/sistemes
def Simular():
    sData = []
    for s in range(1, MOSTRES + 1):
        newData = SimularSistema()
        if WARMUP_testing:
            if sData:
                sData = [(sData[i] + newData[i]) for i in range(len(newData))]
            else:
                sData = newData
        else:
            sData += [newData]

        if ESCRIURE_M:
            print("\n\n\n\n####################\t" + str(s) + "\n")
    return sData


# Simula USERS usuaris en 1 xarxa/sistema
def SimularSistema():
    uData = []
    for u in range(1, USERS + 1):
        newData = SimularUsuario()
        if WARMUP_testing:
            if uData:
                uData = [(uData[i] + newData[i]) for i in range(len(newData))]
            else:
                uData = newData
        else:
            if uData:
                uData += newData
            else:
                uData = newData
        if ESCRIURE_S:
            print("-----\t" + str(u))
    return uData


# Simula 1 usuari
def SimularUsuario():

    global rellotge
    global cuaEnviament
    global vWarmUp
    global enviat

    iniciar_variables()

    esdeveniment = gen_E()
    if ESCRIURE_U:
        escriure_informacio(cuaEnviament, esdeveniment)

    while not muere(esdeveniment):
        rellotge, tipus_E = esdeveniment

        if tipus_E == "Online":
            E_online()
        elif tipus_E == "Offline":
            E_offline()
        elif tipus_E == "Entrada":
            E_entrada()
        elif tipus_E == "Salida":
            E_salida()
        elif tipus_E == "Test":
            E_sincron()

        esdeveniment = gen_E()
        if ESCRIURE_U:
            escriure_informacio(cuaEnviament, esdeveniment)

    if ESCRIURE_S:
        print("Enviats:\t" + str(enviat))
    if WARMUP_testing:
        return vWarmUp
    return enviat


# Defineix l'estat inicial
def iniciar_variables():

    global v_events
    global vWarmUp
    global maxim_temps
    global minim_temps
    global rellotge
    global cuaEnviament
    global online
    global enviat

    v_events = []
    vWarmUp = []
    minim_temps = 3600 * WARMUP
    maxim_temps = minim_temps + 60 * DELTA
    rellotge = 0.0
    cuaEnviament = 0
    online = 1
    enviat = 0

    add_E_offline(rellotge)
    add_E_entrada(rellotge)
    if WARMUP_testing:
        add_E_sincron(rellotge)


# Procesa una entrada (escritura de missatge)
def E_entrada():

    global online
    global cuaEnviament
    global rellotge

    cuaEnviament += 1
    add_E_entrada(rellotge)
    if cuaEnviament == 1 and online:
        add_E_salida(rellotge)


# Procesa una sortida (enviament de missatge)
def E_salida():

    global cuaEnviament
    global rellotge
    global minim_temps
    global enviat

    cuaEnviament -= 1
    if rellotge >= minim_temps:
        enviat += 1
    if cuaEnviament:
        add_E_salida(rellotge)


# Procesa una connexio a la xarxa
def E_online():

    global online
    global cuaEnviament
    global rellotge

    online = 1

    add_E_offline(rellotge)
    if cuaEnviament:
        add_E_salida(rellotge)  # No hi ha envio, generem 1


# Procesa una desconnexio de la xarxa
def E_offline():

    global online
    global rellotge
    global v_events

    online = 0

    add_E_online(rellotge)

    # Anulamos envio si existe
    index = -1
    for i in range(len(v_events)):
        tipo_E = v_events[i][1]
        if tipo_E == "Salida":
            index = i
            break
    if index != -1:
        v_events.pop(index)


# Anota si un usuari estava connectat
def E_sincron():
    
    global online
    global vWarmUp
    global rellotge

    vWarmUp += [online]
    add_E_sincron(rellotge)


# Crea una entrada al dispositiu (escritura de missatge)
def add_E_entrada(rellotge):

    global v_events

    temps_entrada = exponencial(1. / 15)
    temps_E = rellotge + temps_entrada
    tipus_E = 'Entrada'
    E = (temps_E, tipus_E)
    v_events += [E]


# Crea una sortida del dispositiu (enviament de missatge)
def add_E_salida(rellotge):

    global v_events

    temps_salida = triangular(0.1, 0.2, 0.18)
    temps_E = rellotge + temps_salida
    tipus_E = 'Salida'
    E = (temps_E, tipus_E)
    v_events += [E]


# Crea una connexio a la xarxa
def add_E_online(rellotge):

    global v_events

    temps_online = 1 * 60 * 60
    temps_E = rellotge + temps_online
    tipus_E = 'Online'
    E = (temps_E, tipus_E)
    v_events += [E]


# Crea una desconnexio de la xarxa
def add_E_offline(rellotge):

    global v_events

    temps_offline = normal_sin(3 * 60, 30)  # min
    while not(((2 * 60) + 30) < temps_offline < ((3 * 60) + 30)):
        temps_offline = normal_sin(3 * 60, 30)

    temps_E = rellotge + temps_offline * 60  # secs
    tipus_E = 'Offline'
    E = (temps_E, tipus_E)
    v_events += [E]


# Crea un test online/offline per al WARMUP_testing
def add_E_sincron(rellotge):

    global v_events

    temps_E = rellotge + DELTA
    tipus_E = 'Test'
    E = (temps_E, tipus_E)
    v_events += [E]


# Comprova si se supera el temps maxim
def muere(esdeveniment):

    global maxim_temps

    temps_E = esdeveniment[0]
    return temps_E > maxim_temps


# Ordena i extreu l'esdeveniment mes proper
def gen_E():

    global v_events

    v_events.sort(key=lambda tup: tup[0])
    next_E = v_events.pop(0)
    return next_E


# Escriu dades per pantalla
def escriure_informacio(cuaEnviament, esdeveniment):

    global v_events

    v_print = [(round(e[0], 2), e[1]) for e in v_events]
    print (
        '{0:.2f}\t{1:10}\t{2}\t{3}'
        .format(
            esdeveniment[0],
            esdeveniment[1],
            cuaEnviament,
            v_print))


# MAIN

if __name__ == "__main__":

    v = Simular()

    if GRAFICAR and WARMUP_testing:
        plt.plot(v)
        plt.show()

    elif GRAFICAR and BINS > 10:
        plt.hist(v, bins=BINS)
        plt.show()

    elif GRAFICAR:
        plt.hist(v)
        plt.show()
