import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


def resume(df_base, magasin_principal, magasins_comparatifs):

    st.text("")
    
    col1, col2 = st.columns([9,11])

    df_base_magasin = df_base[df_base['num_magasin'] == magasin_principal]

    with col1:
        st.markdown("<h4 style='text-align: center;'>Mon site</h4>", unsafe_allow_html=True)
        st.text("")
        st.write('Nom du manager:', df_base_magasin['manager'].values[0])
        st.write('Région:', df_base_magasin['region'].values[0])

        # st.write('Annee de construction:', str(df_base_magasin['annee_construction'].values[0]))
        st.write('Ouverture le dimanche:', str(df_base_magasin['dimanche_ouvert_str'].values[0]))
        st.write('Autoconsommation photovoltaique:', str(df_base_magasin['pv'].values[0]))

        # Surface commerciale
        st.write('Surface (ou équivalent):', str(int(df_base_magasin['surface_com_m2'].values[0])), 'm²')

        st.write('Conso électrique (2023):', str(int(df_base_magasin['conso_elec_2023_mwh'].values[0])), 'MWh')
        st.write('Conso de gaz (2023):', str(int(df_base_magasin['conso_gaz_2023_mwh'].values[0])), 'MWh')
        st.write('Conso énergétique totale (2023):', str(int(df_base_magasin['conso_energie_2023_mwh'].values[0])), 'MWh')

        # Consommation par m²
        st.write('Conso énergétique par m² (2023):', str(round(df_base_magasin['conso_energie_2023_mwh_par_m2'].values[0],2)), 'MWh/m²')
        st.write('Conso énergétique par m² corrigée (2023):', str(round(df_base_magasin['conso_energie_2023_mwh_par_m2_corrigee'].values[0],2)), 'MWh/m²')


    with col2:
        
        # Title
        st.markdown("<h4 style='text-align: center;'>Ma situation géographique</h4>", unsafe_allow_html=True)
        st.text("")

        # Definir la variable qui va colorer les points
        var_couleur = 'conso_energie_2023_mwh_par_m2_corrigee'
        
        # Handle the colors
        cmap = matplotlib.colormaps["RdYlGn_r"] 
        norm = mcolors.Normalize(0.2, 0.8)
        df_base["color"] = df_base["conso_energie_2023_mwh_par_m2_corrigee"].apply(lambda x: 
                            [int(c*255) for c in cmap(norm(x))[:3]] + [180])  
        
        # Define a Pydeck layer
        layer = pdk.Layer("ScatterplotLayer", data=df_base,
            get_position=["longitude", "latitude"], get_radius="surface_com_m2", get_fill_color="color", 
            pickable=True, opacity=0.6, stroked=True,  
            get_line_color=[128, 128, 128], get_line_width=300)
        
        # Define the map view
        view_state = pdk.ViewState(
            latitude=df_base[df_base['num_magasin'] == magasin_principal]["latitude"].mean(),
            longitude=df_base[df_base['num_magasin'] == magasin_principal]["longitude"].mean(),
            zoom=8, pitch=0,)
        
        # Render the map in Streamlit
        st.pydeck_chart(pdk.Deck(layers=[layer],initial_view_state=view_state, map_style="light",
                                tooltip={"text": 
                                    "Code panonceau: {code_panonceau}\n" +
                                    "Nom de l'adhérent: {adherent}\n" +
                                    "Surface: {surface_com_m2} m²\n " + 
                                    "Conso: {conso_energie_2023_mwh_par_m2_corrigee} MWh/m²"}), height=400)
        
        # Create a colorbar
        fig, ax = plt.subplots(figsize=(5, 0.08))  # Wide and short figure
        cb = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax, orientation="horizontal")
        
        # Set the size of colorticks
        colorbar_fontsize = 5.5
        cb.ax.tick_params(labelsize=colorbar_fontsize)
        cb.set_label("Consommation corrigée [MWh/m²]", fontsize=colorbar_fontsize)
        cb.ax.xaxis.set_tick_params(width=0.3)
        
        st.pyplot(fig)

        # # Bounds for the colorbar
        # vmin = 0.25
        # vmax = 0.9

        # st.markdown("<h4 style='text-align: center;'>Ma situation géographique</h4>", unsafe_allow_html=True)
        # st.text("")

        # fig_map_conso = folium.Map(location=[df_base_magasin['latitude'].mean(), df_base_magasin['longitude'].mean()], zoom_start=8)
        # code = df_base_magasin['code'].values[0]

        # for _, row in df_base.iterrows():

        #     # Determine color based on 'conso_elec_mwh_par_m2' value
        #     normalized_value = (row[var_couleur] - vmin) / (vmax - vmin) 

        #     # Add Circle marker (all magasins but the VIP one)
        #     folium.Circle(
        #         location=[row['latitude'], row['longitude']], radius=row['surface_com_m2'], 
        #         color="grey", weight=1, fill_color=mcolors.rgb2hex(plt.get_cmap('seismic')(normalized_value)), fill_opacity=0.5,
        #         tooltip=f"Num magasin: {row['num_magasin']}<br>Nom du manager: {row['manager']}<br>Surface commerciale: {int(row['surface_com_m2'])} m²<br>Consommation énergétique normalisée corrigée: {round(row[var_couleur],2)} MWh/m²",
        #     ).add_to(fig_map_conso)

        
        # st_folium(fig_map_conso, height=400, width=720)
        # st.image('./pictures/legend_folium.png')
        
    return
        
    