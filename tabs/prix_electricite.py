import numpy as np
import pandas as pd

import plotly
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go

def plot_prix_elec(df_consos, df_carte_identite, df_prix_elec, code_principal='0104', mode_groupe=False): 

    st.markdown("<p style='text-align: center;'> Prix de l'électricité selon deux contrats d'achat différetns: le prix du marché EPEX et les contrats heures pleines/creuses, haute saison/basse saison. Données 2023.</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'> Pour changer de mois, utiliser le curseur ci-dessous: </p>", unsafe_allow_html=True)

    # Mois a visualiser
    mois = st.select_slider(" ",
    options=['Janvier 2023', 'Février 2023', 'Mars 2023', 'Avril 2023', 'Mai 2023', 'Juin 2023', 'Juillet 2023', 'Août 2023', 'Septembre 2023', 'Octobre 2023', 'Novembre 2023', 'Décembre 2023'], key='mois_prix_elec')

    # Slice the dataframe to keep only the selected month
    df_prix_elec_month = df_prix_elec[df_prix_elec['month'] == mois].copy()
    df_prix_elec_month.rename(columns={'month': 'clean_month'}, inplace=True)
    
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
    df_consos_all_grouped_mois = df_consos_all_grouped[(df_consos_all_grouped['clean_month'] == mois)]
    df_consos_all_grouped_mois = df_consos_all_grouped_mois[['clean_month', 'clean_hour', 'p_mw']]
    df_consos_all_grouped_mois.rename(columns={'p_mw': 'conso_mwh'}, inplace=True)
                                                       
    

    # Slide the conso dataframe to get only the month and the code_principal
    df_consos_month = df_consos[(df_consos['clean_month'] == mois) & (df_consos['code'] == code_principal)]
    df_consos_month = df_consos_month.merge(df_carte_identite[['code', 'surface_com_m2']], on='code', how='left')
    df_consos_month['conso_mwh'] = df_consos_month['p_w_m2'] * df_consos_month['surface_com_m2'] * 1e-6
    df_consos_month.drop(columns=['p_w_m2', 'surface_com_m2'], inplace=True)
    

    # Merge the two datagrames on the 'clean_hour' and 'clean_month' columns
    if mode_groupe:
        df_consos_prix_merged = df_consos_all_grouped_mois.merge(df_prix_elec_month, on=['clean_hour', 'clean_month'], how='left')
    else:
        df_consos_prix_merged = df_consos_month.merge(df_prix_elec_month, on=['clean_hour', 'clean_month'], how='left')


    # Create the figure
    fig = go.Figure()

    # Add the bar trace for 'conso_mwh'
    fig.add_trace(go.Bar(
        x=df_consos_prix_merged['clean_hour'],
        y=(df_consos_prix_merged['conso_mwh']).round(3),
        name='Consommation [MWh]',
        opacity=0.1,
        yaxis='y'
    ))

    # Add the line trace for 'market_price_eur_mwh'
    fig.add_trace(go.Scatter(
        x=df_consos_prix_merged['clean_hour'],
        y=df_consos_prix_merged['market_price_eur_mwh'],
        name='Market Price (EPEX SPOT) [€/MWh]',
        mode='lines',
        yaxis='y2',
        line=dict(color='#316395')
    ))

    # Add the line trace for 'hp_hc_price_eur_mwh'
    fig.add_trace(go.Scatter(
        x=df_consos_prix_merged['clean_hour'],
        y=df_consos_prix_merged['hp_hc_price_eur_mwh'],
        name='HP/HC Price [€/MWh]',
        mode='lines',
        yaxis='y2',
        line=dict(color=plotly.colors.qualitative.Set3[4])
    ))

    # Update layout to include two y-axes
    fig.update_layout(
        yaxis=dict(title='Consommation [MWh]', showgrid=False),
        yaxis2=dict(title='Price [€/MWh]', overlaying='y', side='right', showgrid=False, range=[1.1 * min(df_consos_prix_merged['market_price_eur_mwh'].min(),0), 1.1 * max(df_consos_prix_merged['market_price_eur_mwh'].max(), df_consos_prix_merged['hp_hc_price_eur_mwh'].max())]),
        title=' ',
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis_title=' ',
        height=500,
        legend=dict(orientation='h', yanchor="top", y=1.1, xanchor="right", x=0.99),
        hovermode='x unified'
    )

    fig.update_xaxes(title_text=" ", title_font=dict(size=12), showticklabels=True, tickfont=dict(size=16), 
                     ticktext=['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'], 
                     tickvals=['Lundi 12h', 'Mardi 12h', 'Mercredi 12h', 'Jeudi 12h', 'Vendredi 12h', 'Samedi 12h', 'Dimanche 12h'], side='bottom')


    st.plotly_chart(fig)



    # NOW ANALYZE MONTH BY MONTH

    df_prix_elec.rename(columns={'month': 'clean_month'}, inplace=True)
    
    if mode_groupe:
        df_consos_prix_merged_all_months = df_consos.merge(df_prix_elec, on=['clean_hour', 'clean_month'], how='left')
    else:
        df_consos_prix_merged_all_months = df_consos[df_consos['code'] == code_principal].merge(df_prix_elec, on=['clean_hour', 'clean_month'], how='left')
    df_consos_prix_merged_all_months = df_consos_prix_merged_all_months[df_consos_prix_merged_all_months['clean_month'].str.contains('2023')]
    df_consos_prix_merged_all_months = df_consos_prix_merged_all_months.merge(df_carte_identite[['code', 'surface_com_m2']], on='code', how='left')
    df_consos_prix_merged_all_months['conso_mwh'] = df_consos_prix_merged_all_months['p_w_m2'] * df_consos_prix_merged_all_months['surface_com_m2'] * 1e-6

    # Now calculate the price of electriciy (market and hp/hc) for each month (grouped)
    df_consos_prix_merged_all_months['price_market_eur'] = df_consos_prix_merged_all_months['conso_mwh'] * df_consos_prix_merged_all_months['market_price_eur_mwh']
    df_consos_prix_merged_all_months['price_hp_hc_eur'] = df_consos_prix_merged_all_months['conso_mwh'] * df_consos_prix_merged_all_months['hp_hc_price_eur_mwh']

    df_prix_par_mois = df_consos_prix_merged_all_months.groupby('clean_month').agg({'conso_mwh': 'sum', 'price_market_eur': 'sum', 'price_hp_hc_eur': 'sum'}).reset_index()
    # Round to 1 decimal
    df_prix_par_mois['price_market_eur'] = df_prix_par_mois['price_market_eur'].round()
    df_prix_par_mois['price_hp_hc_eur'] = df_prix_par_mois['price_hp_hc_eur'].round()

    # Assign categories to the months and sort them
    df_prix_par_mois['clean_month'] = pd.Categorical(df_prix_par_mois['clean_month'], categories=['Janvier 2023', 'Février 2023', 'Mars 2023', 'Avril 2023', 'Mai 2023', 'Juin 2023', 'Juillet 2023', 'Août 2023', 'Septembre 2023', 'Octobre 2023', 'Novembre 2023', 'Décembre 2023'], ordered=True)
    df_prix_par_mois.sort_values('clean_month', inplace=True)

    # Now plot the price per month for these two contracts, with the same colors as before. No bars, just lines, no consumption.
    fig = go.Figure()

    # Add the line trace for 'price market'
    fig.add_trace(go.Scatter(
        x=df_prix_par_mois['clean_month'],
        y=df_prix_par_mois['price_market_eur'],
        name='Market Price (EPEX SPOT) [€]',
        mode='lines',
        yaxis='y',
        line=dict(color='#316395')
    ))

    # Add the line trace for 'price hp/hc'
    fig.add_trace(go.Scatter(
        x=df_prix_par_mois['clean_month'],
        y=df_prix_par_mois['price_hp_hc_eur'],
        name='HP/HC Price [€]',
        mode='lines',
        yaxis='y',
        line=dict(color=plotly.colors.qualitative.Set3[4])
    ))

    # Update layout 
    fig.update_layout(
        yaxis=dict(title='Facture électrique [€]', showgrid=True),
        title=' ',
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis_title=' ',
        height=500,
        legend=dict(orientation='h', yanchor="top", y=1.1, xanchor="right", x=0.99),
        hovermode='x unified'
    )

    # Set y range
    fig.update_yaxes(range=[0, 1.1 * max(df_prix_par_mois['price_market_eur'].max(), df_prix_par_mois['price_hp_hc_eur'].max())])

    st.plotly_chart(fig)
    
    
    
    
    
    # FINALLY, HEAT MAPS
    
    # Split 'clean_hour' into 'weekday' and 'hour'
    df_consos_prix_merged_all_months['weekday'] = df_consos_prix_merged_all_months['clean_hour'].str.split(' ').str[0]
    df_consos_prix_merged_all_months['hour'] = df_consos_prix_merged_all_months['clean_hour'].str.split(' ').str[1]
    df_consos_prix_merged_all_months['hour'] = df_consos_prix_merged_all_months['hour'].str[:-1].astype(int)

    # Calculate percentage difference
    df_consos_prix_merged_all_months['percentage_higher_market'] = 100 * (df_consos_prix_merged_all_months['price_market_eur'] - df_consos_prix_merged_all_months['price_hp_hc_eur']) / df_consos_prix_merged_all_months['price_hp_hc_eur']

    # Separate data for weekdays and weekends
    weekdays = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']
    df_weekdays = df_consos_prix_merged_all_months[df_consos_prix_merged_all_months['weekday'].isin(weekdays)]
    df_weekends = df_consos_prix_merged_all_months[~df_consos_prix_merged_all_months['weekday'].isin(weekdays)]

    # Function to create heatmap
    def create_heatmap(df, title_suffix):
        df_heatmap = df.groupby(['clean_month', 'hour']).agg({'percentage_higher_market': 'mean'}).reset_index()
        df_heatmap['percentage_higher_market'] = df_heatmap['percentage_higher_market'].round(1)
        df_heatmap = df_heatmap.pivot(index='clean_month', columns='hour', values='percentage_higher_market')
        df_heatmap = df_heatmap.reset_index()

        df_heatmap['clean_month'] = pd.Categorical(
            df_heatmap['clean_month'],
            categories=[
                'Janvier 2023', 'Février 2023', 'Mars 2023', 'Avril 2023',
                'Mai 2023', 'Juin 2023', 'Juillet 2023', 'Août 2023',
                'Septembre 2023', 'Octobre 2023', 'Novembre 2023', 'Décembre 2023'], ordered=True)

        df_heatmap.sort_values('clean_month', inplace=True)
        df_heatmap.set_index('clean_month', inplace=True)

        fig = px.imshow(df_heatmap, color_continuous_scale='RdBu_r',
                        title=f'Pourcentage de différence entre le prix du marché et le prix HP/HC ({title_suffix})',
                        labels=dict(x='Heure', y='Mois', color='Pourcentage de différence'),
                        height=300, zmin=-100, zmax=100)

        fig.update_layout(title={'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
                        margin=dict(l=0, r=0, t=40, b=0),
                        xaxis_title='Heure',
                        yaxis_title=' ',
                        legend=dict(orientation='h', yanchor="top", y=1.1, xanchor="right", x=0.99), height=400)

        return fig

    # Create heatmaps
    fig_weekdays = create_heatmap(df_weekdays, 'Semaine')
    fig_weekends = create_heatmap(df_weekends, 'Week-end')

    # Plot heatmaps
    st.plotly_chart(fig_weekdays)
    st.plotly_chart(fig_weekends)
    
    
    
    # # New plot multi year trend
    # df_prix_elec_week = df_prix_elec[~(df_prix_elec['clean_hour'].str.contains('Samedi') | df_prix_elec['clean_hour'].str.contains('Dimanche'))]
    
    # # Extrat month, year and hour
    # df_prix_elec_week['day'] = df_prix_elec_week['clean_hour'].str.split(' ').str[0]
    # df_prix_elec_week['hour'] = df_prix_elec_week['clean_hour'].str.split(' ').str[1]
    # df_prix_elec_week['hour'] = df_prix_elec_week['hour'].str.replace('h', '').astype(int)
    # df_prix_elec_week['year'] = df_prix_elec_week['clean_month'].str.split(' ').str[1]
    # df_prix_elec_week['month'] = df_prix_elec_week['clean_month'].str.split(' ').str[0]

    # # Groupby year, month and hour
    # df_prix_elec_week_grouped = df_prix_elec_week.groupby(['year', 'month', 'hour']).agg({'market_price_eur_mwh': 'mean', 'hp_hc_price_eur_mwh': 'mean'}).reset_index()
    
    # # Select only year from 2009 to 2023
    # df_prix_elec_week_grouped = df_prix_elec_week_grouped[df_prix_elec_week_grouped['year'].isin([str(i) for i in range(2009, 2024)])]
    
    
    
    # # Create a slider to select the month
    # month_trend = st.select_slider(" ", options=['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'], key='mois_prix_elec_2')
    


    # # Assuming df_prix_elec_week_grouped is your DataFrame and month_test is defined
    # # Define the custom colormap using matplotlib's coolwarm colormap
    # cmap = plt.get_cmap('coolwarm')
    # colors = [cmap(i / 14.0) for i in range(15)] 

    # # Map months to colors
    # year_order = [2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
    # color_map = {month: colors[i] for i, month in enumerate(year_order)}

    # def rgba_to_hex(rgba):
    #     """Convert an RGBA tuple to a hex string."""
    #     r, g, b, a = rgba
    #     r = int(r * 255)
    #     g = int(g * 255)
    #     b = int(b * 255)
    #     return f'#{r:02x}{g:02x}{b:02x}'

    # fig_trends = go.Figure()

    # for i, year in enumerate(df_prix_elec_week_grouped['year'].unique()):
    #     color_tuple = color_map[int(year)]
    #     color_hex = rgba_to_hex(color_tuple)

    #     fig_trends.add_trace(go.Scatter(
    #         x=df_prix_elec_week_grouped[((df_prix_elec_week_grouped['year'] == year) & (df_prix_elec_week_grouped['month'] == month_trend))]['hour'],
    #         y=df_prix_elec_week_grouped[((df_prix_elec_week_grouped['year'] == year) & (df_prix_elec_week_grouped['month'] == month_trend))]['market_price_eur_mwh'],
    #         name=f'{year}',
    #         mode='lines',
    #         line=dict(width=2, color=color_hex),
    #     ))

    # fig_trends.update_layout(
    #     title=f'Prix du marché EPEX pour le mois de {month_trend}, hors week-end',
    #     title_x=0.3,
    #     xaxis_title='Heure',
    #     yaxis_title='Prix [€/MWh]',
    #     margin=dict(l=0, r=0, t=100, b=0),
    #     height=700,
    #     legend=dict(orientation='h', yanchor="top", y=0.99, xanchor="right", x=0.99),
    #     # hovermode='x unified'
    # )
    
    # # Y bounds
    # fig_trends.update_yaxes(range=[0, 1.2 * df_prix_elec_week_grouped[df_prix_elec_week_grouped['month'] == month_trend]['market_price_eur_mwh'].max()])

    # st.plotly_chart(fig_trends)


    # # Calculte the mean spread for each month, defined as the diferrence between the max and the min of the market price
    # df_prix_elec_week_grouped_month = df_prix_elec_week_grouped.groupby(['year', 'month']).agg({'market_price_eur_mwh': ['max', 'min']}).reset_index()
    # df_prix_elec_week_grouped_month.columns = ['year', 'month', 'max_price', 'min_price']
    
    # df_prix_elec_week_grouped_month['spread'] = df_prix_elec_week_grouped_month['max_price'] - df_prix_elec_week_grouped_month['min_price']
    # df_prix_elec_week_grouped_month['spread'] = df_prix_elec_week_grouped_month['spread'].round(1)
    
    # df_prix_elec_week_grouped_month['clean_month'] = df_prix_elec_week_grouped_month['month'] + ' ' + df_prix_elec_week_grouped_month['year']
    
    # # Assign categories to the months and sort them
    # df_prix_elec_week_grouped_month['month'] = pd.Categorical(df_prix_elec_week_grouped_month['month'], categories=['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'], ordered=True)
    # df_prix_elec_week_grouped_month['year'] = pd.Categorical(df_prix_elec_week_grouped_month['year'], categories=[str(i) for i in range(2009, 2024)], ordered=True)
    
    
    
    # df_prix_elec_week_grouped_month.sort_values(by=['year','month'], inplace=True)
    
    # # Now plot the price per month for these two contracts, with the same colors as before. No bars, just lines, no consumption.
    # fig = go.Figure()
    # # Add the line trace for 'spread'
    # fig.add_trace(go.Scatter(
    #     x=df_prix_elec_week_grouped_month['clean_month'],
    #     y=df_prix_elec_week_grouped_month['spread'],
    #     name='Spread [€/MWh]',
    #     mode='lines',
    #     yaxis='y',
    #     line=dict(color='#316395')
    # ))
    
    # # Update layout
    # fig.update_layout(
    #     yaxis=dict(title='Spread [€/MWh]', showgrid=True),
    #     title=' ',
    #     margin=dict(l=0, r=0, t=40, b=0),
    #     xaxis_title=' ',
    #     height=500,
    #     legend=dict(orientation='h', yanchor="top", y=1.1, xanchor="right", x=0.99),
    #     hovermode='x unified'
    # )
    
    # st.plotly_chart(fig)
    

    return