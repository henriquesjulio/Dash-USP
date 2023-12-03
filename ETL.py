import pandas as pd
import os
import glob
import urllib.request, urllib.parse, urllib.error
import json
import ssl
from datetime import datetime

# Carregando os dados para transformar

files = glob.glob(os.path.join('database/datalake', '*.csv'))

df = pd.DataFrame(columns=['Unidade de Despesa', 'Grupo Orçamentário', 'Fonte de Recurso', 'Função', 'Subfunção', 'Elemento', 'Dotação Inicial (R$)', 'Dotação Atual (R$)', 'Empenhado (R$)', 'Liquidado (R$)', 'Pago (R$)', 'Pago Restos (R$)'])

for file in files:
    
    dff = pd.read_csv(file, encoding='latin-1', delimiter = ';')
    
    dff['Ano'] = pd.to_datetime(file[28:32])
    
    df = pd.concat([df, dff])

# Formatando coluna do ano

df['Ano'] = df['Ano'].dt.year

# Formatando colunas que contém números

df['Dotação Inicial (R$)'] = df['Dotação Inicial (R$)'].apply(lambda x: x.replace(',','.')).apply(lambda x: float(x))
df['Dotação Atual (R$)'] = df['Dotação Atual (R$)'].apply(lambda x: x.replace(',','.')).apply(lambda x: float(x))
df['Empenhado (R$)'] = df['Empenhado (R$)'].apply(lambda x: x.replace(',','.')).apply(lambda x: float(x))
df['Liquidado (R$)'] = df['Liquidado (R$)'].apply(lambda x: x.replace(',','.')).apply(lambda x: float(x))
df['Pago (R$)'] = df['Pago (R$)'].apply(lambda x: x.replace(',','.')).apply(lambda x: float(x))
df['Pago Restos (R$)'] = df['Pago Restos (R$)'].apply(lambda x: x.replace(',','.')).apply(lambda x: float(x))

# Ajuste de colunas em excesso

df['Pago (R$)'] = df['Pago (R$)'] + df['Pago Restos (R$)']
df = df.drop(['Pago Restos (R$)'],axis=1)

# Limpando os nomes das unidades de despesa

df['Unidade de Despesa'] = df['Unidade de Despesa'].apply(lambda x: x.split(' - ')[-1])

# Salvando os dados limpos em formato .csv

df.to_csv('database/datawarehouse/Orcamento.csv')
               
print('Orcamento.csv criado.')

# Para extração dos dados de coordenadas

unidades = df['Unidade de Despesa'].unique()

api_key = 'CHAVE DE ACESSO'

serviceurl = "https://maps.googleapis.com/maps/api/geocode/json?"

# Ignorar erros de certificados

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Extração dos dados

dfc = pd.DataFrame()

for unidade in unidades:
    address = unidade.strip()
    parms = dict()
    parms["address"] = address+' USP'
    parms['key'] = api_key
    url = serviceurl + urllib.parse.urlencode(parms)
    
    uh = urllib.request.urlopen(url, context=ctx)
    data = uh.read().decode()
        
    try:
        js = json.loads(data)
        to_df = pd.DataFrame([address, js["results"][0]["geometry"]["location"]["lat"], js["results"][0]["geometry"]["location"]["lng"]]).T  
        dfc = pd.concat([dfc, to_df])
    
    except:
        continue

# Renomeando colunas para aplicação futura

dfc.columns = ["Unidade de Despesa","lat","lng"]

# Carregando os dados tratados no Data Warehouse

dfc.to_csv('database/datawarehouse/Coordenadas.csv')    

print("Coordenadas.csv criado.")