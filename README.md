# Estoque-SIM-SA

Bem vindo ao projeto final do grupo 4 do processo trainee da TITAN! Abaixo algums passos para você conseguir rodar o projeto na sua máquina

## Bibliotecas e arquivos necessários
Primeiramente vamos assumir que você já tem o MySQL Server, o Python e o gerenciador de pacotes pip lindamente instalados na sua máquina, vamos lá:

* Instale o flask com _pip install Flask_

* Instale a extensão para mysql do flask com _pip install flask-mysql_

(_Sugerimos fortemente que faça essas instalações em um abiente isolado com o venv_)

Instale o banco de dados que está dentro da pasta static no servidor mysql da sua máquina (você pode fazer com o workbench, ou com o terminal mesmo)

Altere o seu nome de usuário e a senha para acesso ao mysql server no ínicio do arquivo _main.py_ e altere o path da pasta img (está dentro da pasta static) para conforme a localização na sua máquina

Se você fez tudo certinho, consguirá rodar o projeto ao executar o arquivo _main.py_ :D