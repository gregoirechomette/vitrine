import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium

import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go


def wrapper_plot_pv_forecast(df_consos, df_carte_identite, df_solar, code_principal='0104', mode_groupe=False):
    
    
    if mode_groupe:
        
        plot_pv_forecast_groupe(df_consos, df_solar)
    
    else:
        
        plot_pv_forecast_magasin(df_consos, df_carte_identite, df_solar, code_principal='0104')
        
    
    return


def plot_pv_forecast_magasin(df_consos, df_carte_identite, df_solar, code_principal='0104'):

    st.markdown("<h5 style='text-align: center;'>Aperçu des bénéfices d'une centrale solaire</h5>", unsafe_allow_html=True)
    st.text("")
    col1, col2 = st.columns([1,6])


    # Create the slider
    with col1:
        pv_sizing_option = st.radio("Dimensionner avec:",
                                    ["Puissance", "Surface"],)
    with col2:
        if pv_sizing_option == 'Surface':
            selected_surface_value = st.select_slider('Selectionner la surface de parking avec panneaux solaires (m²)', options=[x * 100 for x in range(5, 81)], value=3000)
            selected_power_value = round(selected_surface_value * 220 * 1e-6,2)
        else:
            selected_power_value = st.select_slider('Selectionner la puissance de la centrale installée (MWc)', options=[round(x * 0.1, 1) for x in range(1, 21)], value=1)

    df_consos_all = df_consos.copy()
    
    # Find the year as the last 4 characters of 'clean_month'
    df_consos_all['year'] = df_consos_all['clean_month'].str[-4:]
    df_consos_all = df_consos_all[df_consos_all['year'] == '2023']

    # Return selected_power_value
    df_magasin_principal = df_consos_all[df_consos_all['code'] == code_principal].copy()
    df_base_magasin = df_carte_identite[df_carte_identite['code'] == code_principal].copy()

    # Create a new colum 'p_w' by multiplying 'p_w_m2' by the selected surface
    df_magasin_principal['p_mw'] = 1e-6 * df_magasin_principal['p_w_m2'] * df_base_magasin['surface_com_m2'].values[0]

    # Merge the two dataframes
    df_magasin_principal = df_magasin_principal.merge(df_solar, on=['clean_month', 'clean_hour'], how='left')
    
    # Rename the consumption column
    df_magasin_principal.rename(columns={'p_mw': 'conso_mw'}, inplace=True)

    # Now calculate the solar production for the selected power value
    df_magasin_principal['prod_mw'] = 1e-3 * selected_power_value * df_magasin_principal['prod_w']

    # Now I would like to calculate the autoconsommation, soutirage and surplus
    df_magasin_principal['autoconso_mw'] = df_magasin_principal[['conso_mw', 'prod_mw']].min(axis=1)
    df_magasin_principal['soutirage_mw'] = df_magasin_principal['conso_mw'] - df_magasin_principal['autoconso_mw']
    df_magasin_principal['surplus_mw'] = df_magasin_principal['prod_mw'] - df_magasin_principal['autoconso_mw']

    # Calculate some indicators for the selected power value
    taux_autoconso = 100 * df_magasin_principal['autoconso_mw'].sum() / df_magasin_principal['prod_mw'].sum()
    taux_couverture = 100 * df_magasin_principal['prod_mw'].sum() / df_magasin_principal['conso_mw'].sum()
    energie_autoconsommee_mwh = df_magasin_principal['autoconso_mw'].sum() * (52/12)


    # Create metrics for the selected power value
    col0, col1, col2, col3, col4 = st.columns([3,4,4,4,4])
    
    with col1:
        st.markdown(f"""
                <div style="text-align: center;">
                    Puissance installée 🌞 <br>
                    <span style="font-size: 22px; font-weight: bold;">{selected_power_value} MWc </span><br>
                </div>
                """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
                <div style="text-align: center;">
                    Autoconsommation 🔌 <br>
                    <span style="font-size: 22px; font-weight: bold;">{int(energie_autoconsommee_mwh)} MWh</span><br>
                </div>
                """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
                <div style="text-align: center;">
                    Taux d'autoconsommation 🔍 <br>
                    <span style="font-size: 22px; font-weight: bold;">{round(taux_autoconso,1)} %</span><br>
                </div>
                """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
                <div style="text-align: center;">
                    Taux de couverture 🛡️ <br>
                    <span style="font-size: 22px; font-weight: bold;">{round(taux_couverture,1)} %</span><br>
                </div>
                """, unsafe_allow_html=True)
    

    plot_year_pv(df_magasin_principal, suffix='_mw')
    plot_week_pv(df_magasin_principal[df_magasin_principal['clean_month'] == 'Février 2023'], suffix='_mw', name='Semaine représentative en hiver')
    plot_week_pv(df_magasin_principal[df_magasin_principal['clean_month'] == 'Juillet 2023'], suffix='_mw', name='Semaine représentative en été')


    return

def plot_pv_forecast_groupe(df_consos, df_solar):
    
    st.markdown("<h5 style='text-align: center;'>Dimensionnement d'une centrale solaire à l'échelle du groupe </h5>", unsafe_allow_html=True)
    st.text("")
    col1, col2 = st.columns([1,6])


    # Create the slider
    with col1:
        pv_sizing_option = st.radio("Dimensionner avec:",
                                    ["Puissance", "Surface"],)
    with col2:
        if pv_sizing_option == 'Surface':
            selected_surface_value = st.select_slider('Selectionner la surface de parking avec panneaux solaires (km²)', options=[round(x * 0.1, 2) for x in range(5, 31)], value=1)
            selected_power_value = round(selected_surface_value * 220,2)
        else:
            selected_power_value = st.select_slider('Selectionner la puissance de la centrale installée (MWc)', options=[round(x * 10   , 10) for x in range(30, 61)], value=350)

    df_consos_all = df_consos.copy()
    
    # Create a dataframe with groupby
    df_consos_all_grouped = df_consos_all.groupby(['clean_month', 'clean_hour']).agg({'p_w_m2': 'sum'}).reset_index()
    df_consos_all_grouped['p_gw'] = df_consos_all_grouped['p_w_m2'] * 4500 * 1e-9

    # Keep only 2023 (clean_month should contain 2023 in it)
    df_consos_all_grouped = df_consos_all_grouped[df_consos_all_grouped['clean_month'].str.contains('2023')]
    
     # Sort the months and the hours
    df_consos_all_grouped['clean_month'] = pd.Categorical(df_consos_all_grouped['clean_month'],
                                                           categories=['Janvier 2023', 'Février 2023', 'Mars 2023', 'Avril 2023',
                                                                       'Mai 2023', 'Juin 2023', 'Juillet 2023', 'Août 2023',
                                                                       'Septembre 2023', 'Octobre 2023', 'Novembre 2023', 'Décembre 2023'],
                                                           ordered=True)

    # Extract the day from clean_hour
    df_consos_all_grouped['day'] = df_consos_all_grouped['clean_hour'].str.split(' ').str[0]
    df_consos_all_grouped['hour'] = df_consos_all_grouped['clean_hour'].str.split(' ').str[1]
    df_consos_all_grouped['hour'] = df_consos_all_grouped['hour'].str.replace('h', '').astype(int)

    df_consos_all_grouped['day'] = pd.Categorical(df_consos_all_grouped['day'],
                                                   categories=['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'],
                                                   ordered=True)

    # Sort the dataframe by month, day and hour
    df_consos_all_grouped = df_consos_all_grouped.sort_values(['clean_month', 'day', 'hour'])
    
    # Merge the two dataframes
    df_consos_all_grouped = df_consos_all_grouped.merge(df_solar, on=['clean_month', 'clean_hour'], how='left')
    
    # Rename the consumption column
    df_consos_all_grouped.rename(columns={'p_gw': 'conso_gw'}, inplace=True)

    # Now calculate the solar production for the selected power value
    df_consos_all_grouped['prod_gw'] = 1e-6 * selected_power_value * df_consos_all_grouped['prod_w']

    # Now I would like to calculate the autoconsommation, soutirage and surplus
    df_consos_all_grouped['autoconso_gw'] = df_consos_all_grouped[['conso_gw', 'prod_gw']].min(axis=1)
    df_consos_all_grouped['soutirage_gw'] = df_consos_all_grouped['conso_gw'] - df_consos_all_grouped['autoconso_gw']
    df_consos_all_grouped['surplus_gw'] = df_consos_all_grouped['prod_gw'] - df_consos_all_grouped['autoconso_gw']
    
    # Calculate some indicators for the selected power value
    taux_autoconso = 100 * df_consos_all_grouped['autoconso_gw'].sum() / df_consos_all_grouped['prod_gw'].sum()
    taux_couverture = 100 * df_consos_all_grouped['prod_gw'].sum() / df_consos_all_grouped['conso_gw'].sum()
    energie_autoconsommee_gwh =  df_consos_all_grouped['autoconso_gw'].sum() * (52/12)


    # Create metrics for the selected power value
    col0, col1, col2, col3, col4 = st.columns([3,4,4,4,4])
    
    with col1:
        st.markdown(f"""
                <div style="text-align: center;">
                    Puissance installée 🌞 <br>
                    <span style="font-size: 22px; font-weight: bold;">{round(selected_power_value)} MWc </span><br>
                </div>
                """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
                <div style="text-align: center;">
                    Autoconsommation 🔌 <br>
                    <span style="font-size: 22px; font-weight: bold;">{int(energie_autoconsommee_gwh)} GWh</span><br>
                </div>
                """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
                <div style="text-align: center;">
                    Taux d'autoconsommation 🔍 <br>
                    <span style="font-size: 22px; font-weight: bold;">{round(taux_autoconso,1)} %</span><br>
                </div>
                """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
                <div style="text-align: center;">
                    Taux de couverture 🛡️ <br>
                    <span style="font-size: 22px; font-weight: bold;">{round(taux_couverture,1)} %</span><br>
                </div>
                """, unsafe_allow_html=True)
    
    
    plot_year_pv(df_consos_all_grouped, unit= 'GWh', suffix= '_gw')
    plot_week_pv(df_consos_all_grouped[df_consos_all_grouped['clean_month'] == 'Février 2023'], unit= 'GWh', suffix= '_gw', name='Semaine représentative en hiver')
    plot_week_pv(df_consos_all_grouped[df_consos_all_grouped['clean_month'] == 'Juillet 2023'], unit= 'GWh', suffix= '_gw', name='Semaine représentative en été')
    
    
    return



def plot_week_pv(df_magasin_principal_month, suffix='_w', unit= 'MWh', name='Mois sélectionné'):
    # Create a bar plot (stacked vertically) for a week in Fevrier 2023
    custom_colors = {
        f"autoconso{suffix}": px.colors.qualitative.Plotly[9],
        f"soutirage{suffix}": px.colors.qualitative.Set1[0],
        f"surplus{suffix}": px.colors.qualitative.Set1[1]
    }

    fig = px.bar(
        df_magasin_principal_month,
        x='clean_hour',
        y = [f'autoconso{suffix}', f'soutirage{suffix}', f'surplus{suffix}'],
        title = 'Semaine moyenne en Février 2023',
        labels = {'value': f'Energie [{unit}]', 'variable': ' '},
        color_discrete_map=custom_colors,
        barmode='relative'
    )

    # Update the layout
    fig.update_layout(
        title=name,
        title_x=0.4,
        height=550,
        showlegend=True,
        margin=dict(l=20, r=20, t=80, b=20),
        legend=dict(orientation='h', yanchor="top", y=1.1, xanchor="right", x=0.99)
    )

    # Change xlabel
    fig.update_xaxes(
        title_text=" ",
        title_font=dict(size=12),
        showticklabels=True,
        tickfont=dict(size=16),
        ticktext=['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'],
        tickvals=['Lundi 12h', 'Mardi 12h', 'Mercredi 12h', 'Jeudi 12h', 'Vendredi 12h', 'Samedi 12h', 'Dimanche 12h'],
        side='bottom'
    )

    # Change the name of the labels in the legend
    fig.for_each_trace(lambda t: t.update(name=t.name.replace(suffix, ' [' + unit + ']')))

    st.plotly_chart(fig)
    return

def plot_year_pv(df_magasin_principal, unit='MWh', suffix='_w'):
    
    # Rescale the values to have the yearly values
    df_magasin_principal_rescaled = df_magasin_principal.copy()
    df_magasin_principal_rescaled[f'autoconso{suffix}'] = (52/12) * df_magasin_principal[f'autoconso{suffix}']
    df_magasin_principal_rescaled[f'soutirage{suffix}'] = (52/12) * df_magasin_principal[f'soutirage{suffix}']
    df_magasin_principal_rescaled[f'surplus{suffix}'] = (52/12) * df_magasin_principal[f'surplus{suffix}']

    # Also group by month
    df_magasin_principal_rescaled = df_magasin_principal_rescaled.groupby(by=['clean_month'], as_index=False).agg({
        f'autoconso{suffix}': 'sum',
        f'soutirage{suffix}': 'sum',
        f'surplus{suffix}': 'sum'
    })

    # Order by month
    df_magasin_principal_rescaled['clean_month'] = pd.Categorical(
        df_magasin_principal_rescaled['clean_month'],
        ['Janvier 2023', 'Février 2023', 'Mars 2023', 'Avril 2023', 'Mai 2023', 'Juin 2023', 'Juillet 2023', 'Août 2023', 'Septembre 2023', 'Octobre 2023', 'Novembre 2023', 'Décembre 2023']
    )
    df_magasin_principal_rescaled.sort_values('clean_month', inplace=True)

    # Create a bar plot (stacked vertically) for a week in Fevrier 2023
    custom_colors = {
        f"autoconso{suffix}": px.colors.qualitative.Plotly[9],
        f"soutirage{suffix}": px.colors.qualitative.Set1[0],
        f"surplus{suffix}": px.colors.qualitative.Set1[1]
    }

    fig = px.bar(
        df_magasin_principal_rescaled,
        x='clean_month',
        y=[f'autoconso{suffix}', f'soutirage{suffix}', f'surplus{suffix}'],
        title='Année 2023',
        labels = {'value': f'Energie [{unit}]', 'variable': ' '},
        color_discrete_map=custom_colors,
        barmode='relative'
    )

    # Update the layout
    fig.update_layout(
        title='Visualisation de l\'autoconsommation sur une année',
        title_x=0.35,
        height=550,
        showlegend=True,
        margin=dict(l=20, r=20, t=80, b=20),
        legend=dict(orientation='h', yanchor="top", y=1.1, xanchor="right", x=0.99)
    )

    # Change xlabel
    fig.update_xaxes(
        title_text=" ",
        title_font=dict(size=12),
        showticklabels=True,
        tickfont=dict(size=16),
        ticktext=['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'],
        tickvals=['Janvier 2023', 'Février 2023', 'Mars 2023', 'Avril 2023', 'Mai 2023', 'Juin 2023', 'Juillet 2023', 'Août 2023', 'Septembre 2023', 'Octobre 2023', 'Novembre 2023', 'Décembre 2023'],
        side='bottom'
    )

    # Change the name of the labels in the legend
    fig.for_each_trace(lambda t: t.update(name=t.name.replace(suffix, ' [' + unit + ']')))

    st.plotly_chart(fig)
    return


