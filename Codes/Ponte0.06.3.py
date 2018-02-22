# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 00:48:55 2018

@author: DMota and Koch
"""



##Bibliotecas
import pandas as pd
from matplotlib import pyplot as plt
import datetime as dt
from math import radians, cos, sin, asin, sqrt


##Entrada de dados
file_x = '000'
data = open('C:\\Users\\danielmota\\Documents\\GitHub\\TransUrb\\' + file_x + '.txt','r')
#data = open('C:\\Users\\Gabriel\\Documents\\GitHub\\TransUrb\\' + file_x + '.txt','r')

##Tranasformar dados em lista
lst_data_txt = list(set(data.readlines()))

##Transformar lista em Dataframe
df1 = pd.Series(lst_data_txt).str.split(',', expand = True)
df1 = df1.sort_values(by = [0,1])
del lst_data_txt

##Nomear colunas
df1.columns = ['Dia','Hora','Linha',u'Veículo','Latitude','Longitude']

##Lat Lon para float
df1.Latitude = df1.Latitude.astype(float)
df1.Longitude = df1.Longitude.astype(float)

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

##Função haversine
def haversine(lon1, lat1, lon2, lat2):        
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371
    return c * r

'''---------'''

##Filtros
line_a = '1364'
line_b = '34132'

'''---------'''

##Filtrando por linha
df2 = df1[(df1['Linha'] == line_a) | (df1['Linha'] == line_b)]
df2 = df2.set_index(['Linha', u'Veículo'])
del df1

##Iterar todos os veículos nas linhas
for (vehicle, df_filtred) in df2.groupby(u'Veículo'):
    pass
    ##Tratando os dados
    df_filtred = df_filtred.reset_index().groupby(['Linha', u'Veículo', 'Hora']).mean().reset_index(level=-1)
    df_filtred = df_filtred.reset_index(level=['Linha',u'Veículo'])
    df_filtred = df_filtred.set_index(['Hora'])
    df3 = df_time.join(df_filtred)
    df3 = df3[~df3.index.duplicated(keep='first')]
    
    ##Criando Dataframe para calcular intervalo de 10 min
    df4 = df3.assign(Intervalo=lst_time_pattern10)
    df4 = df4.fillna(value = 0)

    '''---------'''
    
    ##Calcular a distancia e a velocidade
    lst_speed_temp=[]
    lst_speed_temp.append(0.0)
    for i in range(len(df4)-1):    
        lat1 = df4.get_value(i,2,takeable = True)
        lon1 = df4.get_value(i,3,takeable = True)
        lat2 = df4.get_value(i+1,2,takeable = True)
        lon2 = df4.get_value(i+1,3,takeable = True)
        speed_temp_x = ((haversine(lon1, lat1, lon2, lat2))*1000)/60
        if speed_temp_x < 22:     
            lst_speed_temp.append(speed_temp_x)
        else:
            lst_speed_temp.append(0.0)    
    ##Deletando dados obsoletos (DDO)
    del lat1, lat2, lon1, lon2, speed_temp_x
    df4 = df4.assign(Velocidade=lst_speed_temp)

    '''---------'''
    
    ##Gráfico de posição
    ##Filtro para tirar a posição 0,0
    df_scatter = df4[(df4['Latitude'] != 0) | (df4['Longitude'] != 0)]
    fig, ax = plt.subplots()
    colors = {line_a:'red', line_b:'blue'}
    ax.scatter(df_scatter['Latitude'],df_scatter['Longitude'],\
               c=df_scatter['Linha'].apply(lambda x: colors[x]),\
               s=1)
    plt.title(u'Trajeto do veículo: ' + vehicle)
    plt.show()

    '''---------'''

    ##Gráfico de velocidade
    ##Média para o intervalo
    df_line = df4.groupby('Intervalo')['Velocidade'].mean()
    df_line.plot(x='Intervalo',y='Velocidade', title = u'Velocidade média do veículo: ' + vehicle)
    
    '''---------'''
    
    ##DDO
    del lst_speed_temp, df_filtred, df_line, df_scatter, colors

##DDO
del lst_time_pattern10, df_time, df2, df3




















