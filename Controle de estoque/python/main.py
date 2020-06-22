#Importações Necessárias
from flask import Flask, request, render_template, Blueprint
import gspread
from Modules.delProdutos import Remover_Produto
from Modules.retirarQuantProdutos import Remover_Item

#Conexão com a Planilha
conexao = gspread.service_account()
planilha = conexao.open("Nature Saboaria").sheet1

#Aplicação:
app = Flask("Estoque-SIM-SA", root_path="c:\\Users\\tanko\\estoque-sim-sa\\Controle de estoque\\python\\")
@app.route("/")
def main():
    #Obtendo a planilha completa sem os valores "Nome", "Quantidade" e etc
    planilha_completa = []
    for produto in planilha.get_all_values():
        if produto[0] == "Nome":
            continue
        planilha_completa.append(produto)
    #Gerando um hmtl com todos os produtos da planilha com o Jinja2, dê uma olhada no arquivo listarProdutos e base na pasta templates
    return render_template("listarProdutos.html", planilha_completa = planilha_completa)

#Roteamento para remover um produto
@app.route("/remover")
def remove():
    if Remover_Produto(planilha, request.args.get("nome")) == "S":
        return "Feito!"
    elif Remover_Produto(planilha, request.args.get("nome")) == "P":
        return "Houve um erro na pesquisa do produto! Confira se digitou corretamente"
    else:
        return "Houve um Erro ao deletar o produto!"

#Roteamento para remover uma quantidade de um produto, caso a quantidade do produto fique abaixo do limite, ele dispara um alerta
@app.route("/remover_qtd")
def retirar():
    if Remover_Item(planilha, request.args.get("nome"), int(request.args.get("quantidade")), 5) == "S":
        return "Operação feita com sucesso!"
    elif Remover_Item(planilha, request.args.get("nome"), int(request.args.get("quantidade")), 5) == "L":
        return "Atenção! O produto está abaixo do limite especificado"  
    else:
        return "A quantidade que você quer retirar é maior que a quantidade disponível!Tente colocar um número menor!"

app.run(debug=True, use_reloader=True)