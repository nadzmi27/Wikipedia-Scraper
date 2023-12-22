# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 13:01:29 2023

@author: Nadzmi Ag Thomas
"""
# Import dependencies
import streamlit as st
import Scraper
import pandas as pd

# Set page title
st.set_page_config(
    page_title="Wikipedia Scraper",
    page_icon=":broom:",
)

# ================
# Define functions

# Scrape the links


def scrape_data(data):
    return Scraper.wikipedia_links_to_df(data)

# Convert dataframe to csv


def df_to_csv(df):
    return df.to_csv()


# =========
# Dashboard

# Description
st.header(":rainbow[Wikipedia Scraper!] :sunglasses:", divider='rainbow')

st.write(
    "Wikipedia Scraper will turn list of Wikipedia pages into **.csv** files \
    containing all the necessary information. The data scraped then can be \
    used for task such as NLP. For more information please visit my \
    [github repo](https://github.com/nadzmi27/Wikipedia-Scraper)\
    \n\nTo get started, upload a **.csv** file with a column named **link** \
    containing the links to Wikipedia pages (1 link per row). \
    Other column beside **link** will be included in the final dataframe. \
    For a quick use, write the links in textbox."
)

st.divider()

# Upload file
uploaded_file = st.file_uploader("Upload a **.csv** file")

st.markdown("<p style='text-align: center; color: grey;'>or</p>",
            unsafe_allow_html=True)

# Links input
links_input = st.text_input('Enter links seperated by comma ( , )')

submitted = st.button("Scrape")

st.divider()

# Scraping
if (links_input or uploaded_file) and submitted:
    if links_input:
        links = links_input.split(',')
        links = [x.strip() for x in links]
    else:
        links = pd.read_csv(uploaded_file)

    df_output = scrape_data(links)
    try:
        st.dataframe(df_output)
    except:
        st.dataframe(df_output.astype(str))

    st.download_button(
        label="Download as CSV",
        data=df_to_csv(df_output),
        file_name="wikipedia_scrapes.csv",
        mime='text/csv'
    )
