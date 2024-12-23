#!/bin/bash
# Exemplo de um arquivo para o upsmon.conf
# Coloque esse arquivo no NOTIFYCMD e veja o que sera passado que pode ser aproveitado
# Existem algumas variaveis de ambiente, por isso veja e cuide bem o que eh passado como parametro e o que eh passado como variavel de ambiente

declare -A key_value_array
declare -a key_order
index=1
for arg in "$@"; do
  key="arg$index"
  key_value_array[$key]="$arg"
  key_order+=("$key")
  ((index++))
done

# Caminho do arquivo de saída
output_file="/tmp/dados"

# Salva o array no arquivo na ordem correta
echo "Array de chave-valor:" > "$output_file"
for key in "${key_order[@]}"; do
  echo "$key: ${key_value_array[$key]}" >> "$output_file"
done
set >> /tmp/dados
