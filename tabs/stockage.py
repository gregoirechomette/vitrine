import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium

import plotly
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go


def plot_economies_stockage(df_consos, df_carte_identite, df_prix_elec, code_principal='0104'):

    st.markdown("<p style='text-align: center;'> Possibilités d'économies financières par stockage d'énergie.</p>", unsafe_allow_html=True)

    options_mois = ['Janvier 2023', 'Février 2023', 'Mars 2023', 'Avril 2023', 'Mai 2023', 'Juin 2023', 'Juillet 2023', 'Août 2023', 'Septembre 2023', 'Octobre 2023', 'Novembre 2023', 'Décembre 2023']

    # Create two columns
    col1, col2 = st.columns([1,1])
    with col1:
        # Energie a stocker (kWh, select_slider from 10 to 200 kWh with step 10)
        energie_stockage = st.select_slider('Capacité de stockage [kWh]:', 
        options=[x * 10 for x in range(1, 31)], value=100, label_visibility="visible")

    with col2:
        # Mois a visualiser
        mois = st.select_slider("Choisir le mois à visualiser:",
        options=options_mois,
        value='Juin 2023',
        key='mois_economies_stockage', label_visibility="visible")
        

    # Slice the dataframe to keep only the selected month
    df_prix_elec_month = df_prix_elec[df_prix_elec['clean_month'] == mois]

    # Slice the conso dataframe to get only the month and the code_principal
    df_consos_month = df_consos[(df_consos['clean_month'] == mois) & (df_consos['code'] == code_principal)]

    # Merge the two datagrames on the 'clean_hour' and 'clean_month' columns
    df_consos_prix_merged = df_consos_month.merge(df_prix_elec_month, on=['clean_hour', 'clean_month'], how='left')

    # Merge with the carte_identite dataframe to obtain the surface
    df_consos_prix_merged = df_consos_prix_merged.merge(df_carte_identite[['code', 'surface_com_m2']], on='code', how='left')

    # Calculate the conso_mwh
    df_consos_prix_merged['conso_kwh'] = df_consos_prix_merged['p_w_m2'] * df_consos_prix_merged['surface_com_m2'] * 1e-3
    df_consos_prix_merged.drop(columns=['code', 'p_w_m2'], inplace=True)




    # Loading/unloading rate
    rate = energie_stockage / 2

    # Initialize battery state
    battery_level = 0

    # Create the loading_energy column
    df_consos_prix_merged['loading_energy'] = 0


    # Optimize the loading/unloading strategy - seuil (Mistral)
    for i in range(len(df_consos_prix_merged)):
        price = df_consos_prix_merged.loc[i, 'market_price_eur_mwh']
        conso = df_consos_prix_merged.loc[i, 'conso_kwh']

        if battery_level < energie_stockage and price < df_consos_prix_merged['market_price_eur_mwh'].mean():
            # Load the battery
            load_amount = min(rate, energie_stockage - battery_level)
            battery_level += load_amount
            df_consos_prix_merged.loc[i, 'loading_energy'] = load_amount
        elif battery_level > 0 and price > df_consos_prix_merged['market_price_eur_mwh'].mean():
            # Unload the battery
            unload_amount = min(rate, battery_level, conso)
            battery_level -= unload_amount
            df_consos_prix_merged.loc[i, 'loading_energy'] = -unload_amount

    # Calculate the consumption from the grid and the battery
    df_consos_prix_merged['conso_real_kwh'] = df_consos_prix_merged['conso_kwh'] + df_consos_prix_merged['loading_energy']
    df_consos_prix_merged['conso_real_pos_kwh'] = np.where(df_consos_prix_merged['conso_real_kwh'] > df_consos_prix_merged['conso_kwh'], 
                                                    df_consos_prix_merged['conso_real_kwh'], 
                                                    df_consos_prix_merged['conso_kwh'])

    df_consos_prix_merged['conso_real_neg_kwh'] = np.where(df_consos_prix_merged['conso_real_kwh'] < df_consos_prix_merged['conso_kwh'],
                                                    df_consos_prix_merged['conso_real_kwh'],
                                                    df_consos_prix_merged['conso_kwh'])

    # df_consos_prix_merged['conso_from_battery_kwh'] = -df_consos_prix_merged['loading_energy'].clip(upper=0)
    # df_consos_prix_merged['loading_battery'] = df_consos_prix_merged['loading_energy'].clip(lower=0)
    # df_consos_prix_merged['conso_minus_battery'] = df_consos_prix_merged['conso_kwh'] - df_consos_prix_merged['conso_from_battery_kwh']



    fig = go.Figure()

    # Add the dashed line for conso_real_kwh
    fig.add_trace(go.Scatter(
        x=df_consos_prix_merged['clean_hour'],
        y=df_consos_prix_merged['conso_real_kwh'].round(),
        name='Consommation avec effet batterie [kWh]',
        mode='lines',
        line=dict(color='blue', dash='dash')
    ))

    # Add the solid line for conso_kwh
    fig.add_trace(go.Scatter(
        x=df_consos_prix_merged['clean_hour'],
        y=df_consos_prix_merged['conso_kwh'].round(),
        name='Consommation sans batterie [kWh]',
        mode='lines',
        line=dict(color='blue', dash='solid'),
        fillcolor='lightblue'
    ))

    # Fill the area between conso_kwh and conso_real_kwh with red when conso_real_kwh is above conso_kwh
    fig.add_trace(go.Scatter(
        x=df_consos_prix_merged['clean_hour'],
        y=df_consos_prix_merged['conso_real_pos_kwh'].round(),
        mode='lines',
        name='Chargement',
        line=dict(color='rgba(0,0,0,0)'),  # Transparent line
        fill='tonexty',
        fillcolor='rgba(255,0,0,0.5)',  # Red with 50% opacity
        showlegend=True
    ))

    # Add the solid line for conso_kwh
    fig.add_trace(go.Scatter(
        x=df_consos_prix_merged['clean_hour'],
        y=df_consos_prix_merged['conso_kwh'].round(),
        name='Conso kWh',
        mode='lines',
        line=dict(color='blue', dash='solid'),
        fillcolor='lightblue',
        showlegend=False
    ))

    # Fill the area between conso_kwh and conso_real_kwh with red when conso_real_kwh is above conso_kwh
    fig.add_trace(go.Scatter(
        x=df_consos_prix_merged['clean_hour'],
        y=df_consos_prix_merged['conso_real_neg_kwh'].round(),
        mode='lines',
        name='Déchargement',
        line=dict(color='rgba(0,0,0,0)'),  # Transparent line
        fill='tonexty',
        fillcolor='rgba(0,255,0,0.5)',  # Green with 50% opacity
        showlegend=True
    ))

    # Also add a line with the price of the electricity, in a second y-axis
    fig.add_trace(go.Scatter(
        x=df_consos_prix_merged['clean_hour'],
        y=df_consos_prix_merged['market_price_eur_mwh'],
        name='Prix de l\'électricité [€/MWh]',
        mode='lines',
        opacity=0.5,
        yaxis='y2',
        line=dict(color='red')
    ))

    # Update layout for better visualization
    fig.update_layout(
    title={'text': ' ', 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
    xaxis_title=' ',
    yaxis_title='Puissance [kW]',
    template='plotly_white',
    legend=dict(orientation='h', yanchor="top", y=1.1, xanchor="right", x=0.99),
    margin=dict(l=0, r=0, t=70, b=0),
    height=500,
    hovermode='x unified',
    yaxis=dict(
        range=[0, 1.1 * max(df_consos_prix_merged['conso_kwh'].max(), df_consos_prix_merged['conso_real_kwh'].max())],
        showgrid=False
    ),
    yaxis2=dict(
        title='Prix de l\'électricité [€/MWh]',
        overlaying='y',
        side='right',
        showgrid=False,
        range=[df_consos_prix_merged['market_price_eur_mwh'].min(), 1.5 * df_consos_prix_merged['market_price_eur_mwh'].max()]  # Set the range for the secondary y-axis
    )
)

    # Customize x-axis tick labels
    fig.update_xaxes(title_text=" ",
        title_font=dict(size=12),
        showticklabels=True,
        tickfont=dict(size=16),
        ticktext=['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'],
        tickvals=['Lundi 12h', 'Mardi 12h', 'Mercredi 12h', 'Jeudi 12h', 'Vendredi 12h', 'Samedi 12h', 'Dimanche 12h'],
        side='bottom'
    )

    # # Change the y-axis range
    # fig.update_yaxes(range=[0, 1.1 * max(df_consos_prix_merged['conso_kwh'].max(), df_consos_prix_merged['conso_real_kwh'].max())])

    # Display the chart in Streamlit
    st.plotly_chart(fig)


    return