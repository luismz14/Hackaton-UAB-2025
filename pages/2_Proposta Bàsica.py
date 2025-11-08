import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
from PIL import Image

icon = Image.open("assets/logo_small.png")   
st.set_page_config(
    page_title="AI'll find it — Proposta Bàsica",
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

# app.py
# Streamlit: Grafo de conectividad de municipios (Cataluña) a partir de dos CSV

import io
import numpy as np
import pandas as pd
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

# ---------- Sidebar: carga y controles ----------
st.set_page_config(page_title="Grafo de ciudades", layout="wide")

st.sidebar.header("1) Datos de entrada")
pop_file = st.sidebar.file_uploader(
    "Població_de_Catalunya_per_municipi,_rang_d'edat_i_sexe_*.csv",
    type=["csv"], key="pop_csv"
)
cities_file = st.sidebar.file_uploader(
    "Municipis_Catalunya_Geo_*.csv",
    type=["csv"], key="geo_csv"
)

st.sidebar.header("2) Filtros y opciones")
exclude_year = st.sidebar.number_input(
    "Excluir año (por ej. 2019)", min_value=1800, max_value=2100, value=2019, step=1
)
distance_km = st.sidebar.slider(
    "Umbral de distancia para conectar ciudades (km)", min_value=1, max_value=100, value=10, step=1
)
layout_mode = st.sidebar.selectbox(
    "Layout", ["spring_layout (fuerzas)", "coordenadas UTM"]
)
spring_k = st.sidebar.slider("Parámetro k (spring)", 0.01, 1.0, 0.10, 0.01)
spring_iter = st.sidebar.slider("Iteraciones (spring)", 10, 300, 80, 10)

limit_nodes = st.sidebar.number_input(
    "Máx. nodos a dibujar (muestra aleatoria, 0 = sin límite)", min_value=0, value=0, step=50
)

st.title("Grafo de conectividad entre municipios (Cataluña)")

# ---------- Funciones util ----------
def _to_num_series(s, thousands=".,", decimal=","):
    """Convierte rápido a número 'limpiando' separadores habituales."""
    if s.dtype.kind in "biufc":
        return s
    s = s.astype(str)
    # quita separadores de miles comunes
    for ch in thousands:
        s = s.str.replace(ch, "", regex=False)
    # cambia decimal si viene con coma
    if decimal and decimal != ".":
        s = s.str.replace(decimal, ".", regex=False)
    return pd.to_numeric(s, errors="coerce")

# ---------- Carga y preparación ----------
if pop_file is not None and cities_file is not None:
    try:
        df_population = pd.read_csv(pop_file)
        df_cities = pd.read_csv(cities_file)
    except Exception as e:
        st.error(f"No se pudieron leer los CSV: {e}")
        st.stop()

    with st.expander("Columnas detectadas"):
        st.write("Population:", list(df_population.columns))
        st.write("Cities:", list(df_cities.columns))

    # Chequeo de claves
    if "Codi" not in df_population.columns or "Codi" not in df_cities.columns:
        st.error("Ambos CSV deben contener la columna clave 'Codi'.")
        st.stop()

    # Filtro de año (si existe)
    if "Any" in df_population.columns:
        df_population = df_population[df_population["Any"] != exclude_year]

    # Merge
    df_merged = pd.merge(df_population, df_cities, on="Codi", how="inner")

    # Limpieza de columnas esperadas
    # Nombres según tu ejemplo; si cambian, ajusta aquí o añade detección.
    col_pop_0_14 = "Total. De 0 a 14 anys"
    col_pop_15_64 = "Total. De 15 a 64 anys"
    col_pop_65p = "Total. De 65 anys i més"
    col_x = "UTM X"
    col_y = "UTM Y"
    col_name_pop = "Nom_x" if "Nom_x" in df_merged.columns else "Nom"

    # Convertir a numérico
    for c in [col_pop_0_14, col_pop_15_64, col_pop_65p]:
        if c in df_merged.columns:
            # normalmente estos vienen con puntos o comas como miles/decimal
            df_merged[c] = _to_num_series(df_merged[c], thousands=".", decimal=",")

    for c in [col_x, col_y]:
        if c in df_merged.columns:
            # coordenadas UTM: suelen venir con coma como miles -> limpiar
            df_merged[c] = _to_num_series(df_merged[c], thousands=",", decimal=".")

    # Filas válidas (coordenadas presentes)
    if not {col_x, col_y}.issubset(df_merged.columns):
        st.error("No se han encontrado columnas de coordenadas 'UTM X' y 'UTM Y' en el merge.")
        st.stop()

    df_merged = df_merged.dropna(subset=[col_x, col_y])
    st.success(f"Merge OK. Filas con coordenadas: {len(df_merged):,}")

    # Posible muestreo para velocidad de dibujo
    if limit_nodes and limit_nodes > 0 and len(df_merged) > limit_nodes:
        df_plot = df_merged.sample(limit_nodes, random_state=42).copy()
        st.info(f"Muestreando {limit_nodes} de {len(df_merged)} nodos para visualización.")
    else:
        df_plot = df_merged.copy()

    # ---------- Construcción del grafo ----------
    G = nx.Graph()
    # añade nodos
    for _, row in df_plot.iterrows():
        G.add_node(
            row["Codi"],
            name=row.get(col_name_pop, str(row["Codi"])),
            pop_0_14=row.get(col_pop_0_14, np.nan),
            pop_15_64=row.get(col_pop_15_64, np.nan),
            pop_65_plus=row.get(col_pop_65p, np.nan),
            utm_x=row[col_x],
            utm_y=row[col_y],
        )

    # añade aristas por umbral de distancia
    coords = df_plot[[col_x, col_y]].to_numpy()
    codes = df_plot["Codi"].to_numpy()
    thr_m = distance_km * 1000.0

    # Vectorizado por bloques para evitar O(n^2) puro cuando n grande
    # (simple y sin dependencias extra)
    def edges_within_threshold(codes, coords, thr):
        n = len(codes)
        edges = []
        block = 1024  # tamaño de bloque para memoria
        for i0 in range(0, n, block):
            i1 = min(i0 + block, n)
            a = coords[i0:i1]
            for j0 in range(i0 + 1, n, block):
                j1 = min(j0 + block, n)
                b = coords[j0:j1]
                # dist^2 = (x1-x2)^2 + (y1-y2)^2
                d2 = (
                    (a[:, None, 0] - b[None, :, 0]) ** 2
                    + (a[:, None, 1] - b[None, :, 1]) ** 2
                )
                mask = d2 < (thr * thr)
                if mask.any():
                    idx_a, idx_b = np.where(mask)
                    for ia, ib in zip(idx_a, idx_b):
                        edges.append(
                            (
                                int(codes[i0 + ia]),
                                int(codes[j0 + ib]),
                                float(np.sqrt(d2[ia, ib])),
                            )
                        )
        return edges

    edges = edges_within_threshold(codes, coords, thr_m)
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)

    st.write(f"**Nodos:** {G.number_of_nodes():,}  —  **Aristas:** {G.number_of_edges():,}")

    # ---------- Dibujo ----------
    st.header("Visualización")
    if layout_mode.startswith("spring"):
        pos = nx.spring_layout(G, k=spring_k, iterations=int(spring_iter), seed=42)
    else:
        # usa coordenadas UTM directamente
        pos = {n: (d["utm_x"], d["utm_y"]) for n, d in G.nodes(data=True)}

    fig, ax = plt.subplots(figsize=(10, 8))
    nx.draw_networkx(
        G,
        pos=pos,
        with_labels=False,
        node_size=10,
        width=0.4,
        alpha=0.8,
        edge_color="gray",
        ax=ax,
    )
    ax.set_title("City Connectivity Graph")
    ax.set_xticks([]); ax.set_yticks([])
    st.pyplot(fig, clear_figure=True)

    # ---------- Tabla de nodos ----------
    with st.expander("Ver tabla de nodos"):
        meta = pd.DataFrame(
            {
                "Codi": [n for n in G.nodes()],
                "Nombre": [d.get("name") for _, d in G.nodes(data=True)],
                "UTM X": [d.get("utm_x") for _, d in G.nodes(data=True)],
                "UTM Y": [d.get("utm_y") for _, d in G.nodes(data=True)],
                "Grado": [G.degree(n) for n in G.nodes()],
            }
        ).sort_values("Grado", ascending=False)
        st.dataframe(meta, use_container_width=True)

else:
    st.info("⬅️ Sube los dos CSV en la barra lateral para empezar.")
