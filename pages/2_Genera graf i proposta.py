import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
from PIL import Image
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import contextily as cx
import re
import unicodedata

# pip install streamlit pandas networkx pillow plotly matplotlib contextily pyproj openpyxl
try:
    from bank_optimizer import BankCoverageOptimizer
except Exception:
    BankCoverageOptimizer = None

# ====== Parámetros del caso (ajusta si quieres) ======
PCT_0_14   = 0.146
PCT_15_64  = 0.642
PCT_65_PLUS= 0.212
assert abs((PCT_0_14 + PCT_15_64 + PCT_65_PLUS) - 1.0) < 1e-6

# ====== Página ======
from PIL import Image
import streamlit as st, base64, pathlib
try:
    icon = Image.open("assets/logo_small.png")
except Exception:
    icon = None

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

st.set_page_config(page_title="AI'll find it — Generació De Graf i Proposta", page_icon=icon, layout="wide")
st.title("Bank Coverage Optimizer")
st.markdown("Adaptado a **MunicipiosEspana.xlsx** (Población, Latitud, Longitud, Habitantes). Lee hojas y encabezados automáticamente.")

# ====== Utils robustas ======
def norm_text(s: str) -> str:
    """lower, sin tildes, sin signos, sin espacios dobles."""
    if s is None:
        return ""
    s = str(s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    return s

def to_numeric_locale(series: pd.Series) -> pd.Series:
    """Convierte strings numéricas con coma decimal y/o separador de miles a float."""
    if series.dtype.kind in "biufc":
        return pd.to_numeric(series, errors="coerce")
    s = series.astype(str).str.replace(r"\s+", "", regex=True)
    # si hay comas y puntos, intentar heurística: punto = miles, coma = decimal
    s = s.str.replace(".", "", regex=False)  # quita separadores de miles '.'
    s = s.str.replace(",", ".", regex=False)  # cambia coma decimal por punto
    return pd.to_numeric(s, errors="coerce")

def pick_epsg_from_lon(lon_median: float) -> int:
    if lon_median < -6:
        return 25829
    elif lon_median <= 0:
        return 25830
    else:
        return 25831

def latlon_to_utm(df, lon_col, lat_col, epsg):
    from pyproj import Transformer, CRS
    transformer = Transformer.from_crs(CRS.from_epsg(4326), CRS.from_epsg(epsg), always_xy=True)
    xs, ys = transformer.transform(
        to_numeric_locale(df[lon_col]),
        to_numeric_locale(df[lat_col]),
    )
    return xs, ys

def load_excel_smart(file) -> pd.DataFrame:
    """
    Lee cualquier hoja y detecta la fila de encabezados buscando las columnas objetivo.
    Devuelve un DataFrame con el header correcto.
    """
    # Palabras clave normalizadas
    want = {"poblacion", "latitud", "longitud", "habitantes"}
    # 1) leer todas las hojas sin header para escanear
    book = pd.read_excel(file, sheet_name=None, header=None, engine="openpyxl")
    best = None
    best_info = None  # (sheet_name, header_row, hits)
    for sh_name, df in book.items():
        if df.empty:
            continue
        # buscar en las primeras ~30 filas una fila que contenga varias columnas objetivo
        max_rows_to_scan = min(30, len(df))
        for r in range(max_rows_to_scan):
            row = df.iloc[r].astype(str).tolist()
            norms = [norm_text(x) for x in row]
            hits = set(norms) & want
            # también permitir que 'población' aparezca como 'poblacion' exacto dentro de la celda
            # Si no hay match exacto, intentamos contains
            if len(hits) < 2:
                contains_hits = set()
                for cell in norms:
                    for w in want:
                        if w in cell:
                            contains_hits.add(w)
                hits = contains_hits
            if len(hits) >= 3:  # suficiente para considerar encabezado válido
                try:
                    df2 = pd.read_excel(file, sheet_name=sh_name, header=r, engine="openpyxl")
                except Exception:
                    continue
                # limpiar columnas Unnamed
                df2 = df2[[c for c in df2.columns if not str(c).startswith("Unnamed")]]
                if not df2.empty:
                    best = df2
                    best_info = (sh_name, r, len(hits))
                    break
        if best is not None:
            break

    # Si no se encontró, intentar simplemente la primera hoja con header=0
    if best is None:
        df0 = pd.read_excel(file, sheet_name=0, engine="openpyxl")
        df0 = df0[[c for c in df0.columns if not str(c).startswith("Unnamed")]]
        best = df0

    return best

def visualize_graph_on_map(G, title="Optimized Graph on Map", crs_epsg=25830):
    fig, ax = plt.subplots(figsize=(12, 10))
    pos = {n: (d["utm_x"], d["utm_y"]) for n, d in G.nodes(data=True)}
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='gray', alpha=0.5)

    node_types = {"physical_office": "blue", "mobile_van_stop": "purple", "uncovered": "red"}
    for ntype, color in node_types.items():
        nods = [n for n, d in G.nodes(data=True) if d.get("node_type", "uncovered") == ntype]
        if nods:
            nx.draw_networkx_nodes(G, pos, nodelist=nods, node_color=color, node_size=100, label=ntype)

    labels = {n: d.get("name", "") for n, d in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=7)

    if pos:
        xs, ys = zip(*pos.values())
        bx, by = (max(xs)-min(xs))*0.05, (max(ys)-min(ys))*0.05
        ax.set_xlim(min(xs)-bx, max(xs)+bx)
        ax.set_ylim(min(ys)-by, max(ys)+by)

    try:
        cx.add_basemap(ax, crs=f"epsg:{crs_epsg}", source=cx.providers.CartoDB.Positron)
    except Exception as e:
        st.warning(f"No se pudo añadir basemap (contextily): {e}")

    ax.set_title(title, fontsize=16)
    ax.set_xlabel("UTM X"); ax.set_ylabel("UTM Y")
    ax.set_aspect("equal")
    plt.legend()
    st.pyplot(fig)

# ====== Upload ======
uploaded_file = st.file_uploader("📂 Sube MunicipiosEspana.xlsx (o CSV equivalente)", type=["xlsx", "csv"])
if not uploaded_file:
    st.stop()

# ====== Lectura robusta ======
if uploaded_file.name.lower().endswith(".csv"):
    df_raw = pd.read_csv(uploaded_file)
else:
    df_raw = load_excel_smart(uploaded_file)

st.subheader("Preview (original)")
st.dataframe(df_raw.head())

# ====== Localizar columnas objetivo (flexible a tildes y espacios) ======
colmap = {norm_text(c): c for c in df_raw.columns}
def find_col(*alts):
    for a in alts:
        key = norm_text(a)
        # match exact normalizado
        if key in colmap:
            return colmap[key]
        # intentar contains
        for k, original in colmap.items():
            if key in k:
                return original
    return None

col_poblacion = find_col("población", "poblacion", "municipio", "localidad", "nombre")
col_latitud   = find_col("latitud", "lat")
col_longitud  = find_col("longitud", "lon", "long")
col_hab       = find_col("habitantes", "poblacion total", "total", "pob total")

missing = [n for n, c in [("Población", col_poblacion), ("Latitud", col_latitud),
                          ("Longitud", col_longitud), ("Habitantes", col_hab)] if c is None]
if missing:
    st.error(f"Faltan columnas en el fichero: {', '.join(missing)}")
    st.write("Columnas detectadas:", list(df_raw.columns))
    st.stop()

# ====== Normalización al esquema ======
df = df_raw.copy()
df["name"] = df[col_poblacion].astype(str)

# Coordenadas a UTM
lon_med = to_numeric_locale(df[col_longitud]).median()
utm_epsg = pick_epsg_from_lon(lon_med if pd.notnull(lon_med) else -3.0)

try:
    xs, ys = latlon_to_utm(df, col_longitud, col_latitud, utm_epsg)
    df["utm_x"], df["utm_y"] = xs, ys
    st.info(f"Coordenadas lat/lon convertidas a UTM (EPSG:{utm_epsg}).")
except Exception as e:
    st.error(f"No se pudo convertir lat/lon a UTM: {e}")
    st.stop()

# Desglose por edades a partir de Habitantes
tot = to_numeric_locale(df[col_hab]).fillna(0)
df["pop_0_14"]   = (tot * PCT_0_14).round().astype(int)
df["pop_15_64"]  = (tot * PCT_15_64).round().astype(int)
df["pop_65_plus"]= (tot - (df["pop_0_14"] + df["pop_15_64"])).clip(lower=0).astype(int)

# Mantener sólo lo requerido
df = df[["name", "utm_x", "utm_y", "pop_0_14", "pop_15_64", "pop_65_plus"]]
for c in ["utm_x","utm_y","pop_0_14","pop_15_64","pop_65_plus"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")
df = df.dropna()

st.success(f"✅ Datos normalizados. Filas válidas: {len(df)}")
st.dataframe(df.head())

# ====== Parámetros ======
st.header("Parameters")
num_offices = st.number_input("Number of physical offices", min_value=1, value=3)
num_vans = st.number_input("Number of mobile van stops", min_value=1, value=5)
office_radius = st.number_input("Physical office radius (m)", min_value=1000, value=15000)
van_radius = st.number_input("Mobile van radius (m)", min_value=1000, value=10000)
connection_distance = st.number_input("Distance threshold to connect towns (m)", min_value=1000, value=20000)

# ====== Optimización ======
if st.button("🚀 Run Optimization"):
    if df.empty:
        st.error("No hay filas válidas tras la normalización.")
        st.stop()

    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_node(
            row["name"],
            name=row["name"],
            utm_x=row["utm_x"],
            utm_y=row["utm_y"],
            pop_0_14=row["pop_0_14"],
            pop_15_64=row["pop_15_64"],
            pop_65_plus=row["pop_65_plus"]
        )

    if G.number_of_nodes() == 0:
        st.error("El grafo no tiene nodos.")
        st.stop()

    nodes = list(G.nodes)
    for i, n1 in enumerate(nodes):
        x1, y1 = G.nodes[n1]["utm_x"], G.nodes[n1]["utm_y"]
        for j in range(i+1, len(nodes)):
            n2 = nodes[j]
            x2, y2 = G.nodes[n2]["utm_x"], G.nodes[n2]["utm_y"]
            dist = ((x1-x2)**2 + (y1-y2)**2) ** 0.5
            if dist <= connection_distance:
                G.add_edge(n1, n2, weight=dist)

    st.success(f"✅ Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

    if BankCoverageOptimizer is None:
        st.error("No se pudo importar BankCoverageOptimizer. Coloca 'bank_optimizer.py' junto al script.")
        st.stop()

    optimizer = BankCoverageOptimizer(G, physical_office_radius=office_radius, mobile_van_radius=van_radius)
    try:
        results = optimizer.optimize_coverage(num_offices, num_vans)
    except ZeroDivisionError:
        st.error("El optimizador ha recibido 0 nodos (division by zero). Revisa el dataset.")
        st.stop()

    summary = optimizer.get_coverage_summary()

    st.subheader("📊 Optimization Results")
    st.write(results)

    st.subheader("🏘️ Coverage Summary")
    st.dataframe(summary)

    csv = summary.to_csv(index=False).encode("utf-8")
    st.download_button("💾 Download coverage summary CSV", data=csv, file_name="coverage_summary.csv", mime="text/csv")

    st.subheader("🗺️ Coverage Map")
    visualize_graph_on_map(G, title="Optimized Graph on Map", crs_epsg=utm_epsg)

    st.subheader("🗺️ Interactive Graph Visualization")
    pos = {n: (G.nodes[n]["utm_x"], G.nodes[n]["utm_y"]) for n in G.nodes}

    office_nodes = set(results.get("physical_offices", []))
    van_nodes = set(results.get("mobile_stops", []))

    edge_x, edge_y = [], []
    for a, b in G.edges():
        x0, y0 = pos[a]; x1, y1 = pos[b]
        edge_x.extend([x0, x1, None]); edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color="#888"),
                            hoverinfo="none", mode="lines")

    node_x, node_y, node_color, node_text = [], [], [], []
    for n in G.nodes():
        x, y = pos[n]
        node_x.append(x); node_y.append(y)
        if n in office_nodes:
            node_color.append("red");    node_text.append(f"{n} 🏢 (Office)")
        elif n in van_nodes:
            node_color.append("orange"); node_text.append(f"{n} 🚐 (Mobile Van)")
        else:
            node_color.append("lightblue"); node_text.append(n)

    node_trace = go.Scatter(x=node_x, y=node_y, mode="markers", hoverinfo="text",
                            marker=dict(showscale=False, color=node_color, size=10, line_width=1),
                            text=node_text)

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(text="Optimized Graph Visualization", font=dict(size=18)),
            showlegend=False, hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False)
        )
    )
    st.plotly_chart(fig, use_container_width=True)
