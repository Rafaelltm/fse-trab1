# fse-trab1
#### Aluno: Rafael Leão Teixeira de Magalhães
#### Matrícula: 190019158

# Como rodar?

- Coloque os conteúdos da pasta `central/` na placa que servirá como servidor central.  
- Coloque os conteúdos da pasta `distrib/` nas placas que servirão como servidores distribuídos.
- Nos servidores distribuidos, execute `pip install -r requirements.txt` para instalar as dependências.
- No servidor central, execute `python3 central.py <host> <port>` substituindo `<host>` e `<port>` pelo ip e porta da placa, respectivamente.
- Nos servidores distribuídos, execute `python3 distributed.py <config.json>` substituindo `<config.json>` pelo seu arquivo com a configuração da placa(sala2.json, sala3.json, sala4.json).

# Apresentação
https://user-images.githubusercontent.com/54643266/208867001-df43d278-0c3f-407c-9afe-6f5ceff09159.mp4

link para a apresentação: https://youtu.be/kjNsTHMUnlc

