import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st
import plotly.graph_objects as go

df_path = 'dataset/f1_23_09_22/'

circuits = pd.read_csv(df_path + 'circuits.csv') #
constr_results = pd.read_csv(df_path + 'constructor_results.csv')
constr_standings = pd.read_csv(df_path + 'constructor_standings.csv') #
constructors = pd.read_csv(df_path + 'constructors.csv') #
driver_standings = pd.read_csv(df_path + 'driver_standings.csv') #
drivers = pd.read_csv(df_path + 'drivers.csv') #
lap_times = pd.read_csv(df_path + 'lap_times.csv')
pit_stops = pd.read_csv(df_path + 'pit_stops.csv')
qualifying = pd.read_csv(df_path + 'qualifying.csv') #
races = pd.read_csv(df_path + 'races.csv') #
results = pd.read_csv(df_path + 'results.csv') #
seasons = pd.read_csv(df_path + 'seasons.csv')
sprint_results = pd.read_csv(df_path + 'sprint_results.csv')
status = pd.read_csv(df_path + 'status.csv')

err = 'non disponibile per questa stagione :('
#st.error(err, icon=None)

def timeConverter(stringa):
  try:
    x = stringa.replace('.', ':')
    min, sec, ms = x.split(':')
    ms = float(ms)
    sec = float(sec)*1000
    min = float(min)*60*1000
    sec = (min+sec+ms)/1000
  except:
    sec = np.nan
  return sec

top3circ = ['Monte-Carlo', 'Monza', 'Barcelona']
top5driv = ['max_verstappen', 'leclerc', 'hamilton', 'norris', 'russell']
top3driv = ['max_verstappen', 'leclerc', 'hamilton']

results['position'] = results['position'].apply(pd.to_numeric, errors='coerce')

constructor_df = results.loc[:, ['raceId', 'driverId', 'constructorId', 'fastestLapTime', 'positionOrder']]\
                        .merge(constr_standings.loc[:, ['raceId', 'constructorId', 'points']], 
                               how='left', on=['raceId', 'constructorId'])\
                        .merge(constructors.loc[:, ['constructorId', 'constructorRef']], on='constructorId')\
                        .merge(races.loc[:, ['raceId', 'year', 'circuitId']], on='raceId')\
                        .merge(circuits.loc[:, ['circuitId', 'location']], on='circuitId')\
                        .drop(['constructorId', 'circuitId'], axis=1)

constructor_df.loc[:, 'fastestLapTime'] = [timeConverter(x) for x in constructor_df['fastestLapTime']]
constructor_df.loc[:, 'wins'] = [1 if x==1 else 0 for x in constructor_df['positionOrder']]
new_col = []
for race in constructor_df.raceId.unique():
    temp = constructor_df[constructor_df['raceId']==race]
    dr = temp['fastestLapTime']
    temp.loc[:, 'fLT_norm'] = (dr-dr.min())/(dr.max()-dr.min())
    new_col += list(temp.loc[:, 'fLT_norm'])
constructor_df.loc[:, 'fLT_norm'] = new_col

########################################################################################################################
########################################################################################################################
########################################################################################################################

anno = st.sidebar.slider('Seleziona stagione', int(constructor_df.year.min()), int(constructor_df.year.max()), int(2022))
c_df =  constructor_df[constructor_df['year']==anno]

squadre = list(c_df['constructorRef'].unique())
squadra = st.sidebar.multiselect(
    'Scegli una o più scuderie',
    squadre,
    squadre)
constr_df = c_df[c_df['constructorRef'].isin(squadra)]

########################################################################################################################
########################################################################################################################
########################################################################################################################

stat_b = st.selectbox(
    'Cosa vuoi visualizzare?',
    ('Punti totali',  'Totale vittorie', 'Media piazzamenti'))

if stat_b == 'Punti totali':
    temp = constr_df[constr_df['year']==anno].groupby('constructorRef').points.max().reset_index()
    asc = 'points'
elif stat_b == 'Totale vittorie':
    temp = constr_df[constr_df['year']==anno].groupby('constructorRef').wins.sum().reset_index()
    asc = 'wins'
elif stat_b == 'Media piazzamenti':
    temp = constr_df[constr_df['year']==anno].groupby('constructorRef').positionOrder.mean().reset_index()
    asc = 'positionOrder'


st.bar_chart(data=temp, x='constructorRef', y=asc)

########################################################################################################################
########################################################################################################################
########################################################################################################################

statistica = st.selectbox(
    'Cosa vuoi visualizzare?',
    ('Andamento punti',  'Piazzamenti migliori', 'Andamento giri più veloci'))

if statistica == 'Andamento giri più veloci':
    ord = 'location'
    asc = 'fLT_norm'
elif statistica == 'Andamento punti':
    ord = 'raceId'
    asc = 'points'
elif statistica == 'Piazzamenti migliori':
    ord = 'location'
    asc = 'positionOrder'


fig, ax = plt.subplots(figsize=(15,5))
sns.lineplot(data=constr_df[constr_df['year']==2022], x=ord, y=asc, hue='constructorRef', 
             palette='bright', legend='brief')
fig.set_facecolor('#3A3A3A')
ax.set_facecolor('#212321')
#ax.invert_yaxis()
plt.grid(linewidth=.3)

st.pyplot(fig=fig, clear_figure=True)

