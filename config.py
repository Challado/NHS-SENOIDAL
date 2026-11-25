# Defina as variaveis de configuracao aqui

# Ativa a geracao do arquivo para o driver DUMMY do NUT
ativaNUT = False
# Ativa o envio de MQTT
ativaMQTT = False
# Ativa a gravacao em Banco de Dados
ativaBD = False
# Ativa a gravacao do arquivo JSON
ativaJSON = False
# Nome do seu Nobreak
nome = "MEUNOBREAK"
# Descricao do modelo do seu Nobreak
descricaomodelo = "NHS LINHA SENOIDAL"
# Qual a potencia nominal do seu nobreak
potencia_nominal = 3000
# Qual o fator de Conversao do nobreak
fator_conversao = 0.9
# Numero de baterias. O nobreak ja tem essa informacao la dentro dele, mas voce pode ter colocado um modulo de baterias externo...
# Se caso o valor for None entao ele ira manter os dados da bateria
numero_baterias = None
# Capacidade da bateria em Ah. Voce precisa saber a capacidade da bateria para calcular a autonomia
ah = 9
# Tensao da Bateria em Volts
tensao_bateria = 12
# Caminho do dispositivo
device = "/dev/ttyACM0"
# tempo sem leitura para considerar que nao temos comunicacao com o nobreak
timeout = 10
# Entre quantas leituras enviar os pacotes de inicializacao de hardware para leitura das informacoes caso nao tenham vindo
pacotesenvio = 100
# Caminho do arquivo de log
arquivolog = "/var/log/nhs.log"
# Arquivo que sera monitorado pelo NUT
arquivonut = "/run/nhs/nut.seq"
# Arquivo de saida JSON
arquivojson = "/run/nhs/nhs.json"
# Host MQTT
mqtt_host = "meuhost"
# Porta MQTT
mqtt_port = 1883
# Usuario MQTT
mqtt_user = None
# Senha MQTT
mqtt_pass = None
# QOS MQTT
mqtt_qos = 0
# Intevalo de envio de pacotes do MQTT
# O NHS faz muitas leituras de pacotes nas interfaces. Por isso, fica interessante ignorar alguns pacotes e enviar via MQTT apenas X em X vezes
mqtt_interval = 4
# Modo de leitura do pacote de Hardware: 0 - Leitura normal, 1 (padrão) - Leitura Invertida
hw_pktread = True
# Modo de leitura do pacote de Dados: 0 - Leitura normal, 1 (padrão) - Leitura Invertida
data_pktread = True
# Modo de envio de pacote de Inicialização: 0 (padrão) - Conforme sistema, 1 - Envia inicialização legada, 2 - Envia inicialização padrão, 3 - Envia inicialização extendida
modo_envio_inicializacao = 0
# Baud rate da porta serial
baudrate = 2400
# Paridade da porta serial (N - None, E - Even, O - Odd)
parity = 'N'
# Stop bits da porta serial (1, 1.5, 2)
stopbits = 1
# Controle de fluxo da porta serial (True - Habilitado, False - Desabilitado)
rtscts = False
# Habilita o modo exclusivo da porta serial (True - Habilitado, False - Desabilitado)
exclusive = True
# Tempo de espera entre leituras da porta serial
temposleepread = 1
