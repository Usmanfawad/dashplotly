## biblioteca
import pandas as pd

# #####################################
# ## pegar a classificação por segmento e o preço
# ##################################### 

segmentos = pd.read_json("segmentos_eod - segmentos_eod.json")
prices_segmento_base = pd.read_json(r'prices_segmento_base.json')
inicio = '2021-01-11'
fim = '2021-02-12'

# prices_segmento = prices_segmento_base[prices_segmento_base['data']>=inicio]

def pa_long_ativo_func(inicio,fim,prices_segmento_base):
    """
    o pa_long_ativo retorna o price action para os ativos

    Parameters
    ----------
    inicio : str
        inicio do price action
    fim : str
        fim do price_action
    prices_segmento : dataframe
        dataframe com os preços em formato long

    Returns
    -------
    Retorna o dataframe de price action com as seguintes colunas:
        data, ativo, rentabilidade
    -------
    None.

    """
    prices_segmento = prices_segmento_base[(prices_segmento_base['data']>=inicio)& ((prices_segmento_base['data']<=fim))]
    if 'segmento' in prices_segmento.columns:
        print("a coluna segmento existe no df prices_segmento_base")
        prices_segmento.drop(columns={ 'Volume','segmento'},inplace=True)
    else:
        print("a coluna segmento NÃO existe no df prices_segmento_base")    
    prices_segmento = prices_segmento.drop_duplicates().reset_index()
    prices_segmento = prices_segmento.drop_duplicates().reset_index()
    prices_segmento.sort_values(['data','ativo'],inplace=True)
    prices_wide = prices_segmento.pivot(index='data',columns='ativo')[['open adj', 'high adj', 'low adj', 'Adj Close']]
    prices_wide = prices_wide.fillna(method='bfill')
    prices_wide = prices_wide.fillna(method='ffill')
    prices_wide.columns = prices_wide.columns.map('_'.join).str.strip('_')
    price_action_temp1 = prices_wide/ prices_wide.iloc[0]
    price_action = (price_action_temp1 -1) * 100
    price_action = price_action.round(2)
    price_action = price_action.reset_index()
    pa_long_ativo = price_action.melt(id_vars=['data'], var_name='ativo', value_name='rentabilidade')
    pa_long_ativo = pa_long_ativo.rename(columns={'Date': 'data'})
    pa_long_ativo = pa_long_ativo.round(2)
    pa_long_ativo['tipo'] = pa_long_ativo['ativo'].apply(lambda x:  x.split('_')[0])
    pa_long_ativo['ativo'] = pa_long_ativo['ativo'].apply(lambda x:  x.split('_')[1])
    pa_long_ativo = pa_long_ativo.sort_values(['ativo','data'])
    
    return pa_long_ativo

pa_long_ativo = pa_long_ativo_func(inicio,fim,prices_segmento_base)    


#####################################
## GERAR O RANKING DOS ATIVOS
##################################### 

def ranking_ativo_func(pa_long_ativo):
    """
    o ranking_ativo retorna o ranking de price action dos ativos

    Parameters
    ----------
    pa_long_ativo : dataframe
        dataframe do price action por ativo

    Returns
    -------
    Retorna o ranking de retorno classificado por ativo com as seguintes colunas:
        ativo, segmento, retorno_ult_ativo, ranking_ativo

    """
    ult_data = pa_long_ativo['data'].tail(1).to_string(index=False,header=False)
    ult_data = ult_data.strip()
    ranking_ativo_temp2 = pa_long_ativo[(pa_long_ativo['data'] == ult_data)&(pa_long_ativo['tipo']=='Adj Close')].copy()
    ranking_ativo_temp2 = ranking_ativo_temp2.drop_duplicates()
    ranking_ativo_temp2 = ranking_ativo_temp2.sort_values(['rentabilidade','ativo'], ascending = False)
    ranking_ativo_temp3 = ranking_ativo_temp2.dropna(how='any', inplace=False)
    ranking_ativo_temp4 = ranking_ativo_temp3.reset_index()
    ranking_ativo_temp4.drop(columns='index',inplace=True)
    ranking_ativo_temp4['ranking_ativo'] = ranking_ativo_temp4.index + 1
    ranking_ativo_temp5 = ranking_ativo_temp4.drop(columns=['data','tipo'])
    ranking_ativo_temp5.rename(columns={'rentabilidade': 'retorno_ult_ativo'}, inplace=True)
    ranking_ativo = pd.merge(ranking_ativo_temp5,segmentos,how='left', left_on='ativo',right_on='ativo')    

    return ranking_ativo


# # ult_data = pa_long_ativo['data'].tail(1).to_string(index=False,header=False)
# ult_data = pa_long_ativo['data'].tail(1).to_string(index=False,header=False)
# ult_data = ult_data.strip()

# ranking_ativo_temp2 = pa_long_ativo[pa_long_ativo['data'] == ult_data]
# ranking_ativo_temp2 = pa_long_ativo[pa_long_ativo['data'] == '2021-02-12']
ranking_ativo = ranking_ativo_func(pa_long_ativo)

#####################################
## GERAR O RANKING DOS SEGMENTOS
##################################### 

def pa_segmentos_temp_func(segmentos,pa_long_ativo):
    """
    função do price action intermediário para segmentos

    Parameters
    ----------
    segmentos : dataframe
        tabela depara com a classificação de segmentos para cada ativo.
    pa_long_ativo : dataframe
        dataframe do price action para os ativos

    Returns
    -------
    retorna o price action temporário dos segmentos.

    """
    pa_segmentos_temp1 = pd.merge(segmentos,pa_long_ativo,how='left', left_on=['ativo'], right_on = ['ativo'] )
    pa_segmentos_temp1 = pa_segmentos_temp1[pa_segmentos_temp1['tipo']=='Adj Close']
    pa_segmentos_temp2 = pa_segmentos_temp1.groupby(['data','segmento'])['rentabilidade'].mean()
    pa_segmentos_temp2 = pd.DataFrame(pa_segmentos_temp2)
    pa_segmentos_temp2 = pa_segmentos_temp2.round(2)
    pa_segmentos_temp = pa_segmentos_temp2.reset_index()
    
    return pa_segmentos_temp

pa_segmentos_temp = pa_segmentos_temp_func(segmentos,pa_long_ativo)

def ranking_segmento_func(pa_long_ativo,pa_segmentos_temp):
    """
    retorna o ranking dos segmentos para o último dia de informação

    Parameters
    ----------
    pa_long_ativo : dataframe
        price action dos ativos
    pa_segmentos_temp : dataframe
        price action dos segmentos

    Returns
    -------
    retorna o ranking dos segmentos

    """
    ## classificar o ranking dos segmentos
    ult_data = pa_long_ativo['data'].tail(1).to_string(index=False,header=False)
    ult_data = ult_data.strip()
    ranking_segmento_temp1 = pa_segmentos_temp[pa_segmentos_temp['data'] == ult_data]
    ranking_segmento_temp1 = ranking_segmento_temp1.sort_values('rentabilidade', ascending = False)
    ranking_segmento = ranking_segmento_temp1.reset_index()
    ranking_segmento['ranking_segmento'] = ranking_segmento.index + 1
    ranking_segmento.rename(columns={'rentabilidade': 'retorno_ult_segmento'}, inplace=True)
    ranking_segmento = ranking_segmento.drop(columns=['index', 'data'])
    ranking_segmento = ranking_segmento.round(2)
    # pa_long_segmentos = pd.merge(pa_segmentos_temp, ranking_segmento, how='left', left_on='segmento', right_on='segmento')
    
    return ranking_segmento

ranking_segmento = ranking_segmento_func(pa_long_ativo,pa_segmentos_temp)

# pa_long_segmentos = pd.merge(pa_segmentos_temp, ranking_segmento, how='left', left_on='segmento', right_on='segmento')


#####################################
## GERAR TABELAO PRICE ACTION E DADOS AUXILIARES
##################################### 

def pa_long_func(segmentos,pa_long_ativo, ranking_ativo, ranking_segmento):
    """
    retorna o price action dos ativos juntamento com a coluna segmentos, ranking de ativos
    e ranking de segmentos

    Parameters
    ----------
    segmentos : dataframe
        dataframe de associação dos segmentos para os ativos
    pa_long_ativo : dataframe
        dataframe do price action dos ativos
    ranking_ativo : dataframe
        ranking dos ativos
    ranking_segmento : dataframe
        ranking dos segmentos

    Returns
    -------
    retorna o price action dos ativos

    """
    pa_long_temp1 = pd.merge(segmentos, pa_long_ativo, how='left', left_on=['ativo'], right_on = ['ativo'])
    pa_long_temp2 = pd.merge(pa_long_temp1,
                                      ranking_ativo, how='left', left_on=['ativo'], 
                                      right_on = ['ativo'] ) # join com o ranking de ativos

    pa_long_temp3 = pd.merge(pa_long_temp2, ranking_segmento, how='left', 
                                      left_on=['segmento_y'], right_on = ['segmento']) # join com o ranking de segmentos

    pa_long = pa_long_temp3.drop(columns=['segmento_y','segmento_x'])
    pa_long = pa_long.sort_values(['ativo','data'])
    pa_long = pa_long.dropna()

## fazer join para criar o tabelao com: data, ativo, segmento, rentabilidade_diaria, ranking_ativo, ranking_segmento

    pa_long_temp1 = pd.merge(segmentos, pa_long_ativo, how='left', left_on=['ativo'], right_on = ['ativo'])
    pa_long_temp2 = pd.merge(pa_long_temp1,
                                      ranking_ativo, how='left', left_on=['ativo'], 
                                      right_on = ['ativo'] ) # join com o ranking de ativos

    pa_long_temp3 = pd.merge(pa_long_temp2, ranking_segmento, how='left', 
                                      left_on=['segmento_y'], right_on = ['segmento']) # join com o ranking de segmentos

    pa_long = pa_long_temp3.drop(columns=['segmento_y','segmento_x'])
    pa_long = pa_long.sort_values(['ativo','data'])
    pa_long = pa_long.dropna()
    
    return pa_long

# pa_long = pa_long_func(segmentos,pa_long_ativo, ranking_ativo, ranking_segmento)

# inicio2 = '2021-01-15'
# fim2 = '2021-01-30'

# pa_long_ativo2 = pa_long_ativo_func(inicio2,fim2,prices_segmento_base)

# acoes_lista = pa_long['ativo'].unique()
# segmentos_lista = pa_long_segmentos['segmento'].unique() # lista dos segmentos

#####################################
## EXPORTAR DADOS
##################################### 

## exportar dados para o csv
# pa_long.to_csv(r'pa_long.csv', index = True, header=True, decimal=".")
# pa_long_segmentos.to_csv(r'pa_long_segmentos.csv', index = True, header=True, decimal=".")
# ranking_ativo.to_csv(r'ranking_ativo.csv', index = True, header=True, decimal=".")
# ranking_segmento.to_csv(r'ranking_segmento.csv', index = True, header=True, decimal=".")


