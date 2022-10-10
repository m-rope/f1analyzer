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

driver_df = results.loc[:, ['raceId', 'driverId', 'laps', 'fastestLapTime', 'positionOrder']]\
                        .merge(driver_standings.loc[:, ['raceId', 'driverId', 'points', 'position']], on=['raceId', 'driverId'])\
                        .merge(drivers.loc[:, ['driverId', 'driverRef']], on='driverId')\
                        .merge(races.loc[:, ['raceId', 'year', 'circuitId']], on='raceId')\
                        .merge(circuits.loc[:, ['circuitId', 'location']], on='circuitId')\
                        .merge(qualifying.loc[:, ['raceId', 'driverId', 'position']], 
                            on=['raceId', 'driverId'], how='left', suffixes=('_championship', '_quali'))\
                        .drop(['driverId', 'circuitId'], axis=1)
driver_df.loc[:, 'fastestLapTime'] = [timeConverter(x) for x in driver_df['fastestLapTime']]


anno = st.sidebar.slider('Select season 🗒', int(driver_df.year.min()), int(driver_df.year.max()), int(2022))

driver_df.loc[:, 'poles'] = [1 if x==1 else 0 for x in driver_df['position_quali']]
driver_df.loc[:, 'wins'] = [1 if x==1 else 0 for x in driver_df['positionOrder']]





dr = driver_df.groupby('driverRef').agg(n_wins=('wins', 'sum'),
                                        n_poles=('poles', 'sum'),
                                        avg_race_placement=('positionOrder', 'mean'),
                                        avg_quali_placement=('position_quali', 'mean'),
                                        tot_races=('raceId', 'count'),
                                        tot_laps=('laps', 'sum'),
                                        tot_seasons=('year', 'nunique'),
                                        tot_points=('points', 'sum'),
                                        ).sort_values('tot_races', ascending=False)

dr1 = dr.loc[dr['tot_seasons']>=10]

pilots = list(dr1.index)
dr22 = driver_df.loc[driver_df['year']==2022, 'driverRef'].unique()
pilots += [x for x in dr22 if x not in pilots]
dr = dr[dr.index.isin(pilots)]


st.header("Pilots compared (all-time)")
options = st.multiselect(
    'Choose at least 2 pilots',
    list(dr.index),
    ['vettel', 'leclerc'])


mm_dr=(dr-dr.min())/(dr.max()-dr.min())
mm_dr.sort_values('n_wins', ascending=False, inplace=True)
inv = lambda x: 1-x
mm_dr.loc[:, ['avg_race_placement', 'avg_quali_placement']] = mm_dr.loc[:, ['avg_race_placement', 'avg_quali_placement']].apply(inv)

categories = list(mm_dr.columns) + list(mm_dr.columns)[:1]

fig = go.Figure()


for pil in options:
    fig.add_trace(go.Scatterpolar(
        r=mm_dr.loc[pil, :].tolist() + mm_dr.loc[pil, :].tolist()[:1],
        theta=categories,
        fill='toself',
        name=pil,
    ))
#customization of chart
fig.update_layout(
font_color="ivory",
legend=dict(x=.45, y=1.3, bgcolor='darkslategrey'),
paper_bgcolor="black",
plot_bgcolor="black",
polar = dict(radialaxis = dict(gridwidth=0.5,
                            range=[0, 1], 
                            showticklabels=False, ticks='', gridcolor = "white"),
                angularaxis = dict(showticklabels=True, ticks='outside', 
                            rotation=45,
                            direction = "clockwise",
                            gridcolor = "white"),
            bgcolor = 'darkslategrey', 
))
st.plotly_chart(fig, use_container_width=True, sharing="streamlit")








d = driver_df.groupby(['driverRef', 'year']).agg(n_wins=('wins', 'sum'), 
                                        avg_race_placement=('positionOrder', 'mean'),
                                        avg_quali_placement=('position_quali', 'mean'),
                                        n_poles=('poles', 'sum'),
                                        tot_races=('raceId', 'count')
                                                )\
                                        .reset_index()

d_wq = d.loc[(d['year']==anno) & ((d['n_wins']>0) | (d['n_poles']>0))].groupby('driverRef').sum()#.reset_index()

st.header('Number of wins and poles per pilots and season')
st.bar_chart(d_wq[['n_wins', 'n_poles']])

d_avg = d.loc[(d['year']==anno)].groupby('driverRef').sum()#.reset_index()

d_ch = driver_df.loc[driver_df['year']==anno].groupby(['driverRef', 'raceId']).position_championship.max().reset_index().set_index('raceId')


d_avg = d.loc[(d['year']==anno) & (d['tot_races']>10)].groupby('driverRef').sum().reset_index()

st.header("Race and quali placement's ratio for pilots and seasons")
st.write('data available from 1967')

if int(d_avg[['avg_quali_placement']].sum()) > 5:
    fig, axes = plt.subplots()
    sns.scatterplot(ax=axes, data=d_avg[['driverRef', 'avg_race_placement', 'avg_quali_placement']],
            x='avg_race_placement', y='avg_quali_placement', hue='driverRef', s=250, legend=False)
    axes.plot([0,20], [0,20], c='w', linewidth=1, linestyle='dotted')

    axes.set_facecolor('k')
    fig.set_facecolor('k')
    axes.yaxis.grid(linewidth=.2)
    axes.yaxis.grid(linewidth=.2)
    axes.invert_xaxis()
    axes.invert_yaxis()
    axes.spines[['top', 'bottom', 'right', 'left']].set_visible(False)

    axes.xaxis.label.set_color('w')
    axes.yaxis.label.set_color('w')
    axes.tick_params(axis='x', colors='w')
    axes.tick_params(axis='y', colors='w')

    axes.set_xlim(18,0)
    axes.set_xlim(18,0)

    for i,nome in enumerate(d_avg.driverRef):
        plt.annotate(nome, (d_avg.avg_race_placement[i]-.7, d_avg.avg_quali_placement[i]+.1), color='w')

    st.pyplot(fig=fig, clear_figure=True)

else:
    st.error(err, icon=None)
    

st.header('Ranking trend per season')

d_gr = driver_df.loc[:, ['raceId', 'driverRef', 'year', 'position_championship']].groupby(['raceId', 'driverRef']).max().reset_index()
j = d_gr.groupby(['driverRef', 'year']).count().reset_index()
j = list(j[j['position_championship']>5].driverRef.unique())

d_gr = d_gr[d_gr['driverRef'].isin(j)]

fig2, axes = plt.subplots(figsize=(20,10))
w = d_gr.loc[d_gr['year']==anno]
palette = sns.color_palette('rocket_r', n_colors=50)

for i,pil in enumerate(w.driverRef.unique()):
    k = w.loc[w['driverRef']==pil]
    axes.plot(k.raceId, k.position_championship, label=pil, 
            linewidth=((1/int(k.position_championship[-1:])*10)), c=palette[i])
    plt.annotate(pil, (k.raceId[-1:], k.position_championship[-1:]), color=palette[i])

axes.set_facecolor('k')
fig2.set_facecolor('k')
axes.xaxis.grid(linewidth=.5)
axes.invert_yaxis()
axes.spines[['top', 'bottom', 'right', 'left']].set_visible(False)

axes.xaxis.label.set_color('w')
axes.yaxis.label.set_color('w')
axes.tick_params(axis='y', colors='w')


st.pyplot(fig=fig2, clear_figure=True)

