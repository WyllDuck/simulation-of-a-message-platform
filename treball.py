import matplotlib.pyplot as plt
from distribucions import *
import pandas as pd
import xlsxwriter


MOSTRES = 5  # Nombre de mostres/sistemes
USERS = 500  # Nombre d'usuaris
WARMUP = 100  # Temps de warm up (hores)
DELTA = 1  # Temps de simulacio (minuts)
GET_INFORMATION = 1 * 60 # Temps de mostreig (segons)

ESCRIURE_U = 0  # Mostra estat de l'usuari (1:SI, 0:NO)
ESCRIURE_S = 0  # Mostra estat del sistema (1:SI, 0:NO)
ESCRIURE_M = 0  # Mostra estat de la simulacio (1:SI, 0:NO)
GRAFICAR = 0  # Veure grafica final (1:SI, 0:NO)
BINS = 0  # Nombre de barres de la grafica (>=10:ON, <10:OFF)

WARMUP_testing = 0  # Calcul de warm up (1:SI, 0:NO)


# Simula MOSTRES xarxes/sistemes
def Simular():

    if WARMUP_testing:

        sData = []

        for s in range(1, MOSTRES + 1):

            # Nova Mostra        
            newData = SimularSistema()

            if sData:
                sData = [(sData[i] + newData[i]) for i in range(len(newData))]
            else:
                sData = newData
        
    else:

        informacio_usuaris_M = []
        informacio_perUsuari_M = [] 

        for s in range(1, MOSTRES + 1):

            # Nova Mostra        
            informacio_usuaris, informacio_perUsuari = SimularSistema()

            usuaris = []
            for frame in informacio_perUsuari:
                usuaris.append(pd.DataFrame(frame))
            informacio_perUsuari_M.append(usuaris)
            
            informacio_usuaris_M.append(pd.DataFrame(informacio_usuaris))

    if ESCRIURE_M:
        print("\n\n\n\n####################\t" + str(s) + "\n")
    
    if WARMUP_testing:
        return sData

    return informacio_usuaris_M, informacio_perUsuari_M


# Simula USERS usuaris en 1 xarxa/sistema
def SimularSistema():

    # Emmagatzemar Informacio
    informacio_usuaris = dict()
    informacio_usuaris["Usuaris Online"] = [0] * int((DELTA * 60) / GET_INFORMATION)
    informacio_usuaris["Messatges Enviats"] = [0] * int((DELTA * 60) / GET_INFORMATION)
    informacio_usuaris["Temps (seg)"] = [i * GET_INFORMATION for i in range(1, int((DELTA * 60) / GET_INFORMATION) + 1)]

    # Aqui guardem la informacio de cada usuari per separat
    informacio_perUsuari = []

    for u in range(1, USERS + 1):

        # Nou Usuari
        newData = SimularUsuari()
        
        if WARMUP_testing:

            uData = []
            if uData:
                uData = [(uData[i] + newData[i]) for i in range(len(newData))]
            else:
                uData = newData

        else:

            newData["Usuari numero"] = [u for i in range(int((DELTA * 60) / GET_INFORMATION))]
            informacio_perUsuari.append(newData)

            for it in range(len(newData["esOnline"])):
                informacio_usuaris["Usuaris Online"][it] += newData["esOnline"][it] 

            for it in range(len(newData["msgEnviats"])):
                informacio_usuaris["Messatges Enviats"][it] += newData["msgEnviats"][it]

        if ESCRIURE_S:
            print("-----\t" + str(u))
    
    if WARMUP_testing:
        return uData
    else:
        return informacio_usuaris, informacio_perUsuari


##########
# USUARI #
##########

# Simula 1 usuari
def SimularUsuari():

    global rellotge
    global cuaEnviament
    global vWarmUp
    global msgEnviats
    global informacio

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
        elif tipus_E == "Mostreig":
            E_mostreig()

        esdeveniment = gen_E()
        if ESCRIURE_U:
            escriure_informacio(cuaEnviament, esdeveniment)

    if ESCRIURE_S:
        print("Enviats:\t" + str(msgEnviats))
    if WARMUP_testing:
        return vWarmUp

    return informacio


# Defineix l'estat inicial
def iniciar_variables():

    global v_events
    global vWarmUp
    global maxim_temps
    global minim_temps
    global rellotge
    global cuaEnviament
    global online
    global msgEnviats
    global informacio

    # Estats Inicials:
    v_events = []
    vWarmUp = []
    
    minim_temps = 3600 * WARMUP
    maxim_temps = minim_temps + 60 * DELTA
    rellotge = 0.0
    cuaEnviament = 0

    online = 1
    msgEnviats = 0

    # Estructura per emmagatzemar informacio
    informacio = dict()
    informacio["esOnline"] = []
    informacio["msgEnviats"] = []

    # Esdeveniments Inicials:
    add_E_offline(rellotge)
    add_E_entrada(rellotge)
    add_E_mostreig(rellotge)
    if WARMUP_testing:
        add_E_sincron(rellotge)


####################
# PROCESSAR EVENTS #
####################

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
    global msgEnviats

    cuaEnviament -= 1
    if rellotge >= minim_temps:
        msgEnviats += 1
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

# Recupara dades usuari
def E_mostreig():
    
    global online
    global rellotge
    global informacio
    global minim_temps
    global msgEnviats

    if rellotge > minim_temps:
        informacio["esOnline"].append(online)
        informacio["msgEnviats"].append(msgEnviats)

    msgEnviats = 0

    add_E_mostreig(rellotge)


######################
# ESTADISTICA EVENTS #
######################

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

# Crea un esdeveniment de mostreig
def add_E_mostreig(rellotge):

    global v_events

    temps_E = rellotge + GET_INFORMATION
    tipus_E = 'Mostreig'
    E = (temps_E, tipus_E)
    v_events += [E]


############
# FUNC AUX #
############

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


########
# MAIN #
########

if __name__ == "__main__":

    if WARMUP_testing:
    
        resultat = Simular()
    
        if GRAFICAR:
            plt.plot(resultat)
            plt.show()

    else:

        informacio_usuaris, informacio_perUsuari = Simular()

        for i in range(len(informacio_usuaris)):
            writer = pd.ExcelWriter('simulacions/model_{}.xlsx'.format(i), engine='xlsxwriter')
            informacio_usuaris[i].to_excel(writer, sheet_name='usuaris acumulats')

            for j in range(len(informacio_perUsuari[i])):
                frame = informacio_perUsuari[i][j]
                row = j*(len(informacio_perUsuari[i][j]) + 2)
                frame.to_excel(writer, sheet_name="usuaris", startrow = row)

            writer.save()

    print("Fet")