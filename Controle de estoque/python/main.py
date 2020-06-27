#Importações Necessárias
from flask import Flask, request, render_template, redirect
from unidecode import unidecode
import gspread

#Conexão com a Planilha
conexao = gspread.service_account()
planilha = conexao.open("Nature Saboaria").sheet1

#Aplicação:
#A variável root_path você deve modificar com o caminho completo da pasta python no seu sistema, serve para o Flask achar a pasta templates corretamente ^^
app = Flask("Estoque-SIM-SA", template_folder="Controle de estoque/python/templates")
@app.route("/")
def main():
    #Isso aqui é era só pra mostrar o poder do Jinja2, pode remover se quiser
    #Obtendo a planilha completa sem os valores "Nome", "Quantidade" e etc
    planilha_completa = []
    for produto in planilha.get_all_values():
        if produto[0] == "Nome":
            continue
        planilha_completa.append(produto)

    #Gerando um hmtl com todos os produtos da planilha com o Jinja2, dê uma olhada no arquivo listarProdutos e base na pasta templates
    return render_template("remover_quantidade.html")

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

# Rotas para Inserir Produto
@app.route('/inserir')
def inserir():
    return render_template('inserir_produto.html')

@app.route('/respinserir')
def respinserir():
    return render_template('resposta_inserir_produto.html')

# Rota de Captura das Informações para adicionar na planilha
@app.route('/add', methods=['POST'])
def add():
    arr = [
        'produto', 
        'quantidade', 
        'tiposabonete',
        'marca',
        'tipo',
        'preco',
        'peso',
        'estado',
        'partecorpo'
    ]

    # Laço For para adicionar os dados dentro da minha lista row.
    row = []
    for n in arr:
        item = request.form.get(n)
        row.append(item)
    
    # Laço For para verificar se os dados que o usuários inseriu é compatível com alguma linha dentro da planilha;
    # Caso seja compatível, ele apenas irá alterar a quantidade adicionada.
    same = contsame = 0
    for pos, linha in enumerate(planilha.get_all_values()):
        for cell in range(0, 9):
            if linha[cell] == linha[1]:
                continue
            elif unidecode(linha[cell]).lower().strip() == unidecode(row[cell]).lower().strip():
                same += 1
        
        # Caso seja igual a 8, significa dizer que as 8 colunas de uma linha eram iguais aos dados que o usuário inseriu;
        # Então quer dizer que a linha já existe na planilha, portanto, só a quantidade será alterada.
        if same == 8:
            newquant = int(linha[1]) + int(row[1])
            planilha.update_cell(pos + 1, 2, newquant)
            contsame += 1
            break
        else:
            same = 0
    if contsame == 0:
        index = len(planilha.get_all_values()) + 1
        planilha.insert_row(row, index)
    
    return redirect('/respinserir')

app.run(debug=True, use_reloader=True)
