import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import seaborn as sns
import plotly.figure_factory as ff
import scipy.stats as stats
import os

# Configuración de la página 
st.set_page_config(
    page_title="Dashboard de Spotify",
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
#st.table(tipos_df)

### Corregir fecha de object a date
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')

### Corregir Duplicados
duplicados_totales = df.duplicated().sum()
#st.write(f"hay un total de: {duplicados_totales} duplicados")

df = df.drop_duplicates(subset=['track_name', 'artist_name'], keep='first') # borro los track name y artist name que se dupliquen

### Contar y corregir NA
conteo_na = df.isna().sum()
#st.table(conteo_na)

df = df.dropna(subset=['track_name', 'album_name']) # borro los track name y artist name que tengan NA

### contar y corregir negativos
conteo_negativos = (df[['duration_ms', 'popularity', 'danceability', 'energy', 'key', 'mode', 'stream_count', 'explicit', 'loudness', 'instrumentalness', 'tempo']] < 0).sum()
#st.table(conteo_negativos)

### DATASET FILTRADO POR GENERO POP Y DISCOGRÁFICAS QUE ESTAN EN SPOTIFY (SIN INDEPENDENT)
df_pop_discograficas= df[(df['label'] != 'Independent') & (df['genre'] == 'Pop')]

 
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
        df_filtrado = df_pop_discograficas[
        (df['release_date'].dt.year >= año_rango[0]) & 
        (df['release_date'].dt.year <= año_rango[1])
        ] # esto para que el dataset se filtre segun los parámetros del slider

# Cuerpo del dashboard

## Titulo
st.markdown(f"<h1 style='display: flex; align-items: center;'>\
            {logo_spotify} Estandarización en las Características de las Canciones del Género Pop de Spotify  (2015 - 2025)</h1>", unsafe_allow_html=True) # La fila arriba es la configuración del título.
st.markdown("Se presenta Gráficamente el estudio del Dataset de Spotify")

#Pestañas de análisis de las discográficas, características técnicas y características sonoras

tab1, tab2, tab3 = st.tabs(["🏢 Sellos Discográficos", "⚙️ Análisis de Características Técnicas y Producción", "🔊 Análisis de Características Sonoras"])

with tab1:

    ## Graficar
    discográficas = df_pop_discograficas['label'].unique()
    #st.table(discográficas)
    ## Gráfico 1 
    st.markdown("### Top 7 de Discográficas en Spotify que producen música del género Pop")

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

    df_final = df_final.sort_values(by='stream_count', ascending=False) #ordenamos por cantidad de streams para que el grafico quede ordenado de mayor a menor 


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
    
with tab2:

    #Seccion del Analisis de las Variables Tecnicas y de Produción 
    st.markdown("### Análisis de las Características Técnicas y de  Poducción")

    #Filtrado de dataset para las variables tecnicas de las 3 discograficas mas exitosas 

    top3_nombres= df_pop_discograficas['label'].tolist()  #tomo los nommbres de las discograficas  

    df_solo_majors= df_filtrado[df_filtrado['label'].isin(top3_nombres)] #tomo los registros de las tres discograficas mas exitosas 


    #Agrupación , contando los datos de las discograficas de la variable explicit y  cambio el formato de la columna para que sea mas entendible en el grafico (1 y 0 a explicita y no explicita) 

    df_explicit = df_filtrado.groupby(['explicit']).size().reset_index(name='conteo')
    df_explicit['explicit'] = df_explicit['explicit'].astype(str)
    df_explicit['explicit'] = df_explicit['explicit'].replace({'1': 'Explícita', '0': 'No Explícita'})

    
    ### visualización colores
    SPOTIFY_GREEN = '#1DB954'
    SPOTIFY_BLACK = '#191414'
    WHITE = '#FFFFFF'
    SPOTIFY_FUCHSIA = '#B91D82'
    #Grafico 

    fig_sep = px.bar(
        df_explicit,
        x='explicit',
        y='conteo',
        title='Frecuencia Global del Contenido Explicito en las Canciones ',
        color='explicit',
        labels={'explicit': 'Tipo de letra', 'conteo': 'Cantidad de Canciones'},
        color_discrete_map={'Explícita': SPOTIFY_FUCHSIA, 'No Explícita':SPOTIFY_GREEN},
        template='plotly_dark',
        text_auto=True
    )

    # Ajustes visuales del grafico

    fig_sep.update_traces(
        width=0.4
    ) #ancho de las barras

    fig_sep.update_layout(
        showlegend=False,
        bargap=0.1,
        font= dict(color=WHITE),
        xaxis=dict( showgrid=True),
        yaxis=dict(showgrid=True),
        )# Ajustes en el eje X y Y

    st.plotly_chart(fig_sep, use_container_width=True)
    
    #Porcentajes de canciones explicitas y no explicitas
    total = df_explicit['conteo'].sum()
    cant_si = df_explicit[df_explicit['explicit'] == 'Explícita']['conteo'].sum() #cuenta cuantas canciones son explicitas
    cant_no = df_explicit[df_explicit['explicit'] == 'No Explícita']['conteo'].sum() #cuenta cuantas canciones no son explicitas
    
    porc_si = (cant_si / total * 100).round(2)
    porc_no = (cant_no / total * 100).round(2)

    st.write(f"🔎 El **{porc_si}%** de las canciones  tienen contenido **Explícito** 🔞.")
    st.write(f"🎵 El **{porc_no}%** de las canciones  son aptas para todo público.")
    

    
    ### Variable Loudness
    df_loudness = df_filtrado['loudness']
    group_labels_loudness = ['Distribución de Loudness'] 
    
    
    # Grafico de curva de densidad (KDE)
    fig = ff.create_distplot([df_loudness], group_labels_loudness, show_hist=True, show_rug=False)
    
    #  Personaliza las barras  
    fig.update_traces(opacity=0.5, selector=dict(type='bar'))
    
    # Personalizar la línea (Curva KDE)
    fig.update_traces(line=dict(color='red', width=3), selector=dict(type='scatter'))
    
    # Ajustes estéticos generales
    fig.update_layout(
    title_text='Histograma con Curva de Densidad de Loudness',
    bargap=0.01, 
    template="plotly_dark" 
)
    st.plotly_chart(fig, use_container_width=True)
