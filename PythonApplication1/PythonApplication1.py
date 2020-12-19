#Sistema vencedor MegaSena

# _*_ coding: utf-8 _*_

import requests
import zipfile
import re
import random
from operator    import itemgetter
from datetime    import date
from bs4         import BeautifulSoup
from itertools   import chain, combinations
from pip._vendor.pyparsing import LineStart

# CONSTANTES GLOBAIS

ARQ_HTML_DEZENAS = 'd_megasc.htm'
DATA_ANO_ATUAL   = int(date.today().strftime('%Y'))  # data do ano atual
LINK_CAIXA_ZIP   = 'http://www1.caixa.gov.br/loterias/_arquivos/loterias/D_mgsasc.zip'

# Variáveis globais p/ analize.
ANO_ESCOLHIDO_PARA_ANALIZE    = "" # Sendo populada em 'imprime_menu'
NUM_TOTAL_JOGOS_ANALIZE       = 0
LISTA_TODAS_LINHAS_ELEMENTOS  = []
LISTA_TODAS_ELEMENTOS_ANALIZE = []
LISTA_TODAS_SEQUENCIA_OURO    = [] # ONDE VAI FICAR GUARDADAS AS SEQUÊNCIAS ENQUADRADAS NA ESTATÍSTICA.

dic_qualifica = {}

# ----------------------------- FUNÇÕES TÉCNICAS -------------------------------------------

def baixar_arq_megaSena():
    r = requests.get(LINK_CAIXA_ZIP)

    print('\nStatus Code : ', r.status_code)
    print('Headers       : ', r.headers['content-type'])
    print('Encoding      : ', r.encoding)
    print("Link : ", LINK_CAIXA_ZIP)

    if r.status_code == requests.codes.OK:
        nome_arqui_zip = LINK_CAIXA_ZIP.split("/")[-1]
        with open(nome_arqui_zip, "wb") as code:
            code.write(r.content)
    else:
        try:
            print("Erro Conexão HTTP : ", r.raise_for_status())
        except requests.exceptions.HTTPError as e:
            print(" Excessão ( Erro Conexão HTTP ) : ", e)


def extrai_zipMegaSena():
    arqZip = LINK_CAIXA_ZIP.split("/")[-1]  # Selecionando nome do arquivo zip.
    sourceZip = zipfile.ZipFile(arqZip, 'r')  # abrimos o arquivo zipado para leitura.
    lista_nomes_arq = sourceZip.namelist()  # lista de arquivos no conteúdo do zip.
    for arq in lista_nomes_arq:    
       padrao = re.search('.htm', arq)
       if padrao:
         sourceZip.extract(arq)  # extrai arquivo 'd_megasc.html'

    sourceZip.close()
    # os.remove(arqZip) # remove arquivo.

def extrai_sequencias_arquivo_html():
    global LISTA_TODAS_LINHAS_ELEMENTOS

    lista_todos_elementos_linha = [] # Matriz c/ todas as linhas do ( HTML Reformuladas )
    lista_tupla_cidade_estado   = []   # Vai conter conjunto de tuplas ( cada tupla contém a cidade e o estado ) vencedores no sorteio.
    lista_sequencia_dezenas     = []   # Vai conter a sequência das dezenas do sorteio.
    indice_while_principal      = 0
    elemento_while_principal    = 0
    cont_associadas             = 0
    indice_while_secundario     = 0 

    arq = open("d_megasc.htm", 'r')
    conteudoBeautifulSoup = BeautifulSoup(arq.read().encode('utf-8'), 'html.parser')  # parseando pagina
    table = conteudoBeautifulSoup.find('table', {'width': '1810'})
    lista_todas_linhas_tr = table.findAll('tr')[1:]

    while (indice_while_principal < len ( lista_todas_linhas_tr ) ):

        elemento_while_principal = [ x.contents for x in lista_todas_linhas_tr [ indice_while_principal ].findAll ( 'td' ) ]
        elemento_while_principal = list ( chain ( *elemento_while_principal ) )

        if ( len ( elemento_while_principal ) < 20 ): indice_while_principal += 1; continue
        # Laço de repetição p/ encontrar as TR's associadas.
        indice_while_secundario = indice_while_principal + 1
        cont_associadas = 0
        while ( indice_while_secundario < len ( lista_todas_linhas_tr ) ):
            elemento_while_secundario = [ x.contents for x in lista_todas_linhas_tr [ indice_while_secundario ].findAll ( 'td' ) ]
            elemento_while_secundario = list ( chain ( *elemento_while_secundario ) )
            if ( len ( elemento_while_secundario ) <= 2 ):
                cont_associadas += 1
                indice_while_secundario += 1
            elif ( len ( elemento_while_secundario ) > 2 ):
                break
        # Extraindo os dados da linha principal( Completa )
        lista_sequencia_dezenas.extend ( elemento_while_principal [ 2 : 8 ] )
        if ( len ( elemento_while_principal) == 21 ):
            str_cidade = str ( elemento_while_principal [ 10 ] ).replace (' ', '')
            lista_tupla_cidade_estado.extend ( [ ( str_cidade, elemento_while_principal [ 11 ] ) ] )
        elif ( len ( elemento_while_principal ) == 20 ):
            lista_tupla_cidade_estado.extend ( [ ( "Não Informado", elemento_while_principal [ 10 ] ) ] )
        # Extraindo TR's associadas se ouver.
        if ( cont_associadas > 0 ) :
            cont = 0
            indice_while_terceiro = indice_while_principal + 1
            while ( cont < cont_associadas ):
                colunas_tr_cidade_estado = [ x.contents for x in lista_todas_linhas_tr [ indice_while_terceiro ].findAll ( 'td' ) ]
                colunas_tr_cidade_estado = list ( chain ( *colunas_tr_cidade_estado ) )
                if  ( len ( colunas_tr_cidade_estado ) == 2 ):
                    str_cidade = str ( colunas_tr_cidade_estado [ 0 ] ).replace ( ' ', '' )
                    colunas_tr_cidade_estado [ 0 ] = str_cidade
                    lista_tupla_cidade_estado.extend ( [ ( colunas_tr_cidade_estado [ 0 ], colunas_tr_cidade_estado [ 1 ] ) ] )
                elif ( len ( colunas_tr_cidade_estado ) == 1 ):
                    lista_tupla_cidade_estado.extend ( [ ( "Não Informado", colunas_tr_cidade_estado [ 0 ] ) ] )
                cont += 1
                indice_while_terceiro += 1
        cont_associadas = 0

        # Inserindo e removendo excedentes.
        elemento_while_principal.insert ( 2, lista_sequencia_dezenas.copy () )
        del elemento_while_principal [ 3 : 9 ]
        if ( len ( elemento_while_principal ) == 16 ):
            elemento_while_principal.insert ( 5, lista_tupla_cidade_estado.copy () )
            del elemento_while_principal [ 6 : 8 ]
        elif ( len ( elemento_while_principal ) == 15 ):
            elemento_while_principal.insert ( 5, lista_tupla_cidade_estado.copy() )
            del elemento_while_principal [ 6 ]

        LISTA_TODAS_LINHAS_ELEMENTOS.append ( elemento_while_principal )
        lista_tupla_cidade_estado.clear()
        lista_sequencia_dezenas.clear()
        indice_while_principal += 1

""" Inicializa variáveis globais necessárias ao processamento. """
def inicializa_variaveis_globais():

    global ANO_ESCOLHIDO_PARA_ANALIZE
    global NUM_TOTAL_JOGOS_ANALIZE
    global LISTA_TODAS_LINHAS_ELEMENTOS
    global LISTA_TODAS_ELEMENTOS_ANALIZE

    #print("\nBaixando Arquivo MegaSena ...",end="\n")
    #baixar_arq_megaSena()
    print("Extrai Zip MegaSena ...",end="\n")
    extrai_zipMegaSena()
    print("Extrai Sequencias arquivo HTML ...",end="\n")
    extrai_sequencias_arquivo_html()

    if ( ANO_ESCOLHIDO_PARA_ANALIZE == 0 ) :
       NUM_TOTAL_JOGOS_ANALIZE       = len ( LISTA_TODAS_LINHAS_ELEMENTOS )
       LISTA_TODAS_ELEMENTOS_ANALIZE = LISTA_TODAS_LINHAS_ELEMENTOS
    else :
       LISTA_TODAS_ELEMENTOS_ANALIZE = [ r for r in LISTA_TODAS_LINHAS_ELEMENTOS if str( ANO_ESCOLHIDO_PARA_ANALIZE ) in r[1] ]
       NUM_TOTAL_JOGOS_ANALIZE       = len ( LISTA_TODAS_ELEMENTOS_ANALIZE )

def sequencia_todas_funcoes():

   estatistica_numeros_mais_caem() # 1
   numerosPares_impares    ()      # 2
   numeros_primos          ()      # 3  
   fibonacci               ()      # 4
   sorteios_linhas         ()      # 5
   sorteios_colunas        ()      # 6
   quadrantes_mais_sairam  ()      # 7
   dupla_consecutivas      ()      # 8  
   soma_num_sequencia      ()      # 9
   mascara_unidade_dezena  ()      # 10
   repeticoes_mesma_dezena ()      # 11 
   umeros_quadraticos      ()      # 12
   progressao_aritmetica   ()      # 13
   soma_digitos            ()      # 14
   multiplicidade          ()      # 15
   sub_sequencias_repetidas()      # 16
   sub_digitos_repetidos   ()      # 17

def imprime_menu():
    
    global ANO_ESCOLHIDO_PARA_ANALIZE

    str_titulo = ' MENU DE OPÇÕES MEGA-SENA '
    autor      = 'Leandro Ces'
    email      = 'leandro.eng.lcc@outlook.com'

    print ( '\n' + str_titulo.center ( 60, '*' ) )
    print ( '\nAutor     : ', autor )
    print ( 'Email       : ', email)

    print ( "\nIncializando Variáveis Globais..." )
    inicializa_variaveis_globais()
    
    while True :
   
       print ( "\n 1 - Gerar Estatística ( Executar funções. ) ." )
       print ( " 2 - Gerar Conjunto Ouro " )
       print ( " 3 - Testar Sequência " )
       print ( " 4 - Gerar Sequências Ouro ")
       print ( " 5 - Sair" )
       print ( "\nOpção : ", end = '' )
       opcao = int ( input() )

       if opcao == 1 :
         print ( '\nAno Especifico ou 0 para Todos ' )
         print ( 'Escolha : ', end = '' )
         ANO_ESCOLHIDO_PARA_ANALIZE = int ( input ( ) )
         sequencia_todas_funcoes()

       elif opcao == 2 :
          geracao_todas_possibilidades_mega () 
          func_guarda_em_arq_sequencias_ouro()

       elif opcao == 3 :
          opcao_w = 1
          while ( opcao_w != 0 ) :  
             print( " \nLista : ", end = '' )
             lista_str       = input () # 1,2,3,4,5,6
             lista_int       = [ int ( x ) for x in lista_str.split(",") ]
             lista_int.sort()
             res = func_conjunto_regras_ouro ( lista_int.copy() )
             if ( res == True ) : print ( "\t\t- Sequência Ouro" )
             else : 
                 print("\t\t- Sequência Ruim")
                 lista_negativa = [ x for x in dic_qualifica if dic_qualifica [ x ] == 0 ]
                 for valor in lista_negativa :
                    print("\t\t\t - ",valor)   
             dic_qualifica.clear()

             print("\n Deseja testar Outra Sequência ( 0 - sair / 1 - Continuar ): ", end = '' )
             opcao_w = int ( input() )

       elif opcao == 4 :
          opcao_w = 1
          while opcao_w != 0 :
              print("\nQuantas Sequências Ouro: ", end = '')
              num_seq = int ( input() )
              cont = 0
              print("\n")
              while cont < num_seq :
                   sequencia = gera_volante()
                   res = func_conjunto_regras_ouro_todas_p ( sequencia.copy() )
                   if res == True :
                     print("{} sequência : {}".format ( cont + 1, sequencia ) )
                     cont += 1
              print("\n Deseja testar Outra Sequência ( 0 - sair / 1 - Continuar ): ", end = '' )
              opcao_w = int ( input() )
    
       elif opcao == 5 :
          exit(0)
                  

# ------------------ MÓDULOS ESTATÍSTICOS -------------------------

def estatistica_numeros_mais_caem():

    global LISTA_TODAS_ELEMENTOS_ANALIZE
    global NUM_TOTAL_JOGOS_ANALIZE

    QUANT_MAISCAEM  = 5
    QUANT_MENOSCAEM = 5
    dic_num_vezes_numeros = { x: 0 for x in range ( 1, 61 ) }

    for sorteio_estruturado in LISTA_TODAS_ELEMENTOS_ANALIZE:
        for dezena in sorteio_estruturado [ 2 ]:
            dic_num_vezes_numeros [ int ( dezena ) ] += 1

    lista_valor_crescente = sorted ( dic_num_vezes_numeros.items(), key = itemgetter( 1 ) )
    lista_maisCaem  = lista_valor_crescente [ 55 : ]
    lista_maisCaem.reverse()
    lista_menosCaem = lista_valor_crescente[ : 5 ]

    # imprimindo dados estatísticos.
    titulo = ' Os ' + str(QUANT_MAISCAEM) + ' Números que mais saem e os ' + str ( QUANT_MENOSCAEM ) + ' que menos saem '
    print( "\n" + titulo.center ( 60, '*' ) + "\n" )

    menos = 0
    for indice_t in range ( len ( lista_maisCaem ) ):
        percent_mais  = ( ( lista_maisCaem  [ indice_t ] [ 1 ] / NUM_TOTAL_JOGOS_ANALIZE ) * 100 )
        percent_menos = ( ( lista_menosCaem [ indice_t ] [ 1 ] / NUM_TOTAL_JOGOS_ANALIZE ) * 100 )
        print( '{} - {}x - {:.2f}%'.  format( lista_maisCaem  [ indice_t ] [ 0 ], lista_maisCaem  [ 0 ] [ 1 ], percent_mais ),
               '\t{} - {}x - {:.2f}%'.format( lista_menosCaem [ indice_t ] [ 0 ], lista_menosCaem [ indice_t ] [ 1 ], percent_menos ) )

def numerosPares_impares():

    global LISTA_TODAS_ELEMENTOS_ANALIZE
    global NUM_TOTAL_JOGOS_ANALIZE

    num_pares_local   = 0
    num_impares_local = 0

    dic_possibilidades = { 'Somente Par'    : 0, '1 par e 5 impar': 0, '2 par e 4 impar': 0,
                           '3 par e 3 impar': 0, '4 par e 2 impar': 0, '5 par e 1 impar': 0,
                           'Somente Impar'  : 0}

    for sequencia in LISTA_TODAS_ELEMENTOS_ANALIZE:
        for dezena in sequencia [ 2 ]:
            if int ( dezena ) % 2 == 0 : num_pares_local += 1
            else : num_impares_local += 1

        if   ( num_pares_local   == 6 ) : dic_possibilidades [ 'Somente Par'     ] += 1
        elif ( num_impares_local == 6 ) : dic_possibilidades [ 'Somente Impar'   ] += 1
        elif ( num_impares_local == 5 ) : dic_possibilidades [ '1 par e 5 impar' ] += 1
        elif ( num_impares_local == 4 ) : dic_possibilidades [ '2 par e 4 impar' ] += 1
        elif ( num_impares_local == 3 ) : dic_possibilidades [ '3 par e 3 impar' ] += 1
        elif ( num_impares_local == 2 ) : dic_possibilidades [ '4 par e 2 impar' ] += 1
        elif ( num_impares_local == 1 ) : dic_possibilidades [ '5 par e 1 impar' ] += 1

        num_pares_local   = 0
        num_impares_local = 0

    lista_chaves = sorted ( dic_possibilidades.items(), key = itemgetter ( 1 ) )
    lista_chaves.reverse()
    titulo = ' Números Pares / Impares '
    print( "\n" + titulo.center ( 60, '*' ),"\n" )

    for t in lista_chaves:
        percent = ( ( t [ 1 ] / NUM_TOTAL_JOGOS_ANALIZE ) * 100 )
        print(' {} - {}x - {:.2f}%'.format( t [ 0 ], t [ 1 ], percent ) )

def numeros_primos():

    global LISTA_TODAS_ELEMENTOS_ANALIZE
    global NUM_TOTAL_JOGOS_ANALIZE

    dic_jogos_primos = { x : 0 for x in range ( 0, 7 ) }
    lista_primos     = [ 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59 ]

    for sequencia in LISTA_TODAS_ELEMENTOS_ANALIZE:
        contNumPrimos = 0
        for dezena in sequencia [ 2 ]:
            if int ( dezena ) in lista_primos:
                contNumPrimos += 1
        dic_jogos_primos [ contNumPrimos ] += 1
     
    lista_tuplas = sorted ( dic_jogos_primos.items(), key = itemgetter ( 1 ) )
    lista_tuplas.reverse()

    titulo = ' Números Primos '
    print ( '\n', titulo.center(60, '*'), '\n' )

    for tupla in lista_tuplas:
        percent = ( ( tupla [ 1 ] / NUM_TOTAL_JOGOS_ANALIZE ) * 100 )
        print ( '{} : {}x - {:.2f}%'.format ( tupla [ 0 ], tupla [ 1 ], percent ) )
         
def fibonacci():

    global LISTA_TODAS_ELEMENTOS_ANALIZE
    global NUM_TOTAL_JOGOS_ANALIZE

    dic_fibonacci         = dict ( { 0 : 0, 1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0 } )
    dic_fibonacci_cartela = [ 1, 2, 3, 5, 8, 13, 21, 34, 55 ]
    cont_fibonacci  = 0

    for linha in LISTA_TODAS_ELEMENTOS_ANALIZE:
        sequencia = [ int ( x ) for x in linha [ 2 ] ]
        r = set ( sequencia ) & set ( dic_fibonacci_cartela )
        dic_fibonacci [ len ( r ) ] += 1
        

    lista_tuplas = sorted ( dic_fibonacci.items(), key = itemgetter ( 1 ) )
    lista_tuplas.reverse()

    titulo = ' Números Fibonacci '
    print ( '\n', titulo.center ( 60, '*' ),"\n" )

    for tupla in lista_tuplas:
        percent = ( ( tupla [ 1 ] / NUM_TOTAL_JOGOS_ANALIZE ) * 100 )
        print('{} : {}x - {:.2f}%'.format ( tupla [ 0 ], tupla [ 1 ], percent ) )

def sorteios_linhas():

    global LISTA_TODAS_ELEMENTOS_ANALIZE
    global NUM_TOTAL_JOGOS_ANALIZE

    dic_linhas_count = { x : 0 for x in range ( 1, 7 ) }

    matriz_linhas_volante = { 1 : [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ],
                              2 : [ 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 ],
                              3 : [ 21, 22, 23, 24, 25, 26, 27, 28, 29, 30 ],
                              4 : [ 31, 32, 33, 34, 35, 36, 37, 38, 39, 40 ],
                              5 : [ 41, 42, 43, 44, 45, 46, 47, 48, 49, 50 ],
                              6 : [ 51, 52, 53, 54, 55, 56, 57, 58, 59, 60 ] }

    for linha in LISTA_TODAS_ELEMENTOS_ANALIZE:
        sequencia = linha [ 2 ]
        dic_linha_count = { x : 0 for x in range ( 1, 7 ) }
        for dezena in [ int ( x ) for x in sequencia ]:
            for i in range ( 1, 7 ):
                if any ( dezena == x for x in matriz_linhas_volante.get ( i ) ) :
                       if dic_linha_count [ i ] == 0 : dic_linha_count [ i ] = 1
        quant_linhas = len ( [ x for x in dic_linha_count.values() if x != 0 ] )
        dic_linhas_count [ quant_linhas ] += 1

    lista_tuplas = sorted( dic_linhas_count.items(), key = itemgetter ( 1 ) )
    lista_tuplas.reverse()

    titulo = 'Sorteio Linhas'
    print('\n', '***************** ' + titulo + ' ****************')

    for tupla in lista_tuplas:
        percent = ( ( tupla [ 1 ] / NUM_TOTAL_JOGOS_ANALIZE )  * 100 )
        print(' Em {} Linhas temos {}x {:.2f}% de Sequências '.format ( tupla [ 0 ], tupla [ 1 ], percent ) )

def sorteios_colunas():

    global LISTA_TODAS_ELEMENTOS_ANALIZE
    global NUM_TOTAL_JOGOS_ANALIZE

    dic_colunas_count = { x : 0 for x in range ( 1, 11 ) }

    matriz_colunas_volante = { 1: [ 1, 11, 21, 31, 41, 51 ],
                               2: [ 2, 12, 22, 32, 42, 52 ],
                               3: [ 3, 13, 23, 33, 43, 53 ],
                               4: [ 4, 14, 24, 34, 44, 54 ],
                               5: [ 5, 15, 25, 35, 45, 55 ],
                               6: [ 6, 16, 26, 36, 46, 56 ],
                               7: [ 7, 17, 27, 37, 47, 57 ],
                               8: [ 8, 18, 28, 38, 48, 58 ],
                               9: [ 9, 19, 29, 39, 49, 59 ],
                              10: [ 10, 20, 30, 40, 50, 60 ]
    }

    for linha in LISTA_TODAS_LINHAS_ELEMENTOS:
        sequencia = linha [ 2 ]
        dic_coluna_count = { x : 0 for x in range ( 1, 11 ) }
        for dezena in [ int ( x ) for x in sequencia ] :
            for i in range ( 1, 11 ) :
                if any ( dezena == x for x in matriz_colunas_volante.get ( i ) ):
                   if dic_coluna_count [ i ] == 0 : dic_coluna_count [ i ] = 1
        tam_count_coluna = len ( [ x for x in dic_coluna_count.values() if x != 0 ] )
        dic_colunas_count [ tam_count_coluna ] += 1

    lista_tuplas = sorted ( dic_colunas_count.items(), key = itemgetter ( 1 ) )
    lista_tuplas.reverse()

    titulo = ' Avalição da quant. das Colunas no serteios '
    print ( '\n', titulo.center ( 60, '*' ), "\n" )

    for tupla in lista_tuplas:
        percent = ( ( tupla [ 1 ] / NUM_TOTAL_JOGOS_ANALIZE  ) * 100 )
        print('Em {} Colunas, temos {}x - {:.2f}% Sequências '.format( tupla [ 0 ], tupla [ 1 ], percent ) )


def quadrantes_mais_sairam() :

    global LISTA_TODAS_ELEMENTOS_ANALIZE
    global NUM_TOTAL_JOGOS_ANALIZE

    dicContQuadrantes        = { k : 0 for k in range ( 1, 5 ) }
    identifica_quadrantes    = { 1 : [ 1, 2, 3, 4, 5, 11, 12, 13, 14, 15, 21, 22, 23, 24, 25      ],
                                 2 : [ 6, 7, 8, 9, 10, 16, 17, 18, 19, 20, 26, 27, 28, 29, 30     ],
                                 3 : [ 31, 32, 33, 34, 35, 41, 42, 43, 44, 45, 51, 52, 53, 54, 55 ],
                                 4 : [ 36, 37, 38, 39, 40, 46, 47, 48, 49, 50, 56, 57, 58, 59, 60 ] }


    for linha in LISTA_TODAS_ELEMENTOS_ANALIZE :
        sequencia = linha [ 2 ]
        dic_quadrantes = { x : 0 for x in range ( 1, 5 ) } # p/ identificar em quantos quadrantes diferentes a sequência saiu.
        for dezena in [ int ( x ) for x in sequencia ] :
            for i in range( 1, 5 ) :
               if ( any ( dezena == v for v in identifica_quadrantes [ i ] ) ) :
                  if dic_quadrantes [ i ] == 0 : dic_quadrantes [ i ] = 1
        quant_quadrante_sairam = len ( [ x for x in dic_quadrantes.values() if x != 0 ] )
        dicContQuadrantes [ quant_quadrante_sairam ] += 1

    lista_tuplas = sorted ( dicContQuadrantes.items(), key = itemgetter ( 1 ) )
    lista_tuplas.reverse()

    titulo = ' Quadrantes que os jogos saem '
    print ( " \n " + titulo.center ( 60, '*' ) + " \n " )

    for tupla in lista_tuplas:
        percent = ( ( tupla [ 1 ] / NUM_TOTAL_JOGOS_ANALIZE ) * 100 )
        print(' Em {} Quadrante - {}x - ({:.2f}%) - sequências saíram'.format( tupla [ 0 ], tupla [ 1 ], percent ) )

def dupla_consecutivas() :

    global LISTA_TODAS_ELEMENTOS_ANALIZE
    global NUM_TOTAL_JOGOS_ANALIZE

    dic_possibilidades = { 0 : 0, 1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0 }

    for _linha in LISTA_TODAS_ELEMENTOS_ANALIZE :
        _sequencia = [ int ( x ) for x in _linha [ 2 ] ]
        _cont = 0
        for _i in range ( 0, ( len ( _sequencia ) -1 ) ) :
           if _sequencia [ _i ] + 1 == _sequencia [ _i + 1 ] :
             _cont += 1
        dic_possibilidades [ _cont ] += 1 

    lista_tuplas = sorted ( dic_possibilidades.items(), key = itemgetter ( 1 ) )
    lista_tuplas.reverse()

    titulo = ' Padrão Duplas Consecutivas. '
    print(" \n " + titulo.center ( 60, '*' ) + " \n " )

    for tupla in lista_tuplas:
        percent = ( ( tupla [ 1 ] / NUM_TOTAL_JOGOS_ANALIZE ) * 100 )
        print(' Consecutivo {} - {}x - ({:.2f}%)'.format ( tupla [ 0 ], tupla [ 1 ], percent ) )

"""
   Quero saber se é comum sub-sequências repetidas de :
     0, 3, 4, 5, 6
"""

def sub_sequencias_consecutivas() :

   global LISTA_TODAS_ELEMENTOS_ANALIZE
   global NUM_TOTAL_JOGOS_ANALIZE
   
   dic_final = { 0 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0 }

   for _linha in LISTA_TODAS_ELEMENTOS_ANALIZE :
       sub_tres   = 0
       sub_quatro = 0
       sub_cinco  = 0
       sub_seis   = 0 
       _sequencia = [ int ( x ) for x in _linha [ 2 ] ]
       
       for _i in range ( 0, 4 ) :
          _sub_sequencia = [ _sequencia [ x ] for x in range ( 0, 3 ) ]      
          r = verifica_sequencia_todos_jogos ( _sub_sequencia )
          if r != 0 : sub_tres = 1; break
          else : _sequencia.pop ( 0 )
       
       _sequencia = [ int ( x ) for x in _linha [ 2 ] ]
       for _i in range ( 0, 3 ) :
          
          _sub_sequencia = [ _sequencia [ x ] for x in range ( 0, 4 ) ]
          r = verifica_sequencia_todos_jogos ( _sub_sequencia )
          if r != 0 : sub_quatro = 1; break
          else : _sequencia.pop ( 0 )
          
       _sequencia = [ int ( x ) for x in _linha [ 2 ] ]
       for _i in range ( 0, 2 ) :
             
           _sub_sequencia = [ _sequencia [ x ] for x in range ( 0, 5 ) ]
           r = verifica_sequencia_todos_jogos ( _sub_sequencia )
           if r != 0 : sub_cinco = 1; break
           else : _sequencia.pop ( 0 )
          
       _sequencia = [ int ( x ) for x in _linha [ 2 ] ]   
       r = verifica_sequencia_todos_jogos ( _sequencia )
       if r != 0 : sub_seis = 1

       if   sub_seis   != 0 : dic_final [ 6 ] += 1
       elif sub_cinco  != 0 : dic_final [ 5 ] += 1
       elif sub_quatro != 0 : dic_final [ 4 ] += 1
       elif sub_tres   != 0 : dic_final [ 3 ] += 1
       else : dic_final [ 0 ] += 1
       
   lista_tuplas = sorted ( dic_final.items(), key = itemgetter ( 1 ) )
   lista_tuplas.reverse()

   titulo = ' Padrão Sub-sequências. '
   print(" \n " + titulo.center ( 60, '*' ) + " \n " )

   for tupla in lista_tuplas:
     percent = ( ( tupla [ 1 ] / NUM_TOTAL_JOGOS_ANALIZE ) * 100 )
     print(' Consecutivo {} - {}x - ({:.2f}%)'.format ( tupla [ 0 ], tupla [ 1 ], percent ) )

def soma_num_sequencia() :

    global LISTA_TODAS_ELEMENTOS_ANALIZE
    global NUM_TOTAL_JOGOS_ANALIZE
    soma_dezenas = 0

    # dic_possibilidades : corresponde as somas das sequencias possíveis.
    dic_possibilidades = { k : 0 for k in range( 21, 346 ) }

    for _linha in LISTA_TODAS_ELEMENTOS_ANALIZE :
        _sequencia = _linha [ 2 ]
        for dezena in _sequencia :
            soma_dezenas += int ( dezena )
        dic_possibilidades [ soma_dezenas ] += 1
        soma_dezenas = 0

    # removendo os índices c/ valor 0 do dicionário de possibilidades.
    # dic_possibilidades_f = { k: v for k, v in dic_possibilidades.items() if v != 0 }

    lista_tuplas = sorted( dic_possibilidades.items(), key = itemgetter ( 0  ) )

    titulo = ' Soma das Sequências . '
    print("\n" + titulo.center(60, '*') + "\n")

    sub_lista    = []
    tupla_sub    = []
    inicio       = 0
    fim          = 65
    soma_valor_t = 0

    # Iterar as 5 sequências que mais saíram.
    for conj_lista in range( 0, 5 ) :
        sub_lista = [ x for x in lista_tuplas[ inicio : fim ] ]
        for tupla_sub in sub_lista :
            soma_valor_t += tupla_sub [ 1 ]
        percent = ( ( soma_valor_t / NUM_TOTAL_JOGOS_ANALIZE ) * 100 )

        print(' Faixa de {} a {} - Núm Jogos : {}  - Percent.: {:.2f}% '.format ( sub_lista [ 0 ] [ 0 ], sub_lista [ len( sub_lista) -1] [ 0 ], soma_valor_t, percent ) )
        print(" ------------------------------ ")
        soma_valor_t = 0
        inicio       = fim
        fim          = inicio + 65
        sub_lista.clear()

def mascara_unidade_dezena() :

    global LISTA_TODAS_ELEMENTOS_ANALIZE
    global NUM_TOTAL_JOGOS_ANALIZE
    soma_dezenas = 0

    # Aqui contém as 5 possibilidades de uma mascara
    dic_possibilidades = { ( 0,6 ) : 0, ( 1,5 ) : 0, ( 2, 4 ) : 0, ( 3, 3 ) : 0,
                           ( 4, 2 ) : 0, ( 5, 1 ) : 0, ( 6, 0 ) : 0  }
    dic_unidade_dezena = { "unidade" : 0, "dezena" : 0 }

    for _linha in LISTA_TODAS_ELEMENTOS_ANALIZE :
        _sequencia = _linha [ 2 ]
        for d in _sequencia :
            if int ( d ) < 10 : dic_unidade_dezena [ "unidade" ] += 1
            else : dic_unidade_dezena [ "dezena" ] += 1
        if ( dic_unidade_dezena [ "unidade" ] == 0 and dic_unidade_dezena [ "dezena" ] == 6 ) :
           dic_possibilidades [ ( 0, 6 ) ] += 1
        elif ( dic_unidade_dezena [ "unidade" ] == 1 and dic_unidade_dezena [ "dezena" ] == 5 ) :
             dic_possibilidades [ ( 1, 5 ) ] += 1
        elif ( dic_unidade_dezena [ "unidade" ] == 2 and dic_unidade_dezena [ "dezena" ] == 4 ) :
             dic_possibilidades [ ( 2, 4 ) ] += 1
        elif ( dic_unidade_dezena [ "unidade" ] == 3 and dic_unidade_dezena [ "dezena" ] == 3 ) :
             dic_possibilidades [ ( 3, 3 ) ] += 1
        elif ( dic_unidade_dezena [ "unidade" ] == 4 and dic_unidade_dezena [ "dezena" ] == 2 ) :
             dic_possibilidades [ ( 4, 2 ) ] += 1
        elif ( dic_unidade_dezena [ "unidade" ] == 5 and dic_unidade_dezena [ "dezena" ] == 1 ) :
             dic_possibilidades [ ( 5, 1 ) ] += 1
        elif ( dic_unidade_dezena [ "unidade" ] == 6 and dic_unidade_dezena [ "dezenas" ] == 0 ) :
             dic_possibilidades [ ( 6, 9 ) ] += 1
        dic_unidade_dezena [ "unidade" ] = 0
        dic_unidade_dezena [ "dezena" ]  = 0

    lista_tuplas = sorted ( dic_possibilidades.items(), key = itemgetter ( 1 ) )
    lista_tuplas.reverse()

    titulo = ' Mascara - ( Únidade / Dezena ) . '
    print("\n" + titulo.center(60, '*') + "\n")
    for tupla_p in lista_tuplas :
        percent = ( ( tupla_p [ 1 ] / NUM_TOTAL_JOGOS_ANALIZE ) * 100 )
        print(' Mascara de {} unidade {} dezenas - {}x  - Percent.: {:.2f}% '.format ( tupla_p [ 0 ] [ 0 ], tupla_p [ 0 ] [ 1 ], tupla_p [ 1], percent ) )

def repeticoes_mesma_dezena() :

    global LISTA_TODAS_ELEMENTOS_ANALIZE
    global NUM_TOTAL_JOGOS_ANALIZE

    dic_estatic_repeticoes = { 0 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0 }

    for _linha in LISTA_TODAS_ELEMENTOS_ANALIZE :
        _sequencia = [ int ( x ) for x in _linha [ 2 ] ]
        
        lista_dezenas = [ x for x in _sequencia if x > 9 ]
        dez           = [ x for x in lista_dezenas if x >= 10 and x <= 19 ]
        if dez == [] : dez.append ( 0 )
        
        vinte     = [ x for x in lista_dezenas if x >= 20 and x <= 29 ]
        if vinte == [] : vinte.append ( 0 )
        
        trinta    = [ x for x in lista_dezenas if x >= 30 and x  <= 39 ]
        if trinta == [] : trinta.append ( 0 )
        
        quarenta  = [ x for x in lista_dezenas if x >= 40 and x <= 49 ]
        if quarenta == [] : quarenta.append ( 0 )
        
        cinquenta = [ x for x in lista_dezenas if x >= 50 and x <= 59 ]
        if cinquenta == [] : cinquenta.append ( 0 )

        _lista = [ dez, vinte, trinta, quarenta, cinquenta ]
        maximo = 1
        for _sub in _lista :
            if len ( _sub ) > maximo :
               maximo = len( _sub )
               dic_estatic_repeticoes [ maximo ] += 1
        if maximo == 1 : dic_estatic_repeticoes [ 0 ] += 1 

    lista_tuplas = sorted ( dic_estatic_repeticoes.items(), key = itemgetter ( 1 ) )
    lista_tuplas.reverse()

    titulo = ' Padrão Repetições Dezena . '
    print("\n" + titulo.center(60, '*') + "\n")

    for tuplas in lista_tuplas :
        percent   = ( ( tuplas [ 1 ] / NUM_TOTAL_JOGOS_ANALIZE ) * 100 )
        print( " {} : {} - {:.2f}%".format ( tuplas [ 0 ], tuplas [ 1 ], percent  ) )

# Números quadráticos são aqueles que são o resultado de um outro número que foi elevado ao quadrado.
def numeros_quadraticos () :

    global LISTA_TODAS_ELEMENTOS_ANALIZE

    lista_quadraticos = [ 1, 4, 9, 16, 25, 36, 49 ]
                           
    quadraticos       = { x : 0 for x in range ( 0, 8 ) }

    for _linha in LISTA_TODAS_ELEMENTOS_ANALIZE :
        _sequencia = [ int ( x ) for x in _linha [ 2 ] ]
        _cont = 0
        for _d in _sequencia :
            if _d in lista_quadraticos : _cont += 1
        quadraticos [ _cont ] += 1

    lista_tuplas = sorted ( quadraticos.items(), key = itemgetter ( 1 ) )
    lista_tuplas.reverse()

    titulo = ' Padrão Números Quadráticos . '
    print("\n" + titulo.center(60, '*') + "\n")

    for tuplas in lista_tuplas :
       percent   = ( ( tuplas [ 1 ] / NUM_TOTAL_JOGOS_ANALIZE ) * 100 )
       print( " {} : {}x - {:.2f}%".format ( tuplas [ 0 ], tuplas [ 1 ], percent  ) )
        

"""
   1 - Em cada sequência verifica-se PA de 2 a 20.
   2 - Em cada PA verificado, conta quantos saíu.
       Se o Núm. de PA atual for maior que o anterior, guardo o maior.
   3 - Terminado de verificar todos os PA's da sequência atual, o máximo de PA's encontrados
       é incrementado no dicionário 'dic_matriz_result'.
       Condição para incrementar no dicinário :
          - Se PA máximo == 1 , então incrementa posição 0 do dicionário,
            Senão PA máximo >= 2 
"""
def progressao_aritmetica () :

    global LISTA_TODAS_ELEMENTOS_ANALIZE

    # Resultado final de cada sequência vai sendo incrementado aqui.
    dic_matriz_result = { 0 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0 }


    for _linha in LISTA_TODAS_ELEMENTOS_ANALIZE :
       _sequencia = [ int ( x ) for x in _linha [ 2 ] ]
       _maximo    = 0 # Vai conter o núm. máximo da razão que mais saíu.
       
       for _r in range ( 2, 21 ) : # aqui procuro as razões na sequência em questão,( cada _r é uma razão.).
          _contador  = 0
          
          for _i in range ( 0, 5  ) : # Percorrendo os índices da sequência.
             
             if ( ( _sequencia [ _i ] + _r ) == _sequencia [ _i + 1 ] ) :
               _contador += 1        
          if _contador > _maximo : _maximo = _contador  
       
       if _maximo >= 2 : 
         dic_matriz_result [ _maximo ] += 1
       elif _maximo == 1 :
           dic_matriz_result [ 0 ] += 1
       
    titulo = ' Padrão - Progressão Aritmética . '
    print("\n" + titulo.center(60, '*') + "\n")

    for _k, _v in dic_matriz_result.items() :
       percent   = ( ( dic_matriz_result [ _k ] / NUM_TOTAL_JOGOS_ANALIZE ) * 100 )
       print (" {} - (PA) - Sorteios {}x - {:.2f}% ". format ( _k, dic_matriz_result [ _k ], percent ) )


def soma_digitos() :

    global LISTA_TODAS_ELEMENTOS_ANALIZE

    soma_primeiro_digito= 0
    soma_segundo_digito = 0
    total_digitos       = 0

    dic_soma_digitos = { x : 0 for x in range ( 11, 77 ) }

    for _linha in LISTA_TODAS_ELEMENTOS_ANALIZE :
       _sequencia    = [ int ( x ) for x in _linha [ 2 ] ]
       
       soma_primeiro_digito = 0
       soma_segundo_digito  = 0

       for _c in range ( 0, 6 ) :
          if _sequencia [ _c ] < 10 :
            aux_str = '0'+str ( _sequencia [ _c ] )
          else : aux_str = str ( _sequencia [ _c ] )

          soma_primeiro_digito +=  int ( aux_str [ 0 ] )
          soma_segundo_digito  +=  int ( aux_str [ 1 ] )

       total_digitos = soma_primeiro_digito + soma_segundo_digito
       dic_soma_digitos [ total_digitos ] += 1

    titulo = ' Padrão - Soma dos Dígitos . '
    print("\n" + titulo.center(60, '*') + "\n")

    lista_tuplas = sorted ( dic_soma_digitos.items(), key = itemgetter ( 0 ) )

    percent_intervalo = 0
    quant_intervalo = 0 
    range_inicio    = 0
    range_fim       = 9
    
    while True :
      _subLista = lista_tuplas [ range_inicio : range_fim ]
      if _subLista == [] : break
      for _tupla in _subLista :
         percent_intervalo   += ( ( _tupla [ 1 ] / NUM_TOTAL_JOGOS_ANALIZE ) * 100 )
         quant_intervalo     += _tupla [ 1 ]    
      
      print( " Intervalo De [ {} a {} ] |  {}x - {:.2f}%".format ( _subLista [ 0 ][ 0 ], _subLista [ len( _subLista )-1 ][ 0 ], quant_intervalo, percent_intervalo  ) )
      print("-------------------------------------------")
      percent_intervalo = 0
      quant_intervalo   = 0
      range_inicio += 9
      range_fim    += 9

def multiplicidade () :

    global LISTA_TODAS_ELEMENTOS_ANALIZE

    # Cada x vai ter como valor um sub-dicionário de 0 a 6 c/ valor em 0. 
    dic_multiplos_coleta = { x : { a : 0 for a in range ( 0, 7 ) } for x in range ( 2, 31 )  }

    for _linha in LISTA_TODAS_ELEMENTOS_ANALIZE :
       _sequencia = [ int ( x ) for x in _linha [ 2 ] ]
       for _k in dic_multiplos_coleta.keys() :
           _cont = 0
           for _i in range ( 0, 6 ) :
              if _sequencia [ _i ] % _k == 0 : _cont += 1
           dic_multiplos_coleta [ _k ] [ _cont ] += 1

    titulo = ' Padrão - Multiplicidade . '
    print("\n" + titulo.center(60, '*') + "\n")

    for _key in dic_multiplos_coleta.keys() :
        for _i in range ( 0, 7 ) :
           percent = ( ( dic_multiplos_coleta [ _key ] [ _i ] / NUM_TOTAL_JOGOS_ANALIZE ) * 100 )         
           print ( "Multiplo de {} - {} Dezenas - {}x - {:.2f}%".format( _key, _i, dic_multiplos_coleta [ _key ] [ _i ], percent ) )    
        print("-----------------------")

def sub_digitos_repetidos() :

    global LISTA_TODAS_ELEMENTOS_ANALIZE
    global NUM_TOTAL_JOGOS_ANALIZE

    dic_subs_analizar = { 0 : 0, 4 : 0, 5 : 0, 6 : 0 } 

    for _linha_p in LISTA_TODAS_ELEMENTOS_ANALIZE :
        _sequencia_p = [ int ( x ) for x in _linha_p [ 2 ] ]
        _r = 0
        _s = 0 # Referênciando a mesma sequência.
        for _linha_s in LISTA_TODAS_ELEMENTOS_ANALIZE :
           _sequencia_s = [ int ( x ) for x in _linha_s [ 2 ] ]
           _aux = len ( set ( _sequencia_p  ) & set ( _sequencia_s ) )
           if _aux == 6 : _s += 1 
           if   _aux > _r and ( _aux == 6 and _s > 1 ) : _r = _aux
           elif _aux > _r and _aux == 5 : _r = _aux
           elif _aux > _r and _aux == 4 : _r = _aux  
        dic_subs_analizar [ _r ] += 1  
          
    lista_tuplas = sorted ( dic_subs_analizar.items(), key = itemgetter ( 1 ) )
    lista_tuplas.reverse()

    titulo = ' Padrão Sub-sequências Digitos repetidos. '
    print(" \n " + titulo.center(60, '*') + " \n ")

    for tupla in lista_tuplas :
        percent = ( ( tupla [ 1 ] / NUM_TOTAL_JOGOS_ANALIZE ) * 100 )
        print(' Sub-sequência {} - {}x - ( {:.2f}% )'.format ( tupla [ 0 ], tupla [ 1 ],percent ) )
           
# ------------ Função geradora de todas as possibilidades( Anagrama ) ------------------

def geracao_todas_possibilidades_mega() :

    global LISTA_TODAS_SEQUENCIA_OURO
    global funcao_chegou

    _lista_sequencia = []
    _cont_todas_possibilidade_mega = 0
    _cont_todas_possibilidades_ouro= 0

    for dez1 in range ( 60 ) :
        for dez2 in range ( dez1 + 1, 60 ) :
            for dez3 in range ( dez2 + 1, 60 ) :
                for dez4 in range ( dez3 + 1, 60 ) :
                    for dez5 in range ( dez4 + 1, 60 ) :
                        for dez6 in range ( dez5 + 1, 60 ) :
                            _lista_sequencia.append ( dez1 + 1 )
                            _lista_sequencia.append ( dez2 + 1 )
                            _lista_sequencia.append ( dez3 + 1 )
                            _lista_sequencia.append ( dez4 + 1 )
                            _lista_sequencia.append ( dez5 + 1 )
                            _lista_sequencia.append ( dez6 + 1 )
                            
                            _cont_todas_possibilidade_mega += 1
                            res = func_conjunto_regras_ouro_todas_p ( _lista_sequencia )
                            if res == True :
                              LISTA_TODAS_SEQUENCIA_OURO.append ( _lista_sequencia )
                              _cont_todas_possibilidades_ouro += 1
                            print("Contador_p : ",_cont_todas_possibilidade_mega," - Contador_O : ",_cont_todas_possibilidades_ouro," - Tadas as Possibilidades = > ",_lista_sequencia)
                            _lista_sequencia.clear()

# ------------------------------ funções de apoio . ------------------------------------

# função que gera volantes(sequências) aleatórias em ordem crescente.
def gera_volante () :

    lista_sequencia = []
    while True :
         for x in range ( 0, 6 ) :
            lista_sequencia.append( random.randrange ( 1, 61 ) )
         lista = set ( lista_sequencia )
         if len ( lista ) == 6 : break
         else : lista_sequencia = []
    
    lista_sequencia.sort()
         
    return lista_sequencia

# recebe uma sequencia de inteiros e verifica todos os jogos p saber em quantos a mesma se encontra.
def verifica_sequencia_todos_jogos ( l_sequencia ) :

    global LISTA_TODAS_ELEMENTOS_ANALIZE
    global NUM_TOTAL_JOGOS_ANALIZE
    
    _contador = 0
    tam_sub   = len ( l_sequencia )

    for _linha in LISTA_TODAS_ELEMENTOS_ANALIZE :
        _sequencia = [ int ( x ) for x in _linha [ 2 ] ]
        if tam_sub == 3 :
          for _i in range ( 0, 4 ) :
             if ( ( l_sequencia [ 0 ] == _sequencia [ _i ]     ) and
                  ( l_sequencia [ 1 ] == _sequencia [ _i + 1 ] ) and
                  ( l_sequencia [ 2 ] == _sequencia [ _i + 2 ] ) ) :
               _contador += 1
               if _contador > 1 : return _contador -1
        elif tam_sub == 4 :
          for _i in range ( 0, 3 ) :
             if ( ( l_sequencia [ 0 ] == _sequencia [ _i ]     ) and
                  ( l_sequencia [ 1 ] == _sequencia [ _i + 1 ] ) and
                  ( l_sequencia [ 2 ] == _sequencia [ _i + 2 ] ) and
                  ( l_sequencia [ 3 ] == _sequencia [ _i + 3 ] ) ) :
               _contador += 1 
               if _contador > 1 : return _contador - 1
        elif tam_sub == 5 :
           for _i in range ( 0, 2 ) :  
              if ( ( l_sequencia [ 0 ] == _sequencia [ _i ]     ) and
                  ( l_sequencia [ 1 ] == _sequencia [ _i + 1 ] ) and
                  ( l_sequencia [ 2 ] == _sequencia [ _i + 2 ] ) and
                  ( l_sequencia [ 3 ] == _sequencia [ _i + 3 ] ) and 
                  ( l_sequencia [ 4 ] == _sequencia [ _i + 4 ] ) ) :
                _contador += 1
                if _contador > 1 : return _contador - 1
        elif tam_sub == 6 :
           if ( ( l_sequencia [ 0 ] == _sequencia [ 0 ] ) and
               ( l_sequencia [ 1 ] == _sequencia [ 1 ] ) and
               ( l_sequencia [ 2 ] == _sequencia [ 2 ] ) and
               ( l_sequencia [ 3 ] == _sequencia [ 3 ] ) and 
               ( l_sequencia [ 4 ] == _sequencia [ 4 ] ) and
               ( l_sequencia [ 5 ] == _sequencia [ 5 ] ) ) :
             _contador += 1                  
             if _contador > 1 : return _contador - 1
    
    return 0

    
# verifica se novos indices existe em uma lista
def analiza_indice_lista( _indice_referencia,
                          _quant_indices, # quant. de indices a verificar.
                          _lista ) :
    retorno = False

    for _i in range ( 1, _quant_indices + 1 ):
       try :
           a = _lista [ _indice_referencia + _i ]
       except IndexError :
           retorno = True

    return retorno

""" está função recebe uma sequência em string e rotorna em quantos jogos ela foi encontrada """
def analize_sequencia_conjuntos ( seq_param = "") :

    global LISTA_TODAS_ELEMENTOS_ANALIZE
    cont = 0

    for _linha in  LISTA_TODAS_ELEMENTOS_ANALIZE :
        sequencia = _linha [ 2 ]
        _seq_str  = ','.join ( sequencia )
        if seq_param in _seq_str : cont += 1

    return cont
    
# ------------------------------ funções regras   . ------------------------------------   

"""
  Está função vai ser usada sempre que eu quiser testar uma sequência.
"""
def func_conjunto_regras_ouro ( lista_sequencia ) :

    retorno = False
    aux     = 0

    # Avaliando as necessárias.
    if func_filtro_sub_sequencias_repetidas( lista_sequencia.copy() ) : 
      if func_filtro_digitos_repetidos     ( lista_sequencia.copy() ) :
        if func_filtro_duplaConsecutiva    ( lista_sequencia.copy() ) :
          if func_filtro_repeticao_dezena  ( lista_sequencia.copy() ) :
            if func_filtro_mascara         ( lista_sequencia.copy() ) :
              # 70% dessas funções devem passar. 
              if func_filtro_par_impar             ( lista_sequencia.copy() )  : aux += 1
              if func_filtro_num_primos            ( lista_sequencia.copy() )  : aux += 1
              if func_filtro_fibonacci             ( lista_sequencia.copy() )  : aux += 1
              if func_filtro_linhas                ( lista_sequencia.copy() )  : aux += 1
              if func_filtro_colunas               ( lista_sequencia.copy() )  : aux += 1
              if func_filtro_quadrantes            ( lista_sequencia.copy() )  : aux += 1
              if func_filtro_soma_sequencias       ( lista_sequencia.copy() )  : aux += 1
              if func_filtro_numeros_quadraticos   ( lista_sequencia.copy() )  : aux += 1
              if func_filtro_progressao_aritmetica ( lista_sequencia.copy() )  : aux += 1
              if func_filtro_soma_digitos          ( lista_sequencia.copy() )  : aux += 1
              if func_filtro_multiplicidade        ( lista_sequencia.copy() )  : aux += 1   
    
      
      if aux >= 7 : retorno = True 
    
    return retorno

"""
   Está função é chamada sempre que for necessária criar todas as 
   possibilidades da mega-sena ou gerar algumas sequencias p/ jogos. 
   Cada possibilidade terá que ser testada antes de ser gravada no 
   arquivo. Está função será util para isto pois a mesma tem uma 
   estrutura de teste rápida, assim cada possibilidade pode ser 
   testada muito rapidamente, pois são mais de 50.000.000.
"""
def func_conjunto_regras_ouro_todas_p ( lista_sequencia ) :

    retorno = False 
    aux     = 0
    
    # Analizando as necessárias.
    if func_filtro_digitos_repetidos                ( lista_sequencia.copy() ) :   
      if func_filtro_duplaConsecutiva               ( lista_sequencia.copy() ) : 
        if func_filtro_repeticao_dezena             ( lista_sequencia.copy() ) : 
          if func_filtro_mascara                    ( lista_sequencia.copy() ) :
            if func_filtro_sub_sequencias_repetidas ( lista_sequencia.copy() ) :  
                
              # No minimo 70% tem que passar.
              if func_filtro_par_impar             ( lista_sequencia.copy() ) : aux += 1 
              if func_filtro_num_primos            ( lista_sequencia.copy() ) : aux += 1      
              if func_filtro_fibonacci             ( lista_sequencia.copy() ) : aux += 1 
              if func_filtro_linhas                ( lista_sequencia.copy() ) : aux += 1 
              if func_filtro_colunas               ( lista_sequencia.copy() ) : aux += 1 
              if func_filtro_quadrantes            ( lista_sequencia.copy() ) : aux += 1 
              if func_filtro_soma_sequencias       ( lista_sequencia.copy() ) : aux += 1 
              if func_filtro_numeros_quadraticos   ( lista_sequencia.copy() ) : aux += 1 
              if func_filtro_progressao_aritmetica ( lista_sequencia.copy() ) : aux += 1 
              if func_filtro_soma_digitos          ( lista_sequencia.copy() ) : aux += 1 
              if func_filtro_multiplicidade        ( lista_sequencia.copy() ) : aux += 1                                     
   
    if aux >= 7 : retorno = True
    
    return retorno

def func_filtro_digitos_repetidos( lista_sequencia ) :

   global LISTA_TODAS_ELEMENTOS_ANALIZE
   global NUM_TOTAL_JOGOS_ANALIZE

   retorno = False

   cont_max_digitos = 0
   for _linha in LISTA_TODAS_ELEMENTOS_ANALIZE :
       _sequencia = [ int ( x ) for x in _linha [ 2 ] ]
       _r = len ( set ( lista_sequencia ) & set( _sequencia ) )
       if _r > cont_max_digitos : cont_max_digitos = _r
   
   if cont_max_digitos <= 4 : retorno = True

   return retorno


def func_filtro_par_impar ( lista_sequencia ) :

   retorno = False

   dic_ = {"par" : 0, "impar": 0}
   
   for _d in lista_sequencia :
     if _d % 2 == 0 :  dic_["par"] += 1
     else : dic_["impar"] += 1
    
   if ( ( dic_["par"] == 3 and dic_["impar"] == 3 ) or
        ( dic_["par"] == 4 and dic_["impar"] == 2 ) or
        ( dic_["par"] == 2 and dic_["impar"] == 4 ) ) :
    retorno = True   
      
   return retorno

def func_filtro_num_primos ( lista_sequencia ) :

   lista_primos    = [ 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59 ]
   cont_num_primos = 0
   retorno         = False

   r = len ( set ( lista_primos ) & set ( lista_sequencia ) )
   
   if ( r >= 1 and r <= 3 ) : 
     retorno = True
     
   return retorno

def func_filtro_fibonacci ( lista_sequencia ) :

    lista_finbonacci = [ 1, 2, 3, 5, 8, 13, 21, 34, 55 ]
    retorno = False

    r = len ( set ( lista_sequencia ) & set ( lista_finbonacci ) )
    if ( r <= 2 ) :
      retorno = True  

    return retorno

def func_filtro_linhas ( lista_sequencia ) :

    matriz_linhas_volante = { 1 : [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ],
                              2 : [ 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 ],
                              3 : [ 21, 22, 23, 24, 25, 26, 27, 28, 29, 30 ],
                              4 : [ 31, 32, 33, 34, 35, 36, 37, 38, 39, 40 ],
                              5 : [ 41, 42, 43, 44, 45, 46, 47, 48, 49, 50 ],
                              6 : [ 51, 52, 53, 54, 55, 56, 57, 58, 59, 60 ] }

    res        = 0
    cont_linha = 0
    retorno    = False
    for _i in range( 1, len ( matriz_linhas_volante ) + 1 ) :
      
       res = len ( set ( matriz_linhas_volante [ _i ] ) & set ( lista_sequencia  ) )
       if res != 0 : cont_linha += 1

    if cont_linha >= 3 and cont_linha <= 5 :
      retorno = True

    return retorno

def func_filtro_colunas ( lista_sequencia ) :

    matriz_colunas_volante = { 1: [ 1, 11, 21, 31, 41, 51 ],
                               2: [ 2, 12, 22, 32, 42, 52 ],
                               3: [ 3, 13, 23, 33, 43, 53 ],
                               4: [ 4, 14, 24, 34, 44, 54 ],
                               5: [ 5, 15, 25, 35, 45, 55 ],
                               6: [ 6, 16, 26, 36, 46, 56 ],
                               7: [ 7, 17, 27, 37, 47, 57 ],
                               8: [ 8, 18, 28, 38, 48, 58 ],
                               9: [ 9, 19, 29, 39, 49, 59 ],
                              10: [ 10, 20, 30, 40, 50, 60 ] }

    res         = 0
    cont_coluna = 0
    retorno     = False
    for _i in range( 1, len ( matriz_colunas_volante ) + 1 ) :
      
       res = len ( set ( matriz_colunas_volante [ _i ] ) & set ( lista_sequencia  ) )
       if res != 0 : cont_coluna += 1

    if cont_coluna >= 4 and cont_coluna <= 6 :
      retorno = True

    return retorno

def func_filtro_quadrantes ( lista_sequencia ) :

    identifica_quadrantes    = { 1 : [ 1, 2, 3, 4, 5, 11, 12, 13, 14, 15, 21, 22, 23, 24, 25      ],
                                 2 : [ 6, 7, 8, 9, 10, 16, 17, 18, 19, 20, 26, 27, 28, 29, 30     ],
                                 3 : [ 31, 32, 33, 34, 35, 41, 42, 43, 44, 45, 51, 52, 53, 54, 55 ],
                                 4 : [ 36, 37, 38, 39, 40, 46, 47, 48, 49, 50, 56, 57, 58, 59, 60 ] }


    res            = 0
    cont_quadrante = 0
    retorno        = False
    for _i in range( 1, len ( identifica_quadrantes ) + 1 ) :
                              
       res = len ( set ( identifica_quadrantes [ _i ] ) & set ( lista_sequencia  ) )
       if res != 0 : cont_quadrante += 1

    if cont_quadrante >= 3 and cont_quadrante <= 4 :
      retorno = True

    return retorno

def func_filtro_soma_sequencias ( lista_sequencia ) :

    retorno = False
    soma_lista = sum ( lista_sequencia )

    if ( soma_lista >= 86 and soma_lista <= 280 ) :
      retorno = True
      
    return retorno

def func_filtro_mascara ( lista_sequencia ) :

    retorno = False
    r = len ( [ x for x in lista_sequencia if x < 10 ] )

    if ( r <= 2 ) : 
      retorno = True 

    return retorno

def func_filtro_repeticao_dezena ( lista_sequencia ) :
     
    retorno = False

    analize = { 10 : [ x for x in range ( 10, 20  ) ],  
                20 : [ x for x in range ( 20, 30  ) ],
                30 : [ x for x in range ( 30, 40  ) ],
                40 : [ x for x in range ( 40, 50  ) ],
                50 : [ x for x in range ( 50, 60  ) ] }

    dic_contador = { 10 : 0, 20 : 0, 30 : 0, 40 : 0, 50 : 0 }

    for dezena_ in lista_sequencia :
        aux = 0
        for key_ in analize.keys() :
            aux = len ( [ x for x in analize  [ key_ ] if x > dezena_ and x < dezena + 10 ] )
            if aux != 0 : dic_contador [ key_] += aux; break

    maximo_repeticoes = dic_contador [ max ( dic_contador, key=dic_contador.get ) ]
           
    if maximo_repeticoes >= 2 or maximo_repeticoes <= 3 :
      retorno = True 
      
    return retorno

def func_filtro_numeros_quadraticos ( lista_sequencia ) :

    retorno = False
    lista_quadraticos = [ 1, 4, 9, 16, 25, 36, 49 ]

    _cont = 0;
    for _d in lista_sequencia :
      if _d in lista_quadraticos : _cont += 1
    
    if _cont <= 1 : retorno = True
    
    return retorno
     
def func_filtro_progressao_aritmetica ( lista_sequencia ) :

   retorno = False 

   _contador = 0
   for _r in range ( 2, 21 ) :
      _aux      = 0
      for _i in range ( 0, 5 ) :
         if ( lista_sequencia [ _i ] + _r == lista_sequencia [ _i + 1 ] ) :
           _aux += 1
      if _aux > _contador :
        _contador = _aux  
        
   if _contador <= 2 :
     retorno = True
     
   return retorno 

def func_filtro_soma_digitos ( lista_sequencia ) :

    retorno = False

    _soma_digito_pri = 0
    _soma_digito_seg = 0

    for _i in range ( 0, len ( lista_sequencia ) ) :
        if lista_sequencia [ _i ] < 10 :
          _soma_digito_seg += lista_sequencia [ _i ]
        else :
          str_ = str ( lista_sequencia [ _i ] ) 
          _soma_digito_pri += int ( str_ [ 0 ] )
          _soma_digito_seg += int ( str_ [ 1 ] )        

    soma_total = _soma_digito_pri + _soma_digito_seg

    if soma_total >= 29 and soma_total <= 55 :
      retorno = True

    return retorno

def func_filtro_multiplicidade ( lista_sequencia ) :

   retorno = False 
   dic_multiplicidade = { x : 0 for x in range ( 2, 31 ) }

   for _key in dic_multiplicidade.keys() :
      _cont = 0
      for _dezena in lista_sequencia :
         if _dezena % _key == 0 : _cont += 1
      dic_multiplicidade [ _key ] = _cont

   if ( not ( dic_multiplicidade [ 2 ] >= 1 and dic_multiplicidade [ 2 ] <= 5 ) ) : return retorno
   if ( not ( dic_multiplicidade [ 3 ] >= 1 and dic_multiplicidade [ 3 ] <= 3 ) ) : return retorno
   if ( not ( dic_multiplicidade [ 4 ] <= 3 ) )  : return retorno
   if ( not ( dic_multiplicidade [ 5 ] <= 2 ) )  : return retorno
   if ( not ( dic_multiplicidade [ 6 ] <= 2 ) )  : return retorno
   if ( not ( dic_multiplicidade [ 7 ] <= 2 ) )  : return retorno
   if ( not ( dic_multiplicidade [ 8 ] <= 2 ) )  : return retorno
   if ( not ( dic_multiplicidade [ 9 ] <= 1 ) )  : return retorno
   if ( not ( dic_multiplicidade [ 10 ] <= 1 ) ) : return retorno
   if ( not ( dic_multiplicidade [ 11 ] <= 1 ) ) : return retorno
   if ( not ( dic_multiplicidade [ 12 ] <= 1 ) ) : return retorno
   if ( not ( dic_multiplicidade [ 13 ] <= 1 ) ) : return retorno
   if ( not ( dic_multiplicidade [ 14 ] <= 1 ) ) : return retorno
   if ( not ( dic_multiplicidade [ 15 ] <= 1 ) ) : return retorno
   if ( not ( dic_multiplicidade [ 16 ] <= 1 ) ) : return retorno 
   if ( not ( dic_multiplicidade [ 17 ] <= 1 ) ) : return retorno
   if ( not ( dic_multiplicidade [ 18 ] <= 1 ) ) : return retorno
   if ( not ( dic_multiplicidade [ 19 ] <= 1 ) ) : return retorno
   if ( not ( dic_multiplicidade [ 20 ] <= 1 ) ) : return retorno
   if ( not ( dic_multiplicidade [ 21 ] <= 1 ) ) : return retorno
   if ( not ( dic_multiplicidade [ 22 ] <= 1 ) ) : return retorno
   if ( not ( dic_multiplicidade [ 23 ] <= 1 ) ) : return retorno 
   if ( not ( dic_multiplicidade [ 24 ] <= 1 ) ) : return retorno
   if ( not ( dic_multiplicidade [ 25 ] <= 1 ) ) : return retorno 
   if ( not ( dic_multiplicidade [ 26 ] <= 1 ) ) : return retorno  
   if ( not ( dic_multiplicidade [ 27 ] <= 1 ) ) : return retorno
   if ( not ( dic_multiplicidade [ 28 ] <= 1 ) ) : return retorno
   if ( not ( dic_multiplicidade [ 29 ] <= 1 ) ) : return retorno
   if ( not ( dic_multiplicidade [ 30 ] <= 1 ) ) : return retorno
   
   retorno = True
                                                            
   return retorno

def func_filtro_duplaConsecutiva ( lista_sequencia ) :

   retorno = False
   _cont = 0
   for _i in range ( 0, ( len ( lista_sequencia ) -1 ) ) :
      if lista_sequencia [ _i ] + 1 == lista_sequencia [ _i + 1 ] :
        _cont += 1

   if _cont <= 1 :
    retorno = True

   return retorno

def func_filtro_sub_sequencias_repetidas ( lista_sequencia ) :

    v = 0 
    for _i in range ( 0, 3 ) :
       sub_lista = lista_sequencia [ _i : 3 + v ]
       res = analize_sequencia_conjuntos ( str ( sub_lista ) )
       if res > 0 : return True     
       v += 1
    
    return False   

def func_guarda_em_arq_sequencias_ouro () :

    global LISTA_TODAS_SEQUENCIA_OURO
    _sequencia_str = ""

    file = open ( "c:\\Users\\userIracema\\Desktop\\history_mega_ouro.txt","w" )

    _seq_1 = 1
    for _lista_ouro in LISTA_TODAS_SEQUENCIA_OURO :
        aux    = 1
        for _dezena in _lista_ouro :
            if aux < 6 :
               if ( _dezena < 10 ) :
                  _sequencia_str += _seq_1 + " ) " + str ( 0 ) + str ( _dezena ) + " - "
               else :
                  _sequencia_str += _seq_1 + " ) " + str ( _dezena ) + " - "
            else : # se aux for igual a 6, então .
                if (_dezena < 10):
                    _sequencia_str += _seq_1 + " ) " + str ( 0 ) + str ( _dezena ) + " - "
                else:
                    _sequencia_str += _seq_1 + " ) " + str( _dezena )
            aux    += 1
            _seq_1 += 1
        print(_seq_1+ " ) " + _sequencia_str )
        print(" Guardando Sequência Ouro = >  : ", _sequencia_str )
        file.write( _sequencia_str )
        _sequencia_str = ""
    file.close()





if __name__ == '__main__':

     imprime_menu()
