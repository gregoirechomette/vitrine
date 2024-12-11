import numpy as np
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

import plotly.express as px
import plotly.graph_objects as go

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


def resume(df_base, magasin_principal, magasins_comparatifs):

    st.text("")
    
    col1, col2 = st.columns([2,3])

    df_base_magasin = df_base[df_base['num_magasin'] == magasin_principal]


    with col1:
        st.markdown("<h4 style='text-align: center;'>Mes données magasin</h4>", unsafe_allow_html=True)
        st.text("")
        st.write('Nom du manager:', df_base_magasin['manager'].values[0])
        st.write('Région:', df_base_magasin['region'].values[0])

        # st.write('Annee de construction:', str(df_base_magasin['annee_construction'].values[0]))
        st.write('Ouverture le dimanche:', str(df_base_magasin['dimanche_ouvert_str'].values[0]))
        st.write('Autoconsommation photovoltaique:', str(df_base_magasin['pv'].values[0]))

        # Surface commerciale
        st.write('Surface commerciale:', str(int(df_base_magasin['surface_com_m2'].values[0])), 'm²')

        st.write('Conso électrique (2023):', str(int(df_base_magasin['conso_elec_2023_mwh'].values[0])), 'MWh')
        st.write('Conso de gaz (2023):', str(int(df_base_magasin['conso_gaz_2023_mwh'].values[0])), 'MWh')
        st.write('Conso énergétique totale (2023):', str(int(df_base_magasin['conso_energie_2023_mwh'].values[0])), 'MWh')

        # Consommation par m²
        st.write('Conso énergétique par m² (2023):', str(round(df_base_magasin['conso_energie_2023_mwh_par_m2'].values[0],2)), 'MWh/m²')
        st.write('Conso énergétique par m² corrigée (2023):', str(round(df_base_magasin['conso_energie_2023_mwh_par_m2_corrigee'].values[0],2)), 'MWh/m²')


    with col2:

        # Definir la variable qui va colorer les points
        var_couleur = 'conso_energie_2023_mwh_par_m2_corrigee'

        # Bounds for the colorbar
        vmin = 0.25
        vmax = 0.9

        st.markdown("<h4 style='text-align: center;'>Ma situation géographique</h4>", unsafe_allow_html=True)
        st.text("")
        # folium_only_comparatifs = st.toggle('Afficher uniquement mon magasin et les magasins comparatifs', False)
        folium_only_comparatifs = False

        fig_map_conso = folium.Map(location=[df_base_magasin['latitude'].mean(), df_base_magasin['longitude'].mean()], zoom_start=8)
        code = df_base_magasin['code'].values[0]

        # Loop over all the magasins (df_base)
        if folium_only_comparatifs == False:

            for _, row in df_base.iterrows():

                # Determine color based on 'conso_elec_mwh_par_m2' value
                normalized_value = (row[var_couleur] - vmin) / (vmax - vmin) 

                if row['code'] != code:
                    # Add Circle marker (all magasins but the VIP one)
                    folium.Circle(
                        location=[row['latitude'], row['longitude']], radius=row['surface_com_m2'], 
                        color="grey", weight=1, fill_color=mcolors.rgb2hex(plt.get_cmap('seismic')(normalized_value)), fill_opacity=0.5,
                        tooltip=f"Num magasin: {row['num_magasin']}<br>Nom du manager: {row['manager']}<br>Surface commerciale: {int(row['surface_com_m2'])} m²<br>Consommation énergétique normalisée corrigée: {round(row[var_couleur],2)} MWh/m²",
                    ).add_to(fig_map_conso)

        # Loop over the magasins comparatifs only (df_magasins_comparatifs)
        else:
            df_magasins_comparatifs = df_base[df_base['num_magasin'].isin(magasins_comparatifs)]
            for _, row in df_magasins_comparatifs.iterrows():

                # Determine color based on 'conso_elec_mwh_par_m2' value
                normalized_value = (row[var_couleur] - vmin) / (vmax - vmin)  

                if row['code'] != code:
                    # Add Circle marker (all magasins but the VIP one)
                    folium.Circle(
                        location=[row['latitude'], row['longitude']], radius=row['surface_com_m2'], 
                        color="grey", weight=1, fill_color=mcolors.rgb2hex(plt.get_cmap('seismic')(normalized_value)), fill_opacity=0.5,
                        tooltip=f"Num magasin: {row['num_magasin']}<br>Nom du manager: {row['manager']}<br>Surface commerciale: {int(row['surface_com_m2'])} m²<br>Consommation énergétique normalisée corrigée: {round(row[var_couleur],2)} MWh/m²",
                    ).add_to(fig_map_conso)


        for _, row in df_base.iterrows():

            if row['code'] == code:

                # Determine color based on 'conso_elec_mwh_par_m2' value
                normalized_value = (row[var_couleur] - vmin) / (vmax - vmin) 
                folium.Circle(
                        location=[row['latitude'], row['longitude']], radius=row['surface_com_m2'], 
                        color="grey", weight=1, fill_color=mcolors.rgb2hex(plt.get_cmap('seismic')(normalized_value)), fill_opacity=0.5,
                        tooltip=f"Num magasin: {row['num_magasin']}<br>Nom du manager: {row['manager']}<br>Surface commerciale: {int(row['surface_com_m2'])} m²<br>Consommation énergétique normalisée corrigée: {round(row[var_couleur],2)} MWh/m²",
                    ).add_to(fig_map_conso)

        
        st_folium(fig_map_conso, height=400, width=720)
        st.image('./pictures/legend_folium.png')
        
    return
        
    