#Importações Necessárias
from flask import Flask, request
import gspread
from Modules.delProdutos import Remover_Produto

#Conexão com a Planilha
conexao = gspread.service_account()
planilha = conexao.open("Nature Saboaria").sheet1

#Aplicação:
app = Flask("Estoque-SIM-SA")
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

app.run(debug=True, use_reloader=True)