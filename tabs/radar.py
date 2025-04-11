import numpy as np
import pandas as pd

import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go




def plot_radar(df_radar, df_carte_identite, code_principal='0101', mode_groupe=False):

    if mode_groupe:
        st.markdown("<p style='text-align: center;'> Analyse des consommations électriques moyennes sur 6 moments clés de l\'année (semaines de février, avril et juillet, en journée et de nuit). Les unités du graphique ci-desous représentent la consommation en W/m².</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='text-align: center;'> Analyse des consommations électriques du site sur 6 moments clés de l\'année (semaines de février, avril et juillet, en journée et de nuit). Comparaison aux sites dans le top 20-80%, ainsi que la moyenne. Les unités du graphique ci-desous représentent la consommation en W/m². Plus le site est efficace, plus les points bleus se rapprochent du centre.</p>", unsafe_allow_html=True)

    categories = ['Hiver Nuit','Intersaison Nuit', 'Ete Nuit', 'Ete Jour', 'Intersaison Jour', 'Hiver Jour', 'Hiver Nuit']

    # Slice the dataframe
    df_magasin = df_radar[df_radar['code'] == code_principal]

    pen_factor_mag = df_carte_identite[df_carte_identite['code'] == code_principal]['conso_elec_2023_mwh_par_m2_corrigee'].values[0] / df_carte_identite[df_carte_identite['code'] == code_principal]['conso_elec_2023_mwh_par_m2'].values[0]

    # Calculate some metrics 
    df_radar_med = df_radar.drop(columns=['code']).quantile(0.5)
    df_radar_q20 = df_radar.drop(columns=['code']).quantile(0.2)
    df_radar_q80 = df_radar.drop(columns=['code']).quantile(0.8)
    
    # Upper bound and lower bound
    lower_bound = [df_radar_q20[3], df_radar_q20[5], df_radar_q20[1], df_radar_q20[0], df_radar_q20[4], df_radar_q20[2], df_radar_q20[3]]
    upper_bound = [df_radar_q80[3], df_radar_q80[5], df_radar_q80[1], df_radar_q80[0], df_radar_q80[4], df_radar_q80[2], df_radar_q80[3]]
    moyenne = [df_radar_med[3], df_radar_med[5], df_radar_med[1], df_radar_med[0], df_radar_med[4], df_radar_med[2], df_radar_med[3]]

    # Instantiate the figure
    fig = go.Figure()

    # Plot mean, lower and upper bounds
    fig.add_trace(go.Scatterpolar(r=moyenne,theta=categories,name='Moyenne',line=dict(color=px.colors.qualitative.Pastel2[7], dash='dashdot')))
    fig.add_trace(go.Scatterpolar(r=lower_bound,theta=categories, name='Top 20%', line=dict(color=px.colors.qualitative.Pastel2[0], dash='dash')))
    fig.add_trace(go.Scatterpolar(r=upper_bound,theta=categories, name='Top 80%', line=dict(color=px.colors.qualitative.Pastel1[0], dash='dash')))

    couleur_principale = '#005abb'
    

    if mode_groupe:
        pass
    else:
        fig.add_trace(go.Scatterpolar(r=[pen_factor_mag * df_magasin['p_w_m2_hiver_nuit'].values[0], pen_factor_mag * df_magasin['p_w_m2_hiver_nuit'].values[0]],
                                            theta=['Hiver Nuit', 'Hiver Nuit'], name='Mon site', line=dict(color=couleur_principale, width=0), showlegend=False))
        fig.add_trace(go.Scatterpolar(r=[pen_factor_mag * df_magasin['p_w_m2_intersaison_nuit'].values[0], pen_factor_mag * df_magasin['p_w_m2_intersaison_nuit'].values[0]],
                                            theta=['Intersaison Nuit', 'Intersaison Nuit'], name='Mon site', line=dict(color=couleur_principale, width=0), showlegend=True))
        fig.add_trace(go.Scatterpolar(r=[pen_factor_mag * df_magasin['p_w_m2_ete_nuit'].values[0], pen_factor_mag * df_magasin['p_w_m2_ete_nuit'].values[0]],
                                            theta=['Ete Nuit', 'Ete Nuit'], name='Mon site', line=dict(color=couleur_principale, width=0), showlegend=False))
        fig.add_trace(go.Scatterpolar(r=[pen_factor_mag * df_magasin['p_w_m2_hiver_jour'].values[0], pen_factor_mag * df_magasin['p_w_m2_hiver_jour'].values[0]],
                                            theta=['Hiver Jour', 'Hiver Jour'], name='Mon site', line=dict(color=couleur_principale, width=0), showlegend=False))
        fig.add_trace(go.Scatterpolar(r=[pen_factor_mag * df_magasin['p_w_m2_intersaison_jour'].values[0], pen_factor_mag * df_magasin['p_w_m2_intersaison_jour'].values[0]],
                                            theta=['Intersaison Jour', 'Intersaison Jour'], name='Mon site', line=dict(color=couleur_principale, width=0), showlegend=False))
        fig.add_trace(go.Scatterpolar(r=[pen_factor_mag * df_magasin['p_w_m2_ete_jour'].values[0], pen_factor_mag * df_magasin['p_w_m2_ete_jour'].values[0]],
                                            theta=['Ete Jour', 'Ete Jour'], name='Mon site', line=dict(color=couleur_principale, width=0), showlegend=False))


    # Calculate the maximum
    max_polar = max(pen_factor_mag * df_magasin['p_w_m2_hiver_jour'].values[0], pen_factor_mag * df_magasin['p_w_m2_intersaison_jour'].values[0], pen_factor_mag * df_magasin['p_w_m2_ete_jour'].values[0])

    # Add hover info, name and value in the same way
    fig.update_traces(hoverinfo='name')
    fig.update_polars(sector=[-180,180], angularaxis=dict(direction="clockwise", rotation=-120))

    fig.update_layout(title=' ', title_x=0.3, width=1100, height=650, margin=dict(l=20, r=20, t=80, b=100),
                        polar=dict(radialaxis=dict(visible=True,range=[0, max(120, 1.1* max_polar)], gridcolor='#F6F6F6', gridwidth=0.1)),showlegend=True,)

    st.plotly_chart(fig)

    return fig