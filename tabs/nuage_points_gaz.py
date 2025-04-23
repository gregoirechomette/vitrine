import numpy as np
import pandas as pd

import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go


def wrapper_nuage_points_gaz(df_base_magasins, code_principal='0104', codes_comparatifs=[101,103], seuil=0.2, mode_groupe=False):
    """
    Wrapper function to display the gas consumption analysis for a specific store and its comparatives.
    """
    
    if mode_groupe:
        big_numbers_nuage_points_gaz_groupe(df_base_magasins)
        figure_nuage_points_gaz_groupe(df_base_magasins)
        expander_nuage_points_gaz_magasin()
    
    else:   
        big_numbers_nuage_points_gaz_magasin(df_base_magasins, code_principal)
        figure_nuage_points_gaz_magasin(df_base_magasins, seuil, code_principal, codes_comparatifs)
        expander_nuage_points_gaz_magasin()

    return


def big_numbers_nuage_points_gaz_magasin(df_base_magasins, code_principal='0104'):

    st.markdown("<p style='text-align: center;'> Positionnement de la fraction de gaz dans le mix énergétique de mon site par rapport aux autres sites de ma région et de l\'ensemble des sites du parc. Possibilité également de choisir des sites spécifiques pour comparaison dans la colonne de gauche. Evaluation par rapport à la moyenne nationale et le top 20%.</p>", unsafe_allow_html=True)
    st.text("")
    df_magasin_principal = df_base_magasins[df_base_magasins['code'] == code_principal]

    col1_0, col1_1, col1_2, col1_3, col1_4 = st.columns([2,4,4,4,1])

    # Retrieve the important values
    fraction_gaz = round(df_magasin_principal['gaz_fraction'].sum())
    conso_gaz = round(df_magasin_principal['conso_gaz_2023_mwh'].sum())
    emmissions_gaz = round(0.001 * 227 * df_magasin_principal['conso_gaz_2023_mwh'].sum())
    
    # Show some indicators
    with col1_1:
        st.markdown(f"""
                <div style="text-align: center;">
                    Fraction de gaz (🛢️ vs ⚡)  <br>
                    <span style="font-size: 22px; font-weight: bold;">{fraction_gaz} %</span><br>
                </div>
                """, unsafe_allow_html=True)
        
    with col1_2:
        st.markdown(f"""
                <div style="text-align: center;">
                    Consommation de gaz 🔥  <br>
                    <span style="font-size: 22px; font-weight: bold;">{conso_gaz} MWh</span><br>
                </div>
                """, unsafe_allow_html=True)
        
    with col1_3:
        st.markdown(f"""
                <div style="text-align: center;">
                    Émissions liées au gaz 🌍 [1] <br>
                    <span style="font-size: 22px; font-weight: bold;">{emmissions_gaz} tCO2</span><br>
                </div>
                """, unsafe_allow_html=True)

    st.text("")
    
    return


def big_numbers_nuage_points_gaz_groupe(df_base_magasins):
    
    st.markdown("<p style='text-align: center;'> Positionnement de chaque site en fonction de sa fraction de gaz dans son mix énergétique. Calcul d'indicateurs à l\'échelle globale et coloration des points en fonction de la consommation totale de gaz annuelle. </p>", unsafe_allow_html=True)
    st.text("")
    
    col1_0, col1_1, col1_2, col1_3, col1_4 = st.columns([2,4,4,4,1])

    # Retrieve the important values
    fraction_gaz = round(df_base_magasins['gaz_fraction'].mean())
    conso_gaz_gwh = round(0.001 * df_base_magasins['conso_gaz_2023_mwh'].sum())
    emmissions_gaz_t_CO2 = round(0.001 * 227 * df_base_magasins['conso_gaz_2023_mwh'].sum())
    
    # Show some indicators
    with col1_1:
        st.markdown(f"""
                <div style="text-align: center;">
                    Fraction de gaz (🛢️ vs ⚡) <br>
                    <span style="font-size: 22px; font-weight: bold;">{fraction_gaz} %</span><br>
                    <span style="font-size: 14px; color: gray;">(moyenne)</span>
                </div>
                """, unsafe_allow_html=True)
        
    with col1_2:
        st.markdown(f"""
                <div style="text-align: center;">
                    Consommation de gaz 🔥 <br>
                    <span style="font-size: 22px; font-weight: bold;">{conso_gaz_gwh} GWh</span><br>
                    <span style="font-size: 14px; color: gray;">(total)</span>
                </div>
                """, unsafe_allow_html=True)
        
    with col1_3:
        st.markdown(f"""
                <div style="text-align: center;">
                    Émissions liées au gaz 🌍 [1] <br>
                    <span style="font-size: 22px; font-weight: bold;">{emmissions_gaz_t_CO2} tCO2</span><br>
                    <span style="font-size: 14px; color: gray;">(total)</span>
                </div>
                """, unsafe_allow_html=True)

    st.text("")
    
    return


def figure_nuage_points_gaz_magasin(df_base_magasins, seuil=0.2, code_principal=104, codes_comparatifs=[101,103]):

    # Pick the appropriate column
    col_y = 'gaz_fraction'
    
    # Create an empty figure
    fig = go.Figure()
    
    # Add horizontal lines for the quantile and mean
    # fig.add_hline(y=df_base_magasins[df_base_magasins['pv'] == 'Non'][col_y].quantile(seuil), line_dash='dash', line_color='grey',
    #               annotation_text=f'Limite top 20%: {round(df_base_magasins[df_base_magasins["pv"] == "Non"][col_y].quantile(seuil), 1)} %', annotation_position='top right')
    fig.add_hline(y=df_base_magasins[df_base_magasins['pv'] == 'Non'][col_y].mean(), line_dash='dash', line_color='grey',
                  annotation_text=f'Moyenne: {round(df_base_magasins[df_base_magasins["pv"] == "Non"][col_y].mean(), 1)} %', annotation_position='top right')
    
    # Slice dataframe based on different subsets
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
                      "<b>Région</b>: %{customdata[1]}<br>" \
                      "<b>Surface du site [m²]</b>: %{customdata[2]}<br>" \
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
                      "<b>Région</b>: %{customdata[1]}<br>" \
                      "<b>Surface du site [m²]</b>: %{customdata[2]}<br>" \
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
                      "<b>Région</b>: %{customdata[1]}<br>" \
                      "<b>Surface du site [m²]</b>: %{customdata[2]}<br>" \
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
                      "<b>Région</b>: %{customdata[1]}<br>" \
                      "<b>Surface du site [m²]</b>: %{customdata[2]}<br>" \
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

def figure_nuage_points_gaz_groupe(df_base_magasins):
    
    # Pick the appropriate column
    col_y = 'gaz_fraction'
    col_y_color = 'conso_gaz_2023_mwh'
    
    # Create an empty figure
    fig = go.Figure()
    
    # Add horizontal lines for the quantile and mean
    # fig.add_hline(y=df_base_magasins[df_base_magasins['pv'] == 'Non'][col_y].quantile(0.2), line_dash='dash', line_color='grey',
    #               annotation_text=f'Limite top 20%: {round(df_base_magasins[df_base_magasins["pv"] == "Non"][col_y].quantile(0.2), 1)} %', annotation_position='top right')
    fig.add_hline(y=df_base_magasins[df_base_magasins['pv'] == 'Non'][col_y].mean(), line_dash='dash', line_color='grey',
                  annotation_text=f'Moyenne: {round(df_base_magasins[df_base_magasins["pv"] == "Non"][col_y].mean(), 1)} %', annotation_position='top right')   
    
    # No slicing, plot the points all at once, color proportionnal to the gas fraction
    fig.add_trace(go.Scatter(
        x=df_base_magasins['surface_com_m2'],
        y=df_base_magasins[col_y],
        mode='markers',
        # marker=dict(size=8, color='#005abb', opacity=0.9, line=dict(width=1, color='grey')),
        marker=dict(size=7, color=df_base_magasins[col_y_color], colorscale='Reds', opacity=0.8, line=dict(width=0.5, color='grey')),
        customdata=df_base_magasins[['num_magasin', 'region', 'surface_com_m2', col_y, col_y_color]],
        name=' ',
        hovertemplate="<b>Numéro du site</b>: %{customdata[0]}<br>" \
                      "<b>Région</b>: %{customdata[1]}<br>" \
                      "<b>Surface du site [m²]</b>: %{customdata[2]}<br>" \
                      "<b>Fraction de gaz dans le mix énergétique [%]</b>: %{customdata[3]}<br>"  \
                    "<b>Consommation de gaz [MWh]</b>: %{customdata[4]}<br>" \
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


def expander_nuage_points_gaz_magasin():

    # Expander
    with st.expander("Hypothèses"):
        st.write('[1] La carbonation du gaz est fixée à 227 tCO2/GWh (ADEME)')
    return