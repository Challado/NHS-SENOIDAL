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