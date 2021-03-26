

## import custom functions
from c_price_action_function_teste import pa_long_ativo_func
from c_price_action_function_teste import ranking_ativo_func
from c_price_action_function_teste import pa_segmentos_temp_func
from c_price_action_function_teste import ranking_segmento_func
from c_price_action_function_teste import pa_long_func
from d_price_holc_function_teste import prices_long_holc_ta
from d_price_holc_function_teste import prices_wide_holc_ta
from b_prices_function_atualizacao_teste import update_database

# import libraries
import pandas as pd
import cufflinks as cf
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from datetime import datetime as dt
from plotly.subplots import make_subplots
import datetime as dt 
from datetime import  timedelta, datetime
# import plotly.io as pio

cf.go_offline()

# #####################################
# ## import prices database>
# ##################################### 

# segmentos = pd.read_csv("segmentos_eod.csv")
# prices_segmento_base = pd.read_csv("prices_segmento.csv")
segmentos = pd.read_json("segmentos_eod - segmentos_eod.json")

prices_segmento_base = pd.read_json('prices_segmento_base.json')
prices_segmento_base = update_database(prices_segmento_base)
# prices_segmento_base = pd.read_json(r'prices_segmento_base.json')


# #####################################
# ## auxiliary data for global variables
# ##################################### 
prices_segmento_base_temp = pd.merge(prices_segmento_base,segmentos,how='left',left_on='ativo',right_on='ativo')
segmentos_lista2 = prices_segmento_base_temp['segmento_x'].unique()
acoes_lista = prices_segmento_base_temp['ativo'].unique()
segmentos_lista = prices_segmento_base_temp['segmento_x'].unique() # lista dos segmentos
fim_temp1 = prices_segmento_base_temp['data'].tail(1).iloc[0]
fim_temp2 = dt.datetime.strptime(fim_temp1, '%Y-%m-%d')
inicio_temp2 = fim_temp2 - timedelta(days=59)
inicio_temp = inicio_temp2.strftime('%Y-%m-%d')
fim_temp = fim_temp2.strftime('%Y-%m-%d')

pa_long_ativo = pa_long_ativo_func(inicio_temp,fim_temp,prices_segmento_base_temp)
ranking_ativo = ranking_ativo_func(pa_long_ativo)


pa_segmentos_temp = pa_segmentos_temp_func(segmentos,pa_long_ativo)
ranking_segmento = ranking_segmento_func(pa_long_ativo,pa_segmentos_temp)
segmentos_lista2 = ranking_segmento['segmento'].to_list()
pa_long_segmentos = pd.merge(pa_segmentos_temp, ranking_segmento, 
                              how='left', left_on='segmento', right_on='segmento')
pa_long = pa_long_func(segmentos,pa_long_ativo, ranking_ativo, ranking_segmento)

pa_long = pa_long.sort_values(by=['ranking_ativo'],ascending=True)
acoes_lista = pa_long['ativo'].unique()

# dt.datetime.strptime(ult_dt_prices_base, '%Y-%m-%d')
# # #####################################
# # ## prices long and wide
# # ##################################### 
prices_long_holc = prices_long_holc_ta(segmentos,prices_segmento_base)
prices_wide_holc = prices_wide_holc_ta(segmentos,prices_long_holc)

pa_wide_holc_indice = prices_wide_holc[prices_wide_holc['segmento']=='indice']
pa_wide_holc_ibov = prices_wide_holc[prices_wide_holc['ativo']=='IBOV']

## dados auxiliares para os indices
pa_long_indice = prices_long_holc[prices_long_holc['segmento']=='indice']
indice_lista = pa_long_indice['ativo'].unique()
segmentos_lista = prices_segmento_base_temp['segmento_x'].unique() # lista dos segmentos'

pa_long_ibov = prices_long_holc[(prices_long_holc['segmento']=='indice')&(prices_long_holc['ativo']=='IBOV')]
ult_data2 = prices_long_holc['data'].tail(1).iloc[0]


#####################################
## input de data p/ o price action
##################################### 
# inicio = '2021-01-11'
# fim = prices_segmento_base_temp['data'].tail(1).iloc[0]
# # fim = '2021-03-12'
# # #####################################
# # ## função price action
# # ##################################### 
# pa_long_ativo = pa_long_ativo_func(inicio,fim,prices_segmento_base)
# ranking_ativo = ranking_ativo_func(pa_long_ativo)
# pa_segmentos_temp = pa_segmentos_temp_func(segmentos,pa_long_ativo)
# ranking_segmento = ranking_segmento_func(pa_long_ativo,pa_segmentos_temp)
# pa_long_segmentos = pd.merge(pa_segmentos_temp, ranking_segmento, 
#                               how='left', left_on='segmento', right_on='segmento')
# pa_long = pa_long_func(segmentos,pa_long_ativo, ranking_ativo, ranking_segmento)

# pa_long = pa_long.sort_values(by=['ranking_ativo'],ascending=True)
# acoes_lista = pa_long['ativo'].unique()

# # segmentos_lista = prices_segmento_base_temp['segmento_x'].unique() # lista dos segmentos
# segmentos_lista = ranking_segmento['segmento'].unique()
# ## TESTE
# pio.renderers.default = 'browser'
# fig.show()


### Dash

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )

app.layout = dbc.Container([
        
            html.Div(id='df',
                     style={'display': 'none'},
                     # children = 'df'['ativo'].unique(),
                     ), # Div hidden para armazenar o price action da seleção

            html.Div(id='df2',style={'display': 'none'}), # Div hidden para armazenar o price action de segmentos da seleção
            
            dbc.Row(
            dbc.Col(html.H1("Painel Price Action" , className='text-center text-primary mb-4'), width=12)),
            
            
            dbc.Row([
                
            dbc.Col([
                    
            html.H2(children = 'Evolução do Bovespa',
                            style = {
                                'text-align': 'center',
                                'color':'#456FBV'
                                } 
                            ),            

                      dcc.DatePickerRange(
                       id='DatePickerRange_ind1',  # ID to be used for callback
                       end_date_placeholder_text="Return",  # text that appears when no end date chosen
                       with_portal=False,  # if True calendar will open in a full screen overlay portal
                       first_day_of_week=0,  # Display of calendar when open (0 = Sunday)
                       reopen_calendar_on_clear=True,
                       is_RTL=False,  # True or False for direction of calendar
                       clearable=True,  # whether or not the user can clear the dropdown
                       number_of_months_shown=1,  # number of months shown when calendar is open
                       # min_date_allowed=dt(2018, 1, 1),  # minimum date allowed on the DatePickerRange component
                       # max_date_allowed=dt(2020, 6, 20),  # maximum date allowed on the DatePickerRange component
                       # initial_visible_month=dt(2020, 5, 1),  # the month initially presented when the user opens the calendar
                       # start_date=dt.date(2020, 11, 3),
                        start_date=dt.date(2020, 11, 3),
                        # end_date=dt(2021, 2, 9).date(),
                        end_date = ult_data2,
                       display_format='MMM Do, YY',  # how selected dates are displayed in the DatePickerRange component.
                       month_format='MMMM, YYYY',  # how calendar headers are displayed when the calendar is opened.
                       minimum_nights=2,  # minimum number of days between start and end date
                       persistence=True,
                       persisted_props=['start_date'],
                       persistence_type='session',  # session, local, or memory. Default is 'local'
                       updatemode='singledate', # singledate or bothdates. Determines when callback is triggered
                       style={
                           # 'width': '200px', 
                              'margin-left': 100, 
                              # 'margin-top': 20, 
                              # 'display':'inline-block'
                              }                       
                       ) ,     

                       html.Br(),
                       # html.Br(),
                       # html.Br(),
                       
                       dcc.Graph(id='indice1',
                                  className='container', 
                                 # style={'maxWidth': '850px'}
                                ),                
                ], width={'size':4, 'offset':1, 'order':1},),


            dbc.Col([

            html.H2(children = 'Evolução de Outros Índices',
                            style = {
                                'text-align': 'center',
                                'color':'#456FBV'
                                } 
                            ),                            

                       dcc.DatePickerRange(
                        id='DatePickerRange_ind2',  # ID to be used for callback
                        end_date_placeholder_text="Return",  # text that appears when no end date chosen
                        with_portal=False,  # if True calendar will open in a full screen overlay portal
                        first_day_of_week=0,  # Display of calendar when open (0 = Sunday)
                        reopen_calendar_on_clear=True,
                        is_RTL=False,  # True or False for direction of calendar
                        clearable=True,  # whether or not the user can clear the dropdown
                        number_of_months_shown=1,  # number of months shown when calendar is open
                        # min_date_allowed=dt(2018, 1, 1),  # minimum date allowed on the DatePickerRange component
                        # max_date_allowed=dt(2020, 6, 20),  # maximum date allowed on the DatePickerRange component
                        # initial_visible_month=dt(2020, 5, 1),  # the month initially presented when the user opens the calendar
                        start_date=dt.date(2020, 11, 3),
                        # end_date=dt(2021, 2, 9).date(),
                        end_date = ult_data2,
                        display_format='MMM Do, YY',  # how selected dates are displayed in the DatePickerRange component.
                        month_format='MMMM, YYYY',  # how calendar headers are displayed when the calendar is opened.
                        minimum_nights=2,  # minimum number of days between start and end date
                        persistence=True,
                        persisted_props=['start_date'],
                        persistence_type='session',  # session, local, or memory. Default is 'local'
                        updatemode='singledate',  # singledate or bothdates. Determines when callback is triggered   
                        style={
                            # 'width': '200px', 
                               'margin-left': 100, 
                               # 'margin-top': 20, 
                               'display':'inline-block'
                               }
                        ) , 
                      

                   # html.Br(),                   

                       dcc.Dropdown(id='dropdown3', options=[  
                        {'label': i, 'value': i} for i in indice_lista ## list of unique segments
                        ],
                        value=indice_lista[0],
                        multi=False, placeholder='Filtrar por ...',
                       style={
                           # 'width': '200px', 
                              'margin-left': 50, 
                              # 'margin-top': 20, 
                              # 'display':'inline-block'
                              } 
                        ),
                                             
                        # ]),  
      
                       dcc.Graph(id='indice2',
                                  className='container', 
                                 # style={'maxWidth': '850px'}
                                ),            

                      ], width={'size':4, 'offset':1, 'order':1},),  
        
        
                    
        
        ], no_gutters=True, justify='start'),  # Fechamento da Row evolução do índice e retorno por segmentos
            


             html.H2(children = 'Datas para o Price Action',
                        style = {
                                'text-align': 'center',
                                'color':'#456FBV'
                                } 
                        ),
              html.Br(),

# DataRange do Price Action
            dcc.DatePickerRange(
            id='DatePickerRange1',  # ID to be used for callback
            end_date_placeholder_text="Return",  # text that appears when no end date chosen
            with_portal=False,  # if True calendar will open in a full screen overlay portal
            first_day_of_week=0,  # Display of calendar when open (0 = Sunday)
            reopen_calendar_on_clear=True,
            is_RTL=False,  # True or False for direction of calendar
            clearable=True,  # whether or not the user can clear the dropdown
            number_of_months_shown=1,  # number of months shown when calendar is open
            # min_date_allowed=dt(2018, 1, 1),  # minimum date allowed on the DatePickerRange component
            # max_date_allowed=dt(2020, 6, 20),  # maximum date allowed on the DatePickerRange component
            # initial_visible_month=dt(2020, 5, 1),  # the month initially presented when the user opens the calendar
            start_date=inicio_temp2,
            end_date = fim_temp2,
            display_format='MMM Do, YY',  # how selected dates are displayed in the DatePickerRange component.
            month_format='MMMM, YYYY',  # how calendar headers are displayed when the calendar is opened.
            minimum_nights=2,  # minimum number of days between start and end date
            persistence=True,
            persisted_props=['start_date'],
            persistence_type='session',  # session, local, or memory. Default is 'local'
            updatemode='singledate', # singledate or bothdates. Determines when callback is triggered
            style={
                    # 'width': '200px', 
                    'margin-left': 750, 
                    # 'margin-top': 20, 
                    # 'display':'inline-block'
                  }                       
                              ) ,     
    
            html.Br(),
            html.Br(),
            # html.Br(),
    
    dbc.Row([
        
        dbc.Col([
            
               html.H2(children = 'Retorno por segmentos',
                        style = {
                            'text-align': 'center',
                            'color':'#456FBV'
                            } 
                        ),
    
                dcc.Dropdown(id='dropdown-evolucao-segmento', 
                              options=[{'label': i, 'value': i} for i in segmentos_lista2 ## list of unique segments
                                      ],
                              value=segmentos_lista2[0],
                              multi=True, placeholder='Filtrar por ativo...',
                              style={
                            # 'width': '200px', 
                              'margin-left': 50, 
                              # 'margin-top': 20, 
                              # 'display':'inline-block'
                              } ), 
          
                dbc.Col(dcc.Graph(id='evolucao-segmento')),         
            
            ], width={'size':4, 'offset':1, 'order':1},  ),
             
        dbc.Col([
            
              html.H2(children = 'Ativos por Segmentos',
                        style = {
                                'text-align': 'center',
                                'color':'#456FBV'
                                } 
                        ),
            
              dcc.Dropdown(id='dropdown_ativos_segmentos', options=[  
                        {'label': i, 'value': i} for i in segmentos_lista2 ## list of unique segments
                        ],
                            value=segmentos_lista2[0],
                            multi=True, placeholder='Filtrar por segmentos...',
                            style={
                           # 'width': '200px', 
                              'margin-left': 50, 
                              # 'margin-top': 20, 
                              # 'display':'inline-block'
                              } ),
             
              dcc.Graph(id='retorno_ativos_segmentos'),  
            
            
            ] , width={'size':4, 'offset':1, 'order':1}, ),
        
        
        ],no_gutters=True, justify='start'),
        
      dbc.Row([
          
          dbc.Col([

                # Price Action: seleção de ativos

                html.H2(children = 'Seleção de ativos',
                        style = {
                            'text-align': 'center',
                            'color':'#456FBV'
                            } 
                        ),
    
                dcc.Dropdown(id='dropdown_selecao_ativos', 
                              options=[{'label': i, 'value': i} for i in acoes_lista ## list of unique segments
                                      ],
                              value=acoes_lista[0],
                              multi=True, placeholder='Filtrar por ativo...',
                              style={
                            # 'width': '200px', 
                              'margin-left': 50, 
                              # 'margin-top': 20, 
                              # 'display':'inline-block'
                              } ), 
          
                dbc.Col(dcc.Graph(id='retorno_selecao_ativos')),                    

        
               ], width={'size':4, 'offset':1, 'order':1},), 
                   # xs=12, sm=12, md=12, lg=5, xl=5            
                
                                         
            dbc.Col([

             html.H2(children = 'Evolução do retorno da volatilidade',
                        style = {
                                'text-align': 'center',
                                'color':'#456FBV'
                                } 
                        ),
      
             dcc.Dropdown(id='dropdown-retorno-volatilidade', options=[  
                        {'label': i, 'value': i} for i in acoes_lista ## list of unique segments
                        ],
                            value=acoes_lista[0],
                            multi=False, placeholder='Filtrar por ativo...',
                            style={
                            # 'width': '200px', 
                              'margin-left': 50, 
                              # 'margin-top': 20, 
                              # 'display':'inline-block'
                              } ), 
          
             dbc.Col(dcc.Graph(id='retorno-volatilidade')),
        
               ], width={'size':4, 'offset':1, 'order':1},),
          
          ] , no_gutters=True, justify='start'),

            html.Br(),
            html.Br(),
            
            dbc.Row([           

            dbc.Col([                
                
          html.H2(children = 'Evolução de preços',
                                 style = {
                               'margin-left': 100, 
                               # 'margin-top': 20, 
                               'display':'inline-block'
                                 },),      
           dcc.DatePickerRange(
                        id='DatePickerRange2',  # ID to be used for callback
                        end_date_placeholder_text="Return",  # text that appears when no end date chosen
                        with_portal=False,  # if True calendar will open in a full screen overlay portal
                        first_day_of_week=0,  # Display of calendar when open (0 = Sunday)
                        reopen_calendar_on_clear=True,
                        is_RTL=False,  # True or False for direction of calendar
                        clearable=True,  # whether or not the user can clear the dropdown
                        number_of_months_shown=1,  # number of months shown when calendar is open
                        # min_date_allowed=dt(2018, 1, 1),  # minimum date allowed on the DatePickerRange component
                        # max_date_allowed=dt(2020, 6, 20),  # maximum date allowed on the DatePickerRange component
                        # initial_visible_month=dt(2020, 5, 1),  # the month initially presented when the user opens the calendar
                        start_date=inicio_temp2,
                        end_date = fim_temp2,
                        display_format='MMM Do, YY',  # how selected dates are displayed in the DatePickerRange component.
                        month_format='MMMM, YYYY',  # how calendar headers are displayed when the calendar is opened.
                        minimum_nights=2,  # minimum number of days between start and end date
                        persistence=True,
                        persisted_props=['start_date'],
                        persistence_type='session',  # session, local, or memory. Default is 'local'
                        updatemode='singledate',  # singledate or bothdates. Determines when callback is triggered   
                        style={
                            # 'width': '200px', 
                               'margin-left': 100, 
                               # 'margin-top': 20, 
                               'display':'inline-block'
                               }
                        ) , 
                      
                       # ]),

                    html.Br(),
                   
                  # dbc.Row([
                       dcc.Dropdown(id='dropdown2', options=[  
                        {'label': i, 'value': i} for i in acoes_lista ## list of unique segments
                        ],
                        value=acoes_lista[0],
                        multi=False, placeholder='Filtrar por ...',
                       style={
                           # 'width': '200px', 
                              'margin-left': 40, 
                              # 'margin-top': 20, 
                              # 'display':'inline-block'
                              } 
                        ),
                                             
                        # ]),  
      
                       dcc.Graph(id='evolucao',
                                  className='container', 
                                 # style={'maxWidth': '850px'}
                                ),
             
                
            ], width={'size':4, 'offset':1, 'order':1},),

             ] , no_gutters=True, justify='start'),

        ] ,fluid=True) # fechamento do dbc.Container

## callback que retorna o price action de acordo com a seleção de datas
@app.callback(dash.dependencies.Output('df', 'children'),
              [dash.dependencies.Input('DatePickerRange1', 'start_date'),
               dash.dependencies.Input('DatePickerRange1', 'end_date')])



def price_action(inicio,fim):
    
    pa_long_ativo = pa_long_ativo_func(inicio,fim,prices_segmento_base)
    ranking_ativo = ranking_ativo_func(pa_long_ativo)
    pa_segmentos_temp = pa_segmentos_temp_func(segmentos,pa_long_ativo)
    ranking_segmento = ranking_segmento_func(pa_long_ativo,pa_segmentos_temp)
    pa_long_segmentos = pd.merge(pa_segmentos_temp, ranking_segmento, 
                              how='left', left_on='segmento', right_on='segmento')
    pa_long = pa_long_func(segmentos,pa_long_ativo, ranking_ativo, ranking_segmento)

    pa_long = pa_long.sort_values(by=['ranking_ativo'],ascending=True)
    
    return pa_long.to_json(date_format='iso', orient='split')


## callback que retorna o price action de acordo com a seleção de datas
@app.callback(dash.dependencies.Output('df2', 'children'),
              [dash.dependencies.Input('DatePickerRange1', 'start_date'),
               dash.dependencies.Input('DatePickerRange1', 'end_date')])

def price_action_segmentos(inicio,fim):
    
    pa_long_ativo = pa_long_ativo_func(inicio,fim,prices_segmento_base)
    ranking_ativo = ranking_ativo_func(pa_long_ativo)
    pa_segmentos_temp = pa_segmentos_temp_func(segmentos,pa_long_ativo)
    ranking_segmento = ranking_segmento_func(pa_long_ativo,pa_segmentos_temp)
    pa_long_segmentos = pd.merge(pa_segmentos_temp, ranking_segmento, 
                              how='left', left_on='segmento', right_on='segmento')
    
    
    return pa_long_segmentos.to_json(date_format='iso', orient='split')


# ## callback que retorna o price action de acordo com a seleção de datas
# @app.callback(dash.dependencies.Output('acoes_lista2', 'children'),
#               [dash.dependencies.Input('DatePickerRange1', 'start_date'),
#                dash.dependencies.Input('DatePickerRange1', 'end_date')])

# def acao_lista(inicio,fim):
    
#     pa_long_ativo = pa_long_ativo_func(inicio,fim,prices_segmento_base)
#     ranking_ativo = ranking_ativo_func(pa_long_ativo)
#     pa_segmentos_temp = pa_segmentos_temp_func(segmentos,pa_long_ativo)
#     ranking_segmento = ranking_segmento_func(pa_long_ativo,pa_segmentos_temp)
#     pa_long_segmentos = pd.merge(pa_segmentos_temp, ranking_segmento, 
#                               how='left', left_on='segmento', right_on='segmento')
#     pa_long = pa_long_func(segmentos,pa_long_ativo, ranking_ativo, ranking_segmento)

#     pa_long = pa_long.sort_values(by=['ranking_ativo'],ascending=True)
#     acoes_lista2 = pa_long['ativo'].unique()
    
#     return acoes_lista2.to_json(date_format='iso', orient='split')

# pa_long = pa_long

# Price Action: Seleção de Ativos por Segmentos
@app.callback(dash.dependencies.Output('retorno_ativos_segmentos', 'figure'),
              dash.dependencies.Input('dropdown_ativos_segmentos', 'value'),
              dash.dependencies.Input('df', 'children'))


def update_graph(value_segmento_ativos,df):
    if type(value_segmento_ativos)!=str:
        pa_long = pd.read_json(df, orient='split')
        pa_ativos_segmentos = pa_long[(pa_long['segmento'].isin(value_segmento_ativos))&(pa_long['tipo']=='Adj Close') ]
        pa_ativos_segmentos.sort_values(by=['data'],inplace=True)
    else:
        pa_long = pd.read_json(df, orient='split')
        pa_ativos_segmentos = pa_long[(pa_long['segmento']==value_segmento_ativos)&(pa_long['tipo']=='Adj Close')]
        pa_ativos_segmentos.sort_values(by=['data'],inplace=True)
    
    fig_pa_ativos_segmentos = px.line(pa_ativos_segmentos,x='data', y='rentabilidade', color='ativo', width=800, height=600 )
    
    fig_pa_ativos_segmentos.update_xaxes(
        type='category',
        tickangle = -45)
    
    
    return fig_pa_ativos_segmentos

## Evolução do retorno da volatilidade
@app.callback(dash.dependencies.Output('retorno-volatilidade','figure'),
              dash.dependencies.Input('dropdown-retorno-volatilidade', 'value'),
              dash.dependencies.Input('df', 'children'))

def update_graph(value_volatilidade,df):
    
    if type(value_volatilidade)!=str:
        pa_long = pd.read_json(df, orient='split')
        retorno_volatilidade_temp1 = pa_long[(pa_long['ativo'].isin(value_volatilidade)) ]
    else:
        pa_long = pd.read_json(df, orient='split')
        retorno_volatilidade_temp1 = pa_long[(pa_long['ativo']==value_volatilidade)]
    
    x = retorno_volatilidade_temp1[retorno_volatilidade_temp1['tipo']=='low adj'][['data','rentabilidade']]
    y = retorno_volatilidade_temp1[retorno_volatilidade_temp1['tipo']=='high adj'][['data','rentabilidade']]
    retorno_volatilidade = pd.merge(x,y,left_on="data",right_on="data")
    retorno_volatilidade.sort_values(by=['data'],inplace=True)
    
    fig_retorno_volatilidade = go.Figure()
  
    fig_retorno_volatilidade.add_trace(go.Scatter(x=retorno_volatilidade['data'], y=retorno_volatilidade['rentabilidade_x'],
                                                  fill=None,
                                                  mode='lines',
                                                  line_color='indigo',
                                                  ))
    
    fig_retorno_volatilidade.add_trace(go.Scatter(x=retorno_volatilidade['data'], y=retorno_volatilidade['rentabilidade_y'],
                                                  fill='tonexty', # fill area between trace0 and trace1
                                                  mode='lines', line_color='indigo'))

    fig_retorno_volatilidade.update_layout(
        dict(
                xaxis = dict(type="category", tickangle = -45),
                width=800, height=600)
            )
    
    return fig_retorno_volatilidade

## Price Action: Seleção de Ativos
@app.callback(dash.dependencies.Output('retorno_selecao_ativos', 'figure'),
              dash.dependencies.Input('dropdown_selecao_ativos', 'value'),
              dash.dependencies.Input('df', 'children'))

def update_graph(value_selecao_ativos,df):

    if type(value_selecao_ativos)!=str:
        pa_long = pd.read_json(df, orient='split')
        price_action_segmentos_ativos = pa_long[(pa_long['ativo'].isin(value_selecao_ativos))&(pa_long['tipo']=='Adj Close') ]
        price_action_segmentos_ativos.sort_values(by=['data'],inplace=True)
    else:
        pa_long = pd.read_json(df, orient='split')
        price_action_segmentos_ativos = pa_long[(pa_long['ativo']==value_selecao_ativos)&(pa_long['tipo']=='Adj Close')]
        price_action_segmentos_ativos.sort_values(by=['data'],inplace=True)
    
    fig_pa_segmentos_ativos = px.line(price_action_segmentos_ativos,x='data', y='rentabilidade', color='ativo', width=800, height=600 )
    # fig_pa_segmentos_ativos.sort_values(by=['data'],inplace=True)
    
    
    fig_pa_segmentos_ativos.update_xaxes(
        type='category',
        tickangle = -45)
    
    return fig_pa_segmentos_ativos

## Evolução do retorno dos segmentos
@app.callback(dash.dependencies.Output('evolucao-segmento', 'figure'),
              dash.dependencies.Input('dropdown-evolucao-segmento', 'value'),
               dash.dependencies.Input('df2', 'children'))

def update_graph(value_evolucao_segmento,df2):
    if type(value_evolucao_segmento)!=str:
        pa_long_segmentos = pd.read_json(df2, orient='split')
        evolucao_segmento = pa_long_segmentos[pa_long_segmentos['segmento'].isin(value_evolucao_segmento)]
        evolucao_segmento.sort_values(by=['data'],inplace=True)   
    else:
        pa_long_segmentos = pd.read_json(df2, orient='split')
        evolucao_segmento = pa_long_segmentos[pa_long_segmentos['segmento']==value_evolucao_segmento]
        evolucao_segmento.sort_values(by=['data'],inplace=True)   
        
    fig_evolucao_segmento = px.line(evolucao_segmento,x='data', y='rentabilidade', color='segmento', width=800, height=600 )
    
    fig_evolucao_segmento.update_xaxes(
        type='category',
        tickangle = -45)
    
    return fig_evolucao_segmento

## indices2
@app.callback(
              dash.dependencies.Output('indice2', 'figure'),
              [dash.dependencies.Input('dropdown3', 'value'),
               dash.dependencies.Input('DatePickerRange_ind2', 'start_date'),
               dash.dependencies.Input('DatePickerRange_ind2', 'end_date')]
              )

def update_graph(value2,start_date2, end_date2):
    

    prices_wide_holc_temp1 = pa_wide_holc_indice[(pa_wide_holc_indice['data']>=start_date2) &
                                                (pa_wide_holc_indice['data']<=end_date2)] 
    
    prices_wide_holc_temp1.sort_values(by=['data'],inplace=True)
    
    if type(value2)!=str:
        prices_wide_holc_temp2 = prices_wide_holc_temp1[prices_wide_holc_temp1['ativo'].isin(value2)]
    else:
        prices_wide_holc_temp2 = prices_wide_holc_temp1[prices_wide_holc_temp1['ativo']==value2]  

    fig = make_subplots(vertical_spacing = 0, rows=4, cols=1, row_heights=[0.8, 0.15, 0.15, 0.15])

    fig.add_trace(go.Candlestick(x=prices_wide_holc_temp2['data'],
                open=prices_wide_holc_temp2['open adj'],
                high=prices_wide_holc_temp2['high adj'],
                low=prices_wide_holc_temp2['low adj'],
                close=prices_wide_holc_temp2['Adj Close'],
                name='Preço Ajustado'))

    fig.add_trace(go.Scatter(x=prices_wide_holc_temp2['data'],
                y=prices_wide_holc_temp2['ema_7'],
                    mode='lines',
                    line = dict(color='purple', width=2),
                    name='EMA 7 dias'))

    fig.add_trace(go.Scatter(x=prices_wide_holc_temp2['data'],
                y=prices_wide_holc_temp2['ema_21'],
                    mode='lines',
                    line = dict(color='black', width=2),
                    name='EMA 21 dias'))

    fig.add_trace(go.Scatter(x=prices_wide_holc_temp2['data'], y = prices_wide_holc_temp2['ppo_line'], name='ppo line'), row=2, col=1)
    fig.add_trace(go.Scatter(x=prices_wide_holc_temp2['data'], y = prices_wide_holc_temp2['ppo_signal'], name='ppo signal'), row=2, col=1)
    fig.add_trace(go.Bar(x=prices_wide_holc_temp2['data'], y = prices_wide_holc_temp2['ppo_hist'], name='ppo hist'), row=3, col=1)
    fig.add_trace(go.Scatter(x=prices_wide_holc_temp2['data'], y = prices_wide_holc_temp2['rsi'], name='rsi'), row=4, col=1)
    fig.add_trace(go.Scatter(x=prices_wide_holc_temp2['data'], y = prices_wide_holc_temp2['low_rsi'], name='low rsi'), row=4, col=1)
    fig.add_trace(go.Scatter(x=prices_wide_holc_temp2['data'], y = prices_wide_holc_temp2['high_rsi'], name='high rsi',
                          fill='tonexty', mode='lines', line=dict(width=0.5, color='rgb(222, 196, 255)', dash='dash')), row=4, col=1)

    fig.update_layout(xaxis_rangeslider_visible=False,
                  xaxis=dict(zerolinecolor='black', showticklabels=False, type="category"),
                  xaxis2=dict(showticklabels=False, type="category"),
                  xaxis3=dict(showticklabels=False, type="category"),
                  width=800, height=600
                  )

    fig.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=False)
    
    return fig

## indices1
@app.callback(
              dash.dependencies.Output('indice1', 'figure'),
              [dash.dependencies.Input('DatePickerRange_ind1', 'start_date'),
               dash.dependencies.Input('DatePickerRange_ind1', 'end_date')]
              )

def update_graph(start_date, end_date):
    

    prices_wide_holc_ibov_fig = pa_wide_holc_ibov[(pa_wide_holc_ibov['data']>=start_date) &
                                                (pa_wide_holc_ibov['data']<=end_date)]
    prices_wide_holc_ibov_fig.sort_values(by=['data'],ascending=True)     

    fig = make_subplots(vertical_spacing = 0, rows=4, cols=1, row_heights=[0.8, 0.15, 0.15, 0.15])

    fig.add_trace(go.Candlestick(x=prices_wide_holc_ibov_fig['data'],
                open=prices_wide_holc_ibov_fig['open adj'],
                high=prices_wide_holc_ibov_fig['high adj'],
                low=prices_wide_holc_ibov_fig['low adj'],
                close=prices_wide_holc_ibov_fig['Adj Close'],
                name='Preço Ajustado'))

    fig.add_trace(go.Scatter(x=prices_wide_holc_ibov_fig['data'],
                y=prices_wide_holc_ibov_fig['ema_7'],
                    mode='lines',
                    line = dict(color='purple', width=2),
                    name='EMA 7 dias'))

    fig.add_trace(go.Scatter(x=prices_wide_holc_ibov_fig['data'],
                y=prices_wide_holc_ibov_fig['ema_21'],
                    mode='lines',
                    line = dict(color='black', width=2),
                    name='EMA 21 dias'))

    fig.add_trace(go.Scatter(x=prices_wide_holc_ibov_fig['data'], y = prices_wide_holc_ibov_fig['ppo_line'], name='ppo line'), row=2, col=1)
    fig.add_trace(go.Scatter(x=prices_wide_holc_ibov_fig['data'], y = prices_wide_holc_ibov_fig['ppo_signal'], name='ppo signal'), row=2, col=1)
    fig.add_trace(go.Bar(x=prices_wide_holc_ibov_fig['data'], y = prices_wide_holc_ibov_fig['ppo_hist'], name='ppo hist'), row=3, col=1)
    fig.add_trace(go.Scatter(x=prices_wide_holc_ibov_fig['data'], y = prices_wide_holc_ibov_fig['rsi'], name='rsi'), row=4, col=1)
    fig.add_trace(go.Scatter(x=prices_wide_holc_ibov_fig['data'], y = prices_wide_holc_ibov_fig['low_rsi'], name='low rsi'), row=4, col=1)
    fig.add_trace(go.Scatter(x=prices_wide_holc_ibov_fig['data'], y = prices_wide_holc_ibov_fig['high_rsi'], name='high rsi',
                          fill='tonexty', mode='lines', line=dict(width=0.5, color='rgb(222, 196, 255)', dash='dash')), row=4, col=1)

    fig.update_layout(xaxis_rangeslider_visible=False,
                  xaxis=dict(zerolinecolor='black', showticklabels=False, type="category"),
                  xaxis2=dict(showticklabels=False, type="category"),
                  xaxis3=dict(showticklabels=False, type="category"),
                  width=800, height=600
                  )

    fig.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=False)
    
    return fig

## Evolução de preço por ativo
@app.callback(
              dash.dependencies.Output('evolucao', 'figure'),
              [dash.dependencies.Input('dropdown2', 'value'),
               dash.dependencies.Input('DatePickerRange2', 'start_date'),
               dash.dependencies.Input('DatePickerRange2', 'end_date')]
              )

def update_graph(value2,start_date2, end_date2):

    prices_wide_holc_temp1 = prices_wide_holc[(prices_wide_holc['data']>=start_date2) &
                                                (prices_wide_holc['data']<=end_date2)]

    prices_wide_holc_temp1.sort_values(by=['data'],inplace=True)    
    
    if type(value2)!=str:
        prices_wide_holc_temp2 = prices_wide_holc_temp1[prices_wide_holc_temp1['ativo'].isin(value2)]
    else:
        prices_wide_holc_temp2 = prices_wide_holc_temp1[prices_wide_holc_temp1['ativo']==value2]  

    fig = make_subplots(vertical_spacing = 0, rows=4, cols=1, row_heights=[0.8, 0.15, 0.15, 0.15])

    fig.add_trace(go.Candlestick(x=prices_wide_holc_temp2['data'],
                open=prices_wide_holc_temp2['open adj'],
                high=prices_wide_holc_temp2['high adj'],
                low=prices_wide_holc_temp2['low adj'],
                close=prices_wide_holc_temp2['Adj Close'],
                name='Preço Ajustado'))

    fig.add_trace(go.Scatter(x=prices_wide_holc_temp2['data'],
                y=prices_wide_holc_temp2['ema_7'],
                    mode='lines',
                    line = dict(color='purple', width=2),
                    name='EMA 7 dias'))

    fig.add_trace(go.Scatter(x=prices_wide_holc_temp2['data'],
                y=prices_wide_holc_temp2['ema_21'],
                    mode='lines',
                    line = dict(color='black', width=2),
                    name='EMA 21 dias'))

    fig.add_trace(go.Scatter(x=prices_wide_holc_temp2['data'], y = prices_wide_holc_temp2['ppo_line'], name='ppo line'), row=2, col=1)
    fig.add_trace(go.Scatter(x=prices_wide_holc_temp2['data'], y = prices_wide_holc_temp2['ppo_signal'], name='ppo signal'), row=2, col=1)
    fig.add_trace(go.Bar(x=prices_wide_holc_temp2['data'], y = prices_wide_holc_temp2['ppo_hist'], name='ppo hist'), row=3, col=1)
    fig.add_trace(go.Scatter(x=prices_wide_holc_temp2['data'], y = prices_wide_holc_temp2['rsi'], name='rsi'), row=4, col=1)
    fig.add_trace(go.Scatter(x=prices_wide_holc_temp2['data'], y = prices_wide_holc_temp2['low_rsi'], name='low rsi'), row=4, col=1)
    fig.add_trace(go.Scatter(x=prices_wide_holc_temp2['data'], y = prices_wide_holc_temp2['high_rsi'], name='high rsi',
                          fill='tonexty', mode='lines', line=dict(width=0.5, color='rgb(222, 196, 255)', dash='dash')), row=4, col=1)

    fig.update_layout(xaxis_rangeslider_visible=False,
                  xaxis=dict(zerolinecolor='black', showticklabels=False, type="category"),
                  xaxis2=dict(showticklabels=False, type="category"),
                  xaxis3=dict(showticklabels=False, type="category"),
                  width=1200, height=800
                  )

    fig.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=False)
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=False, dev_tools_ui=False, port=8054)

