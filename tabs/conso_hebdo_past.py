import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium

import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go


# def plot_conso_hebdo(df_consos_all, df_base, df_stats_dimanche_ouvert, df_stats_dimanche_ferme, code_principal=104, magasins_comparatifs=[101,103], color_mean='blue', color_filled='blue'):
def plot_conso_hebdo(df_consos_all, df_consos_stats, df_carte_identite, code_principal='0104', magasins_comparatifs=['0101','0103'], dimanche_ouvert=0):

    st.write(" ")
    st.markdown("<p style='text-align: center;'> Profil des consommations électriques du magasin sur des semaines moyennes. Le magasin peut se comparer à lui même dans le passé en selectionnant des mois au choix. </p>", unsafe_allow_html=True)
    st.write(" ")

    options_mois = ['Avril 2022', 'Mai 2022', 
                    'Juin 2022', 'Juillet 2022', 'Août 2022', 'Septembre 2022', 'Octobre 2022', 'Novembre 2022', 'Décembre 2022', 
                    'Janvier 2023', 'Février 2023', 'Mars 2023', 'Avril 2023', 'Mai 2023', 'Juin 2023', 
                    'Juillet 2023', 'Août 2023', 'Septembre 2023', 'Octobre 2023', 'Novembre 2023', 'Décembre 2023', 'Janvier 2024']

    # Provide two columns for the selection of the months
    col1, col2 = st.columns(2)
    with col1:
        mois_1 = st.selectbox("Selectionner le premier mois",(options_mois),index=0, label_visibility='collapsed')
    with col2:
        mois_2 = st.selectbox("Selectionner le deuxième mois",(options_mois),index=12, label_visibility='collapsed')


    # Slice the dataframes to retrieve month 1 and 2
    df_consos_all_month_1 = df_consos_all[((df_consos_all['clean_month'] == mois_1) & (df_consos_all['code'] == code_principal))].copy()
    df_consos_all_month_2 = df_consos_all[((df_consos_all['clean_month'] == mois_2) & (df_consos_all['code'] == code_principal))].copy()

    # Add a correction factor to account for the change in the consumption
    pen_factor_mag = df_carte_identite[df_carte_identite['code'] == code_principal]['conso_elec_2023_mwh_par_m2_corrigee'].values[0] / df_carte_identite[df_carte_identite['code'] == code_principal]['conso_elec_2023_mwh_par_m2'].values[0]

    # Just define a px plot, add things later only with fig.add_scatter
    fig = px.scatter()
    fig.add_scatter(x=df_consos_all_month_2['clean_hour'], y=round(pen_factor_mag * df_consos_all_month_2['p_w_m2'],1), mode='lines', name=mois_2, line=dict(color='#005abb', width=2))
    fig.add_scatter(x=df_consos_all_month_1['clean_hour'], y=round(pen_factor_mag * df_consos_all_month_1['p_w_m2'],1), mode='lines', name=mois_1, line=dict(color='#f18e00', width=2))

    fig.update_xaxes(title_text=" ", title_font=dict(size=12), showticklabels=True, tickfont=dict(size=16), 
                     ticktext=['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'], 
                     tickvals=['Lundi 12h', 'Mardi 12h', 'Mercredi 12h', 'Jeudi 12h', 'Vendredi 12h', 'Samedi 12h', 'Dimanche 12h'], side='bottom')

    # Define the y limits
    y_max = max(df_consos_all_month_1['p_w_m2'].max(), df_consos_all_month_2['p_w_m2'].max())
    fig.update_yaxes(range=[0, max(120, 1.1 * y_max)], title='Puissance [W/m²]')
    
    # Update layout
    fig.update_layout(title=' ', title_x=0.5, height=550, showlegend=True, margin=dict(l=20, r=20, t=80, b=20),
                      legend=dict(orientation='h', yanchor="top", y=1.05, xanchor="right", x=0.99), hovermode='x unified')
    
    st.plotly_chart(fig)

    return