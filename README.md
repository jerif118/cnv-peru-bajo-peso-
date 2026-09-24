# Análisis de nacimientos del Perú

1. Crea un entorno e instala las dependencias una vez: `python3 -m venv .venv`, `source .venv/bin/activate` y `python -m pip install -r requirements.txt`.
2. Copia `.env.example` a `.env` y completa los datos de tu SQL Warehouse, catálogo y archivo CSV en Unity Catalog.
3. Ejecuta primero `01_calidad_nacimiento.ipynb`; después, en cualquier orden, `02_analisis_bajo_peso.ipynb`, `03_modelo_bajo_peso.ipynb`, `04_resumen_datos.ipynb`, `05_patrones_territorio.ipynb` y `06_prematuridad_territorio.ipynb`.

Los notebooks usan autenticación OAuth de Databricks. La copia local del CSV y `.env` están excluidos de Git; el CSV debe existir en el volumen indicado por `DATABRICKS_RAW_CSV_PATH`.

La conexión está en `lakehouse.py` y las definiciones SQL y gráficos compartidos por el 02 y el 05 en `analisis_comun.py`. En VS Code selecciona `.venv/bin/python` como intérprete de Python y kernel de los notebooks; así se resuelve también el aviso de importación de `databricks`.

La auditoría sigue el diccionario de nacimientos proporcionado. El notebook 01 conserva el origen en `raw`, repara la estructura en `staging`, audita sus valores en `metadata` y crea los datos tipados en `curated`. El 02 y el 05 guardan agregados en `analytics`; el 03 entrena los modelos y guarda el resultado en `modelos`; el 04 guarda las tablas descriptivas del artículo en `resultados/`.

El 01 también carga `datos_referencia/ubigeo_distrito.csv` (altitud, IDH 2019, pobreza y macrorregión por distrito; ver `datos_referencia/FUENTE.md`) como `raw.ubigeo_distrito_referencia` y lo une a `curated` por el ubigeo de residencia.

Población de análisis (`es_registro_analisis` en `curated`): partos únicos de 2015–2025 con peso entre 500 y 6000 g, gestación de 22 a 44 semanas y peso coherente con la semana de gestación y el sexo (dentro de 3 rangos intercuartílicos). Los partos múltiples se excluyen porque su bajo peso (58–93 %) responde a otro mecanismo.

- **01**: además del formato, valida rangos (mes, gestación, talla, departamento del ubigeo), cuenta filas idénticas y recodifica `Hijos_fallec_madre = -1` como `0 O IGNORADO`, porque el diccionario no tiene el valor 0.
- **02**: tasas con IC 95 % de Wilson, bajo peso total y a término (≥37 semanas), tasa anual estandarizada por edad materna y comparación por departamento de residencia.
- **03**: usa todos los partos únicos agregados por combinación de variables (el conteo se usa como `sample_weight`). Organiza la información por momento: escenario prenatal (madre, hogar y territorio) y al parto (establecimiento, atención y semanas de gestación); las capas del parto discriminan más, pero el establecimiento refleja la derivación de embarazos de riesgo y las semanas son parte del mecanismo. En el escenario prenatal compara regresión logística con la edad en splines y gradient boosting (elige con 2024, evalúa una vez en 2025). Modela tres resultados —bajo peso, prematuridad y bajo peso a término— con métricas sin umbral (AUC ROC, AUC PR, log loss, Brier, Brier skill score, observados/esperados, pendiente de calibración) y al marcar el 10 % / 20 % de mayor riesgo (sensibilidad, especificidad, VPP, VPN, F1, exactitud balanceada, MCC, LR+ y matriz de confusión); además, matriz de asociación (V de Cramér), importancia por permutación y perfiles de riesgo con un árbol de decisión para cada resultado.
- **04**: flujo de selección de la población, completitud de cada variable, resumen numérico y Tabla 1 (características según bajo peso), exportados a `resultados/`.
- **05**: patrones territoriales: altitud, macrorregión, pobreza e IDH del distrito, provincias extremas, tendencia por macrorregión, interacciones edad × altitud y edad × hijos vivos, y gráfico de embudo de establecimientos.
- **06**: prematuridad (<37 y <32 semanas) por provincia y edad de la madre: mapas (crudo, ajustado por edad con estandarización indirecta y bajo peso a término), mapas por grupo de edad, riesgo relativo por edad en cada macrorregión, madres primerizas (primer embarazo) × edad, correlaciones entre provincias (Spearman y Pearson ponderado) y matriz de correlación. Usa los límites de `datos_referencia/*.geojson`.
