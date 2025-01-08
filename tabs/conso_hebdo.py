import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium

import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go


# def plot_conso_hebdo(df_consos_all, df_base, df_stats_dimanche_ouvert, df_stats_dimanche_ferme, code_panonceau=104, magasins_comparatifs=[101,103], color_mean='blue', color_filled='blue'):
def plot_conso_hebdo(df_consos_all, df_consos_stats, df_carte_identite, code_principal='0104', magasins_comparatifs=['0101','0103'], dimanche_ouvert=0):

    st.markdown("<p style='text-align: center;'> Profil des consommations électriques du site sur des semaines moyennes pour chaque mois au long de l\'année 2023. Comparaison aux sites dans le top 20-80% (zone hachurée), ainsi que la moyenne. Possibilité de se comparer directement à des sites spécifiques en les selectionnant dans la colonne de gauche. </p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'> Pour changer de mois, utiliser le curseur ci-dessous: </p>", unsafe_allow_html=True)

    # Mois a visualiser
    mois = st.select_slider(" ",
    options=['Janvier 2023', 'Février 2023', 'Mars 2023', 'Avril 2023', 'Mai 2023', 'Juin 2023', 'Juillet 2023', 'Août 2023', 'Septembre 2023', 'Octobre 2023', 'Novembre 2023', 'Décembre 2023'])

    # Slice the dataframes 
    df_consos_all_month = df_consos_all[((df_consos_all['clean_month'] == mois) & (df_consos_all['code'] == code_principal))].copy()
    df_consos_magasins_comparatifs_month = df_consos_all[((df_consos_all['clean_month'] == mois) & (df_consos_all['code'].isin(magasins_comparatifs)))].copy()
    df_consos_stats_month = df_consos_stats[(df_consos_stats['clean_month'] == mois) & (df_consos_stats['dimanche_ouvert'] == dimanche_ouvert)].copy()


    # Just define a px plot, add things later only with fig.add_scatter
    fig = px.scatter()

    # Adjust the consumption
    pen_factor_mag = df_carte_identite[df_carte_identite['code'] == code_principal]['conso_elec_2023_mwh_par_m2_corrigee'].values[0] / df_carte_identite[df_carte_identite['code'] == code_principal]['conso_elec_2023_mwh_par_m2'].values[0]

    fig.add_scatter(x=df_consos_stats_month['clean_hour'], y=round(df_consos_stats_month['p_w_m2_q20_norm'],1), mode='lines', name='Top 20%', line=dict(color='#D3D3D3', dash='dash'), showlegend=False)
    fig.add_scatter(x=df_consos_stats_month['clean_hour'], y=round(df_consos_stats_month['p_w_m2_q80_norm'] ,1), mode='lines', name='Top 20% - 80%', line=dict(color='#D3D3D3', dash='dash'), fill='tonexty', showlegend=True)
    fig.add_scatter(x=df_consos_stats_month['clean_hour'], y=round(df_consos_stats_month['p_w_m2_mean'],1), mode='lines', name='Moyenne globale', line=dict(color='#005abb', dash='dashdot'))

    fig.add_scatter(x=df_consos_all_month['clean_hour'], y=round(pen_factor_mag * df_consos_all_month['p_w_m2'],1), mode='lines', name='Mon site', line=dict(color='#005abb', width=2))

    colors_palette = ['#f18e00', '#6cc24a', '#374650', '#fa6e1e', '#7da055']
    for i, magasin in enumerate(magasins_comparatifs):
        pen_factor_mag_comp = df_carte_identite[df_carte_identite['code'] == magasin]['conso_elec_2023_mwh_par_m2_corrigee'].values[0] / df_carte_identite[df_carte_identite['code'] == magasin]['conso_elec_2023_mwh_par_m2'].values[0]
        df_magasin = df_consos_magasins_comparatifs_month[df_consos_magasins_comparatifs_month['code'] == magasin].copy()
        fig.add_scatter(x=df_magasin['clean_hour'], y=round(pen_factor_mag_comp * df_magasin['p_w_m2'],1), mode='lines', name= df_carte_identite[df_carte_identite['code'] == magasin]['num_magasin'].values[0], line=dict(color=colors_palette[i], width=2))
    
    fig.update_xaxes(title_text=" ", title_font=dict(size=12), showticklabels=True, tickfont=dict(size=16), 
                     ticktext=['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'], 
                     tickvals=['Lundi 12h', 'Mardi 12h', 'Mercredi 12h', 'Jeudi 12h', 'Vendredi 12h', 'Samedi 12h', 'Dimanche 12h'], side='bottom')

    # Define the y limits
    y_max = max(df_consos_all_month['p_w_m2'].max(), df_consos_magasins_comparatifs_month['p_w_m2'].max())
    fig.update_yaxes(range=[0, max(120, 1.1 * y_max)], title='Puissance [W/m²]')

    
    # Update layout
    fig.update_layout(title=' ', title_x=0.5, height=550, showlegend=True, margin=dict(l=20, r=20, t=80, b=20),
                      legend=dict(orientation='h', yanchor="top", y=1.05, xanchor="right", x=0.99), hovermode='x unified')
    
    st.plotly_chart(fig)

    return