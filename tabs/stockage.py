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


def plot_economies_stockage(df_consos, df_carte_identite, df_prix_elec, code_principal='0104', mode_groupe=False):

    st.markdown("<p style='text-align: center;'> Possibilités d'économies financières par stockage d'énergie.</p>", unsafe_allow_html=True)

    options_mois = ['Janvier 2023', 'Février 2023', 'Mars 2023', 'Avril 2023', 'Mai 2023', 'Juin 2023', 'Juillet 2023', 'Août 2023', 'Septembre 2023', 'Octobre 2023', 'Novembre 2023', 'Décembre 2023']

    # Create two columns
    col1, col2 = st.columns([1,1])
    with col1:
        if mode_groupe:
            energie_stockage = st.select_slider('Capacité de stockage [MWh]:', 
            options=[x for x in range(1, 51)], value=10, label_visibility="visible")
        else:
            energie_stockage = st.select_slider('Capacité de stockage [MWh]:', 
            options=[x * 0.01 for x in range(1, 31)], value=0.1, label_visibility="visible")

    with col2:
        # Mois a visualiser
        mois = st.select_slider("Choisir le mois à visualiser:",
        options=options_mois,
        value='Juin 2023',
        key='mois_economies_stockage', label_visibility="visible")
        
        
    # Create a dataframe with groupby
    df_consos_all_grouped = df_consos.groupby(['clean_month', 'clean_hour']).agg({'p_w_m2': 'sum'}).reset_index()
    df_consos_all_grouped['p_mw'] = df_consos_all_grouped['p_w_m2'] * 4500 * 1e-6

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
    
    # Keep only the month of interest
    df_consos_all_grouped_mois = df_consos_all_grouped.copy()
    df_consos_all_grouped_mois = df_consos_all_grouped_mois[['clean_month', 'clean_hour', 'p_mw']]
    df_consos_all_grouped_mois.rename(columns={'p_mw': 'conso_mwh'}, inplace=True)
                                                       
                                                       

    # Slice the dataframe to keep only 2023
    df_prix_elec_month = df_prix_elec[df_prix_elec['clean_month'].isin(options_mois)]

    # Slice the conso dataframe to get only 2023 and the code_principal
    df_consos_month = df_consos[(df_consos['clean_month'].isin(options_mois)) & (df_consos['code'] == code_principal)]
    df_consos_month = df_consos_month.merge(df_carte_identite[['code', 'surface_com_m2']], on='code', how='left')
    df_consos_month['conso_mwh'] = df_consos_month['p_w_m2'] * df_consos_month['surface_com_m2'] * 1e-6
    df_consos_month.drop(columns=['code', 'p_w_m2'], inplace=True)
    

    # Merge the two datagrames on the 'clean_hour' and 'clean_month' columns
    if mode_groupe:
        df_consos_prix_merged = df_consos_all_grouped_mois.merge(df_prix_elec_month, on=['clean_hour', 'clean_month'], how='left')
    else:
        df_consos_prix_merged = df_consos_month.merge(df_prix_elec_month, on=['clean_hour', 'clean_month'], how='left')
    
    
    
    # Loading/unloading rate
    rate = energie_stockage / 2
            
    df_consos_prix_merged['day'] = df_consos_prix_merged['clean_hour'].str.split(' ').str[0]
    df_consos_prix_merged['hour'] = df_consos_prix_merged['clean_hour'].str.split(' ').str[1]
    df_consos_prix_merged['hour'] = df_consos_prix_merged['hour'].str.replace('h', '').astype(int)
    
    # For each subgroup clean_month and day, find the two minimum values of market_price_eur_mwh between hour 0 and 7, and put them in a new column
    df_consos_prix_merged_min_night = df_consos_prix_merged[(df_consos_prix_merged['hour'] >= 0) & (df_consos_prix_merged['hour'] <= 7)].copy()
    df_consos_prix_merged_min_night['min_price_night'] = df_consos_prix_merged_min_night.groupby(['clean_month', 'day'])['market_price_eur_mwh'].transform(lambda x: x.nsmallest(2))
    df_consos_prix_merged_min_night['min_price_night'] = np.where(df_consos_prix_merged_min_night['min_price_night'].notna(), rate, df_consos_prix_merged_min_night['min_price_night'])    
    
    # Same between 7 and 19
    df_consos_prix_merged_min_day = df_consos_prix_merged[(df_consos_prix_merged['hour'] > 7) & (df_consos_prix_merged['hour'] <= 19)].copy()
    df_consos_prix_merged_min_day['min_price_day'] = df_consos_prix_merged_min_day.groupby(['clean_month', 'day'])['market_price_eur_mwh'].transform(lambda x: x.nsmallest(2))
    df_consos_prix_merged_min_day['min_price_day'] = np.where(df_consos_prix_merged_min_day['min_price_day'].notna(), rate, df_consos_prix_merged_min_day['min_price_day'])
    
    # Same between 14 and 23, but with max
    df_consos_prix_merged_max_night = df_consos_prix_merged[(df_consos_prix_merged['hour'] > 14) & (df_consos_prix_merged['hour'] <= 23)].copy()
    df_consos_prix_merged_max_night['max_price_night'] = df_consos_prix_merged_max_night.groupby(['clean_month', 'day'])['market_price_eur_mwh'].transform(lambda x: x.nlargest(2))
    df_consos_prix_merged_max_night['max_price_night'] = np.where(df_consos_prix_merged_max_night['max_price_night'].notna(), -rate, df_consos_prix_merged_max_night['max_price_night'])
    
    # Same between 4 and 10 with max
    df_consos_prix_merged_max_day = df_consos_prix_merged[(df_consos_prix_merged['hour'] > 4) & (df_consos_prix_merged['hour'] <= 10)].copy()
    df_consos_prix_merged_max_day['max_price_day'] = df_consos_prix_merged_max_day.groupby(['clean_month', 'day'])['market_price_eur_mwh'].transform(lambda x: x.nlargest(2))
    df_consos_prix_merged_max_day['max_price_day'] = np.where(df_consos_prix_merged_max_day['max_price_day'].notna(), -rate, df_consos_prix_merged_max_day['max_price_day'])
    
    # Merge the 4 dataframes on clean_month and clean_hour columns
    df_consos_prix_merged = df_consos_prix_merged.merge(df_consos_prix_merged_min_night[['clean_month', 'clean_hour', 'min_price_night']], on=['clean_month', 'clean_hour'], how='left')
    df_consos_prix_merged = df_consos_prix_merged.merge(df_consos_prix_merged_min_day[['clean_month', 'clean_hour', 'min_price_day']], on=['clean_month', 'clean_hour'], how='left')
    df_consos_prix_merged = df_consos_prix_merged.merge(df_consos_prix_merged_max_night[['clean_month', 'clean_hour', 'max_price_night']], on=['clean_month', 'clean_hour'], how='left')
    df_consos_prix_merged = df_consos_prix_merged.merge(df_consos_prix_merged_max_day[['clean_month', 'clean_hour', 'max_price_day']], on=['clean_month', 'clean_hour'], how='left')
    
    # Create a single column that would contain the min and max prices, and call it loading_energy. It shoudl just take the sum of the 4 columns. If value is nan, should be ignored and summation should still hold
    df_consos_prix_merged['loading_energy'] = df_consos_prix_merged['min_price_night'].fillna(0) + df_consos_prix_merged['min_price_day'].fillna(0) + df_consos_prix_merged['max_price_night'].fillna(0) + df_consos_prix_merged['max_price_day'].fillna(0)
    df_consos_prix_merged.drop(columns=['min_price_night', 'min_price_day', 'max_price_night', 'max_price_day'], inplace=True)

    # Calculate the consumption from the grid and the battery
    df_consos_prix_merged['conso_real_mwh'] = df_consos_prix_merged['conso_mwh'] + df_consos_prix_merged['loading_energy']
    df_consos_prix_merged['conso_real_pos_mwh'] = np.where(df_consos_prix_merged['conso_real_mwh'] > df_consos_prix_merged['conso_mwh'], 
                                                    df_consos_prix_merged['conso_real_mwh'], 
                                                    df_consos_prix_merged['conso_mwh'])

    df_consos_prix_merged['conso_real_neg_mwh'] = np.where(df_consos_prix_merged['conso_real_mwh'] < df_consos_prix_merged['conso_mwh'],
                                                    df_consos_prix_merged['conso_real_mwh'],
                                                    df_consos_prix_merged['conso_mwh'])
    
    
    # Mean price of energy charged
    mean_price_charged = df_consos_prix_merged[df_consos_prix_merged['loading_energy'] > 0]['market_price_eur_mwh'].mean()
    
    # Mean price of energy discharged
    mean_price_discharged = df_consos_prix_merged[df_consos_prix_merged['loading_energy'] < 0]['market_price_eur_mwh'].mean()
    
    # Total energy charged in MWh
    total_energy_charged_mwh = df_consos_prix_merged['loading_energy'].clip(lower=0).sum() * (52/12)
    
    # Calculate the savings
    savings = ((mean_price_discharged - mean_price_charged) * total_energy_charged_mwh) / 1e3
    
    
    # Show these indicators
    col1_0, col1_1, col1_2, col1_3, col1_4 = st.columns([1,4,4,4,4])
    
    with col1_1:
        
        if mode_groupe:
            st.markdown(f"""
                    <div style="text-align: center;">
                        Économies potentielles 💰 <br>
                        <span style="font-size: 22px; font-weight: bold;">{round(savings)} k€/an</span><br>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                    <div style="text-align: center;">
                        Économies potentielles 💰 <br>
                        <span style="font-size: 22px; font-weight: bold;">{round(savings,1)} k€/an</span><br>
                    </div>
                    """, unsafe_allow_html=True)
        
    with col1_2:
        if mode_groupe:
            st.markdown(f"""
                    <div style="text-align: center;">
                        Énergie stockée 🌞 <br>
                        <span style="font-size: 22px; font-weight: bold;">{round(0.001 * total_energy_charged_mwh,1)} GWh/an</span><br>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                    <div style="text-align: center;">
                        Énergie chargée 🌞 <br>
                        <span style="font-size: 22px; font-weight: bold;">{round(total_energy_charged_mwh,1)} MWh</span><br>
                    </div>
                    """, unsafe_allow_html=True)
        
    with col1_3:
        st.markdown(f"""
                <div style="text-align: center;">
                    Prix moyen chargé 📈 <br>
                    <span style="font-size: 22px; font-weight: bold;">{round(mean_price_charged, 2)} €/MWh</span><br>
                </div>
                """, unsafe_allow_html=True)
        
    with col1_4:
        st.markdown(f"""
                <div style="text-align: center;">
                    Prix moyen déchargé 📉 <br>
                    <span style="font-size: 22px; font-weight: bold;">{round(mean_price_discharged, 2)} €/MWh</span><br>
                </div>
                """, unsafe_allow_html=True)
        

    # Slice to keep only the selected month
    df_consos_prix_merged_month = df_consos_prix_merged[df_consos_prix_merged['clean_month'] == mois]

    fig = go.Figure()

    # Add the dashed line for conso_real_mwh
    fig.add_trace(go.Scatter(
        x=df_consos_prix_merged_month['clean_hour'],
        y=df_consos_prix_merged_month['conso_real_mwh'].round(2),
        name='Consommation avec effet batterie [MWh]',
        mode='lines',
        line=dict(color='blue', dash='dash')
    ))

    # Add the solid line for conso_mwh
    fig.add_trace(go.Scatter(
        x=df_consos_prix_merged_month['clean_hour'],
        y=df_consos_prix_merged_month['conso_mwh'].round(2),
        name='Consommation sans batterie [MWh]',
        mode='lines',
        line=dict(color='blue', dash='solid'),
        fillcolor='lightblue'
    ))

    # Fill the area between conso_mwh and conso_real_mwh with red when conso_real_mwh is above conso_mwh
    fig.add_trace(go.Scatter(
        x=df_consos_prix_merged_month['clean_hour'],
        y=df_consos_prix_merged_month['conso_real_pos_mwh'].round(2),
        mode='lines',
        name='Chargement',
        line=dict(color='rgba(0,0,0,0)'),  # Transparent line
        fill='tonexty',
        fillcolor='rgba(255,0,0,0.5)',  # Red with 50% opacity
        showlegend=True
    ))

    # Add the solid line for conso_mwh
    fig.add_trace(go.Scatter(
        x=df_consos_prix_merged_month['clean_hour'],
        y=df_consos_prix_merged_month['conso_mwh'].round(2),
        name='Conso kWh',
        mode='lines',
        line=dict(color='blue', dash='solid'),
        fillcolor='lightblue',
        showlegend=False
    ))

    # Fill the area between conso_mwh and conso_real_mwh with red when conso_real_mwh is above conso_mwh
    fig.add_trace(go.Scatter(
        x=df_consos_prix_merged_month['clean_hour'],
        y=df_consos_prix_merged_month['conso_real_neg_mwh'].round(2),
        mode='lines',
        name='Déchargement',
        line=dict(color='rgba(0,0,0,0)'),  # Transparent line
        fill='tonexty',
        fillcolor='rgba(0,255,0,0.5)',  # Green with 50% opacity
        showlegend=True
    ))

    # Also add a line with the price of the electricity, in a second y-axis
    fig.add_trace(go.Scatter(
        x=df_consos_prix_merged_month['clean_hour'],
        y=df_consos_prix_merged_month['market_price_eur_mwh'],
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
    yaxis_title='Puissance [MW]',
    template='plotly_white',
    legend=dict(orientation='h', yanchor="top", y=1.1, xanchor="right", x=0.99),
    margin=dict(l=0, r=0, t=70, b=0),
    height=500,
    hovermode='x unified',
    yaxis=dict(
        range=[0, 1.1 * max(df_consos_prix_merged_month['conso_mwh'].max(), df_consos_prix_merged_month['conso_real_mwh'].max())],
        showgrid=False
    ),
    yaxis2=dict(
        title='Prix de l\'électricité [€/MWh]',
        overlaying='y',
        side='right',
        showgrid=False,
        range=[df_consos_prix_merged_month['market_price_eur_mwh'].min(), 1.5 * df_consos_prix_merged_month['market_price_eur_mwh'].max()]  # Set the range for the secondary y-axis
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
    # fig.update_yaxes(range=[0, 1.1 * max(df_consos_prix_merged['conso_mwh'].max(), df_consos_prix_merged['conso_real_mwh'].max())])

    # Display the chart in Streamlit
    st.plotly_chart(fig)


    return