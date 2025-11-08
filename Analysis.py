import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns

st.title("Noves oficines i predicció de potencials localitzacions futures.")

st.write("> Objectiu: L'objectiu d'aquest projecte es centra en buscar ubicacions idònies per obrir noves oficines de la Caixa d'Enginyers, valorant tant la possiblitat d'oficines fixes com oficinse mòbils que arriben a una determinada zona. A més, es desenvoluparà també un model predictiu amb l'ajuda d'IA que permeti identificar potencials localitzacions futures.")

st.subheader("Dades ")
st.write("> Fonts Oficials: INE, BdE i dades pròpies de Caixa d'Enginyers.")


st.subheader("Conclusió")

#Include emoticons
st.write("This streamlit app adds *different formats* and icons is as :sunglasses:")
st.write("This streamlit app adds *different formats* and icons is as :snow_cloud:")


#Let's create a sidebar

st.sidebar.header("*AI'll fint it*")
st.sidebar.write("**Arnau Muñoz**")
st.sidebar.write("**Míriam López**")
st.sidebar.write("**Luis Martínez**")
st.sidebar.write("**Marc Rodríguez**")



#Basics line chart, area chart and bar chart
chart_data = pd.DataFrame(
np.random.randn(20, 3),
columns=['a', 'b', 'c'])
st.write("This is line chart")
st.line_chart(chart_data)
st.write("This is the area chart")
st.area_chart(chart_data)
st.write("This is the bar chart")
st.bar_chart(chart_data)



#Let's embeed a Matplotlib in our streamlit app
import matplotlib.pyplot as plt

#Example 1
arr = np.random.normal(1, 1, size=100)
fig, ax = plt.subplots()
ax.hist(arr, bins=20)
st.write("Example 1 of plot with Matplotlib")
st.pyplot(fig)

#Seaborn: Seaborn builds on top of a Matplotlib figure so you can display the charts in the same way
import seaborn as sns
penguins = sns.load_dataset("penguins")
st.dataframe(penguins[["species", "flipper_length_mm"]].sample(6))

# Create Figure beforehand
fig = plt.figure(figsize=(9, 7))
sns.histplot(data=penguins, x="flipper_length_mm", hue="species", multiple="stack")
plt.title("Hello Penguins!")
st.write("Example of a plot with Seaborn library")
st.pyplot(fig)



#Step 10: Show a dataframe table in your app
st.dataframe(penguins[["species", "flipper_length_mm"]].sample(6))



#Creating a map Maps
#Let's create randomly a lattitude and longitud variables
df = pd.DataFrame(
np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
columns=['lat', 'lon']) #These columns are totally necessary
st.write("Example of a plot with a map")
st.map(df)


#Let's include Plotly library

import plotly.figure_factory as ff


# Add histogram data
x1 = np.random.randn(200) - 2
x2 = np.random.randn(200)
x3 = np.random.randn(200) + 2

# Group data together
hist_data = [x1, x2, x3]

group_labels = ['Group 1', 'Group 2', 'Group 3']

# Create distplot with custom bin_size
fig = ff.create_distplot(
hist_data, group_labels, bin_size=[.1, .25, .5])

# Plot!
st.write("Example of a plot with Plotly")
st.plotly_chart(fig, use_container_width=True)
