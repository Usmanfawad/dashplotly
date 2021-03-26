
##############################################################################
#######################bibliotecas
##############################################################################

import pandas as pd
import numpy as np
# from eod_historical_data import (get_api_key,
#                                  get_eod_data,
#                                  get_dividends,
#                                  get_exchange_symbols,
#                                  get_exchanges, get_currencies, get_indexes)

import datetime as dt 
import requests_cache
# from io import StringIO
import requests
import io
# import yfinance as yf
from datetime import  timedelta, datetime

##############################################################################
################update database
##############################################################################
def update_database(prices_segmento_base):
    """ update prices database
    

    Parameters
    ----------
    prices_segmento_base : dataframe
        prices dataframe

    Returns
    -------
    return the updated prices dataframe

    """
    ##Cache session (to avoid too much data consumption)
    expire_after = dt.timedelta(days=1)
    session = requests_cache.CachedSession(cache_name='cache', backend='sqlite',
                                        expire_after=expire_after)
    ## read last prices dataframe
    prices_segmento_base = pd.read_json('prices_segmento_base.json')
    prices_segmento_base = prices_segmento_base[["data", "ativo", "segmento", "open adj", "low adj",
       "high adj", "Adj Close", "Volume"]]
    prices_segmento_base = prices_segmento_base[prices_segmento_base['data']<='2021-03-22']
    ## get last day
    ult_dt_prices_base = prices_segmento_base['data'].tail(1).iloc[0] # pega a última data do preço base
    inicio_new_prices = dt.datetime.strptime(ult_dt_prices_base, '%Y-%m-%d') + timedelta(days=1) # pega o próximo dia do último dia
    hoje = dt.datetime.today() # data mais recente
    # get a list of days
    sdate = dt.datetime(2020,1,1)   # start date
    edate = dt.datetime(2030,12,31)   # end date
    date_range = pd.date_range(sdate,edate-timedelta(days=1),freq='d').to_frame()
    datas_df_new = date_range[(date_range.iloc[:,0]>=inicio_new_prices)&(date_range.iloc[:,0]<=hoje)]
    datas_new = datas_df_new.iloc[:,0].to_list()
    ## check if there is data to be update
    if len(datas_df_new.iloc[:,0])==0:
        print("não há dados para ser atualizado")
    else:
        print("executar o loop")
    # loop to get new prices
        prices_new = []
        for i in range(len(datas_new)):
            url="https://eodhistoricaldata.com/api/eod-bulk-last-day/SA?api_token=602ee71c4be599.37805282&date={}" .format(datas_new[i])
            r = session.get(url)
            s = requests.get(url).content
            df_temp = pd.read_csv(io.StringIO(s.decode('utf-8')))
            df_temp = df_temp[df_temp.Open.notnull()]
            prices_new.append(df_temp)

        prices_new = pd.concat(prices_new)

    ## tratamento de dado para pegar o HOL ajustado ao Adjusted Close
        prices_new = prices_new.set_index('Date')
        prices_new.index = pd.to_datetime(prices_new.index)

        def adjust(date, Close, Adjusted_close, in_col, rounding=4):
            '''
            If using forex or Crypto - Change the rounding accordingly!
            '''
            try:
                factor = Adjusted_close / Close
                return round(in_col * factor, rounding)
            except ZeroDivisionError:
                print('WARNING: DIRTY DATA >> {} Close: {} | Adj Close {} | in_col: {}'.format(date, Close, Adjusted_close, in_col))
                return 0
        
        prices_new['open adj'] = np.vectorize(adjust)(prices_new.index.date, prices_new['Close'],\
                                                    prices_new['Adjusted_close'], prices_new['Open'])
    
        prices_new['high adj'] = np.vectorize(adjust)(prices_new.index.date, prices_new['Close'],\
                                                    prices_new['Adjusted_close'], prices_new['High'])

        prices_new['low adj'] = np.vectorize(adjust)(prices_new.index.date, prices_new['Close'],\
                                                    prices_new['Adjusted_close'], prices_new['Low']) 

        prices_new = prices_new.sort_values(by=['Code','Date']).reset_index()
        prices_new.drop(columns={'Ex', 'Open', 'High', 'Low', 'Close'},inplace=True)
        prices_new = prices_new[['Date', 'Code','open adj', 'low adj','high adj', 'Adjusted_close','Volume']]

        prices_new = prices_new.rename(columns={'Date':'data', 'Adjusted_close':'Adj Close' })

        ## merge do prices_new com os segmentos
        segmentos = pd.read_json("segmentos_eod - segmentos_eod.json")
        prices_segmento_new = prices_new.merge(segmentos,how='left', left_on='Code',right_on='ativo')
        prices_segmento_new = prices_segmento_new[prices_segmento_new['segmento'].notnull()]
        prices_segmento_new.drop(columns={'Code'},inplace=True)
        prices_segmento_new = prices_segmento_new[['data','ativo','segmento','open adj', 'low adj', 'high adj', 'Adj Close','Volume']]
        prices_segmento_new['data']= prices_segmento_new['data'].dt.strftime('%Y-%m-%d')
        # append do prices_segmento com prices segmentos new
        prices_segmento_base = prices_segmento_base.append(prices_segmento_new)
        prices_segmento_base = prices_segmento_base.sort_values(by=['ativo','data'])
        # salva o df de preço base atualizado
        prices_segmento_base.reset_index(inplace=True)
        prices_segmento_base = prices_segmento_base[["data", "ativo", "segmento", "open adj", "low adj",
       "high adj", "Adj Close", "Volume"]]
        prices_segmento_base.to_json(r'prices_segmento_base.json')
        return prices_segmento_base        

# prices_segmento_base = pd.read_json('prices_segmento_base.json')

# prices_segmento_base = update_database(prices_segmento_base)
    
# ##############################################################################
# ################Cache session (to avoid too much data consumption)
# ##############################################################################

# expire_after = dt.timedelta(days=1)
# session = requests_cache.CachedSession(cache_name='cache', backend='sqlite',
#                                         expire_after=expire_after)

# ##############################################################################
# ###################ler o df de preços base
# ##############################################################################
# ## le o price_segmento
# #segmentos = pd.read_json("segmentos_eod - segmentos_eod.json")
# # prices_segmento_base = pd.read_csv('prices_segmento_base.csv', index_col=0).reset_index()
# prices_segmento_base = pd.read_json('prices_segmento_base.json')
# prices_segmento_base = prices_segmento_base[["data", "ativo", "segmento", "open adj", "low adj",
#        "high adj", "Adj Close", "Volume"]]
# prices_segmento_base = prices_segmento_base[prices_segmento_base['data']<='2021-03-18']


# # verificar a ultima data com dados
# ult_dt_prices_base = prices_segmento_base['data'].tail(1).iloc[0] # pega a última data do preço base
# inicio_new_prices = dt.datetime.strptime(ult_dt_prices_base, '%Y-%m-%d') + timedelta(days=1) # pega o próximo dia do último dia
# hoje = dt.datetime.today() # data mais recente
# # hoje = '2021-03-10'

# ##############################################################################
# ##################pegar os preços mais recentes
# ##############################################################################
# # pega a listad das novas datas
# sdate = dt.datetime(2020,1,1)   # start date
# edate = dt.datetime(2030,12,31)   # end date

# date_range = pd.date_range(sdate,edate-timedelta(days=1),freq='d').to_frame()

# datas_df_new = date_range[(date_range.iloc[:,0]>=inicio_new_prices)&(date_range.iloc[:,0]<=hoje)]

# datas_new = datas_df_new.iloc[:,0].to_list()

# ## checa se há dados a serem atualizados
# if len(datas_df_new.iloc[:,0])==0:
#     print("não há dados para ser atualizado")
# else:
#     print("executar o loop")
# # loop para pegar os prices new do eod
#     prices_new = []
#     for i in range(len(datas_new)):
#         url="https://eodhistoricaldata.com/api/eod-bulk-last-day/SA?api_token=602ee71c4be599.37805282&date={}" .format(datas_new[i])
#         r = session.get(url)
#         s = requests.get(url).content
#         df_temp = pd.read_csv(io.StringIO(s.decode('utf-8')))
#         df_temp = df_temp[df_temp.Open.notnull()]
#         prices_new.append(df_temp)

#     prices_new = pd.concat(prices_new)

# ## tratamento de dado para pegar o HOL ajustado ao Adjusted Close
#     prices_new = prices_new.set_index('Date')
#     prices_new.index = pd.to_datetime(prices_new.index)

#     def adjust(date, Close, Adjusted_close, in_col, rounding=4):
#         '''
#         If using forex or Crypto - Change the rounding accordingly!
#         '''
#         try:
#             factor = Adjusted_close / Close
#             return round(in_col * factor, rounding)
#         except ZeroDivisionError:
#             print('WARNING: DIRTY DATA >> {} Close: {} | Adj Close {} | in_col: {}'.format(date, Close, Adjusted_close, in_col))
#             return 0
        
#     prices_new['open adj'] = np.vectorize(adjust)(prices_new.index.date, prices_new['Close'],\
#                                                     prices_new['Adjusted_close'], prices_new['Open'])
    
#     prices_new['high adj'] = np.vectorize(adjust)(prices_new.index.date, prices_new['Close'],\
#                                                     prices_new['Adjusted_close'], prices_new['High'])

#     prices_new['low adj'] = np.vectorize(adjust)(prices_new.index.date, prices_new['Close'],\
#                                                     prices_new['Adjusted_close'], prices_new['Low']) 

#     prices_new = prices_new.sort_values(by=['Code','Date']).reset_index()
#     prices_new.drop(columns={'Ex', 'Open', 'High', 'Low', 'Close'},inplace=True)
#     prices_new = prices_new[['Date', 'Code','open adj', 'low adj','high adj', 'Adjusted_close','Volume']]

#     prices_new = prices_new.rename(columns={'Date':'data', 'Adjusted_close':'Adj Close' })

# ## merge do prices_new com os segmentos
#     segmentos = pd.read_json("segmentos_eod - segmentos_eod.json")
#     prices_segmento_new = prices_new.merge(segmentos,how='left', left_on='Code',right_on='ativo')
#     prices_segmento_new = prices_segmento_new[prices_segmento_new['segmento'].notnull()]
#     prices_segmento_new.drop(columns={'Code'},inplace=True)
#     prices_segmento_new = prices_segmento_new[['data','ativo','segmento','open adj', 'low adj', 'high adj', 'Adj Close','Volume']]
#     prices_segmento_new['data']= prices_segmento_new['data'].dt.strftime('%Y-%m-%d')
# # append do prices_segmento com prices segmentos new
#     prices_segmento_base = prices_segmento_base.append(prices_segmento_new)
#     prices_segmento_base = prices_segmento_base.sort_values(by=['ativo','data'])
# # salva o df de preço base atualizado
#     prices_segmento_base.reset_index(inplace=True)
#     prices_segmento_base = prices_segmento_base[["data", "ativo", "segmento", "open adj", "low adj",
#        "high adj", "Adj Close", "Volume"]]
#     prices_segmento_base.to_json(r'prices_segmento_base.json')
    
# # prices_segmento_base_temp1 = pd.read_csv(r'prices_segmento_base.csv')

# # prices_segmento_base_temp1.to_json('prices_segmento_base_temp1.json')

# # prices_segmento_base_temp2 = pd.read_json("prices_segmento_base_temp1.json")

