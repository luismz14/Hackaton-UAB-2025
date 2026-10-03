import streamlit as st
import pandas as pd
from PIL import Image
import os
from utils.AIna_utils import preguntar_chatbot, SYSTEM_PROMPT

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """
    Load Excel/CSV input, promoting a placeholder header row when present.
    """
    try:
        # Llegeix el fitxer segons l'extensió
        if path.endswith(".csv"):
            # Afegeix 'encoding' si tens problemes amb caràcters especials
            df = pd.read_csv(path)
        elif path.endswith(".xlsx"):
            df = pd.read_excel(path, sheet_name=0, header=0, engine="openpyxl")
        else:
            st.warning(f"Format de fitxer no suportat: {path}")
            return pd.DataFrame()

        # Neteja 1: Si la capçalera és "Columna1..."
        if any(str(c).lower().startswith("columna") for c in df.columns):
            df.columns = df.iloc[0].tolist()
            df = df.iloc[1:].reset_index(drop=True)

        # Neteja 2: Normalitzar noms de columnes
        df.columns = [str(c).strip() for c in df.columns]
        return df

    except Exception as e:
        st.error(f"Error en carregar {path}: {e}")
        return pd.DataFrame()

PATHS_DATASETS = [
    "data/BancsProvincia.xlsx",
    "data/CoordenadesMunicipis.csv",
    "data/EmpresesProvincia.xlsx",
    "data/Habitants.xlsx",
    "data/OficinesMunicipi.xlsx",
    "data/PIB.xlsx",
    "data/PIBperCapita.xlsx",
    "data/PIBpercentatge.xlsx",
    "data/PoblacioMunicipi.csv"
]

# Inicialitzem el magatzem de mostres per al chatbot (RAG)
if "context_samples" not in st.session_state:
    st.session_state.context_samples = {}

# Inicialitzem les variables per als nostres gràfics
dfb = None
df_long = None

# Bucle principal de càrrega, processament i mostreig
for path in PATHS_DATASETS:
    # Comprovem que el fitxer existeix abans de carregar-lo
    if not os.path.exists(path):
        st.warning(f"No s'ha trobat el fitxer: {path}")
        continue

    filename = os.path.basename(path)

    # 1. Carregar les dades (utilitzant la nova funció genèrica)
    df_full = load_data(path)
    if df_full.empty:
        continue

    # 2. Processament específic per als GRÀFICS
    # (Agafem la lògica de l'Analisi.py original i la posem aquí)

    if filename == "BancsProvincia.xlsx":
        # Aquest era 'dfb'. No necessita més processament.
        dfb = df_full

    elif filename == "EmpresesProvincia.xlsx":
        # Aquest era 'df_long'. Requereix el processament complex.
        try:
            df_wide = df_full.copy()

            # 1. Identifiquem la columna d'identificació (la primera, 'Provincias/Any')
            id_col = df_wide.columns[0]

            # 2. Identifiquem les columnes de valors (totes les altres, que són els anys)
            value_cols = [col for col in df_wide.columns if col != id_col]

            # 3. Transformem de 'wide' a 'long' amb 'melt'
            df_long = df_wide.melt(
                id_vars=id_col,        # La columna que es manté (Províncies)
                value_vars=value_cols, # Les columnes que volem 'desfer' (Anys)
                var_name="Any",        # Nom de la nova columna per als anys
                value_name="Empresas"  # Nom de la nova columna per als valors
            )

            # 4. Reanomenem la columna de províncies per a més claredat
            df_long.rename(columns={id_col: "Provincia"}, inplace=True)

            # 5. Assegurem que els tipus de dades són correctes
            df_long["Any"] = pd.to_numeric(df_long["Any"], errors="coerce")
            df_long["Empresas"] = pd.to_numeric(df_long["Empresas"], errors="coerce").fillna(0)
        except Exception as e:
            st.error(f"Error processant {filename} per al gràfic: {e}")
            df_long = pd.DataFrame()

    if filename not in st.session_state.context_samples:
        n_samples = min(5, len(df_full))
        if n_samples > 0:
            df_sample = df_full.sample(n=n_samples)
            st.session_state.context_samples[filename] = df_sample

icon = "🏦"
st.set_page_config(
    page_title="AI'll find it — Analasi",
    page_icon=icon,
    layout="wide"
)

st.title("Noves oficines i predicció de potencials localitzacions futures.")

st.write("> Objectiu: L'objectiu d'aquest projecte es centra en buscar ubicacions idònies per obrir noves oficines de la Caixa d'Enginyers, valorant tant la possiblitat d'oficines fixes com oficinse mòbils que arriben a una determinada zona. A més, es desenvoluparà també un model predictiu amb l'ajuda d'IA que permeti identificar potencials localitzacions futures.")

st.subheader("Dades ")
st.write("> Fonts Oficials: INE, BdE i dades pròpies de Caixa d'Enginyers.")

# st.sidebar.header("*AI'll find it*")
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

dfb = load_data("data/BancsProvincia.xlsx")

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
import altair as alt
from pathlib import Path

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """
    Reshape a province-by-year Excel table into long-form company counts.
    """
    try:
        # 1. Carregar les dades
        df_wide = pd.read_excel(path, sheet_name=0, header=0, engine="openpyxl")

        # 2. Netejar noms de columnes (els anys poden tenir espais)
        df_wide.columns = [str(c).strip() for c in df_wide.columns]

        # --- AQUESTA ÉS LA NOVA LÒGICA ---

        # 3. Identifiquem la columna d'identificació (la primera)
        #    (ex: 'Provincias/Any')
        id_col = df_wide.columns[0]

        # 4. Identifiquem les columnes de valors (totes les altres, que són els anys)
        value_cols = [col for col in df_wide.columns if col != id_col]

        # 5. Transformem de 'wide' a 'long' amb 'melt'
        #
        df_long = df_wide.melt(
            id_vars=id_col,        # La columna que es manté (Províncies)
            value_vars=value_cols, # Les columnes que volem 'desfer' (Anys)
            var_name="Any",        # Nom de la nova columna per als anys
            value_name="Empresas"  # Nom de la nova columna per als valors
        )

        # 6. Reanomenem la columna de províncies per a més claredat
        df_long.rename(columns={id_col: "Provincia"}, inplace=True)

        # 7. Assegurem que els tipus de dades són correctes
        df_long["Any"] = pd.to_numeric(df_long["Any"], errors="coerce")
        df_long["Empresas"] = pd.to_numeric(df_long["Empresas"], errors="coerce").fillna(0)

        # 8. (Opcional) Netejar el prefix numèric de la província
        #    Comprova si té el format "XX Nom" i el treu
        if df_long["Provincia"].str.match(r"^\d{2}\s").any():
            df_long["Provincia"] = df_long["Provincia"].str.split(n=1).str[1].str.strip()

        return df_long

    except Exception as e:
        # Si fas servir Streamlit, pots posar un error
        st.error(f"Error en carregar i processar el fitxer {path}: {e}")
        # Retornem un DataFrame buit en cas d'error
        return pd.DataFrame(columns=["Provincia", "Any", "Empresas"])

DATA_PATH = "data/EmpresesProvincia.xlsx"
if not Path(DATA_PATH).exists():
    st.error(f"No se encuentra el archivo: {DATA_PATH}")
    st.stop()

df_long = load_data(DATA_PATH)

st.subheader("Conclusió")

import streamlit as st

st.set_page_config(layout="wide")

col_img, col_list = st.columns([1, 2])

with col_img:
    st.caption("Historical map illustration excluded: reuse permission unresolved. See DATA_SOURCES.md.")

with col_list:
    st.markdown(
        """
        <div style="
            font-size:1.5rem;      /* tamaño del texto */
            line-height:1.6;        /* alto de línea */
        ">
            <ul style="
                margin:0; 
                padding-left:1.4em;   /* sangría de las viñetas */
                ">
                <li><b>Comunitat</b> amb major nombre d'empreses.</li>
                <li><b>Top 5</b> valor PIB tant per càpita com en variació interanual.</li>
                <li><b>Top 2</b> en nombre d'oficines bancàries.</li>
                <li>Volum majoritari d'oficines de <i>Caixa d'Enginyers</i> a Catalunya.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

# =================================================================
# --- SECCIÓ DEL CHATBOT ---
# =================================================================

st.divider()
st.subheader("🤖 Analista Expert (Chatbot)")
st.write("Fes una pregunta sobre les dades, oportunitats de mercat o estratègia financera per a Caixa d'Enginyers.")

# --- CANVI 1: Inicialització ---
# Inicialitzem l'historial del xat NOMÉS amb el system prompt.
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        # Fem servir la variable SYSTEM_PROMPT importada
        {"role": "system", "content": SYSTEM_PROMPT}
        # HEM ELIMINAT el missatge inicial d'assistant d'aquí
    ]

# --- CANVI 2: Lògica de visualització ---
# Display the welcome message without sending it as conversation history.
with st.chat_message("assistant"):
    st.markdown("Hola! Sóc el teu analista assistent. En què et puc ajudar avui?")

# Mostrem la resta de missatges REALS (saltant el system prompt, que no es mostra)
for message in st.session_state.chat_messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
# ---------------------------------------------

# Input de l'usuari
if prompt := st.chat_input("Escriu la teva consulta..."):

    # 1. Afegir i mostrar el missatge de l'usuari (Això no canvia)
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ------------------------------------------------------------------
    # 2. PREPAREM LA TRUCADA (Aquí injectem el RAG amb els 9 datasets)
    # ------------------------------------------------------------------

    context_augmentat = "Hola expert. Tinc diversos datasets. Aquí tens una mostra aleatòria de 5 files de cadascun d'ells. Fes servir aquest context per respondre la meva pregunta:\n\n"

    # Iterem sobre el diccionari que hem omplert a la part de dalt
    if "context_samples" in st.session_state and st.session_state.context_samples:
        for filename, df_sample in st.session_state.context_samples.items():
            context_augmentat += f"--- Fitxer: '{filename}' ---\n"
            # Li diem quines columnes té
            context_augmentat += f"Columnes: {', '.join(df_sample.columns)}\n"
            # Li passem les 5 files aleatòries com a text
            context_augmentat += df_sample.to_string(index=False)
            context_augmentat += "\n\n"
    else:
        context_augmentat = "" # No hi ha dades de context, no afegim res

    # Creem el prompt final que enviarem a l'API
    prompt_augmentat = f"""
    {context_augmentat}
    --- FI DEL CONTEXT ---

    Ara, basant-te estrictament en el context anterior (si és rellevant), respon la meva pregunta:
    "{prompt}"
    """

    # Creem una CÒPIA de l'historial per enviar a l'API
    historial_per_api = list(st.session_state.chat_messages)

    # Substituïm l'últim missatge (el 'prompt' simple) per la nostra versió AUGMENTADA
    historial_per_api[-1] = {"role": "user", "content": prompt_augmentat}

    # ------------------------------------------------------------------
    # 3. FEM LA TRUCADA A L'API
    # ------------------------------------------------------------------
    with st.chat_message("assistant"):
        with st.spinner("Processant..."):
            # Cridem la funció amb l'historial AUGMENTAT
            resposta_bot = preguntar_chatbot(historial_per_api)
            st.markdown(resposta_bot)

    # 4. Guardem la resposta a l'historial REAL (Això no canvia)
    st.session_state.chat_messages.append({"role": "assistant", "content": resposta_bot})
