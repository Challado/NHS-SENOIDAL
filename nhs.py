import serial
import time
import sys
import os
import json
import pprint
import random
import config
import traceback
from funcoes import *

# Variaveis de controle
pkt_info = None
send_extended = 0

try:
    if (os.path.exists(config.arquivolog)):
        os.unlink(config.arquivolog)        
    ser = None
    i = 0
    interacoes = 0
    temposleep = 1
    lastdp = time.time()
    pkt = None
    pkt_info = None
    # Abre a porta Serial
    ser = serial.Serial(config.device, baudrate=2400, bytesize=8, parity='N', stopbits=1, rtscts=True, exclusive=True)
    while (True):
        # Verifica se houve o timeout de leitura. Caso tenha, zera todos os dados
        lastread = time.time() - lastdp
        if (lastread > config.timeout):
            slog("Timeout de leitura. Ultima leitura a %d segundos atras, em %s. Zerando contadores..." % (lastread,time.strftime("%d/%m/%Y %H:%M:%S",time.localtime(lastdp)))
            if (config.ativaNUT):
                nut(None)
            if (config.ativaJSON):
                js(None)
        if (ser.isOpen() == False):
            ser = serial.Serial(config.device, baudrate=2400, bytesize=8, parity='N', stopbits=1, rtscts=True, exclusive=True)
            slog("Serial estava fechada. Reabrindo...")
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
                        pkt = tratar_datapacket(dp,tempodecorrido,pkt_infonobreak = pkt_info)
                        lastdp = time.time()
                        if ((pkt) and (pkt["checksum_OK"])):
                            if (pkt["tipo_pacote"] == 'S'):
                                # Carrega com as informacoes do nobreak
                                pkt_info = pkt
                            else:
                                if (pkt_info):
                                    # Se tem pacote de hardware, vamos em frente
                                    pkt["nome"] = config.nome
                                    pkt["ultimaleitura"] = time.time()
                                    pkt["ultimaleitura_fmt"] = time.strftime("%d/%m/%Y %H:%M:%S",time.localtime(pkt["ultimaleitura"]))
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
                                        pkt["descricaomodelo"] = config.descricaomodelo
                                        pkt["potencia_nominal"] = config.potencia_nominal
                                    pkt["potencia_nominal"] = config.potencia_nominal
                                    # Potencia Aparente - Essa vai ser a potencia em Watts que voce vai ter
                                    pkt["potencia_aparente"] = config.potencia_nominal * config.fator_conversao
                                    pkt["fator_conversao"] = config.fator_conversao
                                    if (config.numero_baterias):
                                        pkt["numero_baterias"] = config.numero_baterias
                                    else:
                                        pkt["numero_baterias"] = pkt_info["numero_de_baterias"]
                                    pkt["ah"] = config.ah
                                    pkt["tensao_bateria"] = config.tensao_bateria
                                    # Calculo da potencia atual
                                    pkt["potencia_nominal_atual"] = pkt["potencia_nominal"] * (pkt["POTRMS"] / 100)
                                    pkt["potencia_aparente_atual"] =  pkt["potencia_aparente"] * (pkt["POTRMS"] / 100)
                                    pkt["amperagem_saida"] = 0
                                    if (config.tensao_bateria > 0):
                                        pkt["amperagem_saida"] = pkt["potencia_aparente_atual"] / config.tensao_bateria
                                    # Calculo da autonomia
                                    # Calculo Basico: 
                                    # Potencia sendo consumida em Watts / Corrente da Bateria = Corrente Atual
                                    # Duracao da bateria = Ampere-Hora da Bateria / Corrente Atual
                                    # Portanto
                                    # Duracao da bateria = (Ampere-Hora da Bateria / (Potencia sendo consumida em Watts / Tensao da Bateria) * 3600) para dar em segundos
                                    # Outra conta que passaram
                                    # Duracao da Bateria = ((Ampere-Hora da Bateria * Tensão da Bateria em V * fator_conversao) / Consumo em Watts) * 3600
                                    #pkt["autonomia"] = (ah / pkt["amperagem_saida"]) * 3600
                                    if (pkt["potencia_aparente_atual"] > 0):
                                        pkt["autonomia"] = ((config.ah * config.tensao_bateria * config.fator_conversao) / pkt["potencia_aparente_atual"]) * 3600
                                    else:
                                        pkt["autonomia"] = ((config.ah * config.tensao_bateria * config.fator_conversao)) * 3600
                                    if (pkt["valores_status"]["modo_bateria"] == 'S'):
                                        pkt["sautonomia"] = segundos_para_tempo(pkt["autonomia"])
                                    else:
                                        pkt["sautonomia"] = "NOBREAK ONLINE"
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
                                    if (config.ativaNUT):
                                        nut(pkt)
                                    if (config.ativaJSON):
                                        js(pkt)
                                    if (config.ativaMQTT):
                                        # Para nao sobrecarregar o mqtt, eh bom enviar os dados em uma frequencia menor
                                        if (i % config.mqtt_interval == 0):
                                            mqtt(pkt,config.nome,subtopico=config.nome)
                                    if (config.ativaBD):
                                        bd(pkt)
                    dadoswaiting = ser.in_waiting
            if (pkt_info == None):
                # Ainda nao foi inicializado o sistema e/ou nao recebi o pacote de hardware. Tentando enviar para receber os dados
                slog("Pacote de Hardware nao foi recebido ainda")
                if (send_extended < 4):
                    enviapacote(ser,1)
                    send_extended = send_extended + 1
                else:
                    enviapacote(ser,random.randint(0,1))
                slog(f"Tempo Insuficiente: incrementando o tempo de leitura. Tempo atual {temposleep} s.")
                temposleep = temposleep + 0.1
        time.sleep(temposleep)
        i = i + 1
except Exception as inst:
    slog("Houve uma excecao:\r\n\r\n%s\r\n--------------\r\n%s\r\n--------------" % (inst, traceback.format_exc()))       
finally:
    slog("Enviando pacote de finalizacao...")
    if (ser):
        enviapacote(ser,4)
        ser.close()
        slog("Pacote enviado e serial finalizada.")
    else:
        slog("Serial nao estava aberto. Finalizando mesmo assim.")
     
        
