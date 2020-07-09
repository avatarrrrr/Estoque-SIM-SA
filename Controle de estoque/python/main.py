#Importações Necessárias
from flask import Flask, request, render_template
from unidecode import unidecode
import gspread
import datetime
import os

#Conexão com a Planilha
conexao = gspread.service_account()
planilha = conexao.open("Nature Saboaria").sheet1
transacoes = conexao.open("transacoes").sheet1

#Aplicação:
#A variável root_path você deve modificar com o caminho completo da pasta python no seu sistema, serve para o Flask achar a pasta templates corretamente ^^
app = Flask("Estoque-SIM-SA", root_path="/home/lucas/Desktop/estoque-sim-sa/Controle de estoque/python")
app.config['UPLOAD_FOLDER'] = '/home/lucas/Desktop/estoque-sim-sa/Controle de estoque/python/static'
#app = Flask("Estoque-SIM-SA",  root_path="/home/rafael/Área de Trabalho/Controle de estoque/estoque-sim-sa/Controle de estoque/python")
#app = Flask("Estoque-SIM-SA",  root_path="H:\\Users\\agata\\Documents\\projeto trainee\\estoque-sim-sa\\Controle de estoque\\python")
#app = Flask("Estoque-SIM-SA",  root_path="C:\\Users\\tanko\\estoque-sim-sa\\Controle de estoque\\python")
#app.config["UPLOAD_FOLDER"] = "C:\\Users\\tanko\\estoque-sim-sa\\Controle de estoque\\python\\static"

@app.route("/")
def main():
    #Pegando os toda a planilha de transações
    tudo = transacoes.get_all_values()

    #Criando uma lista com todas as transações do DIA
    dia = []
    for transacao in tudo:
        if int(transacao[5]) == datetime.datetime.today().day:
            dia.append([transacao[0], transacao[1], transacao[2]])
    #Juntando transacoes repetidas em uma só, somando a quantidade e o preço total
    dia = sorted(dia, key=lambda transacao: int(transacao[1]), reverse=True)
    for transacao in dia:
        for transacao2 in dia:
            if transacao[0] == transacao2[0] and transacao is not transacao2:
                transacao[1] = int(transacao[1]) + int(transacao2[1])
                transacao[2] = round(float(transacao[2]) + float(transacao2[2]), 1)
                dia.remove(transacao2)
    for transacao in dia:
        for transacao2 in dia:
            if transacao[0] == transacao2[0] and transacao is not transacao2:
                transacao[1] = int(transacao[1]) + int(transacao2[1])
                transacao[2] = round(float(transacao[2]) + float(transacao2[2]), 1)
                dia.remove(transacao2)
    #Ordenando a lista pelo produto de maior quantidade:
    diaQuantidade = sorted(dia, key=lambda transacao: int(transacao[1]), reverse=True)

    #Criando uma lista com todas as transações do MÊS
    mes = []
    for transacao in tudo:
        if int(transacao[6]) == datetime.datetime.today().month:
            mes.append([transacao[0], transacao[1], transacao[2]])
    #Juntando transacoes repetidas em uma só, somando a quantidade e o preço total
    mes = sorted(mes, key=lambda transacao: int(transacao[1]), reverse=True)
    for transacao in mes:
        for transacao2 in mes:
            if transacao[0] == transacao2[0] and transacao is not transacao2:
                transacao[1] = int(transacao[1]) + int(transacao2[1])
                transacao[2] = round(float(transacao[2]) + float(transacao2[2]), 1)
                mes.remove(transacao2)
    for transacao in mes:
        for transacao2 in mes:
            if transacao[0] == transacao2[0] and transacao is not transacao2:
                transacao[1] = int(transacao[1]) + int(transacao2[1])
                transacao[2] = round(float(transacao[2]) + float(transacao2[2]), 1)
                mes.remove(transacao2)
    #Ordenando a lista pelo produto de maior quantidade:
    mesQuantidade = sorted(mes, key=lambda transacao: int(transacao[1]), reverse=True)

    #Criando uma lista com todas as transações do ANO
    ano = []
    for transacao in tudo:
        if int(transacao[7]) == datetime.datetime.today().year:
            ano.append([transacao[0], transacao[1], transacao[2]])
    #Juntando transacoes repetidas em uma só, somando a quantidade e o preço total
    ano = sorted(ano, key=lambda transacao: int(transacao[1]), reverse=True)
    for transacao in ano:
        for transacao2 in ano:
            if transacao[0] == transacao2[0] and transacao is not transacao2:
                transacao[1] = int(transacao[1]) + int(transacao2[1])
                transacao[2] = round(float(transacao[2]) + float(transacao2[2]), 1)
                ano.remove(transacao2)
    for transacao in ano:
        for transacao2 in ano:
            if transacao[0] == transacao2[0] and transacao is not transacao2:
                transacao[1] = int(transacao[1]) + int(transacao2[1])
                transacao[2] = round(float(transacao[2]) + float(transacao2[2]), 1)
                ano.remove(transacao2)
    #Ordenando a lista pelo produto de maior quantidade:
    anoQuantidade = sorted(ano, key=lambda transacao: int(transacao[1]), reverse=True)

    return render_template("home.html", diaQuantidade = diaQuantidade, mesQuantidade = mesQuantidade, anoQuantidade = anoQuantidade)

#Roteamento para remover um produto
@app.route("/remover", methods=["POST"])
def deleteProduto():
    #Pesquisa o nome enviado na planilha
    remover = planilha.find(request.form.get("delete"))

    #Faz a remoção do produto e avalia se a exclusão foi bem sucedida ou não
    if planilha.delete_rows(remover.row):
        return u"""
                <script>
                    alert("Feito!")
                    window.location = "/estoque"
                </script>
            """
    else:
        return u"""
                <script>
                    alert("Houve um Erro ao deletar o produto!")
                    window.location = "/estoque"
                </script>
            """

#Roteamento para remover uma transação
@app.route("/deleteTransacao", methods=["POST"])
def deleteTransacao():
    #Pesquisa o nome enviado na planilha
    remover = transacoes.find(request.form.get("transacao"))

    #Faz a remoção da transação e avalia se a exclusão foi bem sucedida ou não
    if transacoes.delete_rows(remover.row):
        return u"""
                <script>
                    alert("Feito!")
                    window.location = "/transacoes"
                </script>
            """
    else:
        return u"""
                <script>
                    alert("Houve um Erro ao deletar a transacao!")
                    window.location = "/transacoes"
                </script>
            """


# Captura qual é o item que irá ser retirada uma determinada quantidade, e exibe o popup
@app.route('/popup', methods=['POST'])
def popup():
    item = planilha.find(request.form.get('item'))
    img = planilha.cell(item.row, 6)
    return render_template('popup.html',
    planilha_completa = planilha.get_all_values(),
    nome = item.value,
    imagem = img.value,
    quantidade = planilha.cell(item.row, 2).value,
    preço = planilha.cell(item.row, 3).value
    )

# Roteamento para remover uma quantidade de um produto, caso a quantidade do produto fique abaixo do limite, ele dispara um alerta
@app.route("/venda", methods=["POST"])
def venda():
    # Procura o Produto
    rm = planilha.find(request.form.get('nome'))

    if request.form.get('quantidade') != '':

        dateToday = datetime.datetime.today()
        #Registra uma transação na planilha transações com o valor do produto, a quantidade, o preço, data e o horário
        transacoes.append_row([request.form.get("nome"), request.form.get("quantidade"), str(float(request.form.get("preço")) * int(request.form.get("quantidade"))), str(dateToday.day) + "/" + str(dateToday.month) + "/" + str(dateToday.year), str(dateToday.hour) + ":" + str(dateToday.minute) + ":" + str(dateToday.second), str(dateToday.day), str(dateToday.month), str(dateToday.year)])

        #Atualiza a célula com o valor da subtração do valor que já tem na célula com o valor que o usuário quer retirar
        planilha.update_cell(rm.row, 2, int(planilha.cell(rm.row, 2).value) - int(request.form.get("quantidade")))

        # Verifica se a quantidade atual está abaixo do valor limite definido pelo usuário (por enquanto o limite é fixo kkkkk)
        if int(planilha.cell(rm.row, 2).value) < 5:
            return render_template("respostaEstoque.html", retorno = "Operação concluida, o total da venda foi de R$: " + str(round(int(request.form.get("quantidade")) * float(request.form.get("preço")), 1)) + "! Atenção! O produto está abaixo do limite especificado")

        else:
            return render_template("respostaEstoque.html", retorno = "Operação concluida, o total da venda foi de R$: " + str(round(int(request.form.get("quantidade")) * float(request.form.get("preço")), 1)) + "!")

# Rotas para editar dados da planilha
@app.route('/popupEdition', methods=['POST'])
def popupEdition():
    item = planilha.find(request.form.get('edit'))
    volume = planilha.cell(item.row, 4).value

    # Utilizando o laço for para capturar apenas o valor do volume
    valor = ''
    for num in volume:
        if num.isnumeric() == True:
            valor += num

    return render_template('editar.html',
    planilha_completa = planilha.get_all_values(),
    nome = item.value,
    quantidade = planilha.cell(item.row, 2).value,
    preço = planilha.cell(item.row, 3).value,
    volume = volume,
    valor = valor,
    corpo = planilha.cell(item.row, 5).value,
    imagem = planilha.cell(item.row, 6).value
    )

# Nessa rota ocorrerá a edição dos itens
@app.route('/editar', methods=['POST'])
def editar():
    conteudo = [
        'nome',
        'quantidade',
        'preço',
        'valor',
        'área do corpo',
        'imagem'
    ]

    # Capturando a linha certa pelo nome do item
    linha = planilha.find(request.form.get('edition')).row

    # Atualizando a planilha com os novos valores
    for pos, item in enumerate(conteudo):
        if pos == 3:
            volume = request.form.get(item) + request.form.get('volume')
            planilha.update_cell(linha, pos + 1, volume)
        elif pos == 5:
            if request.files['imagem'].filename != '':
                request.files['imagem'].save(os.path.join(app.config['UPLOAD_FOLDER'], request.files['imagem'].filename))
                planilha.update_cell(linha, pos + 1, request.files['imagem'].filename)
            else:
                pass
        else:
            planilha.update_cell(linha, pos + 1, request.form.get(item))

    return render_template('respostaEstoque.html', retorno = 'Item salvo com sucesso!')

# Rotas para Inserir Produto
@app.route('/inserir')
def inserir():
    return render_template("incluirProduto.html")

# Rota de Captura das Informações para adicionar na planilha
@app.route('/recebendo_dados', methods=['POST'])
def add():
    arr = [
        'nome', 
        'quantidade', 
        'preço',
        'valor',
        'área do corpo',
        'imagem'
    ]
    # Laço For para adicionar os dados dentro da minha lista row.
    row = []
    for pos, n in enumerate(arr):
        item = request.form.get(n)
        if pos == 3:
            item = request.form.get(n) + request.form.get('volume')
        if pos == 5:
            if request.files["imagem"].filename != "":
                request.files["imagem"].save(os.path.join(app.config["UPLOAD_FOLDER"], request.files["imagem"].filename))
                item = request.files["imagem"].filename
            else:
                pass
        row.append(item)
    
    # Laço For para verificar se os dados que o usuários inseriu é compatível com alguma linha dentro da planilha;
    # Caso seja compatível, ele apenas irá alterar a quantidade adicionada.
    same = contsame = 0
    for pos, linha in enumerate(planilha.get_all_values()):
        for cell in range(0, 6):
            if linha[cell] == linha[1] or linha[cell] == linha[2] or linha[cell] == linha[5]:
                continue
            elif unidecode(linha[cell]).lower().strip() == unidecode(row[cell]).lower().strip():
                same += 1
        
        # Caso seja igual a 4, significa dizer que as 4 colunas de uma linha eram iguais aos dados que o usuário inseriu;
        # Então quer dizer que a linha já existe na planilha, portanto, o produto não será adicionado.
        if same == 3:
            contsame += 1
            return u"""
                <script>
                    alert("O produto já existe no banco de dados!")
                    window.location = "/inserir"
                </script>
            """
        else:
            same = 0
    
    # contsame == 0 significa que não há nenhum item na planilha igual ao inserido pelo usuário, logo, será um novo item
    if contsame == 0:
        index = len(planilha.get_all_values()) + 1
        planilha.insert_row(row, index)
        return u"""
                <script>
                    alert("Novo item adicionado com sucesso!")
                    window.location = "/inserir"
                </script>
            """

@app.route('/estoque')
def estoque():
    return render_template('estoque.html', planilha_completa = planilha.get_all_values())

@app.route('/transacoes')
def transacoess():
    return render_template("transacoes.html", transacoes = reversed(transacoes.get_all_values()))

@app.route("/pesquisa", methods=['POST'])
def pesquisa():
    try:
        pesq = planilha.find(request.form.get("produto"))
    except:
        return u"""
                    <script>
                        alert("Não achamos nada, tente procurar novamente!")
                        window.location = "/estoque"
                    </script>
            """  
    else:
        if pesq.value == '':
            return u"""
                    <script>
                        alert("Você não colou nada para pesquisar, tá doido é?")
                        window.location = "/estoque"
                    </script>
            """
        else:
            return render_template("estoque.html", planilha_completa = [pesq])

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")
        

app.run(debug=True, use_reloader=True)