import numpy as np
import pandas as pd
import zipfile
import plotly.express as px
import matplotlib.pyplot as plt
import requests
from io import BytesIO
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from my_plots import *
import streamlit as st

@st.cache_data
def load_name_data():
    names_file = 'https://www.ssa.gov/oact/babynames/names.zip'
    response = requests.get(names_file)
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        dfs = []
        files = [file for file in z.namelist() if file.endswith('.txt')]
        for file in files:
            with z.open(file) as f:
                df = pd.read_csv(f, header=None)
                df.columns = ['name','sex','count']
                df['year'] = int(file[3:7])
                dfs.append(df)
        data = pd.concat(dfs, ignore_index=True)
    data['pct'] = data['count'] / data.groupby(['year', 'sex'])['count'].transform('sum')
    return data

@st.cache_data
def ohw(df):
    nunique_year = df.groupby(['name', 'sex'])['year'].nunique()
    one_hit_wonders = nunique_year[nunique_year == 1].index
    one_hit_wonder_data = df.set_index(['name', 'sex']).loc[one_hit_wonders].reset_index()
    return one_hit_wonder_data

data = load_name_data()
ohw_data = ohw(data)

st.title("Popularity of Names Over Time")

tab1, tab2 = st.tabs(['Nmaes', 'Year'])
with tab1:
    input_name = st.text_input('Enter a name: ')
    name_data = data[data['name'] == input_name].copy()
    fig = px.line(name_data, x = 'year', y = 'count', color = 'sex')
    st.plotly_chart(fig)

with tab2:
    year_input = st.slider('Year', min_value = 1880, max_value = 2023, value = 2000)
    fig2 = top_names_plot(data, year = year_input)
    st.plotly_chart(fig2)

    st.write('Unique Names Table')
    output_table = unique_names_summary(data, 2000)
    st.dataframe(output_table)

# add a sidebar
st.sidebar.title("Filters")
gender = st.sidebar.radio("Select Gender:", ['Male', 'Female'])
year = st.sidebar.slider("Select Year Range:", 1880, 2023, (2000, 2023))

filtered_data = data[data['sex'] == gender]
filtered_data = filtered_data[
    (filtered_data['year'] >= year[0]) & (filtered_data['year'] <= year[1])
]
# add one more interactive element
name_count = filtered_data['name'].nunique()
st.sidebar.markdown(f"### Total Unique Names: {name_count}")

# add a container
with st.container():
    st.markdown("### One-Hit Wonders")
    st.write(f"Total One-Hit Wonders: {len(ohw_data)}")
    st.dataframe(ohw_data.head(10))
