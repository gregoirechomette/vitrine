import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium

import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go


def desagregation_cdc(df_consos_all, df_consos_stats, df_carte_identite, code_principal='0104'):

    # Slice the dataframes 
    df_consos_magasin_hiver = df_consos_all[((df_consos_all['clean_month'] == 'Décembre 2023') & (df_consos_all['code'] == code_principal))].copy()
    df_consos_magasin_ete = df_consos_all[((df_consos_all['clean_month'] == 'Juillet 2023') & (df_consos_all['code'] == code_principal))].copy()

    df_consos_magasin_hiver = fictitious_desagregation(df_consos_magasin_hiver, season='winter')
    df_consos_magasin_ete = fictitious_desagregation(df_consos_magasin_ete, season='summer')

    # Create a px vertically stacked histogram with the two dataframes.
    custom_colors = {
    "groupe_froid_negatif": px.colors.qualitative.G10[9],
    "groupe_froid_positif": px.colors.qualitative.Set3[4],
    "chauffage": px.colors.qualitative.Plotly[1],
    "climatisation": px.colors.qualitative.Set3[0],
    "eclairage": px.colors.qualitative.Pastel1[5],
    "autres": px.colors.qualitative.Pastel2[7]}

    # Create a px vertically stacked histogram , one fig per dataframe, stacking includes the different categories of consumption.
    fig_hiver = px.bar(df_consos_magasin_hiver, x='clean_hour', y=['groupe_froid_negatif', 'groupe_froid_positif', 'chauffage', 'climatisation', 'eclairage', 'autres'], title='Décembre 2023', labels={'value': 'Puissance [W/m²]', 'variable': ' '}, color_discrete_map=custom_colors, barmode='relative')
    fig_ete = px.bar(df_consos_magasin_ete, x='clean_hour', y=['groupe_froid_negatif', 'groupe_froid_positif', 'chauffage', 'climatisation', 'eclairage', 'autres'], title='Juillet 2023', labels={'value': 'Puissance [W/m²]', 'variable': ' '}, color_discrete_map=custom_colors, barmode='relative')

    # Update the layout
    fig_hiver.update_layout(title='Désagrégation en hiver', title_x=0.4, height=550, showlegend=True, margin=dict(l=20, r=20, t=80, b=20),
                      legend=dict(orientation='h', yanchor="top", y=1.1, xanchor="right", x=0.99), )

    fig_ete.update_layout(title='Désagrégation en ete', title_x=0.4, height=550, showlegend=True, margin=dict(l=20, r=20, t=80, b=20),
                      legend=dict(orientation='h', yanchor="top", y=1.1, xanchor="right", x=0.99), )

    # Change xlabel
    fig_hiver.update_xaxes(title_text=" ", title_font=dict(size=12), showticklabels=True, tickfont=dict(size=16), 
                      ticktext=['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'], 
                      tickvals=['Lundi 12h', 'Mardi 12h', 'Mercredi 12h', 'Jeudi 12h', 'Vendredi 12h', 'Samedi 12h', 'Dimanche 12h'], side='bottom')

    fig_ete.update_xaxes(title_text=" ", title_font=dict(size=12), showticklabels=True, tickfont=dict(size=16),
                        ticktext=['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'], 
                        tickvals=['Lundi 12h', 'Mardi 12h', 'Mercredi 12h', 'Jeudi 12h', 'Vendredi 12h', 'Samedi 12h', 'Dimanche 12h'], side='bottom')

    st.plotly_chart(fig_hiver)
    st.plotly_chart(fig_ete)


    return

def fictitious_desagregation(df_consos_magasin, season='summer'):

    if season == 'summer':

        df_consos_magasin['hour'] = df_consos_magasin['clean_hour'].str.split(' ').str[1].str[:-1].astype(int)
        df_consos_magasin['groupe_froid_negatif'] = 0.0
        df_consos_magasin['groupe_froid_positif'] = 0.0
        df_consos_magasin['eclairage'] = 0.0
        df_consos_magasin['chauffage'] = 0.0
        df_consos_magasin['climatisation'] = 0.0
        df_consos_magasin['autres'] = 0.0

        # In summer, ther is no chauffage, but there is climatisation. Groupes froids are always on, and represent the most important part of the consumption. Climatisation is only during the day, particularly high in the afternoon.
        df_consos_magasin.loc[(df_consos_magasin['hour'] >= 2) & (df_consos_magasin['hour'] <= 20), 'groupe_froid_negatif'] = 0.3 * df_consos_magasin['p_w_m2']
        df_consos_magasin.loc[(df_consos_magasin['hour'] >= 2) & (df_consos_magasin['hour'] <= 20), 'groupe_froid_positif'] = 0.3 * df_consos_magasin['p_w_m2']
        df_consos_magasin.loc[(df_consos_magasin['hour'] >= 2) & (df_consos_magasin['hour'] <= 20), 'eclairage'] = 0.08 * df_consos_magasin['p_w_m2']
        df_consos_magasin.loc[(df_consos_magasin['hour'] >= 2) & (df_consos_magasin['hour'] <= 20), 'climatisation'] = 0.05 * df_consos_magasin['p_w_m2']
        df_consos_magasin.loc[(df_consos_magasin['hour'] >= 12) & (df_consos_magasin['hour'] <= 19), 'climatisation'] = 0.22 * df_consos_magasin['p_w_m2']

        df_consos_magasin.loc[(df_consos_magasin['hour'] < 2) | (df_consos_magasin['hour'] > 20), 'groupe_froid_negatif'] = 0.5 * df_consos_magasin['p_w_m2']
        df_consos_magasin.loc[(df_consos_magasin['hour'] < 2) | (df_consos_magasin['hour'] > 20), 'groupe_froid_positif'] = 0.35 * df_consos_magasin['p_w_m2']

        df_consos_magasin['autres'] = df_consos_magasin['p_w_m2'] - df_consos_magasin['groupe_froid_negatif'] - df_consos_magasin['groupe_froid_positif'] - df_consos_magasin['eclairage'] - df_consos_magasin['climatisation']

    elif season == 'winter':

        df_consos_magasin['hour'] = df_consos_magasin['clean_hour'].str.split(' ').str[1].str[:-1].astype(int)
        df_consos_magasin['groupe_froid_negatif'] = 0.0
        df_consos_magasin['groupe_froid_positif'] = 0.0
        df_consos_magasin['eclairage'] = 0.0
        df_consos_magasin['chauffage'] = 0.0
        df_consos_magasin['climatisation'] = 0.0
        df_consos_magasin['autres'] = 0.0

        # Split the consumption 'p_w_m2' into the different categories with some plausible values. In winter, there is no climatisation. At night (bw 21hand 4h), there is no eclairage. Chauffage is mostly during the day, a little bit at night. Groupes froids are always on, and represent the most important part of the consumption.
        df_consos_magasin.loc[(df_consos_magasin['hour'] >= 3) & (df_consos_magasin['hour'] <= 20), 'groupe_froid_negatif'] = 0.3 * df_consos_magasin['p_w_m2']
        df_consos_magasin.loc[(df_consos_magasin['hour'] >= 3) & (df_consos_magasin['hour'] <= 20), 'groupe_froid_positif'] = 0.3 * df_consos_magasin['p_w_m2']
        df_consos_magasin.loc[(df_consos_magasin['hour'] >= 3) & (df_consos_magasin['hour'] <= 20), 'eclairage'] = 0.1 * df_consos_magasin['p_w_m2']
        df_consos_magasin.loc[(df_consos_magasin['hour'] >= 3) & (df_consos_magasin['hour'] <= 20), 'chauffage'] = 0.2 * df_consos_magasin['p_w_m2']

        df_consos_magasin.loc[(df_consos_magasin['hour'] < 3) | (df_consos_magasin['hour'] > 20), 'groupe_froid_negatif'] = 0.5 * df_consos_magasin['p_w_m2']
        df_consos_magasin.loc[(df_consos_magasin['hour'] < 3) | (df_consos_magasin['hour'] > 20), 'groupe_froid_positif'] = 0.35 * df_consos_magasin['p_w_m2']
        df_consos_magasin.loc[(df_consos_magasin['hour'] < 3) | (df_consos_magasin['hour'] > 20), 'chauffage'] = 0.1 * df_consos_magasin['p_w_m2']

        df_consos_magasin['autres'] = df_consos_magasin['p_w_m2'] - df_consos_magasin['groupe_froid_negatif'] - df_consos_magasin['groupe_froid_positif'] - df_consos_magasin['eclairage'] - df_consos_magasin['chauffage']

    # Round the values
    df_consos_magasin['groupe_froid_negatif'] = round(df_consos_magasin['groupe_froid_negatif'], 1)
    df_consos_magasin['groupe_froid_positif'] = round(df_consos_magasin['groupe_froid_positif'], 1)
    df_consos_magasin['eclairage'] = round(df_consos_magasin['eclairage'], 1)
    df_consos_magasin['chauffage'] = round(df_consos_magasin['chauffage'], 1)
    df_consos_magasin['climatisation'] = round(df_consos_magasin['climatisation'], 1)
    df_consos_magasin['autres'] = round(df_consos_magasin['autres'], 1)

    return df_consos_magasin
