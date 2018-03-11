# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 00:48:55 2018

@author: DMota and Koch
"""



##Módulos
import pandas as pd
from matplotlib import pyplot as plt
import datetime as dt
from math import radians, cos, sin, asin, sqrt
import numpy as np


##Entrada de dados
file_x = '000'

data = pd.read_csv('C:\\Users\\Gabriel\\Documents\\GitHub\\Database\\TransUrb\\' + file_x + '.csv',      
                   names = ['Dia','Hora','Linha',u'Veículo','Latitude','Longitude'],\
                   dtype = {'Latitude':np.float64, 'Longitude':np.float64,\
                            'Linha':np.str, u'Veículo':np.str})
#data = pd.read_csv('C:\\Users\\danielmota\\Documents\\GitHub\\Database\\TransUrb\\' + file_x + '.csv',      
#                   names = ['Dia','Hora','Linha',u'Veículo','Latitude','Longitude'],\
#                   dtype = {'Latitude':np.float64, 'Longitude':np.float64,\
#                            'Linha':np.str, u'Veículo':np.str})

##Tirar duplicadas
df1 = data.drop_duplicates()

'''---------'''

##Criar dataframe de 00:00 até 23:59
lst_time_pattern = []
for i in range(24):
    for j in range(60):
        lst_time_pattern.append(dt.datetime(1900, 1, 1, i, j).strftime('%H:%M'))
df_time = pd.DataFrame(lst_time_pattern)
df_time.columns = ['Hora']
df_time = df_time.set_index('Hora')
del lst_time_pattern

'''---------'''

##Intervalo de tempo em min
interval_x = 30

##Criar lista de 00:00 até 23:59 de 10 em 10min
m = 0
lst_time_pattern10 = []
for k in range(interval_x):
    lst_time_pattern10.append(dt.datetime(1900, 1, 1, 0, 0).strftime('%H:%M'))
for i in range(24):
    for j in range(60):
        m += 1
        if m == interval_x+1:
            for k in range(interval_x):
                lst_time_pattern10.append(dt.datetime(1900, 1, 1, i, j).strftime('%H:%M'))
            m=1

'''---------'''


def haversine(lon1, lat1, lon2, lat2):        
    '''Função haversine'''
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371
    return c * r


def interp(df4, limit):
    '''Função interpolar os NaN's certos'''
    d = df4.notna().rolling(limit + 1).agg(any).fillna(1)
    d = pd.concat({
            i: d.shift(-i).fillna(1)
            for i in range(limit + 1)
            }).prod(level=1)

    return df4.interpolate(limit=limit).where(d.astype(bool))

'''---------'''

##Filtros
line_a = ''
line_b = ''
vehicle = '11138' 

'''---------'''

##Filtrando por linha
#df2 = df1[(df1['Linha'] == line_a) | (df1['Linha'] == line_b)]
df2 = df1[(df1[u'Veículo'] == vehicle)]
#del df1
##Contagem de NaN's
dictx = {}

##Iterar todos os veículos nas linhas
for (vehicle, df_filtred) in df2.groupby(u'Veículo'):
      
    ##Tratando os dados
    df_filtred = df_filtred.reset_index().groupby(['Linha', u'Veículo',\
                                       'Hora']).mean().reset_index(level=-1)
    df_filtred = df_filtred.reset_index(level=['Linha',u'Veículo'])
    df_filtred = df_filtred.set_index(['Hora'])
    df3 = df_time.join(df_filtred)
    df3 = df3[~df3.index.duplicated(keep='first')]
    dictx[vehicle] = df3['Linha'].notna().sum()
    
    ##Criando Dataframe para calcular intervalo de 10 min
    df4 = df3.assign(Intervalo=lst_time_pattern10)
    del df4['index']
    
    '''---------'''

    ##Arrumando os NaN's
#    is_duplicate = df4.duplicated(subset=['Latitude','Longitude'])
#    df4_1 = df4.Latitude.where(~is_duplicate)
#    df4_2 = df4.Longitude.where(~is_duplicate)
#    df4 = df4.drop(columns=['Latitude','Longitude'])
#    df4 = pd.concat([df4, df4_1,df4_2], axis=1)
    df4.pipe(interp, 5)
    df4 = df4.fillna(value = 0)


    '''---------'''
    
    ##Calcular a distancia e a velocidade
    lst_speed_temp=[]
    lst_speed_temp.append(0.0)
    for i in range(len(df4)-1):
        lat1 = df4.iat[i,2]
        lon1 = df4.iat[i,3]
        lat2 = df4.iat[(i+1),2]
        lon2 = df4.iat[(i+1),3]
        speed_temp_x = 3.6*((haversine(lon1, lat1, lon2, lat2))*1000)/60
        if speed_temp_x < 80:     
            lst_speed_temp.append(speed_temp_x)
        else:
            lst_speed_temp.append(0.0)

    ##Deletando dados obsoletos (DDO)
    del lat1, lat2, lon1, lon2, speed_temp_x
    df4 = df4.assign(Velocidade=lst_speed_temp)

    '''---------'''
    
#    ##Gráfico de posição
#    ##Filtro para tirar a posição 0,0
#    df_scatter = df4[(df4['Latitude'] != 0) | (df4['Longitude'] != 0)]
#    fig, ax = plt.subplots()
#    colors = {line_a:'red', line_b:'blue'}
#    ax.scatter(df_scatter['Latitude'],df_scatter['Longitude'],\
#               c=df_scatter['Linha'].apply(lambda x: colors[x]),\
#               s=1)
#    plt.title(u'Trajeto do veículo: ' + vehicle)
#    plt.show()

    '''---------'''

    ##Gráfico de velocidade
    ##Intervalo do gráfico
    interval_xa = '00:00'
    interval_xb = '23:57'
    ##Média para o intervalo
    df_line = df4.groupby('Intervalo')['Velocidade'].mean()
    df_line = df_line.reset_index()##ARRUMAR A HORA
    df_line['Intervalo'] = pd.to_datetime(df_line['Intervalo'], format = '%H:%M').dt.time
    df_line.plot(x='Intervalo',y='Velocidade',\
                       title = u'Velocidade média do veículo: ' + vehicle,\
                       figsize = (14,8))
    plt.xlim(interval_xa, interval_xb)
    plt.ylim()
    plt.show()
    '''---------''' 
    
    ##DDO
    #del lst_speed_temp, df_filtred, df_line, df_scatter, colors

##DDO
#del lst_time_pattern10, df_time, df2, df3






















