from turtle import width
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st
import pydeck as pdk
import plotly.express as px
import altair as alt


def timeConverter(stringa):
  try:
    x = stringa.replace('.', ':')
    min, sec, ms = x.split(':')
    ms = float(ms)
    sec = float(sec)*1000
    min = float(min)*60*1000
    sec = (min+sec+ms)/1000
  except:
    sec = 0
  return sec

df_path = '/Users/mattiaropelato/python/streamlit_test/dataset/f1_23_09_22/'

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
results['position'] = results['position'].apply(pd.to_numeric, errors='coerce')
results['points'] = results['points'].apply(pd.to_numeric, errors='coerce')
results['milliseconds'] = results['milliseconds'].apply(pd.to_numeric, errors='coerce')
results['fastestLapSpeed'] = results['fastestLapSpeed'].apply(pd.to_numeric, errors='coerce')
results.loc[:, 'fastestLapTime'] = [timeConverter(x) for x in results['fastestLapTime']]
results.loc[:, 'milliseconds'] = [x/1000 for x in results['milliseconds']]
pit_stops.loc[:, 'milliseconds'] = [x/1000 for x in pit_stops['milliseconds']]

res = results.groupby('raceId').agg(giri=('laps', 'max'), 
                              seconds=('milliseconds', 'min'),
                              fastestLapTime=('fastestLapTime', 'min'),
                              fastestLapSpeed=('fastestLapSpeed', 'max')
                              )

c_df = res.merge(races.loc[:, ['raceId', 'year', 'circuitId']], on='raceId')\
                        .merge(circuits.loc[:, ['circuitId', 'location', 'country', 'lat', 'lng']], on='circuitId')\
                        .drop('circuitId', axis=1)
c_df['latlng'] = [str(x)+', '+str(y) for x,y in zip(c_df.lat, c_df.lng)]
c = c_df.groupby('latlng').agg(lat=('lat', 'max'),
                                lng=('lng', 'max'),
                                gp=('raceId', 'count')).reset_index().drop('latlng', axis=1)

########################################################################################################################
########################################################################################################################
########################################################################################################################

st.header('Number of races for every location')

lat = list(c.lat.unique())
lng= list(c.lng.unique())
#zoom = 10


st.pydeck_chart(pdk.Deck(
  map_style=None,
  initial_view_state=pdk.ViewState(
    latitude=20,
    longitude=30,
    zoom=.6,
    pitch=50,
  ),
  layers=[
        pdk.Layer(
          "ScatterplotLayer",
          c,
          pickable=True,
          opacity=0.8,
          stroked=True,
          filled=True,
          #radius_scale=1000,
          radius_min_pixels=1,
          #radius_max_pixels=200,
          line_width_min_pixels=1,
          get_position=['lng', 'lat'],
          get_radius=300000,
          get_fill_color=[255, 140, 0],
          get_line_color=[0, 0, 0],
          ),
      pdk.Layer(
          "ColumnLayer",
          c,
          pickable=True,
          opacity=0.8,
          stroked=True,
          filled=True,
          elevation_scale=300000,
          radius=100000,

          radius_min_pixels=5,
          #radius_max_pixels=200,
          line_width_min_pixels=1,
          get_position=['lng', 'lat'],
          get_elevation="gp",
          get_fill_color=[0, 255, 140],
          get_line_color=[0, 0, 0],
      ),

],
))

########################################################################################################################
########################################################################################################################
########################################################################################################################

pit_stops.drop(['time', 'duration'], axis=1, inplace=True)
circ_df = pit_stops.merge(results[['raceId', 'driverId', 'constructorId', 'positionOrder', ]], on=['raceId', 'driverId'])\
         .merge(races[['raceId', 'year', 'circuitId',]], on='raceId')\
         .merge(circuits[['circuitId', 'location']], on='circuitId')
resu = results[['raceId', 'statusId']]\
        .merge(races[['raceId', 'circuitId', 'year']], on='raceId')\
        .merge(circuits[['circuitId', 'location']], on='circuitId')\
        .merge(status, on='statusId')\
        .drop('circuitId', axis=1)
circuit_accidents = resu.loc[resu['statusId'].isin([3, 4, 20])]
circuit_accidents = circuit_accidents[['location', 'status']]
circuit_accidents = pd.crosstab(index=circuit_accidents['location'], columns=circuit_accidents['status'])
circuit_accidents = circuit_accidents.reset_index()

# Determine the number of races held at each circuit
num_races = c_df.groupby('location').raceId.count().reset_index().rename(columns={'raceId': 'num_of_races'})
circuit_accidents = pd.merge(circuit_accidents, num_races, on = 'location', how = 'left')

# Calculate the total number of accidents at each circuit and arrange the dataframe according to this
circuit_accidents['total_accidents'] = circuit_accidents['Accident'] + circuit_accidents['Collision'] + circuit_accidents['Spun off']
circuit_accidents = circuit_accidents.sort_values(by = 'total_accidents', ascending = False)

# Calculate the number of accidents per race
circuit_accidents['accidents_per_race'] = (circuit_accidents['total_accidents']/circuit_accidents['num_of_races']).round(3)

# Clean the dataframe by resetting the index
circuit_accidents = circuit_accidents.reset_index()
circuit_accidents = circuit_accidents.drop(['index'], axis = 1)
circuit_accidents = circuit_accidents[circuit_accidents['num_of_races']>10]

tipo = st.selectbox(
    'Cosa vuoi visualizzare?',
    ('Distribuzione', 'Massimo', 'Minimo', 'Media')
)

arg = st.selectbox(
    'Rispetto a cosa?',
    ('Durata Pit Stop', 'Crashes')
)

if (tipo == 'Distribuzione'): 
  if (arg == 'Durata Pit Stop'):
    source = circ_df[circ_df['milliseconds']<50].groupby(by=['raceId', 'location']).mean().reset_index().sort_values(by='milliseconds',ascending=True)
    fig = alt.Chart(source)\
                    .mark_boxplot(extent=0.5).encode(
                      x='location',
                      y=alt.Y('milliseconds', scale=alt.Scale(zero=False)),
                   ).properties()
  elif (arg == 'Crashes'):
    source = resu.groupby(by=['raceId', 'location']).mean().reset_index()
    fig = alt.Chart(source)\
                        .mark_boxplot().encode(
                          x=alt.X('location', sort='-y'),
                          y=alt.Y('statusId', scale=alt.Scale(zero=False)),
                      )
  


elif (tipo== 'Massimo'):
  if (arg == 'Durata Pit Stop'):
    source = circ_df.groupby(by='location').agg(seconds=('milliseconds', 'max'), n_gp=('raceId', 'nunique')).reset_index().sort_values(by='seconds',ascending=False)
    fig = alt.Chart(source)\
                    .mark_bar().encode(
                      x='location',
                      y='seconds',
                      color='n_gp'
                   )
    rule = alt.Chart(source).mark_rule(color='purple').encode(y='mean(seconds)')

    fig = (fig + rule).properties(width=600)
  elif (arg == 'Crashes'):
    source = circuit_accidents.sort_values('total_accidents').tail(20)
    fig = alt.Chart(source)\
                        .mark_bar().encode(
                          x=alt.X('location', sort='-y'),
                          y='total_accidents',
                          color='num_of_races'
                      )
    rule = alt.Chart(circuit_accidents).mark_rule(color='purple').encode(y='mean(total_accidents)')

    fig = (fig + rule)


elif (tipo== 'Minimo'):
  if (arg == 'Durata Pit Stop'):
    source = circ_df.groupby(by='location').agg(seconds=('milliseconds', 'min'), n_gp=('raceId', 'nunique')).reset_index().sort_values(by='seconds',ascending=False)
    fig = alt.Chart(source)\
                    .mark_bar().encode(
                      x='location',
                      y='seconds',
                      color='n_gp'
                   )
    rule = alt.Chart(source).mark_rule(color='purple').encode(y='mean(seconds)')

    fig = (fig + rule).properties(width=600)
  elif (arg == 'Crashes'):
    source = circuit_accidents.sort_values('total_accidents').head(20)
    fig = alt.Chart(circuit_accidents)\
                        .mark_bar().encode(
                          x=alt.X('location', sort='y'),
                          y='total_accidents',
                          color='num_of_races'
                      )
    rule = alt.Chart(circuit_accidents).mark_rule(color='purple').encode(y='mean(total_accidents)')

    fig = (fig + rule)

elif (tipo== 'Media'):
  if (arg == 'Durata Pit Stop'):
    source = circ_df.groupby(by='location').agg(seconds=('milliseconds', 'mean'), n_gp=('raceId', 'nunique')).reset_index().sort_values(by='seconds',ascending=False)
    fig = alt.Chart(source)\
                    .mark_bar().encode(
                      x='location',
                      y='seconds',
                      color='n_gp'
                   )
  elif (arg == 'Crashes'):
    source = circuit_accidents
    fig = alt.Chart(circuit_accidents)\
                        .mark_bar().encode(
                          x=alt.X('location', sort='-y'),
                          y='accidents_per_race',
                          color='num_of_races'
                      )

st.altair_chart(fig)