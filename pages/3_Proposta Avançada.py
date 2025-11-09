import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
from PIL import Image

icon = Image.open("assets/logo_small.png")   
st.set_page_config(
    page_title="AI'll find it — Proposta Avançada",
    page_icon=icon,        
    layout="wide"
)
import streamlit as st, base64, pathlib

# --- convierte tu logo local a base64 para poder incrustarlo en HTML ---
def img_b64(path: str) -> str:
    return base64.b64encode(open(path, "rb").read()).decode()

logo_path = "assets/logo_small.png"  # cambia la ruta a la tuya
logo_b64  = img_b64(logo_path)

with st.sidebar:
    st.markdown(
        f"""
        <style>
        .brand-row {{
            display:flex;
            align-items:center;      
            gap:10px;                
            margin: 6px 0 14px 0;    
        }}
        .brand-row img {{
            width:28px; height:28px; 
            object-fit:contain;
            border-radius:6px;      
        }}
        .brand-row .brand-text {{
            font-size:1.05rem;  
            font-weight:600;
            font-style:italic;    
            line-height:1;      
        }}
        </style>

        <div class="brand-row">
            <img src="data:image/png;base64,{logo_b64}" alt="logo">
            <div class="brand-text">AI'll find it</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.sidebar.write("**Arnau Muñoz**")
st.sidebar.write("**Míriam López**")
st.sidebar.write("**Luis Martínez**")
st.sidebar.write("**Marc Rodríguez**")

st.subheader("Objectiu")
st.write("Desenvolupar un model d'intel·ligència artificial capaç de predir a tres terminis (2026, 2030 i 2035) el creixement de socis de l'entitat bancària Caixa D'Enginyers a Catalunya.")

st.subheader("Resultats")

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import unicodedata

# ---------- Config ----------
EXCEL_FALLBACK = "data\socios_caixa_enginyers_provincias_EXTENDIDO_2035_REPARTO_PONDERADO.xlsx"
GEOJSON_URL = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/master/public/data/spain-provinces.geojson"

# ---------- Utilidades ----------
def strip_accents(s: str) -> str:
    if not isinstance(s, str):
        return s
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))

ALIASES = {
    # Euskadi
    "araba": "Álava", "alava": "Álava", "araba/álava": "Álava",
    "bizkaia": "Vizcaya", "vizcaya": "Vizcaya",
    "gipuzkoa": "Guipúzcoa", "guipuzcoa": "Guipúzcoa",
    # Catalunya
    "girona": "Girona", "lleida": "Lleida", "tarragona": "Tarragona", "barcelona": "Barcelona",
    # C. Valenciana
    "castello": "Castellón", "castellon": "Castellón", "castellón/castelló": "Castellón",
    "valencia": "Valencia", "valencia/valència": "Valencia",
    "alicante/alacant": "Alicante",
    # Galicia
    "a coruna": "A Coruña", "la coruna": "A Coruña", "coruna": "A Coruña",
    "ourense": "Ourense", "orense": "Ourense",
    # Baleares
    "illes balears": "Islas Baleares", "islas baleares": "Islas Baleares",
    "balears": "Islas Baleares", "baleares": "Islas Baleares",
    # Canarias
    "santa cruz de tenerife": "Santa Cruz de Tenerife",
    # Otras normalizaciones por acento
    "cadiz": "Cádiz", "leon": "León", "avila": "Ávila", "jaen": "Jaén"
}

def normalize_province(name: str) -> str:
    if not isinstance(name, str) or not name.strip():
        return None
    key = strip_accents(name).lower().strip()
    key = key.replace("provincia de ", "").replace("prov. de ", "").replace("prov. ", "")
    if key in ALIASES:
        return ALIASES[key]
    fixes = {
        "avila": "Ávila", "alava": "Álava", "coruna": "A Coruña", "cadiz": "Cádiz",
        "jaen": "Jaén", "leon": "León", "malaga": "Málaga", "vizcaya": "Vizcaya",
        "guipuzcoa": "Guipúzcoa", "castellon": "Castellón", "lleida": "Lleida"
    }
    if key in fixes:
        return fixes[key]
    return " ".join(w.capitalize() for w in key.split())

def to_number(x):
    """Convierte strings con formato ES ('1.234,56') a float. También maneja floats/ints NaN."""
    if pd.isna(x):
        return None
    if isinstance(x, (int, float)):
        return x
    s = str(x).strip()
    # elimina espacios, cambia puntos de miles y coma decimal
    s = s.replace(" ", "").replace(".", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None

@st.cache_data(show_spinner=False)
def load_geojson(url: str):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    gj = r.json()
    geo_names = sorted({feat["properties"]["name"] for feat in gj["features"]})
    return gj, geo_names

geojson, geo_names = load_geojson(GEOJSON_URL)
geo_set = set(geo_names)

# ---------- Entrada: Excel ----------
st.sidebar.header("Datos de entrada")
uploaded = st.sidebar.file_uploader("Sube Excel (años en filas, provincias en columnas)", type=["xlsx", "xls"])
use_fallback = st.sidebar.checkbox("Usar fichero por defecto", value=True)

if uploaded is not None:
    xl = pd.ExcelFile(uploaded)
elif use_fallback:
    xl = pd.ExcelFile(EXCEL_FALLBACK)
else:
    st.info("Sube un Excel o marca 'Usar fichero por defecto'.")
    st.stop()

sheet = st.sidebar.selectbox("Hoja", xl.sheet_names, index=0)
raw = xl.parse(sheet)

if raw.empty:
    st.error("La hoja seleccionada no tiene datos.")
    st.stop()

# ---------- Detección de columna 'Año' y columnas de provincias ----------
# Buscamos una columna que represente el año (por nombre o por tipo entero)
year_col_guess = None
for c in raw.columns:
    cl = str(c).strip().lower()
    if "año" in cl or "ano" in cl or cl == "year":
        year_col_guess = c
        break
if year_col_guess is None:
    # Si no hay nombre claro, tomamos la primera columna
    year_col_guess = raw.columns[0]

# Columnas que NO son provincias (totales, etc.)
non_province_keywords = ["total", "miles", "prov", "nota", "coment", "código", "codigo", "id"]
non_prov_cols = {year_col_guess}
for c in raw.columns:
    cl = str(c).lower()
    if any(k in cl for k in non_province_keywords):
        non_prov_cols.add(c)

# Provincias candidatas = resto de columnas
province_cols = [c for c in raw.columns if c not in non_prov_cols]

# ---------- Limpieza y long format ----------
# Coerciona valores a número
for c in province_cols:
    raw[c] = raw[c].apply(to_number)

# Elige año
years = pd.Series(raw[year_col_guess].unique()).dropna().sort_values()
year_selected = st.sidebar.selectbox("Año", years, index=max(0, len(years)-1))
row = raw.loc[raw[year_col_guess] == year_selected, province_cols]

if row.empty:
    st.error("No hay datos para el año seleccionado.")
    st.stop()

# 'Derretimos' la fila: columnas -> filas (province, value)
wide_dict = row.iloc[0].to_dict()
df_long = pd.DataFrame(
    {"province_raw": list(wide_dict.keys()), "value": list(wide_dict.values())}
)

# Normaliza nombres y filtra no numéricos
df_long["province"] = df_long["province_raw"].apply(normalize_province)
df_long["value"] = pd.to_numeric(df_long["value"], errors="coerce").fillna(0)

# Filtrar provincias válidas y avisar de no-coincidencias
matches = df_long["province"].isin(geo_set)
no_match = df_long.loc[~matches, "province_raw"].tolist()

agg = df_long.loc[matches, ["province", "value"]].groupby("province", as_index=False).sum()

# Garantiza una fila por provincia del GeoJSON
geo_df = pd.DataFrame({"province": geo_names})
merged = geo_df.merge(agg, on="province", how="left")
merged["value"] = merged["value"].fillna(0)

# ---------- Controles de visualización ----------
st.sidebar.header("Visualización")
opacity = st.sidebar.slider("Opacidad", 0.1, 1.0, 0.75, 0.05)
zoom = st.sidebar.slider("Zoom", 3.0, 7.5, 4.0, 0.1)
center_lat = st.sidebar.number_input("Centro lat", value=40.4)
center_lon = st.sidebar.number_input("Centro lon", value=-3.7)
color_scale = st.sidebar.selectbox(
    "Escala de color",
    ["YlOrRd", "Viridis", "Blues", "Cividis", "Plasma", "Turbo", "Reds", "Greens"],
    index=0
)

# ---------- Mapa ----------
fig = px.choropleth_mapbox(
    merged,
    geojson=geojson,
    locations="province",
    featureidkey="properties.name",
    color="value",
    hover_name="province",
    color_continuous_scale=color_scale,
    mapbox_style="carto-positron",
    zoom=zoom,
    center={"lat": center_lat, "lon": center_lon},
    opacity=opacity,
    title="HEAT MAP DE SOCIS"
)
st.plotly_chart(fig, use_container_width=True)

st.image("assets\heatmap_socios_2035_REPARTO_PONDERADO.png", caption="Heatmap de socis per províncies a Catalunya")
