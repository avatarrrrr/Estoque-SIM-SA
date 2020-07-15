
from flask import Flask, request, render_template
from flaskext.mysql import MySQL
from unidecode import unidecode
import gspread
import datetime
import os
import base64

#Conexão com a Planilha
conexao = gspread.service_account()
planilha = conexao.open("Nature Saboaria").sheet1
transacoes = conexao.open("transacoes").sheet1

#Aplicação:
#A variável root_path você deve modificar com o caminho completo da pasta python no seu sistema, serve para o Flask achar a pasta templates corretamente ^^
#O app.config define a pasta padrão onde as imagens mandadas no form devem serem salvas!
#app = Flask("Estoque-SIM-SA", root_path="/home/lucas/Desktop/estoque-sim-sa/Controle de estoque/python")
#app.config['UPLOAD_FOLDER'] = '/home/lucas/Desktop/estoque-sim-sa/Controle de estoque/python/static'
#app = Flask("Estoque-SIM-SA", root_path="C:\\Users\\luqui\\OneDrive\\Área de Trabalho\\estoque-sim-sa\\Controle de estoque\\python")
#app.config['UPLOAD_FOLDER'] = 'C:\\Users\\luqui\\OneDrive\\Área de Trabalho\\estoque-sim-sa\\Controle de estoque\\python\\python'
#app = Flask("Estoque-SIM-SA",  root_path="/home/rafael/Área de Trabalho/Controle de estoque/estoque-sim-sa/Controle de estoque/python")
#app.config["UPLOAD_FOLDER"] = "/home/rafael/Área de Trabalho/Controle de estoque/estoque-sim-sa/Controle de estoque/static"
#app = Flask("Estoque-SIM-SA",  root_path="H:\\Users\\agata\\Documents\\projeto trainee\\estoque-sim-sa\\Controle de estoque\\python")
app = Flask("Estoque-SIM-SA",  root_path="C:\\Users\\tanko\\estoque-sim-sa\\Controle de estoque\\python")
#Configuração do banco de dados mysql, troque a senha conforme a senha do user root no seu mysql server
mysql = MySQL()
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = "estoquesimsa"
app.config["MYSQL_DATABASE_DB"] = "estoque"
app.config["MYSQL_DATABASE_Host"] = "localhost"
mysql.init_app(app)
#Variável principal onde devem serem feitas as operações
db = mysql.connect()
estoque = db.cursor()

@app.route("/")
def main():
    #Pegando os toda a planilha de transações
    tudo = transacoes.get_all_values()

    #Criando uma Dicionário com todas as transações do DIA e já juntando as que tiverem repetidas em uma só, somando as quantidades
    dia = {}
    for transacao in tudo:
        if int(transacao[5]) == datetime.datetime.today().day:
            try:
                dia[unidecode(transacao[0]).lower()] += int(transacao[1])
            except:
                dia[unidecode(transacao[0]).lower()] = int(transacao[1])
    #Ordenando o dicionário pelo produto de maior quantidade:
    dia = sorted(dia.items(), key=lambda transacao: transacao[1], reverse=True)
    if dia == []:
        dia.append(["Não houve nenhuma transação hoje", 1])

    #Criando uma Dicionário com todas as transações do MÊS e já juntando as que tiverem repetidas em uma só, somando as quantidades
    mes = {}
    for transacao in tudo:
        if int(transacao[6]) == datetime.datetime.today().month:
            try:
                mes[unidecode(transacao[0]).lower()] += int(transacao[1])
            except:
                mes[unidecode(transacao[0]).lower()] = int(transacao[1])
    #Ordenando o dicionário pelo produto de maior quantidade:
    mes = sorted(mes.items(), key=lambda transacao: transacao[1], reverse=True)
    if mes == []:
        mes.append(["Não houve nenhuma transação esse mês", 1])
    
    #Criando uma Dicionário com todas as transações do ANO e já juntando as que tiverem repetidas em uma só, somando as quantidades
    ano = {}
    for transacao in tudo:
        if int(transacao[7]) == datetime.datetime.today().year:
            try:
                ano[unidecode(transacao[0]).lower()] += int(transacao[1])
            except:
                ano[unidecode(transacao[0]).lower()] = int(transacao[1])
    #Ordenando o dicionário pelo produto de maior quantidade:
    ano = sorted(ano.items(), key=lambda transacao: transacao[1], reverse=True)
    if ano == []:
        ano.append(["Não houve nenhuma transação esse ano", 1])

    return render_template("home.html", diaQuantidade = dia, mesQuantidade = mes, anoQuantidade = ano)

#Roteamento para remover um produto
@app.route("/remover", methods=["POST"])
def deleteProduto():
    #Faz a deleção no banco de dados
    estoque.execute("DELETE FROM produtos WHERE nome='{}'".format(request.form.get("delete")))
    #Grava a alteração no banco de dados
    db.commit()
    #Retorna a mensagem de sucesso
    return u"""
                <script>
                    alert("Feito!")
                    window.location = "/estoque"
                </script>
            """

#Roteamento para remover uma transação
@app.route("/deleteTransacao", methods=["POST"])
def deleteTransacao():
    #Faz a remoção da transação e avalia se a exclusão foi bem sucedida ou não
    rm = transacoes.find(request.form.get("transacao"))
    if transacoes.delete_rows(rm.row):
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

# Rota de Captura das Informações para adicionar no banco de dados
@app.route('/recebendo_dados', methods=['POST'])
def add():
    #Procurando no banco de dados se já existe um produto com as mesma características
    estoque.execute("SELECT * FROM produtos WHERE nome='{}' AND peso='{}' AND finalidade='{}'".format(request.form.get("nome"), request.form.get("valor") + request.form.get("volume"), request.form.get("área do corpo")))
    #Aqui ele verifica se o comando acima retornou algo, se sim, quer dizer que já tem um produto com essas características, então ele faz um update na tabela
    if estoque.fetchone():
        estoque.execute("UPDATE produtos SET quantidade={} WHERE nome='{}'".format(int(request.form.get("quantidade")) + estoque.fetchone()[1], request.form.get("nome")))
        #Grava os dados da requisição
        db.commit()
        #Retorna mensagem
        return u""" 
                    <script>
                        alert("O item que você tentou adicionar já existe, então nós somamos a quantidade do que você tentou adicionar com o já existente :)")
                        window.location = "/inserir"
                    </script>
                """
    #Caso contrário, insere uma nova linha no banco de dados com os dados da requisição:
    else:
        #Salva a imagem na pasta static
        request.files["imagem"].save(os.path.join("C:\\Users\\tanko\\estoque-sim-sa\\Controle de estoque\\python\\static", request.files["imagem"].filename))
        #Faz o comando SQL
        estoque.execute("INSERT INTO produtos (nome, quantidade, valor, peso, finalidade, imagem) VALUES ('{}', {}, {}, '{}', '{}', '{}')".format(request.form.get("nome"), request.form.get("quantidade"), request.form.get("preço"), request.form.get("valor") + request.form.get("volume"), request.form.get("área do corpo"), request.files["imagem"].filename))
        #Grava as alterações no banco de dados
        db.commit()
        #Retorna mensagem
        return u""" 
                    <script>
                        alert("Novo item adicionado com sucesso!")
                        window.location = "/inserir"
                    </script>
                """

@app.route('/estoque')
def produtos():
    estoque.execute("SELECT * FROM produtos")
    data = estoque.fetchall()
    return render_template('estoque.html', planilha_completa = data)

@app.route('/transacoes')
def transacoess():
    return render_template("transacoes.html", transacoes = reversed(transacoes.get_all_values()))

@app.route("/pesquisa", methods=['POST'])
def pesquisa():
    pesq = []
    for produto in planilha.get_all_values():
        if unidecode(request.form.get("produto")).lower().strip() in unidecode(produto[0]).lower().strip():
            pesq.append(produto)
    if pesq != []:
        return render_template("estoque.html", planilha_completa = pesq)
    return u"""
                <script>
                    alert("Não achamos nenhum produto com esse nome!")
                    window.location = "/estoque"
                </script>
            """  
            
@app.route("/sobre")
def sobre():
    return render_template("sobre.html")
        
app.run(debug=True, use_reloader=True)