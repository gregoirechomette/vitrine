import numpy as np
import pandas as pd
import streamlit as st

@st.cache_data
def load_consos_data(path):
    
    # Load the data and change the format of code_panonceau
    df_consos = pd.read_csv(path)
    df_consos['code'] = df_consos['code'].astype(str).str.zfill(4)

    return df_consos


@st.cache_data
def load_consos_stats(path_consos_stats):

    # Load the stats data when dimanche ouvert and ferme
    df_consos_stats = pd.read_csv(path_consos_stats)

    return df_consos_stats