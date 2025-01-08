import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium

import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go



def big_numbers_nuage_points(df_base_magasins, code_principal='0104'):

    st.markdown("<p style='text-align: center;'> Positionnement de la performance énergétique au m² de mon site par rapport à la performance des autres sites de ma région et de l\'ensemble des sites du parc. Possibilité également de choisir des sites spécifiques pour comparaison dans la colonne de gauche. Evaluation par rapport à la moyenne nationale, et calcul des économies potentielles en se basant sur la performance du 20% des sites les plus performants.</p>", unsafe_allow_html=True)
    st.text("")
    df_magasin_principal = df_base_magasins[df_base_magasins['code'] == code_principal]

    # col_0, col_1, col_2 = st.columns([2, 8, 30])

    # with col_1:
    #     mode = st.radio("Choisir le type de comparaison", ('Éléctricité + gaz', 'Éléctricité uniquement'), label_visibility="visible")

    # if mode == 'Éléctricité uniquement':
    #     mode_output = 'elec'
    # else:
    #     mode_output = 'energie'

    mode_output = 'energie'

    # with col_2:
    
    col1_0, col1_1, col1_2, col1_3, col1_4 = st.columns([2,4,4,4,1])
    if mode_output == 'elec':
        col1_1.metric("\u2001\u2001Economies éléctriques potentielles [1]", '\u2001\u2001' + str(round(df_magasin_principal['potentiel_economies_mwh_elec'].sum())) + " MWh/an", str(round(-100 * df_magasin_principal['potentiel_economies_mwh_elec'].sum() / df_magasin_principal['conso_elec_2023_mwh'].sum())) + " %")
        col1_2.metric("Economies financières potentielles [1]", '\u2001\u2001\u2001' + str(round(df_magasin_principal['potentiel_economies_keuros_elec'].sum(),2)) + " k€/an", str(round(-100 * df_magasin_principal['potentiel_economies_mwh_elec'].sum() / df_magasin_principal['conso_elec_2023_mwh'].sum())) + " %")
        col1_3.metric("\u2001\u2001\u2001\u2001Economies CO2 potentielles [1]", '\u2001' + str(round(df_magasin_principal['potentiel_economies_tC02_elec'].sum(),1 )) + " tCO2/an", str(round(-100 * df_magasin_principal['potentiel_economies_mwh_elec'].sum() / df_magasin_principal['conso_elec_2023_mwh'].sum())) + " %")
    else:   
        col1_1.metric("\u2001\u2001Economies énergétiques potentielles [1]", '\u2001\u2001\u2001' + str(round(df_magasin_principal['potentiel_economies_mwh_energie'].sum())) + " MWh/an", str(round(-100 * df_magasin_principal['potentiel_economies_mwh_energie'].sum() / df_magasin_principal['conso_energie_2023_mwh'].sum())) + " %")
        col1_2.metric("Economies financières potentielles [1]", '\u2001\u2001\u2001' + str(round(df_magasin_principal['potentiel_economies_keuros_energie'].sum(),2)) + " k€/an", str(round(-100 * df_magasin_principal['potentiel_economies_mwh_energie'].sum() / df_magasin_principal['conso_energie_2023_mwh'].sum())) + " %")
        col1_3.metric("\u2001\u2001\u2001\u2001Economies CO2 potentielles [1]", '\u2001' + str(round(df_magasin_principal['potentiel_economies_tC02_energie'].sum(),1 )) + " tCO2/an", str(round(-100 * df_magasin_principal['potentiel_economies_mwh_energie'].sum() / df_magasin_principal['conso_energie_2023_mwh'].sum())) + " %")
    st.text("")


    return mode_output

def figure_nuage_points(df_base_magasins, seuil=0.2, col_y='conso_elec_mwh_par_m2_corrigee', code_principal=104, codes_comparatifs=[101,103], mode='elec'):

    if mode == 'elec':
        col_y = 'conso_elec_2023_mwh_par_m2_corrigee'
        col_y_economies = 'potentiel_economies_mwh_elec'
    else:
        col_y = 'conso_energie_2023_mwh_par_m2_corrigee'
        col_y_economies = 'potentiel_economies_mwh_energie'

    # Create an empty figure
    fig = go.Figure()
    
    # Add horizontal lines for the quantile and mean
    fig.add_hline(y=df_base_magasins[df_base_magasins['pv'] == 'Non'][col_y].quantile(seuil), line_dash='dash', line_color='grey',
                  annotation_text=f'Limite top 20%: {round(df_base_magasins[df_base_magasins["pv"] == "Non"][col_y].quantile(seuil), 2)} MWh/m²', annotation_position='top right')
    fig.add_hline(y=df_base_magasins[df_base_magasins['pv'] == 'Non'][col_y].mean(), line_dash='dash', line_color='grey',
                  annotation_text=f'Moyenne: {round(df_base_magasins[df_base_magasins["pv"] == "Non"][col_y].mean(), 2)} MWh/m²', annotation_position='top right')
    
    # Separate points based on 'Code panonceau' column
    region = df_base_magasins[df_base_magasins['code'] == code_principal]['region'].values[0]
    df_magasin_principal = df_base_magasins[df_base_magasins['code'] == code_principal]
    df_magasins_comparatifs = df_base_magasins[df_base_magasins['code'].isin(codes_comparatifs)]
    df_magasins_sca = df_base_magasins[df_base_magasins['region'] == region]
    df_other_magasins = df_base_magasins[~df_base_magasins['code'].isin([code_principal] + codes_comparatifs)]
    
    # Plot points for 'others'
    fig.add_trace(go.Scatter(
        x=df_other_magasins['surface_com_m2'],
        y=df_other_magasins[col_y],
        mode='markers',
        marker=dict(size=7, color='grey', opacity=0.2, line=dict(width=0.5, color='grey')),
        customdata=df_other_magasins[['num_magasin', 'region', 'surface_com_m2', col_y, col_y_economies]],
        name='Autres sites',
        hovertemplate="<b>Numéro du site</b>: %{customdata[0]}<br>" \
                      "<b>Region</b>: %{customdata[1]}<br>" \
                      "<b>Surface commerciale [m²]</b>: %{customdata[2]}<br>" \
                      "<b>Conso annuelle normalisée corrigée [MWh/m²]</b>: %{customdata[3]}<br>" \
                      "<b>Potentielles économies [MWh]</b>: %{customdata[4]}<br>"
    ))
    
    # Plot points for 'SCA'
    fig.add_trace(go.Scatter(
        x=df_magasins_sca['surface_com_m2'],
        y=df_magasins_sca[col_y],
        mode='markers',
        marker=dict(size=8, color='#f18e00', opacity=0.9, line=dict(width=0.5, color='grey')),
        customdata=df_magasins_sca[['num_magasin', 'region', 'surface_com_m2', col_y, col_y_economies]],
        name='Sites en ' + str(region),
        hovertemplate="<b>Numéro du site</b>: %{customdata[0]}<br>" \
                      "<b>Region</b>: %{customdata[1]}<br>" \
                      "<b>Surface commerciale [m²]</b>: %{customdata[2]}<br>" \
                      "<b>Conso électrique annuelle normalisée corrigée [MWh/m²]</b>: %{customdata[3]}<br>" \
                      "<b>Potentielles économies [MWh]</b>: %{customdata[4]}<br>"
    ))

    # Plot points for 'comparatifs'
    fig.add_trace(go.Scatter(
        x=df_magasins_comparatifs['surface_com_m2'],
        y=df_magasins_comparatifs[col_y],
        mode='markers',
        marker=dict(size=8, color='#6cc24a', opacity=0.9, line=dict(width=1, color='grey')),
        customdata=df_magasins_comparatifs[['num_magasin', 'region', 'surface_com_m2', col_y, col_y_economies]],
        name='Sites comparatifs',
        hovertemplate="<b>Numéro du site</b>: %{customdata[0]}<br>" \
                      "<b>Region</b>: %{customdata[1]}<br>" \
                      "<b>Surface commerciale [m²]</b>: %{customdata[2]}<br>" \
                      "<b>Conso électrique annuelle normalisée corrigée [MWh/m²]</b>: %{customdata[3]}<br>" \
                      "<b>Potentielles économies [MWh]</b>: %{customdata[4]}<br>"
    ))
    
    # Plot points for 'principal'
    fig.add_trace(go.Scatter(
        x=df_magasin_principal['surface_com_m2'],
        y=df_magasin_principal[col_y],
        mode='markers',
        marker=dict(size=8, color='#005abb', opacity=0.9, line=dict(width=1, color='grey')),
        customdata=df_magasin_principal[['num_magasin', 'region', 'surface_com_m2', col_y, col_y_economies]],
        name='Mon site',
        hovertemplate="<b>Numéro du site</b>: %{customdata[0]}<br>" \
                      "<b>Region</b>: %{customdata[1]}<br>" \
                      "<b>Surface commerciale [m²]</b>: %{customdata[2]}<br>" \
                      "<b>Conso électrique annuelle normalisée corrigée [MWh/m²]</b>: %{customdata[3]}<br>" \
                      "<b>Potentielles économies [MWh]</b>: %{customdata[4]}<br>"
    ))
    
    # Update layout
    fig.update_layout(
        xaxis=dict(showgrid=True,gridcolor='LightPink',  gridwidth=1, title=dict(text='Surface [m²] (ou équivalent)', font=dict(size=16))),
        yaxis=dict(showgrid=True,gridcolor='LightGray', gridwidth=1, title=dict(text='Consommation en 2023 [MWh/m²][2]', font=dict(size=16))),
        height=550,
        margin=dict(l=20, r=20, t=0, b=100),
        plot_bgcolor='#F6F6F6',
        legend=dict(orientation="v", xanchor='right', x=1.0, y=0.9, font=dict(size=14)),
        hovermode='closest',
        coloraxis_colorbar=dict(title='Économies annuelles potentielles [GWh]', xanchor='right', x=1.15),
        legend_traceorder="reversed",
    )
    
    # Add annotation for horizontal legend
    fig.add_annotation(dict(font=dict(color="black", size=12),
                            x=1.06, y=0.5, showarrow=False,
                            text='Économies annuelles potentielles [GWh]', textangle=-90,
                            xref="paper", yref="paper", font_size=15))
    
    fig.update_coloraxes(colorscale='Reds')
    
    # Setting the y-axis range
    fig.update_xaxes(gridcolor='lightgrey')
    if mode == 'elec':
        fig.update_yaxes(range=[0, 1], gridcolor='lightgrey')
    else:
        fig.update_yaxes(range=[0, 1.2], gridcolor='lightgrey')
    
    st.plotly_chart(fig)

    return

def expander_nuage_points(euros_mwh, tCO2_gwh, mode='elec'):

    if mode == 'elec':

        with st.expander("Hypothèses"):

            st.write('[1] En suppposant que le magasin arrive à baisser sa consommation au niveau du top 20%, et avec des hypothèses d\'un prix de ' + str(euros_mwh) + '€/MWh électrique et un facteur d\'émission de '  + str(tCO2_gwh) + ' tCO2/GWh électrique.')
            st.write('[2] Les consommations ont été corrigées pour prendre trois facteurs en considération: 1) la surface commerciale: pour chaque 1000 m² supplémentaire de surface commerciale, la consommation électrique diminue de 0.008 [MWh/m²]; 2) le climat: pour chaque degré de température extérieure moyenne en plus, la consommation électrique augmente de 0.016 [MWh/m²]; 3) l\'ouverture le dimanche: pour les magasins ouverts le dimanche, la consommation électrique augmente en moyenne de 3%.')

    else:
        with st.expander("Hypothèses"):
            st.write('[1] En suppposant que le magasin arrive à baisser sa consommation au niveau du top 20%, et avec des hypothèses d\'un prix de ' + str(euros_mwh) + '€/MWh électrique, 101 €/MWh de gaz, un facteur d\'émission de '  + str(tCO2_gwh) + ' tCO2/GWh électrique et 227 tCO2/GWh pour le gaz. Pour arriver au niveau du top 20%, on suppose que le magasin baisse sa consommation d\'éléctricité et de gaz dans les mêmes proportions.')
            st.write('[2] Les consommations ont été corrigées pour prendre trois facteurs en considération: 1) la surface commerciale: pour chaque 1000 m² supplémentaire de surface commerciale, la consommation énergétique diminue de 0.006 [MWh/m²]; 2) le climat: pour chaque degré de température extérieure moyenne en plus, la consommation énergétique augmente de 0.006 [MWh/m²]; 3) l\'ouverture le dimanche: pour les magasins ouverts le dimanche, la consommation énergétique augmente en moyenne de 3%.')

    return