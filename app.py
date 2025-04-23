import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

import folium
from streamlit_folium import st_folium

import sys
sys.path.append('./tabs')
import resume, nuage_points, nuage_points_gaz, conso_hebdo, conso_hebdo_past, radar, desagregation, pv, prix_electricite, stockage
# import resume, nuage_points, nuage_points_gaz, conso_hebdo, conso_hebdo_past, radar, desagregation, pv, prix_electricite
import data_loading
from data_loading import load_consos_data, load_consos_stats
import hmac

# def check_password():
#     """Returns `True` if the user had the correct password."""

#     def password_entered():
#         """Checks whether a password entered by the user is correct."""
#         if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
#             st.session_state["password_correct"] = True
#         else:
#             st.session_state["password_correct"] = False

#     # Return True if the password is validated.
#     if st.session_state.get("password_correct", False):
#         return True

#     # Show input for password.
#     st.text_input(
#         "Password", type="password", on_change=password_entered, key="password"
#     )
#     if "password_correct" in st.session_state:
#         st.error("Password incorrect")
#     return False


# if not check_password():
#     st.stop()  # Do not continue if check_password is not True.

# Configuration globale
st.set_page_config(layout="wide", page_title="AICE DEMO")

# Read the data
df_carte_identite = pd.read_csv('./data/donnees_base_anonymous.csv')
df_carte_identite['code'] = df_carte_identite['code'].astype(str).str.zfill(4)
# df_carte_identite['full_name'] = df_carte_identite['nom_compte'] + ' (' + df_carte_identite['code'].astype(str) + ')'
df_carte_identite['gaz_fraction'] = (100 * df_carte_identite['gaz_fraction']).round(1)

# Replace 'Magasin' by 'Site' in column num_magasin
df_carte_identite['num_magasin'] = df_carte_identite['num_magasin'].str.replace('Magasin', 'Site')


# Read additional data
df_consos = data_loading.load_consos_data('./data/consos_monthly_avg_anonymous.csv')
df_consos_stats = data_loading.load_consos_stats('./data/consos_monthly_avg_stats_anonymous.csv')
df_radar = data_loading.load_consos_data('./data/consos_radar_anonymous.csv')
df_solar = pd.read_csv('./data/solar_prod.csv')
df_prix_elec = pd.read_csv('./data/prix_marche_elec.csv')


# Sidebar
st.markdown("""<style>.css-o18uir.e16nr0p33 {margin-top: -275px;}</style>""", unsafe_allow_html=True)
st.sidebar.image('./pictures/aice.png')

st.sidebar.title(" ")
mode_groupe = st.sidebar.toggle("Niveau global", key="carte_identite")


# Selection du magasin principal
st.sidebar.title("Mon site")
magasin_principal = st.sidebar.selectbox("Choisir un magasin", df_carte_identite['num_magasin'].to_list(), label_visibility="collapsed")
code_principal = df_carte_identite[df_carte_identite['num_magasin'] == magasin_principal]['code'].values[0]

# Selection des magasins comparatifs
st.sidebar.title("Sites comparatifs")
magasins_comparatifs = st.sidebar.multiselect("Choisir des magasins comparatifs", df_carte_identite['num_magasin'].to_list(), label_visibility="collapsed")
codes_comparatifs = df_carte_identite[df_carte_identite['num_magasin'].isin(magasins_comparatifs)]['code'].values


# Tabs
tab_id, tab_nuage, tab_nuage_gaz, tab_conso_hebdo, tab_conso_hebdo_past, tab_radar, tab_desag, tab_pv, tab_prix_elec, tab_stockage = st.tabs(["Vision d\'ensemble \u2001\u2001\u2001\u2001", 
                                                                                "Benchmark efficacité \u2001\u2001\u2001\u2001", 
                                                                                "Part du gaz \u2001\u2001\u2001\u2001", 
                                                                                'Profil de consommation \u2001\u2001\u2001',
                                                                                'Evolution du profil de consommation \u2001\u2001\u2001',
                                                                                'Radar \u2001\u2001\u2001',
                                                                                'Désagregration \u2001\u2001\u2001',
                                                                                'Autoconsommation solaire \u2001\u2001\u2001',
                                                                                'Achat de l\'électricité \u2001\u2001\u2001',
                                                                                'Stockage \u2001\u2001\u2001'])

# tab_id, tab_nuage, tab_nuage_gaz, tab_conso_hebdo, tab_conso_hebdo_past, tab_radar, tab_desag, tab_pv, tab_prix_elec = st.tabs(["Carte d'identité \u2001\u2001\u2001\u2001", 
#                                                                                 "Benchmark efficacité \u2001\u2001\u2001\u2001", 
#                                                                                 "Part du gaz \u2001\u2001\u2001\u2001", 
#                                                                                 'Benchmark profil de consommation \u2001\u2001\u2001',
#                                                                                 'Evolution du profil de consommation \u2001\u2001\u2001',
#                                                                                 'Radar \u2001\u2001\u2001',
#                                                                                 'Désagregration \u2001\u2001\u2001',
#                                                                                 'Autoconsommation solaire \u2001\u2001\u2001',
#                                                                                 'Achat de l\'électricité \u2001\u2001\u2001'])

with tab_id:
    resume.resume(df_carte_identite, magasin_principal, magasins_comparatifs, mode_groupe)    

with tab_nuage:
    st.text("")
    euros_par_mwh = 180; tC02_par_gwh = 32
    nuage_points.wrapper_efficacite_energetique(df_carte_identite, code_principal=code_principal, codes_comparatifs=codes_comparatifs, mode_groupe=mode_groupe, euros_mwh=euros_par_mwh, tCO2_gwh=tC02_par_gwh)
    
    # nuage_points.big_numbers_nuage_points(df_carte_identite, code_principal=code_principal)
    # nuage_points.figure_nuage_points(df_carte_identite, seuil=0.2, col_y='conso_elec_mwh_par_m2_corrigee', code_principal=code_principal, codes_comparatifs=codes_comparatifs)
    # nuage_points.expander_nuage_points(euros_par_mwh, tC02_par_gwh)

with tab_nuage_gaz:
    st.text("")
    
    nuage_points_gaz.wrapper_nuage_points_gaz(df_carte_identite, seuil=0.2, code_principal=code_principal, codes_comparatifs=codes_comparatifs, mode_groupe=mode_groupe)
    # nuage_points_gaz.big_numbers_nuage_points(df_carte_identite, code_principal=code_principal)
    # nuage_points_gaz.figure_nuage_points(df_carte_identite, seuil=0.2, code_principal=code_principal, codes_comparatifs=codes_comparatifs)

with tab_conso_hebdo:
    conso_hebdo.wrapper_plot_conso_hebdo(df_consos, df_consos_stats, df_carte_identite, code_principal=code_principal, magasins_comparatifs=codes_comparatifs, dimanche_ouvert=df_carte_identite[df_carte_identite['code'] == code_principal]['dimanche_ouvert'].values[0], mode_groupe=mode_groupe)
    # conso_hebdo.plot_conso_hebdo(df_consos, df_consos_stats, df_carte_identite, code_principal=code_principal, magasins_comparatifs=codes_comparatifs, dimanche_ouvert=df_carte_identite[df_carte_identite['code'] == code_principal]['dimanche_ouvert'].values[0])

with tab_conso_hebdo_past:
    conso_hebdo_past.wrapper_plot_conso_hebdo(df_consos, df_carte_identite, code_principal=code_principal, mode_groupe=mode_groupe)

with tab_radar:
    radar.plot_radar(df_radar, df_carte_identite, code_principal=code_principal, mode_groupe=mode_groupe)

with tab_desag:
    desagregation.wrapper_desagregation_cdc(df_consos, code_principal=code_principal, mode_groupe=mode_groupe)

with tab_pv:
    pv.wrapper_plot_pv_forecast(df_consos, df_carte_identite, df_solar, code_principal=code_principal, mode_groupe=mode_groupe)

with tab_prix_elec:
    prix_electricite.plot_prix_elec(df_consos, df_carte_identite, df_prix_elec, code_principal=code_principal, mode_groupe=mode_groupe)

with tab_stockage:
    stockage.plot_economies_stockage(df_consos, df_carte_identite, df_prix_elec,code_principal=code_principal, mode_groupe=mode_groupe)


# # Footer
# col_innosolaire_txt, col_innosolaire_logo = st.columns([1, 1])
# with col_innosolaire_txt:
#     st.text("")
#     st.markdown("<p style='text-align: right;'> Développé avec </p>", unsafe_allow_html=True)
# with col_innosolaire_logo:
#     st.image('./pictures/innosolaire.jpg', width=100)