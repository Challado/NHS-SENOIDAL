#!/bin/bash
# NOTIFICA.SH - Script de notificação para o upsmon do NUT

# Verifique se os parâmetros esperados foram passados
if [ "$#" -lt 2 ]; then
  echo "Uso: $0 <NOME_UPS> <EVENTO>"
  exit 1
fi

NOME_UPS="$1"
EVENTO="$2"

# Defina o log de eventos
LOG_FILE="/var/log/nut-eventos.log"

# Função para enviar notificações (modifique conforme necessário)
enviar_notificacao() {
  MENSAGEM="$1"
  # Exemplo: Enviar para um e-mail ou integrar com outro sistema
  echo "$MENSAGEM" | mail -s "Evento no-break: $NOME_UPS" seuemail@example.com
}

# Registre o evento no log
DATA=$(date +"%Y-%m-%d %H:%M:%S")
echo "$DATA - UPS: $NOME_UPS - Evento: $EVENTO" >> "$LOG_FILE"

# Ações específicas com base no evento
case "$EVENTO" in
  "ONBATT")
    enviar_notificacao "Aviso: O no-break $NOME_UPS está operando com bateria. Verifique a situação da energia elétrica."
    ;;
  "ONLINE")
    enviar_notificacao "Informação: O no-break $NOME_UPS voltou a operar com energia elétrica normal."
    ;;
  "LOWBATT")
    enviar_notificacao "Alerta: O no-break $NOME_UPS está com bateria fraca. Ação imediata é necessária."
    ;;
  "SHUTDOWN")
    enviar_notificacao "Crítico: O sistema será desligado devido ao evento SHUTDOWN no no-break $NOME_UPS."
    ;;
  *)
    enviar_notificacao "Evento desconhecido: $EVENTO ocorrido no no-break $NOME_UPS."
    ;;
esac

exit 0
