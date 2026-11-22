#!/usr/bin/env python3
"""Auditoría y limpieza conservadora de dengue_original.csv.
Uso: python scripts/limpiar_dengue.py --entrada dengue_original.csv --salida data
Los duplicados se conservan: no hay identificadores de personas.
"""
import argparse, json, hashlib
from pathlib import Path
import pandas as pd
import numpy as np

def main():
 p=argparse.ArgumentParser();p.add_argument('--entrada',default='dengue_original.csv');p.add_argument('--salida',default='data');p.add_argument('--guardar-individual',action='store_true');a=p.parse_args()
 out=Path(a.salida);out.mkdir(parents=True,exist_ok=True)
 df=pd.read_csv(a.entrada,sep=';',encoding='utf-8-sig',dtype={'ubigeo':'string','diresa':'string','localcod':'string'},low_memory=False)
 originales=list(df.columns); n=len(df)
 duplicados=int(df.duplicated().sum());faltantes={c:int(df[c].isna().sum()) for c in originales}
 for c in ['departamento','provincia','distrito','localidad','enfermedad','diagnostic','tipo_edad','sexo','diresa','localcod','ubigeo']:
  df[c]=df[c].astype('string').str.strip().str.upper();df[c]=df[c].replace('',pd.NA)
 # UBIGEO a seis dígitos, preservando ceros a la izquierda
 df['ubigeo']=df['ubigeo'].str.zfill(6)
 df['edad_anios']=np.select([df.tipo_edad.eq('A').fillna(False),df.tipo_edad.eq('M').fillna(False),df.tipo_edad.eq('D').fillna(False)], [df.edad,df.edad/12,df.edad/365.25],default=np.nan)
 invalida=((df.tipo_edad=='A')&~df.edad.between(0,110))|((df.tipo_edad=='M')&~df.edad.between(0,11))|((df.tipo_edad=='D')&~df.edad.between(0,30))|~df.tipo_edad.isin(['A','M','D'])
 df['edad_invalida']=invalida.fillna(True)
 df.loc[df.edad_invalida,'edad_anios']=np.nan
 df['grupo_edad']=pd.cut(df.edad_anios,bins=[-0.001,1,5,15,30,45,60,111],right=False,labels=['<1','1-4','5-14','15-29','30-44','45-59','60+']).astype('string')
 # No inferir diagnóstico: corroborar códigos, sin sobrescribir la categoría original.
 mapa={'DENGUE SIN SIGNOS DE ALARMA':'A97.0','DENGUE CON SIGNOS DE ALARMA':'A97.1','DENGUE GRAVE':'A97.2'}
 df['codigo_inconsistente']=(df.enfermedad.map(mapa)!=df.diagnostic).fillna(True)
 df['semana_invalida']=~df.semana.between(1,53)
 df['sexo_invalido']=~df.sexo.isin(['F','M'])
 df['caso_con_alarma_o_grave']=df.enfermedad.isin(['DENGUE CON SIGNOS DE ALARMA','DENGUE GRAVE']).astype('int8')
 df['registro_duplicado_exacto']=df.duplicated(subset=originales,keep=False)
 # No hacer deduplicación al no existir identificadores de caso.
 if a.guardar_individual:
  df.to_csv(out/'dengue_limpio_individual_NO_PUBLICAR.csv',index=False,encoding='utf-8-sig')
 # Solo agregados con dimensión poco detallada para publicación web.
 anio=pd.crosstab(df.ano,df.enfermedad).reset_index();anio.columns.name=None
 anio['total']=anio.iloc[:,1:].sum(axis=1);anio.to_csv(out/'casos_por_anio.csv',index=False)
 dep=pd.crosstab(df.departamento,df.enfermedad).reset_index();dep.columns.name=None;dep['total']=dep.iloc[:,1:].sum(axis=1);dep.to_csv(out/'casos_por_departamento.csv',index=False)
 grupos=df.dropna(subset=['grupo_edad']).groupby(['ano','grupo_edad','sexo'],observed=True,dropna=False).agg(total=('caso_con_alarma_o_grave','size'),con_alarma_o_grave=('caso_con_alarma_o_grave','sum')).reset_index()
 grupos=grupos[(grupos.total>=30)&(grupos.con_alarma_o_grave>=5)&((grupos.total-grupos.con_alarma_o_grave)>=5)]
 grupos.to_csv(out/'grupos_modelado_publicables.csv',index=False)
 resumen={'archivo_entrada':str(a.entrada),'filas_originales':n,'columnas_originales':len(originales),'variables':originales,'anos':[int(df.ano.min()),int(df.ano.max())], 'duplicados_exactos_no_eliminados':duplicados,'faltantes_originales':faltantes,'edad_invalida':int(df.edad_invalida.sum()),'codigo_inconsistente':int(df.codigo_inconsistente.sum()),'semana_invalida':int(df.semana_invalida.sum()),'sexo_invalido':int(df.sexo_invalido.sum()),'grupos_anonimizados_publicados':len(grupos),'grupos_total_antes_filtro':int(df.dropna(subset=['grupo_edad']).groupby(['ano','grupo_edad','sexo'],observed=True).ngroups),'registros_incluidos_en_grupos':int(grupos.total.sum()),'registros_fuera_de_grupos':int(n-grupos.total.sum()),'casos_por_tipo':{str(k):int(v) for k,v in df.enfermedad.value_counts().items()},'sha256_original':hashlib.sha256(Path(a.entrada).read_bytes()).hexdigest(),'decisiones':['Conservar duplicados por falta de ID único','No imputar edad imposible; indicar NA en edad_anios','Conservar enfermedad y diagnostic sin sobreescribir','No convertir conteos de casos en incidencia sin denominador poblacional','Excluir datos individuales y ubicaciones finas del paquete público','No evaluar predicción clínica sin controles externos y temporalidad']}
 (out/'auditoria_dengue.json').write_text(json.dumps(resumen,indent=2,ensure_ascii=False),encoding='utf-8')
 print(json.dumps({k:resumen[k] for k in ['filas_originales','duplicados_exactos_no_eliminados','edad_invalida','codigo_inconsistente','grupos_anonimizados_publicados']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
