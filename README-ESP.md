# 🚧 Data Alchemist [WIP]

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.53%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.5%2B-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Polars](https://img.shields.io/badge/Polars-1.37%2B-orange?style=for-the-badge&logo=polars&logoColor=white)](https://pola.rs)
![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-013243?style=for-the-badge&logo=numpy&logoColor=white)
[![Plotly](https://img.shields.io/badge/Plotly-6.5%2B-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?style=for-the-badge&logo=pandas&logoColor=white)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.12%2B-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](https://opensource.org/licenses/MIT)


> ⚠️ **PROYECTO EN DESARROLLO ACTIVO**
> Esta repositorio documenta el diseño y la arquitectura de una plataforma interactiva que democratiza el aprendizaje automático; cargando sus datos, seleccionando su objetivo y la plataforma.

**Data Alchemist** es una plataforma interactiva que democratiza el aprendizaje automático. 
Sube tus datos, selecciona tu objetivo y la plataforma:
- Analiza automáticamente la memoria disponible
- Decidir la estrategia óptima (eager/lazy/streaming)
- Le guía en el preprocesamiento y la selección de modelos
- Entrenar y evaluar en tiempo real
- Exporta tu modelo y datos procesados

✅ Ideal para **científicos de datos**, **analistas** y **cualquier persona** que quiera experimentar 
con ML sin preocuparse por la infraestructura.

---

## 📍 Estado del proyecto

| Módulo                            | Estado           | ¿Qué hace?                                                                        |
|-----------------------------------|------------------|-----------------------------------------------------------------------------------|
| **EDA**                           | ✅ Completado    | Análisis general, nulos, distribuciones, outliers, correlaciones, categóricas     |
| **Limpieza**                      | ✅ Completado    | Nulos (con EDA), duplicados, elimina columnas, tipos de dato y renombrar columnas |
| **Preprocesamiento (numérico)**   | ✅ Completado    | Correlación, distribución y outliers                                              |
| **Preprocesamiento (categórico)** | 🚧 En desarrollo | Dominancia categórica                                                             |
| **Scaling & Encoding**            | 🚧 Siguiente     | Encoding y Scaler                                                                 |
| **Modelado**                      | 🚧 En desarrollo | Selección de algoritmos, ajuste de hiperparámetros                                |
| **Entrenamiento**                 | 🚧 En desarrollo | Métricas, curvas de aprendizaje, comparativas                                     |
| **Exportación**                   | 🚧 En desarrollo | Modelo entrenado + datos procesados (Parquet)                                     |
| **Dashboard visual**              | 📝 Planificado   | Interfaz con sliders y panel principal interactivo                                |

> 🐥 **Ya puedes ejecutar el EDA desde terminal y obtener reportes en JSON + TXT.**

---

## ✨ Características de EDA

### 📊 Análisis General

- Dimensiones del dataset (filas × columnas)
- Columnas disponibles y sus tipos de datos
- Estadísticas descriptivas para columnas numéricas
- Conteo de valores únicos en categóricas

### 🔍 Análisis de Nulos

- Total de nulos por columna y por fila
- Porcentaje de nulos
- Acción sugerida: `keep`, `analyse` o `delete`

### 📊 Distribución (numéricas)

- Rango, media, mediana, IQR
- Forma de la cola (positiva/negativa/balanceada)
- Nivel de concentración de los datos

- **Sugerencias ML**: transformador (`log1p`, `sqrt`, `square`) y escalador (`minMaxScaler`, `robustScaler`, `standarScaler`)

### 🚨 Outliers (numéricas)

- IQR, número y porcentaje de outliers

- **Sugerencias ML**:
  - Escalador (`robustScaler`, `standarScaler`, `minMaxScaler`)
  - Filtrado (`trim`, `capping`)
  - Imputación (`median`, `mean`)
  - Flag (True/False)
  - Transformación (`log1p`, `sqrt`)

### 🔗 Correlaciones (númericas)

- Matriz de correlaciones numéricas
- Detección de alta correlación (threshold configurable)
- Nota con recomendaciones (`eliminar` o `join`)

### 🏷️ Dominio de Categóricas

- Total de valores únicos por columna
- Top valores con porcentaje
- Valores raros detectados

- **Sugerencias ML**:
    - `ordinalEncoder` (pocas categorías)
    - `targetEncoder` (muchas categorías / alta cardinalidad)
    - `oneHotEncoder` (valores raros agrupados)
    - Manejo de nulos en categóricas

---

## ✨ Características de Limpieza

El pipeline de limpieza prepara tus datos **antes** del preprocesamiento. Todas las operaciones son configurables vía YAML y se integran automáticamente en el flujo principal.

### 🔄 Operaciones disponibles

| Operación                  | ¿Qué hace?                              | ¿Cómo se configura?                              |
|----------------------------|-----------------------------------------|--------------------------------------------------|
| **Renombrar columnas**     | Cambia nombres de columnas              | Diccionario `rename_columns` en `config.yml`     |
| **Cambiar tipos de datos** | Casting a Int32, Int64, Float32, Utf8   | Diccionario `change_datatypes` en `config.yml`   |
| **Eliminar duplicados**    | Borra filas duplicadas                  | Booleano `duplicates` en `config.yml`            |
| **Eliminar columnas**      | Borra columnas completas                | Lista `drop_columns` en `config.yml`             |
| **Manejo de nulos**        | Imputa o elimina según análisis del EDA | Usa `JSON_analysis.json` + `config_cleaning.yml` |

### 🧠 Manejo inteligente de nulos

La limpieza de nulos **no es a ciegas**. Utiliza el análisis del EDA para decidir:

1. **keep** -> la columna no tiene nulos, no se hace nada
2. **delete** -> la columna tiene muchos nulos (>65% por defecto), se elimina entera
3. **analyse** -> la columna tiene algunos nulos, se evalúa:
   - ¿% nulos por columna < `columns_percent`? -> se imputan o eliminan filas
   - ¿% filas con nulos > `rows_percent`? -> se eliminan esas filas
   - Si no -> se imputan con **mediana** (numéricas) o **moda** (categóricas)

> 🐥 Todos los valores tienen defaults validados con Pydantic. Si no defines algo, funciona igual.

--- 

## ✨ Características Feature Engineering

Una vez que el EDA genera el reporte `JSON_analysis.json`, el pipeline de preprocesamiento puede **aplicar automáticamente** las transformaciones, imputaciones y filtros sugeridos.

### 🧠 ¿Qué hace?

| Paso	                             | ¿Qué hace?	                                      | ¿En qué se basa?                                                             |
|------------------------------------|--------------------------------------------------|------------------------------------------------------------------------------|
| **Muestreo**	                     | Ajusta el tamaño del dataset dinámicamente	      | `config_preprocessing.yml` (umbrales por tamaño)                             |
| **Manejo de nulos**	               | Imputa o filtra nulos por columna                | Análisis de nulos del EDA + `ml_preprocessing.preprocessing.operations.null` |
| **Transformación de distribución** | Aplica `log1p`, `sqrt` o `square`                | Sugerencias de distribución del EDA                                          |
| **Manejo de outliers**	           | Filtra, imputa, flaggea o transforma             | Sugerencias de outliers del EDA + `preprocessing_outlier_rules`              | 
| **Alta correlación**	             | Combina columnas con alta correlación (promedio) | Análisis de correlación del EDA                                              | 

### 📊 Salida 

Un **DataFrame de Polars preprocesado** con:

- Transformaciones aplicadas (distribución)
- Outliers manejados (filtrados, imputados, flaggeados o transformados)
- Nulos imputados o filtrados
- Columnas con alta correlación combinadas (promedio)
- Muestreo aplicado si el dataset era muy grande

> 🐥 Todas las decisiones son **rastreables** a través de los logs. Revisa la consola para ver exactamente qué se aplicó a cada columna.

---

## ⚙️ Configuración vía YAML

Todo el comportamiento del EDA es **totalmente configurable** sin tocar el código.

> 🐥 Puedes ajustar umbrales, métodos y sugerencias según tu criterio.

### [config.yml](config/config.yml) (principal)

```yaml
path: 
  data: 'users_behavior.csv'
  overhead_percent: 1.8
  sample_data_percent: 0.1 # porcentaje análisis de datos, esto puede cambiar según el sistema para que sea óptimo, no se usa ahora, hasta que se agregue laz y streaming

eda: 
  null_values: True
  null_values_percent_column: 0.65
  null_values_percent_row: 0.40
  basic_analysis_data: 
    distribution: 
      columns: 
      enable: True
    outliers: 
      columns:
      enable: True
      method: # Si no se proporciona un método, el valor será 'iqr'
    correlation: 
      columns: 
      enable: True
    category_dominance: 
      columns: 
      enable: True
      top_n: # Si no se proporciona un top_n, el valor será 2
      rare_threshold_percent: # Si no se da un umbral, el valor será 0,01

cleaning: 
  rename_columns: 
  change_datatypes: 
  duplicates: True # # Eliminar filas duplicadas si True
  drop_columns: 
  
  null_values: 
    null_impute_numerics: # # si Ninguno -> se utilizará la median si se encuentran valores nulos
    null_impute_categorics: #  si None -> el mode se utilizará si se encuentran valores nulos

ml_preprocessing: 
  columns: # si es None, se utilizarán todas las columnas
  
  sampling: # si no se proporciona el valor, se utilizará 'random'
  representative_column: #use cuando se selecciona "representative"
  
  null_num_handler: # si no se da el valor, se utilizará 'median'
  null_cat_handler: # si no se proporciona el valor, se utilizará 'constantValue'
  null_cat_handler_value: # Si no se proporciona ningún valor, se utilizará "Unknown"
  
  distribution: 
    transformer: 
  
  outlier: 
    strategy: # si no se proporciona "iqr" será la estrategia utilizada
    filter: 
    impute_outliers: 
    flag: # Bool True/False
    transform: 
  
  correlation:
    high_correlation: # si None, entonces join será la operación
    remove_column: # solo si se selecciona high_correlation, si no, join será la operación automática para no eliminar ninguna columna
  
  category: # ESTO FALTA
    operation: # si no se proporciona el valor, se proporcionará la operación "Group"
    name_operation_value: # Valor para la operación, si es Ninguno, entonces "Unknown" será el valor automático dado

ml_training: # El codificador y el escalador no funcionan
  target: 'is_ultra'
  
  train_test_search: 0.2
  train_test_final: 0.25 # 🚨 NO DISPONIBLE 🚨
  random_state: 42
  
  encoder: # 🚨 NO DISPONIBLE 🚨 si None=Auto (Reglas en config_modeling), si no, todas las columnas tendrán el codificador que seleccionó 
  scaler: # 🚨 NO DISPONIBLE 🚨 si no hay ninguno, se utilizará auto, el algoritmo decidirá
  scaler_outlier_method: # 🚨 NO DISPONIBLE 🚨 si no hay ninguno, se utilizará iqr
```

### [config_analysis_values.yml](config/config_analysis_values.yml) (decisiones de análisis)

```yaml
distribution_decision_maker: 
  tail_length: 100
  scaler_concentration: 0.3

outlier_decision_maker: 
  scaler: 
    robust_scaler_percent: 5.0
    standard_scaler_percent: 1.0
  filter: 
    none: 10.0
    trim: 2.0
  # ... más configuraciones
```

### [config_cleaning.yml](config/config_cleaning.yml) (decisiones de limpieza para nulos)

```yaml
threshold_nulls:
  rows_percent: 40
  columns_percent: 65
```

### [config_preprocessing.yml](config/config_preprocessing.yml) (decisiones de preprocesamiento para outliers)

```yaml
sample_data:
  min_sample: # < min_sample
    max_files: 10000
  
  medium_sample: # min_sample entre medium_sample
    max_files: 100000
    percent: 0.2
  
  many_sample: # medium_sample entre many_sample
    max_files: 1000000
    percent: 0.05
  
  too_much_sample: # > many_sample
    percent: 0.01

preprocessing_outlier_rules:
  filter_percent: 1 # % < filter_percent
  impute_percent: 5 # % < impute_percent
  transform_percent: 5 # % > transform_percent
  flag_percent: 10 # % > flag_percent
```

---

## 🖥️ Uso actual (terminal)

```bash
# Run EDA con tu config
python main.py 
```

### 🚀 Instalación rápida

```bash 
git clone https://github.com/sm7ss/DataAlchemist # Clona
cd DataAlchemist # Ve a la carpeta

poetry install # Instala dependencias
poetry shell # Activa entorno

python main.py # Ejecuta
```

### 📦 Outputs generados

| **Archivo**	     | **Formato** | **Contenido**                                             |
|--------------------|-------------|-----------------------------------------------------------|
| JSON_analysis.json | JSON	       | Datos estructurados con todos los análisis                | 
| TXT_report.txt     | TXT	       | Reporte legible por humanos con emojis y formato amigable |

### 📄 Ejemplo de salida (TXT)

```text
========================================================================================
                                    DATA ALCHEMIST  
                             🐥 ANALYSIS REPORT (TEXT MODE)
========================================================================================
📅 Date: 2026-04-22
📁 Dataset: users_behavior.csv
📊 Shape: 3214 rows | 5 columns
========================================================================================
GENERAL INFO
----------------------------------------------------------------------------------------
📝 Available Columns: calls, minutes, messages, mb_used, is_ultra
...

🚨 calls
    - IQR: 42.0
    - Total of Outliers: 62
    - Percent: 1.929
    ML Suggestions: 
       - Scaler: minMaxScaler
       - Filter: trim
       - Impute: median
...

✅ High correlations identified for model consideration
⚠️ Priority suggestions: Join, filter, remove or group calls, minutes
...
```

---

## 🛠️ Tecnologías usadas

| **Librería** | **Versión** |	**¿Para qué?**                               |
|--------------|-------------|-----------------------------------------------|
| **Python**	 | 3.10.18     | Lenguaje base                                 |
| **Polars**	 | 1.39.3	     | Procesamiento de datos rápido y eficiente     |
| **Pydantic** | 2.12.5	     | Validación de configuraciones                 |
| **PyYAML**	 | 6.0.3	     | Parseo de archivos YAML                       |
| **tomli**		 | 2.4.1       | Soporte para TOML (alternativo)               |
| **pathlib**	 | built-in    | Manejo de rutas                               |
| **psutil**	 | -	         | Monitoreo de recursos (futuro)                | 
| **datetime** | built-in    | Timestamps en reportes                        |

---

## 🧱 Estructura del proyecto

```text
📂 data_alchemist/
├── 📂 config 
│   └── config_analysis_values.yml    # Configuración análisis
│   └── config_cleaning.yml           # Configuración limpieza
│   └── config_modeling.yml           # Configuración modelado (NO DISPONIBLE)
│   └── config_preprocessing.yml      # Configuración preprocesamiento
│   └── config.yml                    # Configuración principal
├── 📂 data                           # Datasets
├── 📂 eda_analysis                   # Reportes por fechas
├── 📂 src/
│   ├── 📂 cleaning/
│   │   ├── columns_name.py           # Renombra columnas
│   │   ├── datatypes.py              # Cambia tipo de datos de columnas
│   │   ├── drop_columns.py           # Elimina columnas
│   │   ├── duplicated.py             # Elimina duplicados
│   │   ├── nulls.py                  # Imputa, elimina y analiza nulos 
│   │   ├── pipeline.py               # Orquestador de limpieza
│   ├── 📂 eda/
│   │   ├── eda_general_info.py       # Dimensiones, tipos, estadísticas
│   │   ├── eda_null_val.py           # Análisis de nulos
│   │   ├── eda_analysis_data.py      # Distribución, outliers, correlaciones, categóricas
│   │   └── pipeline_eda.py           # Orquestador del pipeline
│   ├── 📂 io/
│   │   └── folder_file_manager.py    # Gestión de outputs (JSON/TXT)
│   ├── 📂 ml_process/
|   |   ├── 📂 preprocessing/
|   |   |   ├── 📂 operations/
│   │   |   |   ├── null.py           # Expresiones para nulos
│   │   |   |   └── transformers.py   # Expresiones para transformadores       
│   │   |   ├── correlation.py        # Expresiones para el análisis de correlación  
│   │   |   ├── distribution.py       # Expresiones para el análisis de distribución   
│   │   |   ├── outliers.py           # DataFrame con datos limpios de Outliers
│   │   └────── pipeline.py           # Orquestador de preprocesamiento
│   ├── 📂 strategies/
│   │   └── cleaning_strategies.py        # Enums para estrategias de limpieza
│   │   └── modeling_strategies.py        # Enums para estrategias de modelado (NO DISPONIBLES)
│   │   └── pre_processing_strategies.py  # Enums para estrategias de feature engineering
│   │   └── strategies.py                 # Enums para estrategias de validación
│   ├── 📂 validation/
|   |   ├── 📂 validation_analysis_values/
│   │   |   └── validation.py                 # Validación de configuración para eda analysis
|   |   ├── 📂 validation_cleaning/
│   │   |   └── validation.py                 # Validación de configuración para limpieza
|   |   ├── 📂 validation_modeling/
│   │   |   └── validation.py                 # Validación de configuración para modelado (NO DISPONIBLE)
|   |   ├── 📂 validation_preprocessing/
│   │   |   └── validation.py                 # Validación de configuración para ML
│   │   └── cleaning_validation.py          # Validación de configuración limpieza
│   │   └── eda_validation.py               # Validación de configuración general
│   │   └── ml_validation.py                # Validación de configuración modelado (NO DISPONIBLE)
│   │   └── pre_processing_validation.py    # Validación de configuración para preprocesamiento
│   │   └── read_validation.py              # Lectura de validaciones
│   │   └── validation.py                   # Orquestador de validaciones
│   └── get_frame.py                        # Carga de datos (eager)
├── .gitinore
├── LICENSE
├── README-ESP.md
├── README.md
├── main.py
└── requirements.txt
```

---

## 🚀 Visión futura (dashboard)

```text
┌─────────────────────────────────────────────────────────────┐
│  🧙‍♂️ DATA ALCHEMIST                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. CARGA DE DATOS (Polars)                                 │
│     └── pl.read_csv() -> detección de tipos, memoria        │
│                                                             │
│  2. EDA Y LIMPIEZA (Polars)                                 │
│     └── nulos, distribuciones, outliers (tu framework)      │
│                                                             │
│  3. PRE-PROCESAMIENTO (Polars -> numpy)                     │
│     └── .to_numpy() / .to_pandas() para Scikit-learn        │
│                                                             │
│  4. MODELADO (Scikit-learn)                                 │
│     └── train_test_split, modelos, métricas                 │
│                                                             │
│  5. VISUALIZACIÓN (Plotly)                                  │
│     └── resultados, curvas, matrices                        │
│                                                             │
│  6. EXPORTACIÓN (Polars)                                    │
│     └── resultados a Parquet/CSV                            │
└─────────────────────────────────────────────────────────────┘
```

### Funcionalidades planeadas:

  - Slider lateral para navegar entre módulos
  - Detección automática de modo: eager | lazy | streaming
  - Aplicación de sugerencias con un clic
  - Entrenamiento de modelos básicos (regresión/clasificación)
  - Exportación a Parquet y modelo entrenado
  - Monitoreo de recursos en tiempo real (100% local)

--- 



## 🤝 Cómo contribuir

1. Haz fork del proyecto
2. Crea tu rama (git checkout -b feature/nueva-funcion)
3. Haz commit (git commit -m 'Añade nueva funcionalidad')
4. Haz push (git push origin feature/nueva-funcion)
5. Abre un Pull Request

> 💡🐥 ¿Ideas para la interfaz? ¿Sugerencias de usabilidad para no programadores? ¡Abierto a feedback!

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT
Eres libre de usarlo, modificarlo y compartirlo

---

## 📬 Contacto

🐥 **Data Alchemist** 
¿Preguntas o sugerencias? Abre un issue o contáctame directamente



