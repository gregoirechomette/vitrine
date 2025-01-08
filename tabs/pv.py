import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium

import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go



def plot_pv_forecast(df_consos, df_carte_identite, df_solar, code_principal='0104'):

    st.markdown("<h4 style='text-align: center;'>Aperçu des bénéfices d'une centrale solaire</h4>", unsafe_allow_html=True)
    st.text("")
    col1, col2 = st.columns([1,6])


    # Create the slider
    with col1:
        pv_sizing_option = st.radio("Dimensionner avec:",
                                    ["Puissance", "Surface"],)
    with col2:
        if pv_sizing_option == 'Surface':
            selected_surface_value = st.select_slider('Selectionner la surface de parking avec panneaux solaires (m²)', options=[x * 100 for x in range(5, 81)], value=3000)
            selected_power_value = selected_surface_value * 220 * 1e-6
        else:
            selected_power_value = st.select_slider('Selectionner la puissance de la centrale installée (MWc)', options=[round(x * 0.1, 1) for x in range(1, 21)], value=1)

    df_consos_all = df_consos.copy()
    
    # Find the year as the last 4 characters of 'clean_month'
    df_consos_all['year'] = df_consos_all['clean_month'].str[-4:]
    df_consos_all = df_consos_all[df_consos_all['year'] == '2023']

    # Return selected_power_value
    df_magasin_principal = df_consos_all[df_consos_all['code'] == code_principal]
    df_base_magasin = df_carte_identite[df_carte_identite['code'] == code_principal]

    # Create a new colum 'p_w' by multiplying 'p_w_m2' by the selected surface
    df_magasin_principal['p_w'] = df_magasin_principal['p_w_m2'] * df_base_magasin['surface_com_m2'].values[0]

    # Merge the two dataframes
    df_magasin_principal = df_magasin_principal.merge(df_solar, on=['clean_month', 'clean_hour'], how='left')\
    
    # Rename the consumption column
    df_magasin_principal.rename(columns={'p_w': 'conso_w'}, inplace=True)

    # Now calculate the solar production for the selected power value
    df_magasin_principal['prod_w'] = 1000 * selected_power_value * df_magasin_principal['prod_w']

    # Now I would like to calculate the autoconsommation, soutirage and surplus
    df_magasin_principal['autoconso_w'] = df_magasin_principal[['conso_w', 'prod_w']].min(axis=1)
    df_magasin_principal['soutirage_w'] = df_magasin_principal['conso_w'] - df_magasin_principal['autoconso_w']
    df_magasin_principal['surplus_w'] = df_magasin_principal['prod_w'] - df_magasin_principal['autoconso_w']

    # Calculate some indicators for the selected power value
    taux_autoconso = 100 * df_magasin_principal['autoconso_w'].sum() / df_magasin_principal['prod_w'].sum()
    taux_couverture = 100 * df_magasin_principal['prod_w'].sum() / df_magasin_principal['conso_w'].sum()
    energie_autoconsommee_mwh = 1e-6 * df_magasin_principal['autoconso_w'].sum() * (52/12)

    # Create metrics for the selected power value
    col0, col1, col2, col3, col4 = st.columns([3,4,4,4,1])
    with col1:
        st.metric("Taux d'autoconsommation", str(round(taux_autoconso,1)) + " %")
    with col2:
        st.metric("Taux de couverture", str(round(taux_couverture,1)) + " %")
    with col3:
        st.metric("Energie autoconsommée", str(round(energie_autoconsommee_mwh,1)) + " MWh")

    # Plot février 2023
    plot_week_pv(df_magasin_principal[df_magasin_principal['clean_month'] == 'Février 2023'], name='Semaine représentative en hiver')
    plot_week_pv(df_magasin_principal[df_magasin_principal['clean_month'] == 'Juillet 2023'], name='Semaine représentative en été')


    return



def plot_week_pv(df_magasin_principal_month, name= 'Mois sélectionné'):

    # Create a bar plot (stacked vertically) for a week in Fevrier 2023
    custom_colors = {"autoconso_w": px.colors.qualitative.Plotly[9], "soutirage_w": px.colors.qualitative.Set1[0],  "surplus_w": px.colors.qualitative.Set1[1] }

    fig = px.bar(df_magasin_principal_month, x='clean_hour', y=['autoconso_w', 'soutirage_w', 'surplus_w'], title='Semaine moyenne en Février 2023', labels={'value': 'Energie [W]', 'variable': ' '}, color_discrete_map=custom_colors, barmode='relative')

    # Update the layout
    fig.update_layout(title=name, title_x=0.4, height=550, showlegend=True, margin=dict(l=20, r=20, t=80, b=20),
                      legend=dict(orientation='h', yanchor="top", y=1.1, xanchor="right", x=0.99), )

    # Change xlabel
    fig.update_xaxes(title_text=" ", title_font=dict(size=12), showticklabels=True, tickfont=dict(size=16), 
                      ticktext=['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'], 
                      tickvals=['Lundi 12h', 'Mardi 12h', 'Mercredi 12h', 'Jeudi 12h', 'Vendredi 12h', 'Samedi 12h', 'Dimanche 12h'], side='bottom')

    # Change the name of the labels in the legend
    fig.for_each_trace(lambda t: t.update(name=t.name.replace("_w", " [W]")))


    st.plotly_chart(fig)

