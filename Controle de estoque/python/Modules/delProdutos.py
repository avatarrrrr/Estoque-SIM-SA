#Módulo responsável por excluir um produto!
def Remover_Produto(planilha, produto):
    #Pesquisa o nome enviado na planilha
    remover = planilha.find(produto)
    #Verifica se encontrou o produto
    if not remover:
        return "P"
    #Faz a remoção do produto e avalia se a exclusão foi bem sucedida ou não
    if planilha.delete_rows(remover.row):
        return "S"
    else:
        return "D"