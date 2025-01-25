# NHS-SENOIDAL
Monitoramento dos nobreaks da linha SENOIDAL da NHS.

Esse projeto visa auxiliar quem tiver um nobreak NHS da linha SENOIDAL a monitorar seus equipamentos em uma forma mais dinâmica, moderna e flexível.

## Motivação
O último projeto oficial da NHS para monitoria dos seus equipamentos para ambientes *NIX foi o NHSControl 3.0, sendo que o código-fonte desse projeto é totalmente proprietário da empresa, e foi lançado em 2012. Além do software ser extremamente limitado em termos de configurações, notificações e flexibilidade (em diversos sentidos), de lá pra cá houveram muitas mudanças, principalmente no código / estrutura da GLIB, sendo necessário por vezes ter que utilizar vários artifícios para que o software funcione a contento. Por este motivo, decidi, através de muita engenharia reversa e alguma ajuda do amigo @clyra do projeto nhs2mqtt (https://github.com/clyra/nhs2mqtt) criar algo funcional em python que pode ajudar muitos administradores de sistema a ter uma maior flexibilidade e principalmente modularizar e monitorar de forma mais simples e funcional seus equipamentos baseados no protocolo NHS 3.0.

OBSERVAÇÃO IMPORTANTE: Esse projeto está escrito, no momento, para ambientes *NIX like. Apesar de ser possível executá-lo em ambiente WINDOWS, existem muitas mudanças necessárias no código para a correta integração. O seu uso nesse sistema operacional é desencorajado, porém, sinta-se livre para tentar utilizar o mesmo neste sistema.

### Instalação
  - Instale as dependências (em se falando de ambiente debian-like)
    - python3-paho-mqtt
    - bibliotecas do seu banco de dados (se for utilizar)
    - python3-serial
  - Faça o download dos arquivos nhs.py, funcoes.py e config.py
  - Coloque no diretório de sua preferência
  - Edite o arquivo de configurações config.py com os dados relevantes
  - Verifique as permissões do arquivo /var/log/nhs.log
  - Configure o arquivo de inicialização automática (existe um exemplo para o systemd nesse repositório)

### Funcionalidades
1) Integração com o NUT.
   
   O nut (https://github.com/networkupstools/nut) é um projeto já bastante robusto e confiável para monitoramento e integração de sistemas de monitoramento de unidades UPS (mais comumente conhecido como "NOBREAK"). Com este script e o uso do driver DUMMY do NUT, é possível monitorar de forma bastante precisa seu equipamento NHS, tendo uma gama enorme de tipos de alerta e de automações as quais o NHS CONTROL não propicia.

  Por falar em NUT, eu escrevi um driver que está integrado diretamente às novas versões do NUT chamado nhs_ser.c. Caso você prefira instalar o NUT puro, somente com o driver NHS, isso também é possível apenas compilando as últimas versões do software. 
  
   Para que seu sistema funcione integrado ao NUT, será preciso:
   - Instalar o NUT
     Instale e configure o NUT conforme sua necessidade. A documentação oficial do NUT pode ate ajudar bastante nesta etapa;

   - Configurar corretamente o driver DUMMY
     -- arquivo ups.conf
       ```
       [meunobreak]
        driver = dummy-ups
        port = /run/nhs/nut.seq
        desc = Meu nobreak NHS
       ```

2) Integração MQTT
   
   Envie as informações via MQTT para seu broker favorito, para tratar as mesmas da melhor forma, inclusive possibilitando seu uso no GRAFANA. Os dados são enviados em formato JSON para melhor tratamento e compatibilidade.

3) Integração com Banco de dados
   
   Existe um código embrionário dentro do arquivo de funções para a inserção das informações de monitoramento no seu banco de dados preferido

4) Arquivo JSON

   Este script possibilia o salvamento das informações obtidas pelo seu equipamento NHS num arquivo json para que você possa implementar você mesmo seus recursos de monitoramento personalizados, se assim preferir. O arquivo estará localizado no diretório /run/nhs/nhs.json
   
5) Integração com SNMP
   
   Através deste software é possivel, através de uma MIB própria, monitorar alguns aspectos do seu nobreak NHS. Este software não envia traps snmp (está no nosso TODO), mas ainda assim é possível obter várias informações do equipamento.
   IMPORTANTE: as informações obtidas por este script dependem de você habilitar corretamente a geração do arquivo JSON para a conversão dos dados entre os formatos. Lembre-se de HABILITAR a geração de arquivos JSON no script principal para que esta funcionalidade seja habilitada a contento, caso contrário você não conseguirá obter informações do equipamento.
   
  - Configurar seu snmpd.conf (se estiver usando o snmpd do net-snmp)
    -- Abra o arquivo snmpd.conf, ou, se estiver usando distribuições mais modernas do debian, no diretório snmpd.conf.d, crie o arquivo nhs.conf
    -- Cole o seguinte conteúdo no arquivo:
       pass .1.3.9951.1.1 /etc/snmp/nhs-snmp.py
    -- Copie o arquivo nhs-snmp.py para o diretório indicado acima (no nosso exemplo, /etc/snmp)
    -- Reestarte o serviço
    -- Para verificar o funcionamento, tente executar o seguinte comando:
       snmpget -v 2c -c <comunidade> <seu servidor snmp> .1.3.6.1.4.1.9951.1
    -- Se você executar este script em linha de comando, passando o parâmetro geramib para o mesmo, será gerado um arquivo .mib chamado nhs-snmp-mib.txt no diretório atual. O mesmo pode ser utilizado em sistemas como o DUDE para melhor monitoria do seu equipamento

### TO-DO
- Correções diversas no código.

   
     
