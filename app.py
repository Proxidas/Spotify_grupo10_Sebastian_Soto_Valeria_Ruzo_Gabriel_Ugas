import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import seaborn as sns
import plotly.figure_factory as ff
import os
import matplotlib.pyplot as plt



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

##DATASET FILTRADA POR GENERO POP
df_pop = df[df['genre'] == 'Pop']

### DATASET FILTRADO POR GENERO POP Y DISCOGRÁFICAS QUE ESTAN EN SPOTIFY (SIN INDEPENDENT)
df_pop_discograficas = df[(df['label'] != 'Independent') & (df['genre'] == 'Pop')]

 
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
            {logo_spotify} Comportamiento en las Características de las Canciones del Género Pop de Spotify  (2015 - 2025)</h1>", unsafe_allow_html=True) # La fila arriba es la configuración del título.
st.markdown("Se presenta Gráficamente el estudio del Dataset de Spotify")



## Gráfico 1 

### crear un selector de cantidad de discográficas a mostrar
top_discograficas = st.selectbox("Cantidad de discográficas a ver",
                                    options=["3", "5", "Todas"],
                                    index=0)

### filtramos por label y contamos stream_count

###DATA SIN INDEPENDENT (los quitamos porque no son una discografica)
df_count_musicas_sin_indie = df_filtrado['label'].value_counts().reset_index()
df_count_musicas_sin_indie.columns = ['Discográfica', 'Cantidad de Canciones']

df_count_musicas_con_indie = df_pop['label'].value_counts().reset_index()
df_count_musicas_con_indie.columns = ['Discográfica', 'Cantidad de Canciones']


### Lógica para el Top (3, 5 o Todas)
if top_discograficas == "Todas":
    df_final = df_count_musicas_sin_indie.sort_values(by='Cantidad de Canciones', ascending=False)
else:
    # Convertimos el texto "3" o "5" a número entero para filtrar
    n = int(top_discograficas)
    df_final = df_count_musicas_sin_indie.sort_values(by='Cantidad de Canciones', ascending=False).head(n)

SPOTIFY_GREEN = '#1DB954'
SPOTIFY_BLACK = '#191414'
SPOTIFY_FUCHSIA = '#B91D82'
WHITE = '#FFFFFF'

### creación del gráfico
st.subheader(f"Top {top_discograficas} Discográficas en Spotify que producen música del género Pop")

fig_label = px.bar(
    df_final,
    x='Discográfica',
    y='Cantidad de Canciones',
    labels={'Discográfica': 'Discográfica', 'Cantidad de Canciones': 'Cantidad de Canciones'},
    template='plotly_dark'
    )

### personalizar
fig_label.update_traces(
    marker_color=SPOTIFY_GREEN,
    marker_line_color=WHITE,
    marker_line_width=0.5
    )

fig_label.update_layout(
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
        )
    )
st.plotly_chart(fig_label, use_container_width=True)

# Sumamos el total de canciones con y sin indie para calcular el porcentaje
total_global = df_count_musicas_con_indie['Cantidad de Canciones'].sum()   # Total de canciones pop (con indie)
total_sin_indie = df_count_musicas_sin_indie['Cantidad de Canciones'].sum() # Total de canciones pop de las discograficas (sin indie)
    
# Calculo del porcentaje que representan las discográficas sobre el total
porc_total_discografica = (total_sin_indie / total_global) * 100
    
col1, col2 = st.columns(2)
with col1:
    st.metric("Cantidad Total de Canciones Pop con Sellos Discográficos", f"{total_sin_indie}")
with col2:
    st.metric("Porcentaje de Canciones Pop con Sellos Discográficos en Spotify", f"{porc_total_discografica:.2f}%")


#Seccion del Analisis de las Variables Tecnicas y de Produción 
st.markdown("### Análisis de las Características Técnicas y de  Poducción")

# variables tecnicas
var_tecnicas = {
    "Energía": "energy",
    "Volumen (dB)": "loudness",
    "Instrumentalidad": "instrumentalness",
    "Duración (ms)": "duration_ms"
}

#crea las pestñas para seleccionar la variable
tabs = st.tabs(list(var_tecnicas.keys()))
for i, (nombre_visual, columna ) in enumerate(var_tecnicas.items()):
    with tabs[i]:

        st.subheader(f"Análisis de {nombre_visual}")

        fig_tecnicas = px.violin(df_filtrado,
                        y=columna,
                        box=True,
                        hover_data=df_filtrado.columns,
                        color_discrete_sequence=[SPOTIFY_GREEN],
        )
        fig_tecnicas.update_layout(
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            yaxis_title=nombre_visual,
            xaxis_title="Frecuencia en el Pop",
            height=600
        )

        st.plotly_chart(fig_tecnicas, use_container_width=True)

        # Estadísticas de soporte
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Media", f"{df_filtrado[columna].mean():.2f}")
        with col2:
            st.metric("Desviación Estándar", f"{df_filtrado[columna].std():.2f}")
        with col3:
            st.metric("Índice de Estandarización (Curtosis)", f"{df_filtrado[columna].kurt():.2f}")
        with col4:
            st.metric("Coeficiente de Variación", f"{(df_filtrado[columna].std() / df_filtrado[columna].mean() * 100):.2f}%")
            

# Variable Explicit

#Agrupación , contando los datos de las discograficas de la variable explicit y  cambio el formato de la columna para que sea mas entendible en el grafico (1 y 0 a explicita y no explicita) 

df_explicit = df_filtrado.groupby(['explicit']).size().reset_index(name='conteo')
df_explicit['explicit'] = df_explicit['explicit'].astype(str)
df_explicit['explicit'] = df_explicit['explicit'].replace({'1': 'Explícita', '0': 'No Explícita'})

#Grafico 
st.subheader("Análisis de contenido explicito")

fig_exp = px.bar(
    df_explicit,
    x='explicit',
    y='conteo',
    color='explicit',
    labels={'explicit': 'Tipo de letra', 'conteo': 'Cantidad de Canciones'},
    color_discrete_map={'Explícita': SPOTIFY_FUCHSIA, 'No Explícita':SPOTIFY_GREEN},
    template='plotly_dark',
    text_auto=True
    )

# Ajustes visuales del grafico

fig_exp.update_traces(
        width=0.4
) #ancho de las barras

fig_exp.update_layout(
    showlegend=False,
    bargap=0.1,
    font= dict(color=WHITE),
    xaxis=dict( showgrid=True),
    yaxis=dict(showgrid=True),
)# Ajustes en el eje X y Y

st.plotly_chart(fig_exp, use_container_width=True)
    
#Porcentajes de canciones explicitas y no explicitas
total = df_explicit['conteo'].sum()
cant_si = df_explicit[df_explicit['explicit'] == 'Explícita']['conteo'].sum() #cuenta cuantas canciones son explicitas
cant_no = df_explicit[df_explicit['explicit'] == 'No Explícita']['conteo'].sum() #cuenta cuantas canciones no son explicitas
    
porc_si = (cant_si / total * 100).round(2)
porc_no = (cant_no / total * 100).round(2)

col1, col2 = st.columns(2)
with col1:
    st.metric("El porcentaje de Canciones Explícitas", f"{porc_si}%")
with col2:
    st.metric("El porcentaje de Canciones No Explícitas", f"{porc_no}%")

#Analisis de las caracteristicas sonoras

st.markdown("### Análisis de las Características Sonoras")

#variables sonoras
var_sonoras = {
    "Clave Musical": "key",
    "Bailabilidad": "danceability",
    "Tempo (BPM)": "tempo"
}

#crea pestañas para seleccionar la variable
tabs_sonoras = st.tabs(list(var_sonoras.keys())) 
for i, (nombre_visual, columna) in enumerate(var_sonoras.items()):
    with tabs_sonoras[i]:

        st.subheader(f"Análisis de {nombre_visual}")

#creación del gráfico
        fig_sonoras = px.violin(df_filtrado,
                        y=columna,
                        box=True,
                        hover_data=df_filtrado.columns,
                        color_discrete_sequence=[SPOTIFY_GREEN],
        )

    #diseño del gráfico
        fig_sonoras.update_layout(
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            yaxis_title=nombre_visual,
            xaxis_title="Frecuencia en el Pop",
            height=600
        )

        st.plotly_chart(fig_sonoras, use_container_width=True)

        #  Estadísticas de soporte
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Media", f"{df_filtrado[columna].mean():.2f}")
        with col2:
            st.metric("Desviación Estándar", f"{df_filtrado[columna].std():.2f}")
        with col3:
            st.metric("Índice de Estandarización (Curtosis)", f"{df_filtrado[columna].kurt():.2f}")
        with col4:
            st.metric("Coeficiente de Variación", f"{(df_filtrado[columna].std() / df_filtrado[columna].mean() * 100):.2f}%")


# Analisis de la var mode

st.subheader("Análisis de la Modalidad Musical")

# Agrupación por modalidad musical y conteo
df_mode = df_filtrado.groupby(['mode']).size().reset_index(name='conteo')  
df_mode['mode'] = df_mode['mode'].astype(str)
df_mode['mode'] = df_mode['mode'].replace({'1': 'Mayor', '0': 'Menor'})

# Gráfico
fig_mode = px.bar(
    df_mode,
    x='mode',
    y='conteo',
    color='mode',
    labels={'mode': 'Modalidad Musical', 'conteo': 'Cantidad de Canciones'},
    color_discrete_map={'Mayor': SPOTIFY_GREEN, 'Menor': SPOTIFY_FUCHSIA},
    template='plotly_dark',
    text_auto=True
)

# Ajustes visuales del gráfico
fig_mode.update_traces(
        width=0.4
)

fig_mode.update_layout(
    showlegend=False,
    bargap=0.1,
    font= dict(color=WHITE),
    xaxis=dict( showgrid=True),
    yaxis=dict(showgrid=True),
)

st.plotly_chart(fig_mode, use_container_width=True)

#porcentajes de canciones en modo mayor y menor
total_mode = df_mode['conteo'].sum()
cant_mayor = df_mode[df_mode['mode'] == 'Mayor']['conteo'].sum()
cant_menor = df_mode[df_mode['mode'] == 'Menor']['conteo'].sum()

porc_mayor = (cant_mayor / total_mode * 100).round(2)
porc_menor = (cant_menor / total_mode * 100).round(2)  

col1, col2 = st.columns(2)
with col1:
    st.metric("El porcentaje de Canciones en Modo Mayor", f"{porc_mayor}%")
with col2:
    st.metric("El porcentaje de Canciones en Modo Menor", f"{porc_menor}%")

#correlacion estre las variables 
st.markdown("### Correlación entre las Variables Técnicas y Sonoras")

caracteristicas = ['tempo', 'loudness', 'instrumentalness', 'energy', 'duration_ms', 'danceability']
matriz_correlacion = df_filtrado[caracteristicas].corr()

#grafico
fig_correlacion= px.imshow(
    matriz_correlacion,
    text_auto=".2f",      
    aspect="auto",        
    color_continuous_scale='RdBu_r', 
    labels=dict(color="Correlación"),
)
st.plotly_chart(fig_correlacion, use_container_width=True)
st.dataframe(matriz_correlacion)