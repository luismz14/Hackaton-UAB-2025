# Hackaton-UAB-2025 — Optimització de cobertura bancària

**Descripció del repositori**  
Aquest projecte desenvolupa una solució per **optimitzar la cobertura de serveis bancaris** a Catalunya combinant: anàlisi de dades (demografia, oferta bancària), **algorismes de grafs**, un mòdul d’**optimització** (oficines fixes + unitats mòbils) i una **aplicació interactiva amb Streamlit** que inclou un **xatbot RAG** per fer consultes en llenguatge natural sobre les dades carregades. També inclou un quadern d’**anàlisi exploratòria** que justifica l’enfocament i avalua l’impacte.

> Documentació viva: **https://deepwiki.com/arnaumunozbarrera/Hackaton-UAB-2025**

---

## Taula de continguts
- [Visió general](#visió-general)
- [Arquitectura](#arquitectura)
- [Tecnologies](#tecnologies)
- [Requisits](#requisits)
- [Instal·lació i entorn](#instal·lació-i-entorn)
- [Execució](#execució)
  - [Mode Aplicació (Streamlit)](#mode-aplicació-streamlit)
  - [Mode Exploratori (Jupyter)](#mode-exploratori-jupyter)
- [Comandes útils](#comandes-útils)
- [Estructura del repositori](#estructura-del-repositori)
- [Llicència](#llicència)
- [Enllaços](#enllaços)


---

## Visió general
- **Problema:** Hi ha zones amb **baixa cobertura bancària** (oficines/caixers), que impacta la inclusió financera i l’accés a serveis.
- **Solució:** Model que avalua cobertura i suggereix **ubicacions òptimes** per a noves oficines i **parades d’unitats mòbils** (furgó), maximitzant població servida i minimitzant solapaments/costos.
- **Sortida:** App interactiva per explorar escenaris, carregar datasets, generar grafs i obtenir una **proposta automàtica** amb mètriques de cobertura.

---

## Arquitectura
- **Analytical Core** — `Informe Final.ipynb`: EDA, mètriques, visualitzacions i experiments de models.
- **Interactive App** — `Analisi.py`: App Streamlit multipàgina (sidebar) per explorar dades, llançar optimitzacions i visualitzar resultats.
- **Pages** — `pages/`:
  - `1_Model.py`: explicació/model base.
  - `3_Genera graf i proposta.py`: càrrega de dades, generació de graf i proposta (N oficines, M parades).
  - `4_Proposta Avançada.py`: anàlisi i ajustos avançats.
- **Optimization Engine** — `bank_optimizer.py`: classe/funcions per puntuar nodes i selecció greedy en dues fases.
- **RAG Utils** — `utils/AIna_utils.py`: utilitats per compondre prompts i consultar el LLM amb mostres del dataset.

---

## Tecnologies
- **Python 3.10+**
- **Streamlit** (UI multipàgina)
- **pandas**, **numpy** (ETL i manipulació)
- **networkx** (grafs)
- **scikit-learn** (modelatge/auxiliars)
- **altair**, **matplotlib** (gràfics)
- **openpyxl** (Excel)
- **contextily** (mapes base)
- **Jupyter** (notebooks)

> Si necessites crear ràpidament el fitxer de dependències:
> ```bash
> python -m pip freeze > requirements.txt
> ```

---

## Requisits
- **Git** ≥ 2.30  
- **Python** ≥ 3.10  
- **pip** ≥ 23  
- (Opcional) **Jupyter** per a notebooks

---

## Instal·lació i entorn
```bash
# 1) Clona el repositori
git clone https://github.com/arnaumunozbarrera/Hackaton-UAB-2025.git
cd Hackaton-UAB-2025

# 2) Crea i activa un entorn virtual
python -m venv .venv
# Windows (PowerShell):
. .venv/Scripts/Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

# 3) Instal·la dependències
pip install -r requirements.txt
# Si no existeix, instal·la manualment les llibreries clau:
# pip install streamlit pandas numpy networkx scikit-learn altair matplotlib contextily openpyxl jupyter

# ─────────────────────────────────────────────────────────────
# Comandes ràpides per afegir al final del README (copiar/enganxar)
# ─────────────────────────────────────────────────────────────

# Llançar l’app (Streamlit)
streamlit run Analisi.py

