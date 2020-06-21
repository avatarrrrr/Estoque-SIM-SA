#Importações Necessárias
from flask import Flask, request, render_template, Blueprint
import gspread
from Modules.delProdutos import Remover_Produto

#Conexão com a Planilha
conexao = gspread.service_account()
planilha = conexao.open("Nature Saboaria").sheet1

#Aplicação:
app = Flask("Estoque-SIM-SA", root_path="c:\\Users\\tanko\\estoque-sim-sa\\Controle de estoque\\python\\")
@app.route("/")
def main():
    return render_template("remover.html")

#Roteamento para remover um produto
@app.route("/remover")
def remove():
    if Remover_Produto(planilha, request.args.get("nome")):
        return "Feito!"
    else:
        return "Houve um erro!"

app.run(debug=True, use_reloader=True)