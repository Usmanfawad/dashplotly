
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
import yfinance as yf
# from datetime import  timedelta, datetime


##############################################################################
################Cache session (to avoid too much data consumption)
##############################################################################

expire_after = dt.timedelta(days=1)
session = requests_cache.CachedSession(cache_name='cache', backend='sqlite',
                                        expire_after=expire_after)

# verificar a ultima data com dados
inicio = '2020-08-27'
fim = '2020-08-31'

##############################################################################
##################pega os preços mais recentes
##############################################################################
# pega a listad das novas datas
prices = yf.download(tickers="MGLU3.SA", start=inicio,end=fim, 
                            rounding=True)[['Open', 'High','Low','Adj Close', 'Volume']].reset_index()

datas = pd.DataFrame(prices['Date'])
datas_lista = datas['Date'].to_list()

# loop para pegar os prices new do eod
prices = []
for i in range(len(datas_lista)):
    url="https://eodhistoricaldata.com/api/eod-bulk-last-day/SA?api_token=602ee71c4be599.37805282&date={}" .format(datas_lista[i])
    r = session.get(url)
    s = requests.get(url).content
    df_temp = pd.read_csv(io.StringIO(s.decode('utf-8')))
    df_temp = df_temp[df_temp.Open.notnull()]
    prices.append(df_temp)

prices = pd.concat(prices)

## tratamento de dado para pegar o HOL ajustado ao Adjusted Close
prices = prices.set_index('Date')
prices.index = pd.to_datetime(prices.index)

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
        
prices['open adj'] = np.vectorize(adjust)(prices.index.date, prices['Close'],\
                                                    prices['Adjusted_close'], prices['Open'])
    
prices['high adj'] = np.vectorize(adjust)(prices.index.date, prices['Close'],\
                                                    prices['Adjusted_close'], prices['High'])

prices['low adj'] = np.vectorize(adjust)(prices.index.date, prices['Close'],\
                                                    prices['Adjusted_close'], prices['Low']) 


    
prices = prices.sort_values(by=['Code','Date']).reset_index()
prices.drop(columns={'Ex', 'Open', 'High', 'Low', 'Close'},inplace=True)
prices = prices.rename(columns={'Date': 'data', 'Adjusted_close':'Adj Close' })
prices = prices[['data', 'Code','open adj', 'low adj','high adj', 'Adj Close','Volume']]

## merge do prices_new com os segmentos
segmentos = pd.read_json("segmentos_eod - segmentos_eod.json")
prices_segmento_base = prices.merge(segmentos,how='left', left_on='Code',right_on='ticker')
prices_segmento_base = prices_segmento_base[prices_segmento_base['segmento'].notnull()]
prices_segmento_base.drop(columns={'Code'},inplace=True)
prices_segmento_base = prices_segmento_base[['data','ticker','segmento','open adj', 'low adj', 'high adj', 'Adj Close','Volume']]
prices_segmento_base['data']= prices_segmento_base['data'].dt.strftime('%Y-%m-%d')

# teste_temp1 = prices_segmento[prices_segmento['ticker']=='WEGE3']

## salvar prices segmentos
# prices_segmento_base = pd.read_csv(r'prices_segmento.csv')
# prices_segmento = prices_segmento.rename(columns={'Date':'data'})
# prices_segmento_base.to_csv(r'prices_segmento_base.csv', index = False, header=True, decimal=".")
prices_segmento_base.reset_index(inplace=True)
prices_segmento_base = prices_segmento_base[["data", "ticker", "segmento", "open adj", "low adj",
       "high adj", "Adj Close", "Volume"]]
prices_segmento_base.to_json(r'prices_segmento_base.json')
# prices_segmento_base.to_csv(r'prices_segmento_base.csv', index = False, header=True, decimal=".")

# prices_segmento_base = pd.read_json(r'prices_segmento_base.json')
# prices_segmento_base.rename(columns={'ticker':'ativo'},inplace=True)
