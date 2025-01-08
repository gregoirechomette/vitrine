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

    st.markdown("<p style='text-align: center;'> Positionnement de la fraction de gaz dans le mix énergétique de mon site par rapport aux autres sites de ma région et de l\'ensemble des sites du parc. Possibilité également de choisir des sites spécifiques pour comparaison dans la colonne de gauche. Evaluation par rapport à la moyenne nationale et le top 20%.</p>", unsafe_allow_html=True)
    st.text("")
    df_magasin_principal = df_base_magasins[df_base_magasins['code'] == code_principal]

    col1_0, col1_1, col1_2, col1_3, col1_4 = st.columns([2,4,4,4,1])

    col1_1.metric(" Fraction de gaz de mon mix énergie", '\u2001\u2001\u2001\u2001\u2001\u2001' + str(round(df_magasin_principal['gaz_fraction'].sum(),1)) + " %")
    col1_2.metric(" Consommation de gaz (2023)", '\u2001\u2001\u2001' + str(round(df_magasin_principal['conso_gaz_2023_mwh'].sum())) + " MWh")
    col1_3.metric(" Emmissions liées au gaz (2023)", '\u2001\u2001\u2001' + str(round(0.001 * 227 * df_magasin_principal['conso_gaz_2023_mwh'].sum())) + " tCO2")

    return

def figure_nuage_points(df_base_magasins, seuil=0.2, code_principal=104, codes_comparatifs=[101,103]):

    # Pick the appropriate column
    col_y = 'gaz_fraction'
    
    # Create an empty figure
    fig = go.Figure()
    
    # Add horizontal lines for the quantile and mean
    fig.add_hline(y=df_base_magasins[df_base_magasins['pv'] == 'Non'][col_y].quantile(seuil), line_dash='dash', line_color='grey',
                  annotation_text=f'Limite top 20%: {round(df_base_magasins[df_base_magasins["pv"] == "Non"][col_y].quantile(seuil), 1)} %', annotation_position='top right')
    fig.add_hline(y=df_base_magasins[df_base_magasins['pv'] == 'Non'][col_y].mean(), line_dash='dash', line_color='grey',
                  annotation_text=f'Moyenne: {round(df_base_magasins[df_base_magasins["pv"] == "Non"][col_y].mean(), 1)} %', annotation_position='top right')
    
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
        customdata=df_other_magasins[['num_magasin', 'region', 'surface_com_m2', col_y]],
        name='Autres sites',
        hovertemplate="<b>Numéro du site</b>: %{customdata[0]}<br>" \
                      "<b>SCA</b>: %{customdata[1]}<br>" \
                      "<b>Surface commerciale [m²]</b>: %{customdata[2]}<br>" \
                      "<b>Fraction de gaz dans le mix énergétique (%)</b>: %{customdata[3]}<br>" 
    ))
    
    # Plot points for 'region'
    fig.add_trace(go.Scatter(
        x=df_magasins_sca['surface_com_m2'],
        y=df_magasins_sca[col_y],
        mode='markers',
        marker=dict(size=8, color='#f18e00', opacity=0.9, line=dict(width=0.5, color='grey')),
        customdata=df_magasins_sca[['num_magasin', 'region', 'surface_com_m2', col_y]],
        name='Sites en ' + str(region),
        hovertemplate="<b>Numéro du site</b>: %{customdata[0]}<br>" \
                      "<b>SCA</b>: %{customdata[1]}<br>" \
                      "<b>Surface commerciale [m²]</b>: %{customdata[2]}<br>" \
                      "<b>Fraction de gaz dans le mix énergétique (%)</b>: %{customdata[3]}<br>" 
    ))

    # Plot points for 'comparatifs'
    fig.add_trace(go.Scatter(
        x=df_magasins_comparatifs['surface_com_m2'],
        y=df_magasins_comparatifs[col_y],
        mode='markers',
        marker=dict(size=8, color='#6cc24a', opacity=0.9, line=dict(width=1, color='grey')),
        customdata=df_magasins_comparatifs[['num_magasin', 'region', 'surface_com_m2', col_y]],
        name='Sites comparatifs',
        hovertemplate="<b>Numéro du site</b>: %{customdata[0]}<br>" \
                      "<b>SCA</b>: %{customdata[1]}<br>" \
                      "<b>Surface commerciale [m²]</b>: %{customdata[2]}<br>" \
                      "<b>Fraction de gaz dans le mix énergétique (%)</b>: %{customdata[3]}<br>" 
    ))
    
    # Plot points for 'principal'
    fig.add_trace(go.Scatter(
        x=df_magasin_principal['surface_com_m2'],
        y=df_magasin_principal[col_y],
        mode='markers',
        marker=dict(size=8, color='#005abb', opacity=0.9, line=dict(width=1, color='grey')),
        customdata=df_magasin_principal[['num_magasin', 'region', 'surface_com_m2', col_y]],
        name='Mon site',
        hovertemplate="<b>Numéro du site</b>: %{customdata[0]}<br>" \
                      "<b>SCA</b>: %{customdata[1]}<br>" \
                      "<b>Surface commerciale [m²]</b>: %{customdata[2]}<br>" \
                      "<b>Fraction de gaz dans le mix énergétique (%)</b>: %{customdata[3]}<br>" 
    ))
    
    # Update layout
    fig.update_layout(
        xaxis=dict(showgrid=True,gridcolor='LightPink',  gridwidth=1, title=dict(text='Surface [m²] (ou équivalent)', font=dict(size=16))),
        yaxis=dict(showgrid=True,gridcolor='LightGray', gridwidth=1, title=dict(text='Fraction de gaz dans le mix énergétique [%]', font=dict(size=16))),
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
    fig.update_yaxes(range=[-5, 55], gridcolor='lightgrey')

    st.plotly_chart(fig)

    return
