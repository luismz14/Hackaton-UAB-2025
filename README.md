# Banking Coverage Optimization in Catalonia

A UAB 2025 hackathon prototype for exploring banking access in Catalonia. The project combines demographic and economic data, graph-based coverage optimization, and a Streamlit dashboard. An optional chatbot sends selected dataset context and conversation messages to a remote language model.

## Project structure

- `Analisi.py`: dashboard, data loading, charts, and chatbot interface.
- `bank_optimizer.py`: greedy placement of physical offices and mobile banking stops on a municipality graph, with population coverage and distance-based scoring.
- `pages/1_Proposta Bàsica.py`: basic proposal page.
- `pages/2_Genera graf i proposta.py`: graph construction and office/mobile-stop proposal.
- `pages/3_Proposta Avançada.py`: advanced proposal page.
- `utils/AIna_utils.py`: remote chatbot integration.
- `Informe Final.ipynb`: exploratory analysis and historical project evidence.
- `data/` and `utils/*.xlsx`: retained identified statistics and demonstration fixture; other historical inputs must be supplied locally (see provenance document).
- `assets/`: dashboard images and coverage figures.

## Setup and usage

Run commands from the repository root. Python dependencies are pinned in `requirements.txt`; this maintenance pass did not reinstall that environment or verify a minimum Python version.

```bash
python -m venv .venv
```

Activate in Windows PowerShell with `.\.venv\Scripts\Activate.ps1`, or on macOS/Linux with `source .venv/bin/activate`.

```bash
python -m pip install -r requirements.txt
python -m streamlit run Analisi.py
```

The public tree is incomplete for historical execution: several required workbooks are intentionally excluded. Obtain authorized local copies at the exact paths in [DATA_SOURCES.md](DATA_SOURCES.md) before launching affected pages. The setup commands do not supply these inputs.

Keep the working directory at the repository root because data and asset paths are relative. Open `Informe Final.ipynb` in a Jupyter-capable editor for the exploratory workflow. A notebook frontend may need to be supplied separately.

The application uses pandas, NumPy, NetworkX, Streamlit, matplotlib, and contextily, with openpyxl for Excel files. Map tiles and the optional chatbot require external services; offline operation of those features has not been verified.

## Security and limitations

The optional chatbot reads `PUBLICAI_API_KEY` from the process environment when the application starts. Set it locally before launching Streamlit. In PowerShell:

```powershell
$env:PUBLICAI_API_KEY = "<your newly issued credential>"
python -m streamlit run Analisi.py
```

On macOS/Linux, use `export PUBLICAI_API_KEY="<your newly issued credential>"` before starting the application. The helper does not automatically load a `.env` file. If the variable is missing, chatbot requests return a configuration message without contacting the API; the dashboard can still be used.

A credential was previously committed and has been removed from the current helper. The user will handle revocation/rotation and any Git-history cleanup manually. Removing it from the working tree does not remove historical exposure. Never commit a real credential or reuse the exposed value.

The chatbot transmits data context to a third-party service. Review the input tables and their sharing permissions before using that feature. No source-code license is included. [DATA_SOURCES.md](DATA_SOURCES.md) records retained-source terms, excluded inputs, and unresolved provenance.

The notebook and some original implementation text remain in Catalan as historical material. Four machine-specific paths in the saved notebook reduce portability. This prototype has no automated test suite, and the original analysis and optimization results were preserved rather than regenerated.
