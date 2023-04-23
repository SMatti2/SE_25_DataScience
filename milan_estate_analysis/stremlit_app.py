import os

import folium
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from streamlit_folium import folium_static

import geopandas as gpd

# Load data
nei_sale_rent = pd.read_csv('rent_sale_per_neighborhood.csv')

st.write("""
# Milan's Sale and Rent Prices

""")


# SIDE BAR FILTERS

# Sidebar filters for the historical data
st.sidebar.title(('Filters for the Line Plots'))

selected_neighborhood1 = st.sidebar.selectbox(
    'Select a neighborhood', sorted(nei_sale_rent['Neighborhood'].unique()), key='nbh1')

selected_type1 = st.sidebar.selectbox(
    'Select a type', nei_sale_rent['Type'].unique(), key=f'type1')

selected_status1 = st.sidebar.selectbox(
    'Select a status', nei_sale_rent['Status'].unique(), key=f'status1')

# Sidebar filters for the bar charts
st.sidebar.title(('Filters for the Bar Charts'))

selected_year2 = st.sidebar.selectbox(
    'Select a year', sorted(nei_sale_rent['Year'].unique()), key=f'year2')

selected_type2 = st.sidebar.selectbox(
    'Select a type', nei_sale_rent['Type'].unique(), key=f'type2')

selected_status2 = st.sidebar.selectbox(
    'Select a status', nei_sale_rent['Status'].unique(), key=f'status2')

# Sidebar filters for the map
st.sidebar.title(('Filters for the Map'))

selected_year3 = st.sidebar.selectbox(
    'Select a year', sorted(nei_sale_rent['Year'].unique()), key=f'year3')
selected_type3 = st.sidebar.selectbox(
    'Select a type', nei_sale_rent['Type'].unique(), key=f'type3')
selected_status3 = st.sidebar.selectbox(
    'Select a status', nei_sale_rent['Status'].unique(), key=f'status3')


# FIRST PLOT

filtered_df = nei_sale_rent[(nei_sale_rent['Neighborhood'] == selected_neighborhood1) & (
    nei_sale_rent['Type'] == selected_type1) & (nei_sale_rent['Status'] == selected_status1)]

st.write(f"""
    ### Average Sale and Rent Prices in the years in {selected_neighborhood1}
""")

yearly_avg_rent_sale = filtered_df.groupby(
    'Year')[['Avg_Sale_Price', 'Avg_Rent_Price']].mean()

show_data = st.checkbox("See the raw data")
if show_data:
    yearly_avg_rent_sale

fig, ax1 = plt.subplots()

ax2 = ax1.twinx()

ax1.plot(yearly_avg_rent_sale.index,
         yearly_avg_rent_sale['Avg_Sale_Price'], 'b')
ax1.set_xlabel('Year')
ax1.set_ylabel('Sale Price', color='b')
ax1.tick_params('y', colors='b')

ax2.plot(yearly_avg_rent_sale.index,
         yearly_avg_rent_sale['Avg_Rent_Price'], 'r')
ax2.set_ylabel('Rent Price', color='r')
ax2.tick_params('y', colors='r')

fig.tight_layout()

st.pyplot(fig)


# SECOND PLOT & THIRD PLOT
filtered_df2 = nei_sale_rent[(nei_sale_rent['Year'] == selected_year2) &
                             (nei_sale_rent['Type'] == selected_type2) &
                             (nei_sale_rent['Status'] == selected_status2)]


# Given a year, show the average sale and rent prices for each neighborhood
year_avg_rent_sale = filtered_df2[filtered_df2['Year'] == selected_year2].groupby(
    ['Neighborhood'])[['Avg_Sale_Price', 'Avg_Rent_Price']].mean()


# Calculate the percentage rent and sale prices
year_avg_rent_sale['Rent_Sale_Rateo'] = (
    year_avg_rent_sale['Avg_Rent_Price'] / year_avg_rent_sale['Avg_Sale_Price']) * 100

# Sort the values by the rateo
year_avg_rent_sale = year_avg_rent_sale.sort_values(
    by='Rent_Sale_Rateo', ascending=False)


st.write(f"""
    ### Best and worst 10 neighborhoods for rent sale rateo in {selected_year2}
""")
show_data2 = st.checkbox("See the raw data", key=f"year_avg_rent_sale")
if show_data2:
    year_avg_rent_sale

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        fig1, ax1 = plt.subplots(figsize=(5, 4))
        ax1.bar(year_avg_rent_sale.head(10).index,
                year_avg_rent_sale.head(10)['Rent_Sale_Rateo'])
        ax1.set_title('Best')
        ax1.set_ylim([0, year_avg_rent_sale['Rent_Sale_Rateo'].max() + 0.05])
        ax1.set_xticklabels(year_avg_rent_sale.head(10).index, rotation=90)

        st.pyplot(fig1)

    with col2:
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        ax2.bar(year_avg_rent_sale.tail(10).index,
                year_avg_rent_sale.tail(10)['Rent_Sale_Rateo'])
        ax2.set_title('Worst')
        ax2.set_ylim([0, year_avg_rent_sale['Rent_Sale_Rateo'].max() + 0.05])
        ax2.set_xticklabels(year_avg_rent_sale.tail(10).index, rotation=90)
        st.pyplot(fig2)


# # FOURTH PLOT the MAP
neighborhood = gpd.GeoDataFrame.from_file(
    './milan_districts_modified.geojson')

filtered_df3 = nei_sale_rent[(nei_sale_rent['Year'] == selected_year3) &
                             (nei_sale_rent['Type'] == selected_type3) &
                             (nei_sale_rent['Status'] == selected_status3)]

# Given a year, show the average sale and rent prices for each neighborhood
year_avg_rent_sale2 = filtered_df3[filtered_df3['Year'] == selected_year3].groupby(
    ['Neighborhood'])[['Avg_Sale_Price', 'Avg_Rent_Price']].mean()

# Make neighborhood a column
year_avg_rent_sale2.reset_index(inplace=True)

# Create a map of the city of Milan
m = folium.Map(location=[45.464664, 9.188540], zoom_start=12)


folium.Choropleth(
    geo_data=neighborhood,
    name='choropleth',
    data=year_avg_rent_sale2,
    columns=['Neighborhood', 'Avg_Sale_Price'],
    key_on='feature.properties.NIL',
    fill_color='YlGnBu',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Average Sale Price'
).add_to(m)


folium_static(m)
