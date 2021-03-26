# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 13:41:29 2021

@author: Pc
"""


import pandas as pd

# from c_price_action_function_teste import pa_long_ativo_func
# from c_price_action_function_teste import ranking_ativo_func
# from c_price_action_function_teste import pa_segmentos_temp_func
# from c_price_action_function_teste import ranking_segmento_func
# from c_price_action_function_teste import pa_long_func
from d_price_holc_function_teste import prices_long_holc_ta
from d_price_holc_function_teste import prices_wide_holc_ta
import numpy as np

segmentos = pd.read_json("segmentos_eod - segmentos_eod.json")
prices_segmento_base = pd.read_json(r'prices_segmento_base.json')

# # ## função prices ta
# # ##################################### 
prices_long_holc = prices_long_holc_ta(segmentos,prices_segmento_base)
prices_wide_holc = prices_wide_holc_ta(segmentos,prices_long_holc)

# df_temp1 = prices_long_holc[(prices_long_holc['tipo']=='ppo_hist')& (prices_long_holc['ativo']=='MILS3')]
df_temp1 = prices_long_holc[(prices_long_holc['tipo']=='ppo_hist')& (prices_long_holc['data']>='2021-03-08')]
df_temp1['lag1'] = df_temp1.groupby('ativo')['valor'].shift()

df_temp1['change_trend'] = np.select([df_temp1['lag1']>0,df_temp1['valor']<=0], [df_temp1['lag1'],df_temp1['valor']])    
df_temp1.drop(df_temp1[df_temp1['change_trend']!=0].index,inplace=True)
df_temp1.drop(df_temp1[df_temp1['lag1'].isnull()].index,inplace=True)

df_temp1.sort_values(by=['segmento','data','ativo'],inplace=True)

df_temp2 = df_temp1[['data', 'ativo', 'segmento']]

df_temp2.to_csv(r'change_trend.csv')
# df.drop(df[df.score < 50].index, inplace=True)