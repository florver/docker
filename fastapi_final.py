# -*- coding: utf-8 -*-
"""FastApi_final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WWnnQ_sshGWY1jVLyyvF8olx6ud4blCL
"""

from fastapi import FastAPI

from fastapi.responses import StreamingResponse
import io
import pandas as pd 
import datetime
from datetime import date
import json

import psycopg2

engine = psycopg2.connect(
    database="postgres",
    user='postgres',
    password='riverplate1995',
    host="grupo-kvd.c7ezedheahhk.us-east-1.rds.amazonaws.com",
    port='5432'
)

#### Tabla TOPCTR ####
cursor = engine.cursor()
cursor.execute("""SELECT * FROM base_TopCTR_Final""")
data_TopCTR = cursor.fetchall()

cols=[]
for elt in cursor.description:
  cols.append(elt[0])
df_ctr = pd.DataFrame(data=data_TopCTR, columns=cols)

#### Tabla TOPProduct ####
cursor = engine.cursor()
cursor.execute("""SELECT * FROM base_TopProduct_Final""")
data_TopProduct = cursor.fetchall()

cols=[]
for elt in cursor.description:
  cols.append(elt[0])
df_tp = pd.DataFrame(data=data_TopProduct, columns=cols)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Bienvenidos a la app de recomendaciones"}

@app.get("/recommendations/{adv}/{Modelo}")
async def recommendations(adv: str = 'Y0W3K7OV6ZLILW96OO3K', Modelo: str ='TopProduct'):
  hoy = date.today().strftime('%Y-%m-%d')
  if Modelo=='TopProduct':
    
    df_tp=df_tp[(df_tp['date']==hoy)]
    result_prod=df_tp[df_tp['advertiser_id']==adv]['product_id'].to_list()

  else:
    
    df_ctr=df_ctr[(df_ctr['date']==hoy)]
    result_prod=df_ctr[df_ctr['advertiser_id']==adv]['product_id'].to_list()

  return {'date': hoy,'advertiser_id': adv, "Modelo":Modelo, "product_id":result_prod}

@app.get("/history/{adv}")
async def history(adv: str = 'Y0W3K7OV6ZLILW96OO3K'):

  hoy = date.today().strftime('%Y-%m-%d')
  filter=(date.today()-datetime.timedelta(days= 7)).strftime('%Y-%m-%d')

  df_tp['Model']='TopProduct'
  df_tp=df_tp[['date','Model','advertiser_id','product_id']]
   
  df_ctr['Model']='TopCTR'
  df_ctr=df_ctr[['date','Model','advertiser_id','product_id']]
  df_final=pd.concat([df_tp,df_ctr])
  base=df_final[(df_final['date']>filter) & (df_final['date']<=hoy)]

  result_prod=base[base['advertiser_id']==adv]['product_id'].to_list()
  result_mod=base[base['advertiser_id']==adv]['Model'].to_list()
  result_date=base[base['advertiser_id']==adv]['date'].to_list()

  return {'date': result_date,'advertiser_id': adv, "Modelo":result_mod, "product_id":result_prod}

@app.get("/stats")
async def stats():

  hoy = date.today().strftime('%Y-%m-%d')
  filter=(date.today()-datetime.timedelta(days= 7)).strftime('%Y-%m-%d')
  
  df_tp['Model']='TopProduct'
  df_tp=df_tp[['date','Model','advertiser_id','product_id']]
  
  df_ctr['Model']='TopCTR'
  df_ctr_sel=df_ctr[['date','Model','advertiser_id','product_id']]
  df_final=pd.concat([df_tp,df_ctr_sel])

  base=df_final[(df_final['date']>filter) & (df_final['date']<=hoy)]

  cant=base.groupby(["date"], as_index=True).agg({'advertiser_id':'nunique'}).to_json()
  cant_product=base[base['date']==hoy].groupby(["date","advertiser_id"], as_index=True).agg({'product_id':'nunique'}).to_json()
  top_impression=df_ctr.groupby(["advertiser_id"], as_index=True).agg({'impression':'sum'}).to_json()
  top_clicks=df_ctr.groupby(["advertiser_id"], as_index=True).agg({'click':'sum'}).to_json()


  return {'Cantidad advertiser': cant, 'Productos último día':cant_product, 'Top Impression Advertiser':top_impression, 'Top Click Advertiser':top_clicks}
