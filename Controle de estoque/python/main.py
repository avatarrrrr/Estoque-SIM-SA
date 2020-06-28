#Importações Necessárias
from flask import Flask, request, render_template, redirect
import gspread

#Conexão com a Planilha
conexao = gspread.service_account()
planilha = conexao.open("Nature Saboaria").sheet1

#Aplicação:
#A variável root_path você deve modificar com o caminho completo da pasta python no seu sistema, serve para o Flask achar a pasta templates corretamente ^^
app = Flask("Estoque-SIM-SA", root_path="c:\\Users\\tanko\\estoque-sim-sa\\Controle de estoque\\python\\")
@app.route("/")
def main():
    return render_template("incluirProduto.html")

#Roteamento para remover um produto
@app.route("/remover", methods=["POST"])
def remove():
    #Pesquisa o nome enviado na planilha
    remover = planilha.find(request.form.get("nome"))
    #Verifica se encontrou o produto
    if not remover:
        return render_template("reposta.html", retorno = "Houve um erro na pesquisa do produto! Confira se digitou corretamente.")
    #Faz a remoção do produto e avalia se a exclusão foi bem sucedida ou não
    if planilha.delete_rows(remover.row):
        return render_template("reposta.html", retorno = "Feito!")
    else:
        return render_template("reposta.html", retorno = "Houve um Erro ao deletar o produto!")

#Roteamento para remover uma quantidade de um produto, caso a quantidade do produto fique abaixo do limite, ele dispara um alerta
@app.route("/remover_qtd", methods=["POST"])
def retirar():
    #Procura o Produto
    rm = planilha.find(request.form.get("nome"))
    #Verifica se encontrou o produto
    if not rm:
        return render_template("reposta.html", retorno = "Houve um erro na pesquisa do produto! Confira se digitou corretamente.")
    #Verifica se a quantidade que vai ser retirada é maior que a quantidade disponível, se sim, retorna um erro
    if int(planilha.cell(rm.row, 2).value) < int(request.form.get("quantidade")):
        return render_template("reposta.html", retorno = "A quantidade que você quer retirar é maior que a quantidade disponível!Tente colocar um número menor!")
    #Atualiza a célula com o valor da subtração do valor que já tem na célula com o valor que o usuário quer retirar
    planilha.update_cell(rm.row, 2, int(planilha.cell(rm.row, 2).value) - int(request.form.get("quantidade")))
    #Verifica se a quantidade atual está abaixo do valor limite definido pelo usuário (por enquanto o limite é fixo kkkkk)
    if int(planilha.cell(rm.row, 2).value) < 5:
        return render_template("reposta.html", retorno = "Atenção! O produto está abaixo do limite especificado")
    else:
        return render_template("reposta.html", retorno = "Operação feita com sucesso!")

app.run(debug=True, use_reloader=True)