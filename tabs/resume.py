import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


def resume(df_base, magasin_principal, magasins_comparatifs, mode_groupe):
    
    if mode_groupe:
        resume_mode_groupe(df_base)
    
    else:   
        resume_mode_magasin(df_base, magasin_principal, magasins_comparatifs)
    return

def resume_mode_magasin(df_base, magasin_principal, magasins_comparatifs):

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
        colorbar_fontsize = 7.5
        cb.ax.tick_params(labelsize=colorbar_fontsize)
        cb.set_label("Consommation corrigée [MWh/m²/an]", fontsize=colorbar_fontsize)
        cb.ax.xaxis.set_tick_params(width=0.3)
        
        st.pyplot(fig)
        
    return


# Create a function for the mode_groupe that only displays the map on the whole page

def resume_mode_groupe(df_base):
    
    st.text(" ")
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
        latitude=df_base["latitude"].mean(),
        longitude=df_base["longitude"].mean(),
        zoom=4.5, pitch=0,)
    
    # Render the map in Streamlit
    st.pydeck_chart(pdk.Deck(layers=[layer],initial_view_state=view_state, map_style="light",
                            tooltip={"text": 
                                "Code panonceau: {code_panonceau}\n" +
                                "Nom de l'adhérent: {adherent}\n" +
                                "Surface: {surface_com_m2} m²\n " + 
                                "Conso: {conso_energie_2023_mwh_par_m2_corrigee} MWh/m²"}), height=500)
    
    
    
    # Create a colorbar
    fig, ax = plt.subplots(figsize=(20, 0.18))  # Tall and narrow figure for vertical colorbar
    cb = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax, orientation="horizontal")

    # Set the size of colorticks
    colorbar_fontsize = 14
    cb.ax.tick_params(labelsize=colorbar_fontsize)
    cb.set_label("Consommation corrigée [MWh/m²/an]", fontsize=colorbar_fontsize, labelpad=10)
    cb.ax.yaxis.set_label_position("right")
    cb.ax.yaxis.label.set_rotation(0)  # Rotate the label text

    st.pyplot(fig)
    
    return