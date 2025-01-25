#!/usr/bin/env python3
import sys
import json
import time
import pprint
import os
import re

def copiar_a_partir_do_elemento(arr, num):
    # Encontra o índice do número fornecido
    try:
        index = arr.index(num)
        # Retorna o subarray a partir do próximo elemento após o índice
        return arr[index+1:]
    except ValueError:
        # Caso o número não seja encontrado no array
        return "Número não encontrado no array."

def gerar_mib(array_dados, oid_base, nome_mib="NHS-SNMP-MIB", caminho_saida="nhs-snmp-mib.txt"):
    basemib = oid_base.split('.')[-2]  # Extrai 9999 de .1.3.6.1.4.1.9999.1

    nome_mib_sanitizado = re.sub(r'[^a-zA-Z0-9]','',nome_mib).lower()

    cabecalho = f"""\
{nome_mib.upper()} DEFINITIONS ::= BEGIN

IMPORTS
    OBJECT-GROUP FROM SNMPv2-CONF
    MODULE-IDENTITY, OBJECT-TYPE, Integer32, enterprises FROM SNMPv2-SMI
    DisplayString FROM SNMPv2-TC;

{nome_mib_sanitizado} MODULE-IDENTITY
    LAST-UPDATED "{time.strftime("%Y%m%d%H%MZ", time.gmtime())}"
    ORGANIZATION "Gerado Automaticamente"
    CONTACT-INFO "lucas@lucas.inf.br"
    DESCRIPTION "NHS UPS SNMP"
    REVISION "{time.strftime("%Y%m%d%H%MZ", time.gmtime())}"
    DESCRIPTION
        "This is a dynamically generated MIB."
    ::= {{ enterprises {basemib} }}

{nome_mib_sanitizado}Objects OBJECT IDENTIFIER ::= {{ {nome_mib_sanitizado} 1 }}

"""

    objetos = []
    grupo = []
    posicao = 1

    for linha in array_dados:
        oid, tipo, valor, nome = linha
        parte_relativa = oid.replace(oid_base + ".", "").replace('.', ' ')

        # Sanitiza o nome do objeto
        nome_sanitizado = re.sub(r'[^a-zA-Z0-9]','', nome)
        nomegrupo = f"{nome_sanitizado}{posicao}".lower()

        if tipo == "INTEGER":
            tipo_snmp = "Integer32"
        elif tipo == "STRING":
            tipo_snmp = "DisplayString"
        else:
            raise ValueError(f"Tipo desconhecido: {tipo}")

        descricao = f"""
{nomegrupo} OBJECT-TYPE
    SYNTAX      {tipo_snmp}
    MAX-ACCESS  read-only
    STATUS      current
    DESCRIPTION
        "OID dynamically generated for {nome}."
    ::= {{ {nome_mib_sanitizado}Objects {parte_relativa} }}
"""
        objetos.append(descricao)
        grupo.append(nomegrupo)
        posicao += 1

    # Adiciona grupo de conformidade
    conformance = f"""
{nome_mib_sanitizado}Conformance OBJECT IDENTIFIER ::= {{ {nome_mib_sanitizado} 2 }}

{nome_mib_sanitizado}Group OBJECT-GROUP
    OBJECTS {{ {', '.join(grupo)} }}
    STATUS  current
    DESCRIPTION
        "Grupo de conformidade para todos os objetos da MIB."
    ::= {{ {nome_mib_sanitizado}Conformance 1 }}
"""

    conteudo = cabecalho + "".join(objetos) + conformance + "\nEND\n"

    with open(caminho_saida, "w") as arquivo:
        arquivo.write(conteudo)

    print(f"MIB gerada com sucesso em '{caminho_saida}'.")

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def json_to_array(data, base_oid, sequence_start=1):
    result = []
    sequence = sequence_start

    def process_element(key, value, parent_oid, seq=1):
        oid = f"{parent_oid}.{seq}"
        intseq = 1
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                process_element(sub_key, sub_value, oid, intseq)
                intseq += 1
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                process_element(f"{key}_{idx}", item, oid, intseq)
                intseq += 1
        else:
            if is_float(value):
                value_type = "INTEGER"
                value = round(float(value))
            else:
                value_type = "STRING"
                value = str(value)
            result.append([oid, value_type, value, key])
        seq += 1

    for key, value in data.items():
        process_element(key, value, base_oid, sequence)
        sequence += 1

    return result

arq = open("/tmp/snmp-log.txt",'a')

if len(sys.argv) < 2:
    print("NONE")
    arq.write(time.strftime("%d/%m/%Y %H:%M:%S") + " -- Tamanho Errado de Argumentos -- " +  " ".join(sys.argv) + "\r\n")
else:
    json_file_path = "/run/nhs/nhs.json"
    basemib = 9999
    oid_base = f".1.3.6.1.4.1.{basemib}.1"
    operation = sys.argv[1]
    oid = sys.argv[2] if len(sys.argv) > 2 else ""
    js = None
    if (os.path.exists(json_file_path)):
        jsarq = open(json_file_path,'r')
        if (jsarq):
            js = json.load(jsarq)
            jsarq.close()

            valores = json_to_array(js,oid_base)
            if (operation == "imprime"):
                for v in valores:
                    print(v)
            elif (operation == "arquivomib"):
                gerar_mib(valores,oid_base)
            else:
                for v in valores:
                    if (v[0] == oid):
                        print("%s\r\n%s\r\n%s" % (v[0],v[1],v[2]))
        else:
            print("%s\r\n%s\r\n%s" % (oid, "STRING", "Aquivo NHS JSON não foi aberto"))
            arq.write(time.strftime("%d/%m/%Y %H:%M:%S") + " -- " +  " ".join(sys.argv) + " -- " + "Aquivo NHS JSON não foi aberto" + "\r\n")
    else:
        print("%s\r\n%s\r\n%s" % (oid, "STRING", "Arquivo NHS JSON não encontrado"))
        arq.write(time.strftime("%d/%m/%Y %H:%M:%S") + " -- " +  " ".join(sys.argv) + " -- " + "Arquivo NHS JSON não encontrado" + "\r\n")
arq.close()
