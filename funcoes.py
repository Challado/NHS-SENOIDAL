import os
import os
import sys
import time
import datetime
import pprint
import struct
import pty
import termios
import json
import sqlite3
import paho.mqtt.client as mqttclient
import config

datapacket = []
datapacketstart = False
# Define some variables
mqttcli = None
mqtt_connected = False

minmax = {
            "voltagem_entrada": {"max": float('-inf'), "min": float('inf')},
            "tensaobateria": {"max": float('-inf'), "min": float('inf')},
            "potencia": {"max": float('-inf'), "min": float('inf')},
            "voltagem_saida": {"max": float('-inf'), "min": float('inf')},
            "temperatura": {"max": float('-inf'), "min": float('inf')},
            "amperagem_saida": {"max": float('-inf'), "min": float('inf')}
        }
        
# Declaracao do array com os dados do nobreak e VA
# Caso queira sobrescrever, va ao codigo principal
upsinfo = {
    0: {"upsdesc": "NHS LINHA SENOIDAL", "VA": 3000},
    1: {"upsdesc": "NHS COMPACT PLUS", "VA": 1000},
    2: {"upsdesc": "NHS COMPACT PLUS SENOIDAL", "VA": 1000},
    3: {"upsdesc": "NHS COMPACT PLUS RACK", "VA": 1000},
    4: {"upsdesc": "NHS PREMIUM PDV", "VA": 1500},
    5: {"upsdesc": "NHS PREMIUM PDV SENOIDAL", "VA": 1500},
    6: {"upsdesc": "NHS PREMIUM 1500VA", "VA": 1500},
    7: {"upsdesc": "NHS PREMIUM 2200VA", "VA": 2200},
    8: {"upsdesc": "NHS PREMIUM SENOIDAL", "VA": 1500},
    9: {"upsdesc": "NHS LASER 2600VA", "VA": 2600},
    10: {"upsdesc": "NHS LASER 3300VA", "VA": 3300},
    11: {"upsdesc": "NHS LASER 2600VA ISOLADOR", "VA": 2600},
    12: {"upsdesc": "NHS LASER SENOIDAL", "VA": 2600},
    13: {"upsdesc": "NHS LASER ON-LINE", "VA": 2600},
    15: {"upsdesc": "NHS COMPACT PLUS 2003", "VA": 1000},
    16: {"upsdesc": "COMPACT PLUS SENOIDAL 2003", "VA": 1000},
    17: {"upsdesc": "COMPACT PLUS RACK 2003", "VA": 1000},
    18: {"upsdesc": "PREMIUM PDV 2003", "VA": 1500},
    19: {"upsdesc": "PREMIUM PDV SENOIDAL 2003", "VA": 1500},
    20: {"upsdesc": "PREMIUM 1500VA 2003", "VA": 1500},
    21: {"upsdesc": "PREMIUM 2200VA 2003", "VA": 2200},
    22: {"upsdesc": "PREMIUM SENOIDAL 2003", "VA": 1500},
    23: {"upsdesc": "LASER 2600VA 2003", "VA": 2600},
    24: {"upsdesc": "LASER 3300VA 2003", "VA": 3300},
    25: {"upsdesc": "LASER 2600VA ISOLADOR 2003", "VA": 2600},
    26: {"upsdesc": "LASER SENOIDAL 2003", "VA": 2600},
    27: {"upsdesc": "PDV ONLINE 2003", "VA": 1500},
    28: {"upsdesc": "LASER ONLINE 2003", "VA": 3300},
    29: {"upsdesc": "EXPERT ONLINE 2003", "VA": 5000},
    30: {"upsdesc": "MINI 2", "VA": 500},
    31: {"upsdesc": "COMPACT PLUS 2", "VA": 1000},
    32: {"upsdesc": "LASER ON-LINE", "VA": 2600},
    33: {"upsdesc": "PDV SENOIDAL 1500VA", "VA": 1500},
    34: {"upsdesc": "PDV SENOIDAL 1000VA", "VA": 1000},
    36: {"upsdesc": "LASER ONLINE 3750VA", "VA": 3750},
    37: {"upsdesc": "LASER ONLINE 5000VA", "VA": 5000},
    38: {"upsdesc": "PREMIUM SENOIDAL 2000VA", "VA": 2000},
    39: {"upsdesc": "LASER SENOIDAL 3500VA", "VA": 3500},
    40: {"upsdesc": "PREMIUM PDV 1200VA", "VA": 1200},
    41: {"upsdesc": "PREMIUM 1500VA", "VA": 1500},
    42: {"upsdesc": "PREMIUM 2200VA", "VA": 2200},
    43: {"upsdesc": "LASER 2600VA", "VA": 2600},
    44: {"upsdesc": "LASER 3300VA", "VA": 3300},
    45: {"upsdesc": "COMPACT PLUS SENOIDAL 700VA", "VA": 700},
    46: {"upsdesc": "PREMIUM ONLINE 2000VA", "VA": 2000},
    47: {"upsdesc": "EXPERT ONLINE 10000VA", "VA": 10000},
    48: {"upsdesc": "LASER SENOIDAL 4200VA", "VA": 4200},
    49: {"upsdesc": "NHS COMPACT PLUS EXTENDIDO 1500VA", "VA": 1500},
    50: {"upsdesc": "LASER ONLINE 6000VA", "VA": 6000},
    51: {"upsdesc": "LASER EXT 3300VA", "VA": 3300},
    52: {"upsdesc": "NHS COMPACT PLUS 1200VA", "VA": 1200},
    53: {"upsdesc": "LASER SENOIDAL 3000VA GII", "VA": 3000},
    54: {"upsdesc": "LASER SENOIDAL 3500VA GII", "VA": 3500},
    55: {"upsdesc": "LASER SENOIDAL 4200VA GII", "VA": 4200},
    56: {"upsdesc": "LASER ONLINE 3000VA", "VA": 3000},
    57: {"upsdesc": "LASER ONLINE 3750VA", "VA": 3750},
    58: {"upsdesc": "LASER ONLINE 5000VA", "VA": 5000},
    59: {"upsdesc": "LASER ONLINE 6000VA", "VA": 6000},
    60: {"upsdesc": "PREMIUM ONLINE 2000VA", "VA": 2000},
    61: {"upsdesc": "PREMIUM ONLINE 1500VA", "VA": 1500},
    62: {"upsdesc": "PREMIUM ONLINE 1200VA", "VA": 1200},
    63: {"upsdesc": "COMPACT PLUS II MAX 1400VA", "VA": 1400},
    64: {"upsdesc": "PREMIUM PDV MAX 2200VA", "VA": 2200},
    65: {"upsdesc": "PREMIUM PDV 3000VA", "VA": 3000},
    66: {"upsdesc": "PREMIUM SENOIDAL 2200VA GII", "VA": 2200},
    67: {"upsdesc": "LASER PRIME SENOIDAL 3200VA GII", "VA": 3200},
    68: {"upsdesc": "PREMIUM RACK ONLINE 3000VA", "VA": 3000},
    69: {"upsdesc": "PREMIUM ONLINE 3000VA", "VA": 3000},
    70: {"upsdesc": "LASER ONLINE 4000VA", "VA": 4000},
}

def imprime(dados):
    adado = []
    hdado = []
    sdado = []
    for dado in dados:
         adado.append(dado)
         if (isinstance(dado,bytes)):
             dado = convertebyte(dado)
         hdado.append(hex(dado))
         sdado.append(str(dado))
    return [adado, hdado, sdado]

def calcula_checksum(pacote,posicao_inicial = 1,posicao_final = -2):
    pkt = pacote[posicao_inicial:posicao_final]
    novopacote = []
    for item in pkt:
        if (isinstance(item,bytes)):
            novopacote.append(convertebyte(item))
        else:
            novopacote.append(int(item))
    soma2 = sum(novopacote)  # Soma de todos os bytes, exceto o cabeçalho e o final
    return (soma2 & 0xFF)

def invertearray(arr):
    return arr[::-1]
    
def slog(s,endchr="\r\n",debug=False,lf = None):
    if (lf == None):
        lf = config.arquivolog
    arq = open(lf,"a+")
    arq.write(time.strftime("%d/%m/%Y %H:%M:%S") + " -- " + str(s).strip().encode('utf-8','replace').decode('utf-8','replace') + endchr)
    arq.close()
    if (debug):
        print(s)

def convertebyte(b,tipo = "big",doFloat = False):
    resultado = b
    if (isinstance(b,bytes)):
        resultado = int.from_bytes(b,tipo)
        if (doFloat):
            if (tipo == "big"):
                resultado = struct.unpack('>f', resultado.to_bytes(4, byteorder=tipo))[0]
            else:
                resultado = struct.unpack('<f', resultado.to_bytes(4, byteorder=tipo))[0]
    return resultado
    
def retornahexa(array):
    hexarray = []
    for valor in array:
        if (isinstance(valor,bytes)):
            valor = convertebyte(valor)
        hexarray.append(str(hex(valor)).upper().replace('X','x'))
    return hexarray
    
def enviapacote(ser,tipopacote = 0):
    # Ja deixa no jeito um pacote data e hora
    dt = datetime.datetime.now()
    # Envia varios tipos de pacote
       
    pacotes_inicializacao = [
        # 0 - Inicializacao normal
        [0xFF, 0x09, 0x53, 0x03, 0x00, 0x00, 0x00, 0x5F, 0xFE],
        # 1 - Inicializacao Estendida
        [0xFF, 0x09, 0x53, 0x83, 0x00, 0x00, 0x00, 0xDF, 0xFE],
        # 2 - Finalizacao
        [0xFF, 0x09, 0x53, 0x01, 0x00, 0x00, 0x00, 0x5D, 0xFE], 
        # 3 - Valor de potencia
        [0xFF, ord('W'), 3, dt.year & 0xFF, dt.month & 0xFF, dt.day & 0xFF, 0x00, dt.hour & 0xFF, dt.minute & 0xFF, dt.second & 0xFF, 0xF3],
        # 4 - Finalizacao Extendida
        [0xFF, 0x09, 0x53, 0b00000000, 0x00, 0x00, 0x00, 0xFE],
        # 5 - Pacote especial
        [0xFF, 0x5, 0x1, 0x6, 0xFE]
    ]
    pacote_inicializacao = pacotes_inicializacao[tipopacote]
    if not (tipopacote in [5]):
        checksum = calcula_checksum(pacote_inicializacao)
        pacote_inicializacao[7] = checksum
    if (ser):
        ser.write(bytearray(pacote_inicializacao))
        ser.flush()
        ser.reset_input_buffer()
    slog(f"Pacote enviado: {pacote_inicializacao} {retornahexa(pacote_inicializacao)}.")
    
def arraybinario(data):
    """Turn the string data, into a list of bits (1, 0)'s"""
    if sys.version_info[0] < 3:
        # Turn the strings into integers. Python 3 uses a bytes
        # class, which already has this behaviour.
        data = [ord(c) for c in data]
    l = len(data) * 8
    result = [0] * l
    pos = 0
    for ch in data:
        i = 7
        while i >= 0:
            if ch & (1 << i) != 0:
                result[pos] = 1
            else:
                result[pos] = 0
            pos += 1
            i -= 1
    return invertearray(result)


# Função para imprimir os bits de um byte
def imprimir_bits(byte):
    return f'{byte:08b}'

def tratar_datapacket(pacote,tempoleitura,DebugTela = False,pkt_infonobreak = None):
    # Os pacotes NHS tem varios tamanhos e respostas
    # Consulte documentacao para maiores detalhes
    resposta = None
    lenpacote = len(pacote)
    tamanhopacote = convertebyte(pacote[1])
    # Nunca confie na informacao repassada do pacote. Sempre confira o tamanho do pacote com o seu tamanho real
    if (lenpacote >= 17) and (tamanhopacote == lenpacote):
        resposta = {}
        resposta["tempoleitura"] = tempoleitura
        resposta["comprimento"] = tamanhopacote
        resposta["tipo_pacote"] = pacote[2].decode('utf-8', 'replace')
        if (resposta["comprimento"] in [18,50]):
            # Inicializa alguns valores obrigatorios
            resposta["serial"] = ''

            resposta["modelo"] = convertebyte(pacote[3])
            resposta["versao_do_hardware"] = convertebyte(pacote[4])
            resposta["versao_do_software"] = convertebyte(pacote[5])
            resposta["configuracao"] = convertebyte(pacote[6])
            resposta["arraybits_configuracao"] = arraybinario(pacote[6])
            
            valores = {}
            valores["modo_oem"] = 'S' if resposta["arraybits_configuracao"][0] == 1 else 'N'
            valores["buzzer_inativo"] = 'S' if resposta["arraybits_configuracao"][1] == 1 else 'N'
            valores["potmin_desativada"] = 'S' if resposta["arraybits_configuracao"][2] == 1 else 'N'
            valores["rearme_ativado"] = 'S' if resposta["arraybits_configuracao"][3] == 1 else 'N'
            valores["bootloader_ativado"] = 'S' if resposta["arraybits_configuracao"][4] == 1 else 'N'
            valores["alarme_rtc_ativado"] = 'S' if resposta["arraybits_configuracao"][5] == 1 else 'N'
            resposta["valores_configuracao"] = valores
            
            resposta["numero_de_baterias"] = convertebyte(pacote[7])
            resposta["subtensao_em_120_V"] = convertebyte(pacote[8])
            resposta["sobretensao_em_120_V"] = convertebyte(pacote[9])
            resposta["subtensao_em_220_V"] = convertebyte(pacote[10])
            resposta["sobretensao_em_220_V"] = convertebyte(pacote[11])
            resposta["tensao_de_saida_120_V"] = convertebyte(pacote[12])
            resposta["tensao_de_saida_220_V"] = convertebyte(pacote[13])
            resposta["status"] = convertebyte(pacote[14])
            resposta["arraybits_status"] = arraybinario(pacote[14])
            
            valores = {}
            valores["entrada_em_220_V"] = 'S' if resposta["arraybits_status"][0] == 1 else 'N'
            valores["saida_em_220_V"] = 'S' if resposta["arraybits_status"][1] == 1 else 'N'
            valores["bateria_selada"] = 'S' if resposta["arraybits_status"][2] == 1 else 'N'
            valores["mostrar_tensao_de_saida"] = 'S' if resposta["arraybits_status"][3] == 1 else 'N'
            valores["mostrar_temperatura"] = 'S' if resposta["arraybits_status"][4] == 1 else 'N'
            valores["mostrar_corrente_do_carregador"] = 'S' if resposta["arraybits_status"][5] == 1 else 'N'
            resposta["valores_status"] = valores
            
            resposta["corrente_do_carregador"] = convertebyte(pacote[15])

            checksum = calcula_checksum(pacote)
            resposta["checksum_calculado"] = checksum
            if (resposta["comprimento"] == 18):
                resposta["checksum"] = convertebyte(pacote[16])
            else:
                resposta["checksum"] = convertebyte(pacote[48])
            resposta["checksum_OK"] = False
            if (checksum == resposta["checksum"]):
                resposta["checksum_OK"] = True                
            if (resposta["comprimento"] == 50):
                i = 0
                strSerial = ''
                resposta["serial"] = ''
                while (i < 16):
                    valores = {}
                    posicao = 16 + i
                    valores["inteiro"] = convertebyte(pacote[posicao])
                    valores["caractere"] = pacote[posicao].decode("utf-8","replace")
                    resposta[f"serial{i}"] = valores 
                    strSerial = strSerial + pacote[posicao].decode("utf-8","replace")
                    i = i + 1
                resposta["serial"] = strSerial
                resposta["ano"] = convertebyte(pacote[32])
                resposta["mes"] = convertebyte(pacote[33])
                resposta["dia_da_semana"] = convertebyte(pacote[34])
                resposta["dia"] = convertebyte(pacote[35])
                resposta["hora"] = convertebyte(pacote[36])
                resposta["minuto"] = convertebyte(pacote[37])
                resposta["segundo"] = convertebyte(pacote[38])
                resposta["alarme_mes"] = convertebyte(pacote[39])
                resposta["alarme_dia_da_semana"] = convertebyte(pacote[40])
                resposta["alarme_dia"] = convertebyte(pacote[41])
                resposta["alarme_hora"] = convertebyte(pacote[42])
                resposta["alarme_minuto"] = convertebyte(pacote[43])
                resposta["alarme_segundo"] = convertebyte(pacote[44])
        if (resposta["comprimento"] == 21):
            # pacote de Dados
            partealta = convertebyte(pacote[3],"little")
            partebaixa = convertebyte(pacote[4],"little")
            dado = float(f"{partealta}.{partebaixa}")
            resposta["tensao_de_entrada_rms_parte_alta"] = partealta
            resposta["tensao_de_entrada_rms_parte_baixa"] = partebaixa
            resposta["VACINRMS"] = dado
            
            partealta = convertebyte(pacote[5])
            partebaixa = convertebyte(pacote[6])
            dado = float(f"{partealta}.{partebaixa}")
            resposta["tensao_bateria_parte_alta"] = partealta
            resposta["tensao_bateria_parte_baixa"] = partebaixa
            resposta["VDCMED"] = dado
            if (partebaixa == 0):
                resposta["tensao_atual_bateria"] = dado / 10
            else:
                resposta["tensao_atual_bateria"] = dado
                
            resposta["POTRMS"] = convertebyte(pacote[7])
            
            partealta = convertebyte(pacote[8])
            partebaixa = convertebyte(pacote[9])
            dado = float(f"{partealta}.{partebaixa}")
            resposta["tensao_de_entrada_minima_parte_alta"] = partealta
            resposta["tensao_de_entrada_minima_parte_baixa"] = partebaixa
            resposta["VACINRMSMIN"] = dado
            
            partealta = convertebyte(pacote[10])
            partebaixa = convertebyte(pacote[11])
            dado = float(f"{partealta}.{partebaixa}")
            resposta["tensao_de_entrada_maxima_parte_alta"] = partealta
            resposta["tensao_de_entrada_maxima_parte_baixa"] = partebaixa
            resposta["VACINRMSMAX"] = dado
            
            partealta = convertebyte(pacote[12])
            partebaixa = convertebyte(pacote[13])
            dado = float(f"{partealta}.{partebaixa}")
            resposta["tensao_de_saida_rms_parte_alta"] = partealta
            resposta["tensao_de_saida_rms_parte_baixa"] = partebaixa
            resposta["VACOUTRMS"] = dado
            
            partealta = convertebyte(pacote[14])
            partebaixa = convertebyte(pacote[15])
            dado = float(f"{partealta}.{partebaixa}")
            resposta["temperatura_parte_alta"] = partealta
            resposta["temperatura_parte_baixa"] = partebaixa
            resposta["TEMPMED"] = dado
            
            resposta["ICARREGRMS"] = convertebyte(pacote[16])
            # Na documentacao diz que cada 25 pesos = 750 mA, o que quer dizer que a cada 1 peso é 30 mA
            resposta["potencia_carregador"] = resposta["ICARREGRMS"] * 30
            
            resposta["status"] = convertebyte(pacote[17])
            resposta["arraybits_status"] = arraybinario(pacote[17])
            
            
            status = resposta["status"]
            valores = {}
            valores["carregador_ativo"] = 'S' if bool(status & 0b10000000) else 'N'
            valores["bypass_ativo"] = 'S' if bool(status & 0b01000000) else 'N'
            valores["saida_em_220_V"] = 'S' if bool(status & 0b00100000) else 'N'
            valores["entrada_em_220_V"] = 'S' if bool(status & 0b00010000) else 'N'
            valores["falha_rapida_da_rede"] = 'S' if bool(status & 0b00001000) else 'N'
            valores["falha_da_rede"] = 'S' if bool(status & 0b00000100) else 'N'
            valores["bateria_baixa"] = 'S' if bool(status & 0b00000010) else 'N'
            valores["modo_bateria"] = 'S' if bool(status & 0b00000001) else 'N'
            resposta["valores_status"] = valores
            resposta["checksum"] = convertebyte(pacote[19])
            checksum = calcula_checksum(pacote)
            resposta["checksum_calculado"] = checksum
            resposta["checksum_OK"] = False
            if (checksum == resposta["checksum"]):
                resposta["checksum_OK"] = True            
            resposta["dadosnobreak"] = pkt_infonobreak
    if (DebugTela):
        pprint.pprint(resposta)
    return resposta

def criadatapacket(dado):
    global datapacket
    global datapacketstart
    retorno = None
    
    dado = dado
    if (dado ==  b'\xff'):
        # Inicio do pacote
        datapacketstart = True
    if (datapacketstart):
        datapacket.append(dado)
        if (dado == b'\xfe'):
            # Fim da transmissao
            hex = retornahexa(datapacket)
            slog(f"Datapacket recebido: {datapacket} -- {hex}. Tamanho {len(datapacket)}.")
            retorno = datapacket
            datapacket = []
            datapacketstart = False
    return retorno

def atualizarmaximos(pkt_dados):
    global minmax
    minmax["voltagem_entrada"]["max"] = pkt_dados["VACINRMSMIN"]
    minmax["voltagem_entrada"]["min"] = pkt_dados["VACINRMSMAX"]
    if (pkt_dados["tensao_atual_bateria"] > minmax["tensaobateria"]["max"]):
        minmax["tensaobateria"]["max"] = pkt_dados["tensao_atual_bateria"]
    if (pkt_dados["tensao_atual_bateria"] < minmax["tensaobateria"]["min"]):
        minmax["tensaobateria"]["min"] = pkt_dados["tensao_atual_bateria"]
    if (pkt_dados["POTRMS"] > minmax["potencia"]["max"]):
        minmax["potencia"]["max"] = pkt_dados["POTRMS"]
    if (pkt_dados["POTRMS"] < minmax["potencia"]["min"]):
        minmax["potencia"]["min"] = pkt_dados["POTRMS"]
    if (pkt_dados["VACOUTRMS"] > minmax["voltagem_saida"]["max"]):
        minmax["voltagem_saida"]["max"] = pkt_dados["VACOUTRMS"]
    if (pkt_dados["VACOUTRMS"] < minmax["voltagem_saida"]["min"]):
        minmax["voltagem_saida"]["min"] = pkt_dados["VACOUTRMS"]
    if (pkt_dados["TEMPMED"] > minmax["temperatura"]["max"]):
        minmax["temperatura"]["max"] = pkt_dados["TEMPMED"]
    if (pkt_dados["TEMPMED"] < minmax["temperatura"]["min"]):
        minmax["temperatura"]["min"] = pkt_dados["TEMPMED"]
    if (pkt_dados["amperagem_saida"] > minmax["amperagem_saida"]["max"]):
        minmax["amperagem_saida"]["max"] = pkt_dados["amperagem_saida"]
    if (pkt_dados["amperagem_saida"] < minmax["amperagem_saida"]["min"]):
        minmax["amperagem_saida"]["min"] = pkt_dados["amperagem_saida"]

def js(pkt):
    # Funcao que ira criar a saida de dados para o JSON
    # Defina aqui o caminho onde voce quer que o software guarde os dados
    arquivo = getattr(config, "arquivojson", None)
    if (arquivo == None):
        arquivo = "/run/nhs/nhs.json"
    diretorio = os.path.dirname(arquivo)
    if (not os.path.exists(diretorio)):
        os.makedirs(diretorio)
    arq = open(arquivo,"w")
    if (pkt):
        arq.write(json.dumps(pkt))
    arq.close()

def nut(pkt):        
    # Funcao que ira criar a saida de dados para o NUT
    # Defina aqui o caminho onde voce quer que o software guarde os dados
    global minmax
    arquivo = getattr(config,"arquivonut", None)
    if (arquivo == None):
        arquivo = "/run/nhs/nut.seq"
    diretorio = os.path.dirname(arquivo)
    if (not os.path.exists(diretorio)):
        os.makedirs(diretorio)
    arq = open(arquivo,"w")
    if (pkt):
        # Vamos iniciar a montagem do pacote do nut conforme a documentacao
        #|====================================================================================
        #| Name                | Description                                | Example value
        #| device.model        | Device model                               | BladeUPS
        #| device.mfr          | Device manufacturer                        | Eaton
        #| device.serial       | Device serial number (opaque string)       | WS9643050926
        #| device.type         | Device type (ups, pdu, scd, psu, ats)      | ups
        #| device.description  | Device description (opaque string)         | Some ups
        #| device.contact      | Device administrator name (opaque string)  | John Doe
        #| device.location     | Device physical location (opaque string)   | 1st floor
        #| device.part         | Device part number (opaque string)         | 123456789
        #| device.macaddr      | Physical network address of the device     | 68:b5:99:f5:89:27
        #| device.uptime       | Device uptime in seconds                   | 1782
        #| device.count        | Total number of daisychained devices       | 1
        #|====================================================================================
        arq.write("device.model: %s\r\n" % pkt["descricaomodelo"])
        arq.write("device.mfr: %s\r\n" % "NHS")
        arq.write("device.serial: %s\r\n" % pkt["dadosnobreak"]["serial"])
        arq.write("device.type: %s\r\n" % "ups")
        arq.write("device.description: %s\r\n" % pkt["nome"])
        
        # Vamos descobrir o estado do nobreak
        status = "OL"
        btstate = "resting"
        st = pkt["valores_status"]
        if (st["modo_bateria"] == 'S'):
            # Está na bateria
            status = "OB"
            if (st["bateria_baixa"] == 'S'):
                # If battery is LOW, warn user!
                status = "LB"
        else:
            # Verifique se a ENERGIA (rede elétrica) não está presente. Bem, podemos verificar a falha na rede também...
            if (pkt["VACINRMS"] <= pkt["subtensao"]) or (st["falha_da_rede"] == 'S'):
                status = "OB DISCHRG"
                btstate = "discharging" 
            else:
                # MAINS is present. We need to check some situations. NHS only charge if have more than min_input_power. If MAINS is less or equal min_input_power then ups goes to BATTERY
                if (pkt["VACINRMS"] > pkt["subtensao"]):
                    if (st["carregador_ativo"] == 'S'):
                        status = "OL CHRG"
                        btstate = "charging"
                    else:
                        if (st["falha_da_rede"] == 'S') or (st["falha_rapida_da_rede"] == 'S'):
                            status = "OB"
                        else:
                            
                            status = "OL"
                else:
                    if (st["bateria_baixa"] == 'S'):
                        status = "LB"
                    else:
                        status = "OB"
        # |===============================================================================
        # | Name                  | Description                  | Example value
        # | ups.status            | UPS status                   | <<_status_data,OL>>
        arq.write("ups.status: %s\r\n" % status)
        # | ups.alarm             | UPS alarms                   | OVERHEAT
        # | ups.time              | Internal UPS clock time
        #                           (opaque string)              | 12:34
        # | ups.date              | Internal UPS clock date
        #                           (opaque string)              | 01-02-03
        # | ups.model             | UPS model                    | SMART-UPS 700
        arq.write("ups.model: %s\r\n" % pkt["descricaomodelo"])
        # | ups.mfr               | UPS manufacturer             | APC
        arq.write("ups.mfr: %s\r\n" % "NHS")
        # | ups.mfr.date          | UPS manufacturing date
        #                           (opaque string)              | 10/17/96
        # | ups.serial            | UPS serial number (opaque
        #                           string)                      | WS9643050926
        arq.write("ups.serial: %s\r\n" % pkt["dadosnobreak"]["serial"])
        # | ups.vendorid          | Vendor ID for USB devices    | 0463
        # | ups.productid         | Product ID for USB devices   | 0001
        # | ups.firmware          | UPS firmware (opaque string) | 50.9.D
        arq.write("ups.firmware: %04.4d\r\n" % pkt["dadosnobreak"]["versao_do_software"])
        # | ups.firmware.aux      | Auxiliary device firmware    | 4Kx
        arq.write("ups.firmware.aux: %04.4d\r\n" % pkt["dadosnobreak"]["versao_do_hardware"])
        # | ups.temperature       | UPS temperature (degrees C)  | 042.7
        arq.write("ups.temperature: %03.3d\r\n" % pkt["TEMPMED"])
        # | ups.load              | Load on UPS (percent)        | 023.4
        arq.write("ups.load: %03.3d\r\n" % pkt["POTRMS"])
        # | ups.load.high         | Load when UPS
        #                           switches to overload
        #                           condition ("OVER") (percent) | 100
        # | ups.id                | UPS system identifier
        #                           (opaque string)              | Sierra
        arq.write("ups.id: %s\r\n" % pkt["nome"])
        # | ups.delay.start       | Interval to wait before
        #                           restarting the load
        #                           (seconds)                    | 0
        # | ups.delay.reboot      | Interval to wait before
        #                           rebooting the UPS (seconds)  | 60
        # | ups.delay.shutdown    | Interval to wait after
        #                           shutdown with delay command
        #                           (seconds)                    | 20
        # | ups.timer.start       | Time before the load will be
        #                           started (seconds)            | 30
        # | ups.timer.reboot      | Time before the load will be
        #                           rebooted (seconds)           | 10
        # | ups.timer.shutdown    | Time before the load will be
        #                           shutdown (seconds)           | 20
        # | ups.test.interval     | Interval between self tests
        #                           (seconds)                    | 1209600 (two weeks)
        # | ups.test.result       | Results of last self test
        #                           (opaque string)              | Bad battery pack
        # | ups.test.date         | Date of last self test
        #                           (opaque string)              | 07/17/12
        # | ups.display.language  | Language to use on front
        #                           panel (*** opaque)           | E
        # | ups.contacts          | UPS external contact sensors
        #                           (*** opaque)                 | F0
        # | ups.efficiency        | Efficiency of the UPS (ratio
        #                           of the output current on the
        #                           input current) (percent)     | 95
        arq.write("ups.efficiency: %04.2f\r\n" % pkt["eficiencia"])
        # | ups.power             | Current value of apparent
        #                           power (Volt-Amps)            | 500
        arq.write("ups.power: %03.3d\r\n" % pkt["potencia_nominal_atual"])
        # | ups.power.nominal     | Nominal value of apparent
        #                           power (Volt-Amps)            | 500
        arq.write("ups.power.nominal: %03.3d\r\n" % pkt["potencia_nominal"])
        # | ups.realpower         | Current value of real
        #                           power (Watts)                | 300
        arq.write("ups.realpower: %03.3d\r\n" % pkt["potencia_aparente_atual"])
        # | ups.realpower.nominal | Nominal value of real
        #                           power (Watts)                | 300
        arq.write("ups.realpower.nominal: %03.3d\r\n" % pkt["potencia_aparente"])
        # | ups.beeper.status     | UPS beeper status
        #                           (enabled, disabled or muted) | enabled
        if pkt["dadosnobreak"]["valores_configuracao"]["buzzer_inativo"] == 'S':
            strstatus = "disabled"
        else: 
            strstatus = "enabled"
        arq.write("ups.beeper.status: %s\r\n" % strstatus) 
        # | ups.type              | UPS type (*** opaque)        | offline
        # | ups.watchdog.status   | UPS watchdog status
        #                           (enabled or disabled)        | disabled
        # | ups.start.auto        | UPS starts when mains is
        #                           (re)applied                  | yes
        # | ups.start.battery     | Allow to start UPS from
        #                           battery                      | yes
        # | ups.start.reboot      | UPS coldstarts from battery
        #                           (enabled or disabled)        | yes
        # | ups.shutdown          | Enable or disable UPS
        #                           shutdown ability (poweroff)  | enabled
        # |===============================================================================

        #|=================================================================================
        #| Name                        | Description                       | Example value
        #| input.voltage               | Input voltage (V)                 | 121.5
        arq.write("input.voltage: %03.3d\r\n" % pkt["VACINRMS"])
        #| input.voltage.maximum       | Maximum incoming voltage seen (V) | 130
        arq.write("input.voltage.maximum: %03.3d\r\n" % minmax["voltagem_entrada"]["max"])
        #| input.voltage.minimum       | Minimum incoming voltage seen (V) | 100
        arq.write("input.voltage.minimum: %03.3d\r\n" % minmax["voltagem_entrada"]["min"])
        #| input.voltage.status        | Status relative to the
        #                                thresholds                        | critical-low
        # Valores possiveis aqui
        # good - Esta entre o maximo e o minimo
        # warning-low - Alerta que esta quase chegando no minimo
        # critical-low - Chegou no minimo
        # warning-high - Alerta que esta quase chegando no maximo
        # critical-high - Chegou no maximo
        # 
        # Vamos atribuir que esse valor seja em torno de 20% do valor maximo e minimo
        wlow = pkt["subtensao"] + (pkt["subtensao"] * 0.2)
        clow = pkt["subtensao"] + (pkt["subtensao"] * 0.1)
        whigh = pkt["sobretensao"] - (pkt["sobretensao"] * 0.2)
        chigh = pkt["sobretensao"] - (pkt["sobretensao"] * 0.1)
        if (pkt["VACINRMS"] < clow):
            arq.write("input.voltage.status: %s\r\n" % "critical-low")
        elif (pkt["VACINRMS"] > chigh):
            arq.write("input.voltage.status: %s\r\n" % "critical-high")
        elif (pkt["VACINRMS"] < wlow):
            arq.write("input.voltage.status: %s\r\n" % "warning-low")
        elif (pkt["VACINRMS"] > whigh):
            arq.write("input.voltage.status: %s\r\n" % "warning-high")
        else:
            arq.write("input.voltage.status: %s\r\n" % "good")
        #| input.voltage.low.warning   | Low warning threshold (V)         | 205
        arq.write("input.voltage.low.warning: %03.3d\r\n" % wlow)
        #| input.voltage.low.critical  | Low critical threshold (V)        | 200
        arq.write("input.voltage.low.critical: %03.3d\r\n" % clow)
        #| input.voltage.high.warning  | High warning threshold (V)        | 230
        arq.write("input.voltage.high.warning: %03.3d\r\n" % whigh)
        #| input.voltage.high.critical | High critical threshold (V)       | 240
        arq.write("input.voltage.high.critical: %03.3d\r\n" % chigh)
        #| input.voltage.nominal       | Nominal input voltage (V)         | 120
        arq.write("input.voltage.nominal: %03.3d\r\n" % pkt["tensao_saida"])
        #| input.voltage.extended      | Extended input voltage range      | no
        #| input.transfer.delay        | Delay before transfer to mains
        #                                (seconds)                         | 60
        #| input.transfer.reason       | Reason for last transfer
        #                                to battery (*** opaque)           | T
        #| input.transfer.low          | Low voltage transfer point (V)    | 91
        arq.write("input.transfer.low: %03.3d\r\n" % pkt["subtensao"])
        #| input.transfer.high         | High voltage transfer point (V)   | 132
        arq.write("input.transfer.high: %03.3d\r\n" % pkt["sobretensao"])
        #| input.transfer.low.min      | smallest settable low
        #                                voltage transfer point (V)        | 85
        #| input.transfer.low.max      | greatest settable low
        #                                voltage transfer point (V)        | 95
        #| input.transfer.high.min     | smallest settable high
        #                                voltage transfer point (V)        | 131
        #| input.transfer.high.max     | greatest settable high
        #                                voltage transfer point (V)        | 136
        #| input.eco.switchable        | Input High Efficiency (aka ECO)
        #                                mode switch (0-2)                 | normal
        #| input.sensitivity           | Input power sensitivity           | H (high)
        #| input.quality               | Input power quality (***
        #                                opaque)                           | FF
        #| input.current               | Input current (A)                 | 4.25
        #| input.current.nominal       | Nominal input current (A)         | 5.0
        #| input.current.status        | Status relative to the
        #                                thresholds                        | critical-high
        #| input.current.low.warning   | Low warning threshold (A)         | 4
        #| input.current.low.critical  | Low critical threshold (A)        | 2
        #| input.current.high.warning  | High warning threshold (A)        | 10
        #| input.current.high.critical | High critical threshold (A)       | 12
        #| input.feed.color            | Color of the input feed
        #                                (opaque string)                   | 3831236
        #| input.feed.desc             | Description of the input feed     | Feed A
        #| input.frequency             | Input line frequency (Hz)         | 60.00
        #| input.frequency.nominal     | Nominal input line
        #                                frequency (Hz)                    | 60
        #| input.frequency.status      | Frequency status                  | out-of-range
        #| input.frequency.low         | Input line frequency low (Hz)     | 47
        #| input.frequency.high        | Input line frequency high (Hz)    | 63
        #| input.frequency.extended    | Extended input frequency range    | no
        #| input.transfer.boost.low    | Low voltage boosting
        #                                transfer point (V)                | 190
        #| input.transfer.boost.high   | High voltage boosting
        #                                transfer point (V)                | 210
        #| input.transfer.trim.low     | Low voltage trimming
        #                                transfer point (V)                | 230
        #| input.transfer.trim.high    | High voltage trimming
        #                                transfer point (V)                | 240
        #| input.transfer.eco.low      | Low voltage ECO
        #                                transfer point (V)                | 218
        #| input.transfer.bypass.low   | Low voltage Bypass
        #                                transfer point (V)                | 184
        #| input.transfer.eco.high     | High voltage ECO
        #                                transfer point (V)                | 241
        #| input.transfer.bypass.high  | High voltage Bypass
        #                                transfer point (V)                | 264
        #| input.transfer.frequency.bypass.range | Frequency range Bypass transfer
        #                                point (percent of nominal Hz)     | 10
        #| input.transfer.frequency.eco.range    | Frequency range ECO transfer
        #                                point (percent of nominal Hz)     | 5
        #| input.transfer.hysteresis   | Threshold of switching protection modes,
        #                                voltage transfer point (V)        | 10
        #| input.transfer.forced       | Input forced transfer modes
        #                                (enabled or disabled)             | enabled
        #| input.bypass.switch.on      | Put the UPS in bypass mode        | on
        #| input.bypass.switch.off     | Take the UPS out of bypass mode   | disabled
        #| input.load                  | Load on (ePDU) input (percent
        #                                of full)                          | 25
        #| input.realpower             | Current sum value of all (ePDU)
        #                                phases real power (W)             | 300
        #| input.realpower.nominal     | Nominal sum value of all (ePDU)
        #                                phases real power (W)             | 850
        #| input.power                 | Current sum value of all (ePDU)
        #                                phases apparent power (VA)        | 500
        #| input.source                | The current input power source    | 1
        #| input.source.preferred      | The preferred power source        | 1
        #| input.phase.shift           | Voltage dephasing between input
        #                                sources (degrees)                 | 181
        #|=================================================================================

        #|===============================================================================
        #| Name                      | Description                    | Example value
        #| output.voltage            | Output voltage (V)             | 120.9
        #| output.voltage.nominal    | Nominal output voltage (V)     | 120
        #| output.frequency          | Output frequency (Hz)          | 59.9
        #| output.frequency.nominal  | Nominal output frequency (Hz)  | 60
        #| output.current            | Output current (A)             | 4.25
        #| output.current.nominal    | Nominal output current (A)     | 5.0
        #|===============================================================================
        arq.write("output.voltage: %03.3d\r\n" % pkt["VACOUTRMS"])
        arq.write("output.voltage.nominal: %03.3d\r\n" % pkt["tensao_saida"])
        arq.write("output.current: %04.2f\r\n" % pkt["amperagem_saida"])
        #|===============================================================================
        #| Name                  | Description
        #| alarm                 | Alarms for phases, published in ups.alarm
        #| current               | Current (A)
        arq.write("output.current: %04.2f\r\n" % pkt["amperagem_saida"])
        #| current.maximum       | Maximum seen current (A)
        arq.write("output.current.maximum: %04.2f\r\n" % minmax["amperagem_saida"]["max"])
        #| current.minimum       | Minimum seen current (A)
        arq.write("output.current.minimum: %04.2f\r\n" % minmax["amperagem_saida"]["min"])
        #| current.status        | Status relative to the thresholds
        #| current.low.warning   | Low warning threshold (A)
        #| current.low.critical  | Low critical threshold (A)
        #| current.high.warning  | High warning threshold (A)
        #| current.high.critical | High critical threshold (A)
        #| current.peak          | Peak current
        #| voltage               | Voltage (V)
        arq.write("output.voltage: %04.2f\r\n" % pkt["VACOUTRMS"])
        #| voltage.nominal       | Nominal voltage (V)
        arq.write("output.voltage.nominal: %04.2f\r\n" % pkt["tensao_saida"])
        #| voltage.maximum       | Maximum seen voltage (V)
        arq.write("output.voltage.maximum: %04.2f\r\n" % minmax["voltagem_saida"]["max"])
        #| voltage.minimum       | Minimum seen voltage (V)
        arq.write("output.voltage.minimum: %04.2f\r\n" % minmax["voltagem_saida"]["min"])
        #| voltage.status        | Status relative to the thresholds
        if (pkt["VACOUTRMS"] < clow):
            arq.write("voltage.status: %s\r\n" % "critical-low")
        elif (pkt["VACOUTRMS"] > chigh):
            arq.write("voltage.status: %s\r\n" % "critical-high")
        elif (pkt["VACOUTRMS"] < wlow):
            arq.write("voltage.status: %s\r\n" % "warning-low")
        elif (pkt["VACOUTRMS"] > whigh):
            arq.write("voltage.status: %s\r\n" % "warning-high")
        else:
            arq.write("voltage.status: %s\r\n" % "good")
        #| voltage.low.warning   | Low warning threshold (V)
        arq.write("output.voltage.low.warning: %04.2f\r\n" % wlow)
        #| voltage.low.critical  | Low critical threshold (V)
        arq.write("output.voltage.low.critical: %04.2f\r\n" % clow)
        #| voltage.high.warning  | High warning threshold (V)
        arq.write("output.voltage.high.warning: %04.2f\r\n" % whigh)
        #| voltage.high.critical | High critical threshold (V)
        arq.write("output.voltage.high.critical: %04.2f\r\n" % chigh)
        #| power                 | Apparent power (VA)
        arq.write("output.power: %04.2f\r\n" % ((pkt["potencia_nominal"] * pkt["POTRMS"]) /100 ))
        #| power.maximum         | Maximum seen apparent power (VA)
        arq.write("output.power.maximum: %04.2f\r\n" % ((pkt["potencia_nominal"] * minmax["potencia"]["max"]) / 100 ))
        #| power.minimum         | Minimum seen apparent power (VA)
        arq.write("output.power.minimum: %04.2f\r\n" % ((pkt["potencia_nominal"] * minmax["potencia"]["min"]) / 100 ))
        #| power.percent         | Percentage of apparent power related to maximum load
        arq.write("output.power.percent: %03.03d\r\n" % pkt["POTRMS"])
        #| power.maximum.percent | Maximum seen percentage of apparent power
        arq.write("output.power.maximum.percent: %03.3d\r\n" % minmax["potencia"]["max"])
        #| power.minimum.percent | Minimum seen percentage of apparent power
        arq.write("output.power.minimum.percent: %03.3d\r\n" % minmax["potencia"]["min"])
        #| realpower             | Real power (W)
        arq.write("output.realpower: %s\r\n" % pkt["potencia_aparente"])
        #| powerfactor           | Power Factor (dimensionless value between 0.00 and 1.00)
        arq.write("output.powerfactor: %s\r\n" % pkt["fator_conversao"])
        #| crestfactor           | Crest Factor (dimensionless value greater or equal to 1)
        #| load                  | Load on (ePDU) input
        #|===============================================================================
        #|===============================================================================
        #| Name                         | Description                         | Example value
        #| battery.charge               | Battery charge (percent)            | 100.0
        carga = (pkt["tensao_atual_bateria"] * 100) / pkt["tensao_bateria"] 
        if (carga > 100):
            carga = 100
        arq.write("battery.charge: %04.2f\r\n" % carga)
        #| battery.charge.approx        | Rough approximation of battery
        #                                 charge (opaque, percent)            | <85
        #| battery.charge.low           | Remaining battery level when
        #                                 UPS switches to LB (percent)        | 20
        #| battery.charge.restart       | Minimum battery level for
        #                                 UPS restart after power-off         | 20
        #| battery.charge.warning       | Battery level when UPS switches
        #                                 to "Warning" state (percent)        | 50
        #| battery.charger.status       | Status of the battery charger
        #                                 (see the note below)                | charging
        arq.write("battery.charger.status: %s\r\n" % btstate)
        #| battery.voltage              | Battery voltage (V)                 | 24.84
        arq.write("battery.voltage: %04.2f\r\n" % pkt["tensao_atual_bateria"])
        #| battery.voltage.cell.max     | Maximum battery voltage seen of the
        #                                 Li-ion cell (V)                     | 3.44
        #| battery.voltage.cell.min     | Minimum battery voltage seen of the
        #                                 Li-ion cell (V)                     | 3.41
        #| battery.voltage.nominal      | Nominal battery voltage (V)         | 024
        arq.write("battery.voltage.nominal: %03.3d\r\n" % pkt["tensao_bateria"])
        #| battery.voltage.low          | Minimum battery voltage, that
        #                                 triggers FSD status                 | 21,52
        #| battery.voltage.high         | Maximum battery voltage
        #                                 (i.e. battery.charge = 100)         | 26,9
        #| battery.capacity             | Battery capacity (Ah)               | 7.2
        arq.write("battery.capacity: %03.3d\r\n" % pkt["ah"])
        #| battery.capacity.nominal     | Nominal battery capacity (Ah)       | 8.0
        arq.write("battery.capacity.nominal: %03.3d\r\n" % pkt["ah"])
        #| battery.current              | Battery current (A)                 | 1.19
        arq.write("battery.current: %04.2f\r\n" % (pkt["amperagem_saida"] / pkt["numero_baterias"]))
        #| battery.current.total        | Total battery current (A)           | 1.19
        arq.write("battery.current.total: %04.2f\r\n" % pkt["amperagem_saida"])
        #| battery.status               | Health status of the battery
        #                                 (opaque string)                     | ok
        #| battery.temperature          | Battery temperature (degrees C)     | 050.7
        #| battery.temperature.cell.max | Maximum battery temperature seen
        #                                 of the Li-ion cell (degrees C)      | 25.85
        #| battery.temperature.cell.min | Minimum battery temperature seen
        #                                 of the Li-ion cell (degrees C)      | 24.85
        #| battery.runtime              | Battery runtime (seconds)           | 1080
        arq.write("battery.runtime: %03.3d\r\n" % pkt["autonomia"])
        #| battery.runtime.low          | Remaining battery runtime when
        #                                 UPS switches to LB (seconds)        | 180
        arq.write("battery.runtime.low: %03.3d\r\n" % 30)
        #| battery.runtime.restart      | Minimum battery runtime for UPS
        #                                 restart after power-off (seconds)   | 120
        #| battery.alarm.threshold      | Battery alarm threshold             | 0 (immediate)
        #| battery.date                 | Battery installation or last change
        #                                 date (opaque string)                | 11/14/20
        #| battery.date.maintenance     | Battery next change or maintenance
        #                                 date (opaque string)                | 11/13/24
        #| battery.mfr.date             | Battery manufacturing date
        #                                 (opaque string)                     | 2005/04/02
        #| battery.packs                | Number of internal battery packs    | 1
        arq.write("battery.packs: %03.3d\r\n" % pkt["numero_baterias"])
        #| battery.packs.bad            | Number of bad battery packs         | 0
        #| battery.packs.external       | Number of external battery packs    | 1
        #| battery.type                 | Battery chem
        # istry (opaque
        #                                 string)                             | PbAc
        #| battery.protection           | Prevent deep discharge of
        #                                 battery                             | yes
        #| battery.energysave           | Switch off when running on
        #                                 battery and no/low load             | no
        #| battery.energysave.load      | Switch off UPS if on battery and
        #                                 load level lower (percent)          | 5
        #| battery.energysave.delay     | Delay before switch off UPS if on
        #                                 battery and load level low (min)    | 3
        #| battery.energysave.realpower | Switch off UPS if on battery
        #                                 and load level lower (Watts)        | 10
        #|===============================================================================
    else:
        # Nobreak esta com problema
        arq.write("ups.status: COMMBAD\r\n")
    arq.close()

# Define algumas funcoes do mqtt
def conectando(client, userdata, flags, rc):
        global mqtt_connected
        if (rc == 0):
            mqtt_connected = True

def desconectando(client, userdata, flags, rc):
        global mqtt_connected
        mqtt_connected = False

def conectandov2(client, userdata, flags, rc, properties):
        global mqtt_connected
        if (rc == 0):
            mqtt_connected = True

def desconectandov2(client, userdata, flags, rc, properties):
        global mqtt_connected
        mqtt_connected = False

def junta(obj, prefixo=''):
    """
    Achata uma estrutura JSON que pode conter listas e dicionários, transformando-a
    em um único dicionário com chaves compostas pelos níveis hierárquicos.

    Args:
        obj (list, dict, qualquer outro): A estrutura JSON (lista, dicionário ou valor simples).
        prefixo (str): O prefixo das chaves, usado para identificar níveis hierárquicos.

    Returns:
        dict: Um dicionário achatado com chaves compostas e seus valores.
    """
    resultado = {}

    if isinstance(obj, dict):
        for chave, valor in obj.items():
            nova_chave = f"{prefixo}_{chave}" if prefixo else chave
            resultado.update(junta(valor, prefixo=nova_chave))
    elif isinstance(obj, list):
        for i, valor in enumerate(obj):
            nova_chave = f"{prefixo}_{i}" if prefixo else str(i)
            resultado.update(junta(valor, prefixo=nova_chave))
    else:
        resultado[prefixo] = obj

    return resultado
    

def mqtt(pkt,local,topico = "nhsups",subtopico = "evento"):
    # Defina as variaveis do mqtt aqui
    global mqttcli
    global mqtt_connected

    if (mqttcli == None):
        try:
            mqttcli = mqttclient.Client(local)
        except:
            mqttcli = mqttclient.Client(mqttclient.CallbackAPIVersion.VERSION2,local)
        slog("Cliente MQTT Inicializado")
        mqttcli.username_pw_set(config.mqtt_user,config.mqtt_pass)
    else:
        slog("Cliente MQTT ja inicializado")
    if (mqtt_connected == False):
        try:
            mqttcli.connect(config.mqtt_host,config.mqtt_port)
            slog("Conectando cliente MQTT")
            mqttcli.loop_start()
            slog("Cliente MQTT Conectado")
        except Exception as inst:
            slog("Ocorreu uma excecao ao conectar o cliente MQTT: %s" % inst)
    else:
        slog("Cliente MQTT ja conectado")
    slog("Disparando mqtt")
    mqttcli.publish(topico + "/" + subtopico,json.dumps(junta(pkt)),qos=config.mqtt_qos)

def bd(pkt):
    # Saida para banco de dados
    # Este é um exemplo de como voce pode salvar os dados em um banco de dados sqlite3
    # Aqui voce podera criar suas proprias definicoes no banco e alimentar como achar prudente
    bd = sqlite3.connect("/run/nhs/nhs.db")
    cursor = bd.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS nobreak (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, datahora TEXT, pkt TEXT)")
    cursor.execute("INSERT INTO nobreak (nome,datahora,pkt) VALUES (?,?,?)",(pkt["nome"],pkt["datahora"],json.dumps(pkt)))
    bd.commit()
    bd.close()

# Função para criar e configurar uma porta serial virtual
def create_virtual_serial():
    master_fd, slave_fd = pty.openpty()  # Cria um par master/slave
    slave_name = os.ttyname(slave_fd)  # Nome da porta serial virtual (como /dev/pts/1)

    # Configurar a porta virtual
    attrs = termios.tcgetattr(slave_fd)
    attrs[0] = 0  # iflag: Desativar processamento especial de entrada
    attrs[1] = 0  # oflag: Desativar processamento especial de saída
    attrs[2] = termios.CS8 | termios.CREAD | termios.CLOCAL  # cflag: 8N1
    attrs[3] = 0  # lflag: Modo raw
    attrs[4] = termios.B2400  # ispeed: Baud rate de entrada
    attrs[5] = termios.B2400  # ospeed: Baud rate de saída
    termios.tcsetattr(slave_fd, termios.TCSANOW, attrs)

    return master_fd, slave_fd, slave_name    