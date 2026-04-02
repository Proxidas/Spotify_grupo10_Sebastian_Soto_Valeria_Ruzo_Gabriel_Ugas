import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os 

# Configuración de la página 
st.set_page_config(
    page_title="Dashboard de Spotify grupo 10",
    page_icon="🎵",
    layout="wide"  
)
    
carpeta_del_proyecto = os.path.dirname(os.path.abspath(__file__))
ruta_al_csv = os.path.join(carpeta_del_proyecto, '18. Spotify 2015-2025.csv')

# creo definición para cache de datos
@st.cache_data
def cargar_datos():
## Caragar el dataset
    if os.path.exists(ruta_al_csv):
        return pd.read_csv(ruta_al_csv)
    else:
        st.error(f"No se encontró el archivo en: {ruta_al_csv}")
        return pd.DataFrame()

df = cargar_datos()

## Manejo del Dataset

### Normalizar nombres de columnas
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

### Tipos de datos
tipos_df = df.dtypes.astype(str).reset_index()
tipos_df.columns = ["columna", "tipo de dato"]
st.table(tipos_df)

### Corregir fecha de object a date
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')

### Corregir Duplicados
duplicados_totales = df.duplicated().sum()
st.write(f"hay un total de: {duplicados_totales} duplicados")

df = df.drop_duplicates(subset=['track_name', 'artist_name'], keep='first') # borro los track name y artist name que se dupliquen

### Contar y corregir NA
conteo_na = df.isna().sum()
st.table(conteo_na)

df = df.dropna(subset=['track_name', 'album_name']) # borro los track name y artist name que tengan NA

### contar y corregir negativos
conteo_negativos = (df[['duration_ms', 'popularity', 'danceability', 'energy', 'key', 'mode', 'stream_count', 'explicit', 'loudness', 'instrumentalness', 'tempo']] < 0).sum()
st.table(conteo_negativos)

## Filtrar por género pop
df_pop = df[df['genre'] == 'Pop']  

# Para Logo spotify
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">', unsafe_allow_html=True)
logo_spotify = '<i class="fab fa-spotify" style="color: #1DB954; font-size: 1.5em; margin-right: 10px;"></i>'

#Sidebar
with st.sidebar:
    st.header("Navegación")
    st.markdown(f"{logo_spotify} **Proyecto Spotify**", unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("Filtros")
    
    ## Para hacer un filtro por año
    with st.expander("Rango de Datos\n(Fecha)", expanded=True):
        año_min = int(df['release_date'].dt.year.min())
        año_max = int(df['release_date'].dt.year.max())
        año_rango = st.slider(
            "Selecciona el periodo de tiempo:",
            min_value=año_min,
            max_value=año_max,
            value=(año_min, año_max)
        )
        df_filtrado = df[
        (df['release_date'].dt.year >= año_rango[0]) & 
        (df['release_date'].dt.year <= año_rango[1])
        ] # esto para que el dataset se filtre segun los parámetros del slider

# Cuerpo del dashboard

## Titulo
st.markdown(f"<h1 style='display: flex; align-items: center;'>\
            {logo_spotify} Evolución de las Características del Género Pop entre 2015 y 2025</h1>", unsafe_allow_html=True) # La fila arriba es la configuración del título.
st.markdown("Se presenta Gráficamente el estudio del Dataset de Spotify")

## Graficar
discográficas = df['label'].unique()
st.table(discográficas)
## Gráfico 1 
st.markdown("### Análisis de exito de las discográficas")

### crear un selector de cantidad de discográficas a mostrar
top_discograficas = st.selectbox("Cantidad de discográficas a ver",
                                 options=["3", "5", "Todas"],
                                 index=0)

### filtramos por label y contamos stream_count
label_streams = df_filtrado.groupby('label')['stream_count'].sum().reset_index()

### quitámos los datos independent pues no son una discográfica
label_streams = label_streams[label_streams['label'] != 'Independent']

### ordenamos por roden alfabético
label_streams = label_streams.sort_values(by='label', ascending=True)

### aplicamos el filtro
if top_discograficas == "Todas":
    df_final = label_streams
else:
    n = int(top_discograficas) 
    df_final = label_streams.sort_values(by= 'stream_count', ascending=False).head(n) #ordenamos segun exito temporalmente

df_final = df_final.sort_values(by='label', ascending=True) #ordenamos alfabéticamente

### visualización colores
SPOTIFY_GREEN = '#1DB954'
SPOTIFY_BLACK = '#191414'
WHITE = '#FFFFFF'

### creación del gráfico
fig1 = px.bar(
    df_final,
    x='label',
    y='stream_count',
    title='Cantidad de streams por discográfica',
    labels={'label': 'Discográfica', 'stream_count': 'Cantidad de streams'},
    template='plotly_dark',
)
### personalizar
fig1.update_traces(
    marker_color=SPOTIFY_GREEN,
    marker_line_color=WHITE,
    marker_line_width=0.5
)

fig1.update_layout(
    plot_bgcolor= SPOTIFY_BLACK,
    paper_bgcolor= SPOTIFY_BLACK,
    font=dict(color=WHITE),
    bargap=0.8 ,
    xaxis=dict(
        gridcolor=SPOTIFY_GREEN,
        showgrid=True,
        categoryorder='trace',
        tickfont=dict(
            family= 'Arial Black, sans-serif',
            size=12,
            color=WHITE
        )
    ),
    yaxis=dict(
        gridcolor=SPOTIFY_GREEN,
        showgrid=True,
        title="Suma de Streams"
    )
)
st.plotly_chart(fig1, use_container_width=True)


