
import pandas as pd
import ta

# pegar a classificação por segmento

## PEGAR OS PREÇOS DOS ATIVOS

segmentos = pd.read_json("segmentos_eod - segmentos_eod.json")
prices_holc = pd.read_json(r'prices_segmento_base.json')

def prices_long_holc_ta(segmentos,prices_holc):
    """
    retorna o dataframe de prices long com os indicadores tecnicos

    Parameters
    ----------
    prices_holc : DataFrame
        dataframe long de preços. Colunas: data, ativo, preços HOLC e Volume

    Returns
    -------
    retorna o dataframe de prices long com os indicadores tecnicos

    """

    if 'segmento' in prices_holc.columns:
        print("a coluna segmento existe no df prices_segmento_base")
        prices_holc.drop(columns={'segmento'},inplace=True)
    else:
        print("a coluna segmento NÃO existe no df prices_segmento_base")

    ##gerar indicadores tecnicos
    prices_holc['ema_21'] = ta.trend.ema_indicator(close=prices_holc["Adj Close"],window=21,fillna=False) # média móvel exponencial de 21 dias
    prices_holc['ema_7'] = ta.trend.ema_indicator(close=prices_holc["Adj Close"],window=7,fillna=False) # média móvel exponencial de 21 dias
    prices_holc['ppo_line'] = ta.momentum.ppo(close =  prices_holc["Adj Close"], window_slow = 26, 
                                          window_fast = 12, fillna = True)
    prices_holc['ppo_hist'] = ta.momentum.ppo_hist(close =  prices_holc["Adj Close"], window_slow = 26, 
                                       window_sign= 9  , window_fast = 12, fillna = True)
    prices_holc['ppo_signal'] = ta.momentum.ppo_signal(close =  prices_holc["Adj Close"], window_slow = 26, 
                                       window_sign= 9  , window_fast = 12, fillna = True)

    prices_holc['pvo'] = ta.momentum.pvo(volume =  prices_holc["Volume"], window_slow = 26,
                                          window_sign= 9  ,   window_fast = 12, fillna = True)

    prices_holc['rsi'] = ta.momentum.rsi(close =  prices_holc["Adj Close"], window=14,fillna=True)
    prices_holc['low_rsi'] = 30
    prices_holc['high_rsi'] = 70
    ## gerar prices no formato long
    prices_long_holc = prices_holc.melt(id_vars=['data','ativo'], var_name='tipo', value_name='valor')
    prices_long_holc = pd.merge(prices_long_holc,segmentos,how='left',left_on='ativo',right_on='ativo')

    return prices_long_holc
    
# prices_long_holc = prices_long_holc_ta(segmentos,prices_holc)

def prices_wide_holc_ta(segmentos,prices_long_holc):
    """retorna o prices holc com os indicadores tecnicos no formato wide
    
    Parameters
    ----------
    :param segmentos: segmentos dos ativos 
    :prices_long_loc DataFrame: dataframe dos prices holc no formato long

    """
    prices_wide_holc = prices_long_holc.pivot_table(index=["data","ativo"],columns='tipo',values='valor').reset_index()
    prices_wide_holc = prices_wide_holc.sort_values('data')
    prices_wide_holc = pd.merge(prices_wide_holc,segmentos,how='left',left_on='ativo',right_on='ativo')
    
    return prices_wide_holc 

# prices_wide_holc = prices_wide_holc_ta(segmentos,prices_long_holc)
