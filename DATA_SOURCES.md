# Data sources and publication scope

This prototype mixes observed statistics, derived data, AI-generated values, fictitious membership assumptions and forecasts. These categories are not interchangeable. Publication review: 2026-10-03. Historical results were not rerun or independently validated. Repository-authored source code uses [MIT](LICENSE); third-party data, assets, libraries, submodules and models retain their own terms. upstream data conditions remain separate.

## Retained observed inputs

| Local file | Identified source and scope | Attribution and conditions |
| --- | --- | --- |
| `data/CoordenadesMunicipis.csv` | Strong schema/content match to Generalitat **Municipis Catalunya Geo**, dataset [9aju-tpwc](https://analisi.transparenciacatalunya.cat/en/Urbanisme-infraestructures/Municipis-Catalunya-Geo/9aju-tpwc), with municipality geography associated with Idescat/ICGC. Original export date unknown; not claimed byte-identical to the current download. | Source: Generalitat de Catalunya, Municipis Catalunya Geo; underlying Idescat/ICGC information. Follow the dataset's terms and [Generalitat reuse conditions](https://web.gencat.cat/ca/generalitat/dades-indicadors/dades-obertes/llicencies). Retain supplied source/update metadata; identify adaptations and do not imply endorsement. |
| `data/PoblacioMunicipi.csv` | Strong match to Generalitat **Població de Catalunya per municipi, rang d'edat i sexe**, [b4rr-d25b](https://analisi.transparenciacatalunya.cat/d/b4rr-d25b): 2019–2020 municipal-register information prepared by Idescat. [Catalogue/source description](https://datos.gob.es/gl/catalogo/a09002970-poblacion-de-cataluna-por-municipio-rango-de-edad-y-sexo). | Source: Generalitat de Catalunya / Idescat, Padró municipal d'habitants, 2019–2020. Catalogue links Generalitat reuse terms. Original local export date unknown; preserve source-specific terms and distinguish derived calculations. |
| `data/model/IPC.xlsx` | Workbook sheet `tabla-50944` identifies INE [table 50944](https://www.ine.es/jaxiT3/Tabla.htm?L=0&t=50944), provincial annual CPI, base 2021; local series 2009–2022. Exact local download date unknown; values were not individually reconciled. | Source: INE, table 50944. INE-owned statistical information generally uses **CC BY 4.0**, unless otherwise indicated; cite original/derived use, supplied update date and avoid endorsement. [INE reuse notice](https://www.ine.es/dyngs/AYU/index.htm?cid=125). Current table's 2026 update is not the local export date. |

Government material does not share one universal license. Dataset-specific conditions and third-party content exceptions override general reuse notices. Do not relicense these inputs as project source code. Original export dates remain unrecovered, not invented.

## Project fixture and derived figures

`utils/ProbaCamiGraph.xlsx` is a five-row graph-upload demonstration fixture using rounded municipality coordinates/population groups. Workbook contributor metadata matches project contributor Arnau Muñoz Barrera. Its limited test schema/content supports retaining it as a project demonstration, **not authoritative official municipal statistics**. No official-source attribution is asserted.

The six `assets/{girona,lleida,tarragona}_bank_coverage{,_map}.png` files are project-authored historical optimization illustrations associated with the municipal geography/population workflow. They show proposed/model-selected facilities, not an observed bank network or validated optimum. Source: project calculations using Generalitat/Idescat municipal inputs described above. The three map variants retain embedded credits and use CARTO Positron: **© [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), © [CARTO](https://carto.com/attribution/)**. Keep these credits with copied figures and follow [CARTO basemap terms](https://www.carto.com/legal/basemap-terms/); documentation credits do not replace image credits.

`assets/heatmap_socios_2035_REPARTO_PONDERADO.png` remains as user-approved historical **project-modeled forecast visualization**, not official statistics, verified bank membership, or evidence of a validated forecast. Its underlying historical membership base is unverified; the input workbooks are excluded. No bank-data permission or authoritative provenance is asserted by retaining this aggregate model-output illustration.

## Excluded historical local inputs

The following files are not redistributed. Paths identify where separately obtained, authorized local copies were expected by the historical project; exact-path ignore rules prevent accidental addition. Preserve their original schemas; a current download may differ. These references are not download permission, verified provenance, or a promise that the application runs without the files.

| Expected local path | Historical role; unresolved provenance |
| --- | --- |
| `data/BancsProvincia.xlsx` | Provincial bank offices; probable Banco de España table 4.49 family; exact historical export/reference date not established. |
| `data/EmpresesProvincia.xlsx` | Businesses by province, 2009–2022; probable INE DIRCE; exact table/filter/export not established. |
| `data/model/EmpresesProvincia.xlsx` | Model copy of provincial businesses, 2009–2022; same unresolved INE DIRCE provenance. |
| `data/Habitants.xlsx` | Population, 2008–2025; probable official historical series mixed with Aina-generated 2023–2025 values; historical source unresolved. |
| `data/OficinesMunicipi.xlsx` | Municipal bank offices, 2015–2025; exact provider/export unresolved. |
| `data/PIB.xlsx` | GDP, 2009–2022; probable INE regional accounts; exact revision/export unresolved. |
| `data/PIBperCapita.xlsx` | GDP per capita, 2009–2022; probable INE regional accounts; exact revision/export unresolved. |
| `data/PIBpercentatge.xlsx` | Probable GDP growth derived from unresolved underlying GDP export. |
| `data/model/Densidad.xlsx` | Provincial population density, 2009–2022; probable official statistics, exact source unresolved. |
| `data/model/HipotequesAnuals(2009-2022).xlsx` | Annual provincial mortgages; probable INE mortgage statistics, exact category/table/export unresolved. |
| `data/model/PIB.xlsx` | Provincial GDP subset, 2009–2022; probable INE regional accounts, exact revision/export unresolved. |
| `data/model/socios_caixa_enginyers_provincias_EXTENDIDO.xlsx` | Historical membership allocations, 2009–2024; base, authority, units and redistribution rights unresolved. |
| `data/socios_caixa_enginyers_provincias_EXTENDIDO_2035_REPARTO_PONDERADO.xlsx` | Derived membership forecast/allocations through 2035; underlying membership base unresolved. |
| `utils/MunicipiosEspana.xlsx` | Spanish municipalities, coordinates, altitude and population; original source unresolved. |

For membership inputs, both factual authority and redistribution rights remain unresolved. The notebook explicitly labels a regional membership table fictitious; this does not establish that every historical workbook row is synthetic. Do not present the excluded historical base as observed bank data. The forecast workbook is a derived project allocation, not an official projection.

The notebook describes Aina-generated population values for 2023–2025; `Habitants.xlsx` mixed these with probable official historical values and is excluded. Its discussion also mentions newer generated company values, whereas the inspected company workbooks contained only 2009–2022. The historical narrative is preserved, not corrected through a new experiment.

`assets/cat_map.png`, `assets/furgo.jpeg`, `assets/logo_small.png` and `assets/Eina_AINA.jpeg` are excluded because original authorship/reuse permission was not established. The dashboard no longer loads the excluded branding or map illustration. They are optional historical visuals, not replacement data.

The advanced page fetches provincial GeoJSON from Click That 'Hood; its [upstream metadata](https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/spain-provinces.metadata.json) identifies CartoDB Common Data. The hosting project's MIT license does not establish all original geographic-data terms. This network dependency remains unresolved and is not vendored here.

## Historical evidence, execution and security

The original Catalan/Spanish notebook narrative, code, identifiers and saved outputs remain historical evidence. Embedded excerpts/results are not a newly cleared raw-data distribution or scientifically corrected experiment. Dataset availability and schema inconsistencies, graph edge cases and forecast methodology remain unresolved. Restore authorized local inputs only for a deliberate historical run; do not silently substitute current data and interpret old scores as reproduced.

`PUBLICAI_API_KEY` remains environment-only. The owner handles rotation/revocation and any history cleanup manually. Optional chatbot calls send selected local data context externally; provide only data authorized for that use.

Excluded originals are preserved outside this public working tree. Working-tree exclusions do **not** remove prior Git copies. Historical removal is a separate manual owner decision.
