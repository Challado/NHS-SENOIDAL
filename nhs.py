import serial
import time
import sys
import os
import json
import pprint
import random
from funcoes import *

# Variaveis de controle
emumode = False
pkt_info = None
send_extended = 0

# Grava arquivo para o NUT
ativaNUT = True
# Envia MQTT
ativaMQTT = True
# Envia para o Banco de Dados
ativaBD = False
# Saida JSON
ativaJSON = True


# Consulte o manual do teu nobreak para fornecer as informacoes corretas
# Eh importante que voce forneca os dados certos para que os calculos sejam fornecidos corretamente
# Defina os dados do teu nobreak aqui
nome = "MEUNOBREAK"
# A descricao do modelo e a potencia em VA podem ser obtidos de uma relacao de modelos no arquivo funcoes.py, no array upsinfo. Caso nao esteja la pode colocar aqui
descricaomodelo = "NHS LINHA SENOIDAL"
# Potencia Nominal em VA. 
potencia_nominal = 3000
# Fator de conversao
fator_conversao = 0.9

# Numero de baterias. O nobreak ja tem essa informacao la dentro dele, mas voce pode ter colocado um modulo de baterias externo...
# Se caso o valor for None entao ele ira manter os dados da bateria
numero_baterias = None
# Capacidade da bateria em Ah. Voce precisa saber a capacidade da bateria para calcular a autonomia
ah = 9
# Tensao da Bateria em Volts
tensao_bateria = 12

device = "/dev/ttyACM0"
try:
    if (os.path.exists("/var/log/nhs.log")):
        os.unlink("/var/log/nhs.log")        
    ser = None
    i = 0
    interacoes = 0
    temposleep =1
    lastdp = None
    pkt = None
    pkt_info = None
    while (True):
        if ((not ser) or (ser.isOpen() == False)):
            ser = serial.Serial(device, baudrate=2400, bytesize=8, parity='N', stopbits=1, rtscts=True)
            slog("Serial estava fechada. Reabrindo")
            if (ativaJSON):
                js(None)
            if (ativaNUT):
                # Precisa escrever NADA no nut pois esta desconectado
                nut(None)
        else:
            dadoswaiting = ser.in_waiting
            if (dadoswaiting > 0):
                while (dadoswaiting > 0):
                    ch = ser.read(1)
                    dp = criadatapacket(ch)
                    if (dp):
                        pkt = None
                        tempodecorrido = 0
                        if (lastdp):
                            tempodecorrido = time.time() - lastdp
                        if (emumode):
                            # Modo emulacao, manda tudo como TRUE
                            pkt = tratar_datapacket(dp,tempodecorrido,pkt_infonobreak = pkt_info)
                        else:
                            pkt = tratar_datapacket(dp,tempodecorrido,pkt_infonobreak = pkt_info)
                        lastp = time.time()
                        if ((pkt) and (pkt["checksum_OK"])):
                            if (pkt["tipo_pacote"] == 'S'):
                                # Carrega com as informacoes do nobreak
                                pkt_info = pkt
                            else:
                                if (pkt_info):
                                    # Se tem pacote de hardware, vamos em frente
                                    pkt["nome"] = nome
                                    pkt["ultimaleitura"] = time.time()
                                    # Com os dados do teu nobreak, fizemos algumas mudancas no pacote de retorno
                                    # Vamos calcular por exemplo tua potencia atual do nobreak, o percentual da tua potencia atual em relacao a potencia nominal
                                    # E tambem a autonomia do nobreak
                                    try:
                                        infoups = upsinfo[pkt_info["modelo"]]
                                    except:
                                        infoups = None
                                    if (infoups):
                                        pkt["descricaomodelo"] = infoups["upsdesc"]
                                        pkt["potencia_nominal"] = infoups["VA"]
                                    else:
                                        pkt["descricaomodelo"] = descricaomodelo
                                        pkt["potencia_nominal"] = potencia_nominal
                                    pkt["potencia_nominal"] = potencia_nominal
                                    # Potencia Aparente - Essa vai ser a potencia em Watts que voce vai ter
                                    pkt["potencia_aparente"] = potencia_nominal * fator_conversao
                                    pkt["fator_conversao"] = fator_conversao
                                    if (numero_baterias):
                                        pkt["numero_baterias"] = numero_baterias
                                    else:
                                        pkt["numero_baterias"] = pkt_info["numero_de_baterias"]
                                    pkt["ah"] = ah
                                    pkt["tensao_bateria"] = tensao_bateria
                                    # Calculo da potencia atual
                                    pkt["potencia_nominal_atual"] = pkt["potencia_nominal"] * (pkt["POTRMS"] / 100)
                                    pkt["potencia_aparente_atual"] =  pkt["potencia_aparente"] * (pkt["POTRMS"] / 100)
                                    pkt["amperagem_saida"] = pkt["potencia_aparente_atual"] / tensao_bateria
                                    # Calculo da autonomia
                                    # Calculo Basico: 
                                    # Potencia sendo consumida em Watts / Corrente da Bateria = Corrente Atual
                                    # Duracao da bateria = Ampere-Hora da Bateria / Corrente Atual
                                    # Portanto
                                    # Duracao da bateria = (Ampere-Hora da Bateria / (Potencia sendo consumida em Watts / Tensao da Bateria) * 3600) para dar em segundos
                                    # Outra conta que passaram
                                    # Duracao da Bateria = ((Ampere-Hora da Bateria * Tensão da Bateria em V * fator_conversao) / Consumo em Watts) * 3600
                                    #pkt["autonomia"] = (ah / pkt["amperagem_saida"]) * 3600
                                    pkt["autonomia"] = ((ah * tensao_bateria * fator_conversao) / pkt["potencia_aparente_atual"]) * 3600
                                    if (pkt["valores_status"]["saida_em_220_V"] == 'S'):
                                        pkt["tensao_saida"] = pkt_info["tensao_de_saida_220_V"]
                                        pkt["sobretensao"] = pkt_info["sobretensao_em_220_V"]
                                        pkt["subtensao"] = pkt_info["subtensao_em_220_V"]
                                    else:
                                        pkt["tensao_saida"] = pkt_info["tensao_de_saida_120_V"]
                                        pkt["sobretensao"] = pkt_info["sobretensao_em_120_V"]
                                        pkt["subtensao"] = pkt_info["subtensao_em_120_V"]
                                    # Eficiencia do nobreak: tensao de entrada / tensao de saida
                                    pkt["eficiencia"] = (pkt["VACOUTRMS"] * pkt["VACINRMS"]) / 100
                                    atualizarmaximos(pkt)
                                    # Agora para frente comecamos a fazer os PROCESSAMENTOS dos pacotes
                                    #slog(pprint.pformat(pkt))
                                    if (ativaNUT):
                                        nut(pkt)
                                    if (ativaJSON):
                                        js(pkt)
                                    if (ativaMQTT):
                                        # Para nao sobrecarregar o mqtt, eh bom enviar os dados em uma frequencia menor
                                        if (i % 4 == 0):
                                            mqtt(pkt,nome,subtopico=nome)
                                    if (ativaBD):
                                        bd(pkt)
                                else:
                                    slog("Pacote de Hardware nao foi recebido ainda")
                                    if (send_extended < 4):
                                        enviapacote(ser,1)
                                        send_extended = send_extended + 1
                                    else:
                                        enviapacote(ser,random.randint(0,1))
                    dadoswaiting = ser.in_waiting
            else:
                slog(f"Tempo Insuficiente: incrementando o tempo de leitura. Tempo atual {temposleep} s")
                temposleep = temposleep + 0.1
        time.sleep(temposleep)
        i = i + 1
        
finally:
    slog("Enviando pacote de finalizacao")
    if (ser):
        enviapacote(ser,4)
        ser.close()
        slog("Pacote enviado e serial finalizada")
    else:
        slog("Serial nao estava aberto")
     
        
