from flask import Flask, request, render_template
from flaskext.mysql import MySQL
from unidecode import unidecode
import gspread
import datetime
import os

#Conexão com a Planilha
conexao = gspread.service_account()
planilha = conexao.open("Nature Saboaria").sheet1
transacoes = conexao.open("transacoes").sheet1

#Aplicação:
#O app.config["UPLOAD_FOLDER"] define a pasta padrão onde as imagens mandadas no form devem serem salvas!
app = Flask("Estoque-SIM-SA")
app.config["UPLOAD_FOLDER"] = "C:\\Users\\tanko\\Projects\\Estoque-SIM-SA\\static\\img"
#Configuração do banco de dados mysql, troque a senha conforme a senha do user root no seu mysql server
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = "estoquesimsa"
app.config["MYSQL_DATABASE_DB"] = "estoque"
app.config["MYSQL_DATABASE_Host"] = "localhost"
#Inicialização do MySQl
mysql = MySQL()
mysql.init_app(app)
db = mysql.connect()
estoque = db.cursor()

#Rotas do Front:

@app.route("/")
def main():

    #Criando uma Dicionário com todas as transações do DIA e já juntando as que tiverem repetidas em uma só, somando as quantidades
    estoque.execute("SELECT * FROM transações WHERE data=CURRENT_DATE()")
    dia = {}
    for transacao in estoque.fetchall():
        try:
            dia[unidecode(transacao[0]).lower()] += int(transacao[1])
        except:
            dia[unidecode(transacao[0]).lower()] = int(transacao[1])

    #Ordenando o dicionário pelo produto de maior quantidade:
    dia = sorted(dia.items(), key=lambda transacao: transacao[1], reverse=True)
    if dia == []:
        dia.append(["Não houve nenhuma transação hoje", 1])

    #Criando uma Dicionário com todas as transações do MÊS e já juntando as que tiverem repetidas em uma só, somando as quantidades
    estoque.execute("SELECT * FROM transações WHERE MONTH(data) = MONTH(CURRENT_DATE())")
    mes = {}
    for transacao in estoque.fetchall():
        try:
            mes[unidecode(transacao[0]).lower()] += int(transacao[1])
        except:
            mes[unidecode(transacao[0]).lower()] = int(transacao[1])
    
    #Ordenando o dicionário pelo produto de maior quantidade:
    mes = sorted(mes.items(), key=lambda transacao: transacao[1], reverse=True)
    if mes == []:
        mes.append(["Não houve nenhuma transação esse mês", 1])
    
    #Criando uma Dicionário com todas as transações do ANO e já juntando as que tiverem repetidas em uma só, somando as quantidades
    estoque.execute("SELECT * FROM transações WHERE YEAR(data) = YEAR(CURRENT_DATE())")
    ano = {}
    for transacao in estoque.fetchall():
        try:
            ano[unidecode(transacao[0]).lower()] += int(transacao[1])
        except:
            ano[unidecode(transacao[0]).lower()] = int(transacao[1])

    #Ordenando o dicionário pelo produto de maior quantidade:
    ano = sorted(ano.items(), key=lambda transacao: transacao[1], reverse=True)
    if ano == []:
        ano.append(["Não houve nenhuma transação esse ano", 1])

    return render_template("home.html", diaQuantidade = dia, mesQuantidade = mes, anoQuantidade = ano)

@app.route('/inserir')
def inserir():
    return render_template("incluirProduto.html")

@app.route('/estoque')
def produtos():
    estoque.execute("SELECT * FROM produtos")
    data = estoque.fetchall()
    return render_template('estoque.html', planilha_completa = data)

@app.route('/transacoes')
def transacoess():
    estoque.execute("SELECT * FROM transações")
    data = estoque.fetchall()
    return render_template("transacoes.html", transacoes = reversed(data))

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

#Pop up de venda
@app.route('/popup', methods=['POST'])
def popup():
    #Procura pelo produto escolhido no banco de dados
    estoque.execute("SELECT * FROM produtos WHERE id={}".format(request.form.get("item")))
    produto = estoque.fetchone()
    #Pega agora todos os produtos no banco de dados
    estoque.execute("SELECT * FROM produtos")
    #Retorna a página com os dados requisitados
    return render_template('popup.html', planilha_completa = estoque.fetchall(), nome = produto[1], imagem = produto[6], quantidade = produto[2], preço = produto[3])

#Pop-up de edição de planilha
@app.route('/popupEdition', methods=['POST'])
def popupEdition():
    #Pesquisa o produto no banco de dados
    estoque.execute("SELECT * FROM produtos WHERE id={}".format(request.form.get("id")))
    produto = estoque.fetchone()
    #Pega todos os produtos do banco de dados
    estoque.execute("SELECT * FROM produtos")
    #Separando string de inteiro do volume
    string = ''
    number = ''
    for s in produto[4]:
        if s.isdigit():
            number += s
        else:
            string += s
    #Retornando a página com os valores
    return render_template('editar.html', planilha_completa = estoque.fetchall(), id = produto[0], nome = produto[1], quantidade = produto[2], preço = produto[3], volume = string, valor = number, corpo = produto[5], imagem = produto[6])

#Rotas do Back:

#Roteamento para remover um produto ou uma transação
@app.route("/delete", methods=["DELETE"])
def deleteProduto():
    #Faz a deleção no banco de dados
    estoque.execute("DELETE FROM produtos WHERE id={}".format(request.get_data().decode("utf-8")))
    #Grava a alteração no banco de dados
    db.commit()
    #Retorna código de sucesso
    return "OK", 200

#Roteamento para fazer uma venda, caso a quantidade do produto fique abaixo do limite, ele dispara um alerta
limite = 5
@app.route("/venda", methods=["POST"])
def venda():
    #Procura o produto no banco de dados
    estoque.execute("SELECT quantidade, valor FROM produtos WHERE nome='{}'".format(request.form.get("nome")))
    produto = estoque.fetchone()
    quantidade = produto[0]
    preço = produto[1]

    #Atualiza a quantidade do produto com a subtração do valor que tem nele com a quantidade vendida
    estoque.execute("UPDATE produtos SET quantidade='{}' WHERE nome='{}'".format(quantidade - int(request.form.get("quantidade")), request.form.get("nome")))

    #Registrando nova transação
    estoque.execute("INSERT INTO transações (nome, quantidade, preço, data) VALUES ('{}', {}, {},  CURRENT_DATE)".format(request.form.get("nome"), request.form.get("quantidade"), round(preço * float(request.form.get("quantidade")), 1)))

    #Grava as alterações no banco de dados
    db.commit()

    #Verifica se o resultado da subtração ficou menor que o limite e retorna uma mensagem correspondente
    if quantidade - int(request.form.get("quantidade")) < limite:
        return render_template("respostaEstoque.html", retorno = "Operação Concluída, o total da venda foi R$ " + str(round(preço * int(request.form.get("quantidade")), 1)) + "! Este produto está abaixo do limite!")
    else:
        return render_template("respostaEstoque.html", retorno = "Operação Concluída, o total da venda foi R$ " + str(round(preço * int(request.form.get("quantidade")), 1)) + "!")

#Inserção de produtos
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
        request.files["imagem"].save(os.path.join(app.config["UPLOAD_FOLDER"], request.files["imagem"].filename))
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

#Edição de produtos
@app.route('/editar', methods=['POST'])
def editar():
    #Ver se o usário inseriu uma imagem, se sim, ele salva a imagem e o insere junto com os outros dados no banco de dados, se não, atualiza o banco de dados com os dados menos a imagem
    if request.files['imagem'].filename != '':
        request.files['imagem'].save(os.path.join(app.config['UPLOAD_FOLDER'], request.files['imagem'].filename))
        estoque.execute("UPDATE produtos SET nome='{}', quantidade={}, valor={}, peso='{}', finalidade='{}', imagem='{}' WHERE id={}".format(request.form.get("nome"), request.form.get("quantidade"), request.form.get("preço"), request.form.get("valor") + request.form.get("volume"), request.form.get("área do corpo"), request.files['imagem'].filename, request.form.get("id")))
        db.commit()
    else:
        estoque.execute("UPDATE produtos SET nome='{}', quantidade={}, valor={}, peso='{}', finalidade='{}' WHERE id={}".format(request.form.get("nome"), request.form.get("quantidade"), request.form.get("preço"), request.form.get("valor") + request.form.get("volume"), request.form.get("área do corpo"), request.form.get("id")))
        db.commit()
    return render_template('respostaEstoque.html', retorno = 'Item salvo com sucesso!')


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
        
app.run(debug=True, use_reloader=True)