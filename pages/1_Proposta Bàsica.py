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

st.header("Objectiu")
st.write("El codi té com a objectiu seleccionar la ubicació òptima d’oficines bancàries fixes i mòbils per maximitzar la cobertura de la població d’una regió. Per fer-ho, treballa amb un graf de municipis, on cada node representa un municipi i les arestes representen la seva proximitat geogràfica.")

st.subheader("Dades d’entrada")
st.write("Per crear el graf cal disposar de:" \
"- Nom del municipi" \
"- Codi o identificador únic" \
"- Població (en diferents franges d’edat o total)" \
"- Coordenades UTM (X, Y)" \
"\nA partir d'aquestes dades es genera un graf per poder treballar-hi.")

st.image("assets/girona_bank_coverage.png")
st.image("assets/girona_bank_coverage_map.png")

st.image("assets/lleida_bank_coverage.png")
st.image("assets/lleida_bank_coverage_map.png")

st.image("assets/tarragona_bank_coverage.png")
st.image("assets/tarragona_bank_coverage_map.png")