import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
from PIL import Image

icon = Image.open("assets/logo_small.png")   
st.set_page_config(
    page_title="AI'll find it — Analysis",
    page_icon=icon,        
    layout="wide"
)

st.title("Noves oficines i predicció de potencials localitzacions futures.")

st.write("> Objectiu: L'objectiu d'aquest projecte es centra en buscar ubicacions idònies per obrir noves oficines de la Caixa d'Enginyers, valorant tant la possiblitat d'oficines fixes com oficinse mòbils que arriben a una determinada zona. A més, es desenvoluparà també un model predictiu amb l'ajuda d'IA que permeti identificar potencials localitzacions futures.")

st.subheader("Dades ")
st.write("> Fonts Oficials: INE, BdE i dades pròpies de Caixa d'Enginyers.")

# st.sidebar.header("*AI'll find it*")
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

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt


@st.cache_data
def load_data(path: str):
    dfb = pd.read_excel(path, sheet_name=0, header=0, engine="openpyxl")

    # 1) Si la cabecera es "Columna1..." usar primera fila como header real
    if any(str(c).lower().startswith("columna") for c in dfb.columns):
        dfb.columns = dfb.iloc[0].tolist()
        dfb = dfb.iloc[1:].reset_index(drop=True)

    # 2) Normalizar nombres de columnas
    dfb.columns = [str(c).strip() for c in dfb.columns]
    return dfb

dfb = load_data("data/Bancs per provincia.xlsx")

name_col = "Provincia"
cols_val = [
    "Banco de España",
    "Oficinas en España",
    "Entidades de depósito",
    "Otras entidades de crédito y EFC",
]

for c in cols_val:
    if c in dfb.columns:
        dfb[c] = pd.to_numeric(dfb[c], errors="coerce").fillna(0)

posibles_sel = [
    "Seleccion","Selección","SELECCION","SELECCIÓN","Plot","PLOT","Marcar",
    "Include","Selected"
]
sel_col = next((c for c in dfb.columns if str(c).strip() in posibles_sel), None)

# ---------- Sidebar ----------
if sel_col:
    use_sel = st.checkbox(f"Usar columna de selección: **{sel_col}**", value=True)
else:
    use_sel = False

top_n = st.slider("Top N per Oficines", min_value=5, max_value=30, value=12, step=1)

st.divider()
present_cols = [c for c in ["Banco de España","Entidades de depósito","Otras entidades de crédito y EFC"] if c in dfb.columns]
stacked_cols = present_cols

# DataFrame a graficar
def _to_bool(v):
    s = str(v).strip().lower()
    return (v is True) or (s in ("1","si","sí","true","x","y","yes"))

if use_sel and sel_col:
    dfb_plot = dfb[dfb[sel_col].apply(_to_bool)].copy()
else:
    if "Oficinas en España" in dfb.columns:
        dfb_plot = dfb.sort_values("Oficinas en España", ascending=False).head(top_n).copy()
    else:
        dfb_plot = dfb.copy()

if stacked_cols:
    st.subheader("Entitats per Provincia")
    # Convertir a formato largo (melt)
    long_df = dfb_plot[[name_col] + stacked_cols].melt(
        id_vars=name_col, var_name="Tipus", value_name="Valor"
    )
    chart2 = (
        alt.Chart(long_df)
        .mark_bar()
        .encode(
            x=alt.X(f"{name_col}:N", sort="-y", title="Provincia"),
            y=alt.Y("Valor:Q", title="Número de entidades"),
            color=alt.Color("Tipus:N", title="Tipus d'Entitat"),
            tooltip=[name_col, "Tipus", "Valor"]
        )
    ).properties(height=500)
    st.altair_chart(chart2, use_container_width=True)

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from pathlib import Path

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=0, header=0, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]

    prov_col = "Provincias" if "Provincias" in df.columns else "Provincia"

    df = df[
        (df["CCAA"].astype(str).str.strip().str.lower() != "total")
        & (df[prov_col].astype(str).str.strip().str.lower() == "total")
    ].copy()

    columnas_total = [c for c in df.columns if ("Total" in c and c.split()[0].isdigit())]
    columnas_total = sorted(columnas_total, key=lambda c: int(c.split()[0]))

    df_grouped = df.groupby("CCAA", as_index=False)[columnas_total].sum()

    long_df = df_grouped.melt(
        id_vars="CCAA", value_vars=columnas_total, var_name="Col", value_name="Empresas"
    )
    long_df["Any"] = long_df["Col"].str.split().str[0].astype(int)
    long_df = long_df.drop(columns=["Col"])
    long_df["Empresas"] = pd.to_numeric(long_df["Empresas"], errors="coerce").fillna(0)

    return long_df

DATA_PATH = "data/Empresa per mida y provincia 2008-2022.xlsx"
if not Path(DATA_PATH).exists():
    st.error(f"No se encuentra el archivo: {DATA_PATH}")
    st.stop()

df_long = load_data(DATA_PATH)

chart = (
    alt.Chart(df_long)
    .mark_line(point=True)
    .encode(
        x=alt.X("Any:O", title="Any"),
        y=alt.Y("Empresas:Q", title="Número de empresas", axis=alt.Axis(format=",.0f")),
        color=alt.Color("CCAA:N", title="CCAA", legend=alt.Legend(orient="right")),
        tooltip=[
            alt.Tooltip("CCAA:N"),
            alt.Tooltip("Any:O"),
            alt.Tooltip("Empresas:Q", title="Empresas", format=",.0f"),
        ],
    )
    .properties(height=520)
    .interactive()
)

st.altair_chart(chart, use_container_width=True)

st.subheader("Conclusió")

import streamlit as st

st.set_page_config(layout="wide")

col_img, col_list = st.columns([1, 2])   

with col_img:
    st.image("assets/cat_map.png", caption="Mapa de Catalunya", use_container_width=True)

with col_list:
    st.markdown("""
- Comunitat amb major nombre d'empreses.
- Top 5 valor PIB tant per càpita com en variació interanual.
- Top 2 en nombre d'oficines bancàries.
- Volum majoritari d'oficines de Caixa D'Enginyers a Catalunya. 
    """)