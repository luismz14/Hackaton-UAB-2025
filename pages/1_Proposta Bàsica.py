import streamlit as st
from PIL import Image

icon = "🏦"
st.set_page_config(
    page_title="AI'll find it — Proposta Bàsica",
    page_icon=icon,
    layout="wide"
)

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
st.caption("Project coverage scenarios using Generalitat/Idescat municipal data. Basemaps: © OpenStreetMap contributors, © CARTO. See DATA_SOURCES.md for sources and reuse terms.")

st.title("Proposta: Oficina Mòbil a les Cooperatives Locals")
st.markdown("""
### Objectiu general
Apropar els serveis financers de la *Caixa d'Enginyers* a les zones rurals mitjançant una *furgoneta adaptada com a oficina mòbil*.  
Aquesta iniciativa vol *millorar la inclusió financera* i *enfortir el vincle cooperatiu* amb les comunitats locals.
""")

st.header("Context i necessitat")
st.markdown("""
Molts *pobles i zones rurals* pateixen una *manca d’oficines bancàries*, fet que dificulta l'accés als serveis financers bàsics.  
Les *cooperatives agràries i de consum* són punts clau de trobada i col·laboració entre la població local, i poden esdevenir *espais estratègics per oferir serveis de la Caixa d’Enginyers*.
""")

st.info("""
Proposta: Col·locar una *furgoneta-oficina mòbil* de la Caixa d’Enginyers a les cooperatives dels municipis seleccionats, amb un calendari rotatiu setmanal.
""")

st.header("Justificació de la proposta")
st.markdown("""
La *Caixa d’Enginyers* és una *cooperativa de crèdit, **sense propietaris externs* i amb *valors alineats amb les cooperatives locals*:
- Governança democràtica: els socis són també els propietaris.
- Compromís amb el territori i el desenvolupament sostenible.
- Reinversió dels beneficis en serveis per als socis.

Aquesta afinitat fa que la col·laboració amb les cooperatives locals sigui *natural i coherent* amb la filosofia de l'entitat.
""")

st.success("""
Relació clau: Les cooperatives i la Caixa d’Enginyers comparteixen els mateixos valors: *solidaritat, proximitat i retorn social*.
""")

st.header("Impacte esperat")
st.markdown("""
L’oficina mòbil permetrà:
- Atendre *socis actuals* en zones on no hi ha oficines físiques.
- *Captar nous socis* que desconeixen l’entitat.
- Oferir *assessorament personalitzat* en productes financers, assegurances, estalvi i inversió responsable.
- *Donar visibilitat* a la Caixa d’Enginyers en entorns on no és present.
""")

st.header("Importància de donar a conèixer els productes")
st.markdown("""
Molts possibles socis *desconeixen els productes i avantatges* que ofereix la Caixa d’Enginyers.  
Per això, cada visita de la furgoneta hauria d’incloure:
- *Sessions informatives breus* sobre productes clau (com comptes, targetes, assegurances i fons sostenibles).
- *Material divulgatiu* personalitzat per a cada cooperativa.
- *Promocions especials* per a nous socis o contractacions in situ.
""")

st.warning("""
Objectiu estratègic: No només oferir serveis, sinó *vendre i educar* sobre els productes que aporten valor real a la comunitat.
""")

st.header("Conclusió")
st.markdown("""
La proposta de la *furgoneta-oficina mòbil* reforça el compromís de la Caixa d’Enginyers amb el territori i amb els seus valors cooperatius.  
A més, obre una via efectiva per *arribar a nous socis, divulgar productes útils i promoure l’educació financera* a zones amb baixa cobertura bancària.
""")

st.markdown("---")
st.caption("Proposta elaborada per a la iniciativa de proximitat de la Caixa d’Enginyers.")
