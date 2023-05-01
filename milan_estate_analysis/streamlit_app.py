import os

import folium
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import geopandas as gpd
from datetime import datetime
from streamlit_folium import folium_static


# Load data
nei_sale_rent = pd.read_csv(
    'milan_estate_analysis/rent_sale_per_neighborhood.csv')
# nei_sale_rent = pd.read_csv(
#     './rent_sale_per_neighborhood.csv')

st.write("""
# Milan's Sale and Rent Prices Analysis

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
select_rent_sale = st.sidebar.selectbox(
    'Select a rent or sale', ['Rent', 'Sale'], key=f'rent_sale')


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


# Question: Which are the neighborhoods in which normal civil houses of normal type that during the years increased the most in terms of average sale price?

st.write(f"""
    ### Neighborhoods Sale Prices Increase and decrease in the last 10 years
""")
abitazioni_civili = nei_sale_rent[(nei_sale_rent['Type'] == 'Abitazioni civili') & (
    nei_sale_rent['Status'] == 'NORMALE')]
avg_sale_abitazioni_civili = abitazioni_civili.groupby(
    ['Neighborhood', 'Year'])[['Avg_Sale_Price']].mean()

# Percentage increase in the average sale price between the first and last year for each neighborhood
percentage_increase = avg_sale_abitazioni_civili.groupby('Neighborhood')[
    ['Avg_Sale_Price']].apply(lambda x: (x.iloc[-1] - x.iloc[0]) / x.iloc[0] * 100)
# Rename the column
percentage_increase.rename(
    columns={'Avg_Sale_Price': 'Percentage_Increase'}, inplace=True)
# Sort the neighborhoods by the percentage increase
sorted_neighborhoods = percentage_increase.sort_values(
    by='Percentage_Increase', ascending=False)

show_data2 = st.checkbox("See the raw data", key='raw_data2')
if show_data2:
    sorted_neighborhoods


with st.container():
    col1, col2 = st.columns(2)
    with col1:
        fig1, ax1 = plt.subplots(figsize=(8, 7))
        ax1.barh(sorted_neighborhoods.head(10).index,
                 sorted_neighborhoods.head(10)['Percentage_Increase'])
        ax1.set_title('Most Increased')
        ax1.set_xlabel('Percentage Increase')
        st.pyplot(fig1)

    with col2:
        fig2, ax2 = plt.subplots()
        ax2.barh(sorted_neighborhoods.tail(10).index,
                 sorted_neighborhoods.tail(10)['Percentage_Increase'])
        ax2.set_title('Least Increased')
        ax2.set_xlabel('Percentage Increase')
        st.pyplot(fig2)


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
    ### Best and worst neighborhoods for rent sale rateo in {selected_year2}
""")
show_data3 = st.checkbox("See the raw data", key=f"raw_data3")
if show_data3:
    year_avg_rent_sale

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        fig1, ax1 = plt.subplots(figsize=(8, 7))
        ax1.bar(year_avg_rent_sale.head(10).index,
                year_avg_rent_sale.head(10)['Rent_Sale_Rateo'])
        ax1.set_title('Best')
        ax1.set_ylim([0, year_avg_rent_sale['Rent_Sale_Rateo'].max() + 0.05])
        ax1.set_xticklabels(year_avg_rent_sale.head(10).index, rotation=90)

        st.pyplot(fig1)

    with col2:
        fig2, ax2 = plt.subplots()
        ax2.bar(year_avg_rent_sale.tail(10).index,
                year_avg_rent_sale.tail(10)['Rent_Sale_Rateo'])
        ax2.set_title('Worst')
        ax2.set_ylim([0, year_avg_rent_sale['Rent_Sale_Rateo'].max() + 0.05])
        ax2.set_xticklabels(year_avg_rent_sale.tail(10).index, rotation=90)
        st.pyplot(fig2)


# FOURTH PLOT the MAP

st.write(f"""
    ### {select_rent_sale} Prices in {selected_year3}
""")

# Load the geojson file
neighborhood = gpd.GeoDataFrame.from_file(
    'milan_estate_analysis/milan_districts_modified.geojson')
# neighborhood = gpd.GeoDataFrame.from_file(
#     './milan_districts_modified.geojson')

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

if select_rent_sale == 'Rent':
    map_columns = ['Neighborhood', 'Avg_Rent_Price']
else:
    map_columns = ['Neighborhood', 'Avg_Sale_Price']

folium.Choropleth(
    geo_data=neighborhood,
    name='choropleth',
    data=year_avg_rent_sale2,
    columns=map_columns,
    key_on='feature.properties.NIL',
    fill_color='YlGnBu',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Average Sale Price'
).add_to(m)


folium_static(m)


# FIFTH PLOT

st.write("""
    ### AirBnBs Earnings in 2022
""")


# Read the airbnb data
# airbnb = pd.read_csv('./airbnb_listings2022_modified.csv')
airbnb = pd.read_csv('milan_estate_analysis/airbnb_listings2022_modified.csv')

# Clean up the price column
airbnb['price'] = airbnb['price'].str.replace(
    ',', '').str.replace('$', '').astype(float)


# Group the airbnb data by neighborhood and calculate the earnings
nei_earnings_2022 = airbnb.groupby(['neighborhood_cleansed'])[
    'price', 'availability_365'].mean().reset_index()

nei_earnings_2022['yearly_earnings'] = nei_earnings_2022['price'] * \
    (365 - nei_earnings_2022['availability_365'])

show_data4 = st.checkbox("See the raw data", key='raw_data4')
if show_data4:
    nei_earnings_2022

# Create a map of the city of Milan
m = folium.Map(location=[45.464664, 9.188540], zoom_start=12)

folium.Choropleth(
    geo_data=neighborhood,
    name='choropleth',
    data=nei_earnings_2022,
    columns=['neighborhood_cleansed', 'yearly_earnings'],
    key_on='feature.properties.NIL',
    fill_color='Reds',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Average Sale Price'
).add_to(m)


folium_static(m)


# Question: Is the nightly rate of an Airbnb affected by the sale price per sqm in the neighborhood?

st.write("""
    ### Nightly rate of an Airbnb vs Sale Price per sqm
""")

# Create a dictionary to map neighborhoods to colors
neighborhood_colors = {
    neighborhood: color
    for neighborhood, color in zip(
        nei_earnings_2022['neighborhood_cleansed'].unique(),
        sns.color_palette(n_colors=len(
            nei_earnings_2022['neighborhood_cleansed'].unique()))
    )
}

# Merge the airbnb data with the nei_sale_rent data
nei_sale_rent_bnb_2022 = nei_earnings_2022.merge(
    nei_sale_rent[nei_sale_rent['Year'] == 2022],
    left_on='neighborhood_cleansed',
    right_on='Neighborhood',
    how='outer'
).dropna()


# Create a scatter plot with colored dots based on the neighborhood
fig, ax = plt.subplots(figsize=(10, 8))
for neighborhood, group in nei_sale_rent_bnb_2022.groupby('neighborhood_cleansed'):
    ax.scatter(
        group['Avg_Sale_Price'],
        group['price'],
        color=neighborhood_colors[neighborhood],
        label=neighborhood,
    )


ax.set_xlabel('Sale Price per sqm')
ax.set_ylabel('Average Price per Night')
ax.set_title('Relationship between Airbnb Earnings and Sale Price per sqm')

# Put the legend outside the plot
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

yticks = list(range(0, 401, 50)) + list(range(600, 1401, 200))
ax.set_yticks(yticks)


st.pyplot(fig)
