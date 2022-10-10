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

tipo = st.selectbox(
    'Cosa vuoi visualizzare?',
    ('Distribuzione', 'Massimo', 'Minimo', 'Media')
)

arg = st.selectbox(
    'Rispetto a cosa?',
    ('Durata Pit Stop', 'Not implemented yet')
)

if (tipo == 'Distribuzione'): 
  if (arg == 'Durata Pit Stop'):
    fig = px.box(circ_df[circ_df['milliseconds']<50].groupby(by=['raceId', 'location']).mean().reset_index().sort_values(by='milliseconds',ascending=True),
                 x='location',
                 y='milliseconds',
                )

elif (tipo== 'Massimo'):
  if (arg == 'Durata Pit Stop'):
    fig = px.bar(circ_df.groupby(by='location').agg(seconds=('milliseconds', 'max'), n_gp=('raceId', 'nunique')).reset_index().sort_values(by='seconds',ascending=False),
                    x='location',
                    y='seconds',
                    color = 'n_gp',
#                    continuous_color_scale = px.colors.sequential.sunset,
                )
#    source = circ_df.groupby(by='location').agg(seconds=('milliseconds', 'max'), n_gp=('raceId', 'nunique')).reset_index().sort_values(by='seconds',ascending=False)
#    fig = alt.Chart(source)\
#                    .make_bar().encode(
#                      x='location',
#                      y='seconds',
#                   )
#    rule = alt.Chart(source).mark_rule(color='red').encode(y='mean(milliseconds)')

#    (fig + rule).properties(width=600)

elif (tipo== 'Minimo'):
  if (arg == 'Durata Pit Stop'):
    fig = px.bar(circ_df.groupby(by='location').agg(seconds=('milliseconds', 'min'), n_gp=('raceId', 'nunique')).reset_index().sort_values(by='seconds',ascending=False),
                    x='location',
                    y='seconds',
                    color = 'n_gp',
#                    color_discrete_sequence = n_colors('rgb(0, 0, 255)', 'rgb(255, 0, 0)', 25, colortype = 'rgb'),
                )

elif (tipo== 'Media'):
  if (arg == 'Durata Pit Stop'):
    fig = px.bar(circ_df.groupby(by='location').agg(seconds=('milliseconds', 'mean'), n_gp=('raceId', 'nunique')).reset_index().sort_values(by='seconds',ascending=False),
                    x='location',
                    y='seconds',
                    color = 'n_gp',
                )

st.plotly_chart(fig)
