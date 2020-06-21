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
    pass

#Roteamento para remover um produto
@app.route("/remover")
def remove():
    if Remover_Produto(planilha, request.args.get("nome")):
        return "Feito!"
    else:
        return "Houve um erro!"

@app.route("/remover_qtd")
def retirar():
    if Remover_Item(planilha, request.args.get("nome"), int(request.args.get("quantidade")), 5):
        return "Operação feita com sucesso!"
    else:
        return "Atenção! O produto está abaixo do limite especificado"

app.run(debug=True, use_reloader=True)