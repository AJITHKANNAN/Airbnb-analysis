import pandas as pd
import pymongo
import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu

# Setting up page configuration
st.set_page_config(page_title= "Airbnb Data Visualization",
                   layout= "wide",
                   initial_sidebar_state= "expanded",
                   menu_items={'About': """Data collected from Mongodb atlas"""}
                  )

# Creating option menu in the side bar
with st.sidebar:
    selected = option_menu("Menu", ["Home","Synopsis","Examine"], 
                           icons=["house","graph-up-arrow","bar-chart-line"],
                           menu_icon= "menu-button-wide",
                           default_index=0
                           )

# Connecting with MONGODB ATLAS and collecting the data
client = pymongo.MongoClient("mongodb+srv://root:password@cluster0.6ofum1s.mongodb.net/Airbnb_analysis")
db = client.sample_airbnb
col = db.listingsAndReviews

# READING THE CLEANED DATAFRAME
df = pd.read_csv('Airbnb_test.csv')

# HOME PAGE
if selected == "Home":
    
    st.markdown("## :blue[Domain]:")
    st.subheader("Travel Industry, Property Management and Tourism")
    st.markdown("## :blue[Technologies used]:")
    st.subheader("Python, Pandas, Plotly, Streamlit, MongoDB")
    st.markdown("## :blue[Overview]:")
    st.subheader(""" Get Airbnb data from MongoDB Atlas, perform data cleaning and, develop interactive visualizations, to gain insights about pricing variations, availability patterns, and location-based trends. """ )
    st.markdown("#   ")
    st.markdown("#   ")
    
    
# OVERVIEW PAGE
if selected == "Synopsis":
    tab1,tab2 = st.tabs(["$\huge  -RAW DATA- $",  "$\huge -INSIGHTS- $"])
    
    # RAW DATA TAB
    with tab1:
        
        # RAW DATA
        col1,col2 = st.columns(2)
        if col1.button("View Raw JSON data"):
            col1.write(col.find_one())
            
        # DATAFRAME FORMAT
        if col2.button("View Dataframe"):
            col1.write(col.find_one())
            col2.write(df)
       
    # INSIGHTS TAB
    with tab2:
        
        # GETTING USER INPUTS
        country = st.sidebar.multiselect('Select the Countries',sorted(df.Country.unique())) 
        prop = st.sidebar.multiselect('Select the Property type',sorted(df.Property_type.unique()))
        room = st.sidebar.multiselect('Select the Room_type',sorted(df.Room_type.unique()))
        
        price = st.slider('Set your Price Range',df.Price.min(),df.Price.max(),(df.Price.min(),df.Price.max()))
        
        # USER INPUT INTO QUERY
        query = f'Country in {country} & Room_type in {room} & Property_type in {prop} & Price >= {price[0]} & Price <= {price[1]}'
        
        # CREATING COLUMNS
        col1,col2 = st.columns(2,gap='medium')
        with col1:
            
            # TOP 10 Property Types
            df1 = df.query(query).groupby(["Property_type"]).size().reset_index(name="Listings").sort_values(by='Listings',ascending=False)[:10]
            fig = px.bar(df1,
                         title='Top 10 Property Types',
                         y='Listings',
                         x='Property_type',
                         orientation='v',
                         color='Property_type',
                        )
            st.plotly_chart(fig,use_container_width=True) 
        
            # TOP 10 HOSTS at that Region
            df2 = df.query(query).groupby(["Host_name"]).size().reset_index(name="Listings").sort_values(by='Listings',ascending=False)[:10]
            fig = px.bar(df2,
                         title='Top 10 Hosts with Highest number of Listings',
                         x='Listings',
                         y='Host_name',
                         orientation='h',
                         color='Host_name',
                         )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig,use_container_width=True)
        
        with col2:
            
            # TOTAL LISTINGS OF EACH ROOM TYPES 
            df1 = df.query(query).groupby(["Room_type"]).size().reset_index(name="counts")
            fig = px.pie(df1,
                         title='Total Listings in each Room_types',
                         names='Room_type',
                         values='counts',
                         color_discrete_sequence=px.colors.sequential.Rainbow
                        )
            fig.update_traces(textposition='outside', textinfo='value+label')
            st.plotly_chart(fig,use_container_width=True)
            
            # COUNTRY WISE TOTAL LISTINGS 
            country_df = df.query(query).groupby(['Country'],as_index=False)['Name'].count().rename(columns={'Name' : 'Total_Listings'})
            fig = px.choropleth(country_df,
                                title='Total Listings in each Country',
                                locations='Country',
                                locationmode='country names',
                                color='Total_Listings',
                                color_continuous_scale=px.colors.sequential.Plasma
                               )
            st.plotly_chart(fig,use_container_width=True)
        
# EXPLORE PAGE
if selected == "Examine":
    st.markdown(" Examine the data")
    
    # GETTING USER INPUTS
    country = st.sidebar.multiselect('Select a Country',sorted(df.Country.unique()))
    prop = st.sidebar.multiselect('Select Property_type',sorted(df.Property_type.unique()))
    room = st.sidebar.multiselect('Select Room_type',sorted(df.Room_type.unique()))
    
    price = st.slider('Select Price',df.Price.min(),df.Price.max(),(df.Price.min(),df.Price.max()))
    
    # CONVERTING THE USER INPUT INTO QUERY
    query = f'Country in {country} & Room_type in {room} & Property_type in {prop} & Price >= {price[0]} & Price <= {price[1]}'
    
    # HEADING 1
    st.markdown("## Price Prediction")
    
    # CREATING COLUMNS
    col1,col2 = st.columns(2,gap='medium')
    
    with col1:
        
        # AVERAGE PRICE BY ROOM TYPE 
        price_df = df.query(query).groupby('Room_type',as_index=False)['Price'].mean().sort_values(by='Price')
        fig = px.bar(data_frame=price_df,
                     x='Room_type',
                     y='Price',
                     color='Price',
                     title='Average Price in each Room type'
                    )
        st.plotly_chart(fig,use_container_width=True)
        
        # Heading 2
        st.markdown("## Analyzing Availability ")
        
        # AVAILABILITY BY ROOM TYPE 
        fig = px.box(data_frame=df.query(query),
                     x='Room_type',
                     y='Availability_365',
                     color='Room_type',
                     title='Availability by Room_type'
                    )
        st.plotly_chart(fig,use_container_width=True)
        
    with col2:
        
        # AVERAGE PRICE IN COUNTRIES 
        country_df = df.query(query).groupby('Country',as_index=False)['Price'].mean()
        fig = px.scatter_geo(data_frame=country_df,
                                       locations='Country',
                                       color= 'Price', 
                                       hover_data=['Price'],
                                       locationmode='country names',
                                       size='Price',
                                       title= 'Average Price in each Country',
                                       color_continuous_scale='agsunset'
                            )
        col2.plotly_chart(fig,use_container_width=True)
        
        st.markdown("#   ")
        st.markdown("#   ")
        
        # AVERAGE AVAILABILITY IN COUNTRIES 
        country_df = df.query(query).groupby('Country',as_index=False)['Availability_365'].mean()
        country_df.Availability_365 = country_df.Availability_365.astype(int)
        fig = px.scatter_geo(data_frame=country_df,
                                       locations='Country',
                                       color= 'Availability_365', 
                                       hover_data=['Availability_365'],
                                       locationmode='country names',
                                       size='Availability_365',
                                       title= 'Average Availability in each Country',
                                       color_continuous_scale='agsunset'
                            )
        st.plotly_chart(fig,use_container_width=True)
        
        