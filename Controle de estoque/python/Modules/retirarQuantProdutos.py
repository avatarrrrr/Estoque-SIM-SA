#Esse módulo irá tirar uma determinada quantidade de um produo, se a quantidade do produto for menor do que o limite fixado pelo usuária, ele emitirá um alerta
def Remover_Item(planilha, produto, quantidade, limite):
    #Procura o Produto
    rm = planilha.find(produto)
    #Verifica se a quantidade que vai ser retirada é maior que a quantidade disponível, se sim, retorna um erro
    if int(planilha.cell(rm.row, 2).value) < quantidade:
        return "F"
    #Atualiza a célula com o valor da subtração do valor que já tem na célula com o valor que o usuário quer retirar
    planilha.update_cell(rm.row, 2, int(planilha.cell(rm.row, 2).value) - quantidade)
    #Verifica se a quantidade atual está abaixo do valor limite definido pelo usuário
    if int(planilha.cell(rm.row, 2).value) < limite:
        return "L"
    else:
        return "S"