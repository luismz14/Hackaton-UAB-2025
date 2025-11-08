import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns

st.title("Noves oficines i predicció de potencials localitzacions futures.")

st.write("> Objectiu: L'objectiu d'aquest projecte es centra en buscar ubicacions idònies per obrir noves oficines de la Caixa d'Enginyers, valorant tant la possiblitat d'oficines fixes com oficinse mòbils que arriben a una determinada zona. A més, es desenvoluparà també un model predictiu amb l'ajuda d'IA que permeti identificar potencials localitzacions futures.")

st.subheader("Dades ")
st.write("> Fonts Oficials: INE, BdE i dades pròpies de Caixa d'Enginyers.")


st.subheader("Conclusió")

st.sidebar.header("*AI'll fint it*")
st.sidebar.write("**Arnau Muñoz**")
st.sidebar.write("**Míriam López**")
st.sidebar.write("**Luis Martínez**")
st.sidebar.write("**Marc Rodríguez**")


import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Bancos por provincia", layout="wide")

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