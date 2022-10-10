import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pydeck as pdk
import streamlit as st
import time

st.set_page_config(
    page_title="Hello",
    page_icon="🏁",
)

row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns((.1, 2.3, .1, 1.3, .1))
with row0_1:
    st.title('F1 Analyzer🏎🏎')
with row0_2:
    st.text("")
    st.subheader('Streamlit App by [Mattia Ropelato](https://www.linkedin.com/in/mattia-ropelato-49735ba8/)')
row3_spacer1, row3_1, row3_spacer2 = st.columns((.1, 3.2, .1))
with row3_1:
    st.markdown("👋 Here's a tool to explore F1 datas from its foundation in the '50 until this season, you can explore stats regarding pilots, teams and circuits. Enjoy!")
    st.markdown("Source code [f1analyzer GitHub Repository](https://github.com/m-rope/streamlit_test)")
    st.markdown("(note that it's a work in progress project.. More features and a nicer layout are coming soon 😉)")


st.sidebar.success("⬆️ Select a tab and start exploring! 🏁")
