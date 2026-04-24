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

| Módulo               | Estado           | ¿Qué hace?                                                                    |
|----------------------|------------------|-------------------------------------------------------------------------------|
| **EDA**              | ✅ Completado    | Análisis general, nulos, distribuciones, outliers, correlaciones, categóricas |
| **Limpieza**         | 🚧 En desarrollo | Aplicación de sugerencias de limpieza                                         |
| **Preprocesamiento** | 🚧 En desarrollo | Transformaciones, escalado, encoding                                          |
| **Modelado**         | 🚧 En desarrollo | Selección de algoritmos, ajuste de hiperparámetros                            |
| **Entrenamiento**    | 🚧 En desarrollo | Métricas, curvas de aprendizaje, comparativas                                 |
| **Exportación**      | 🚧 En desarrollo | Modelo entrenado + datos procesados (Parquet)                                 |
| **Dashboard visual** | 📝 Planificado   | Interfaz con sliders y panel principal interactivo                            |

> 🐥 **Ya puedes ejecutar el EDA desde terminal y obtener reportes en JSON + TXT.**

---

## ✨ Características actuales (EDA)

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
  - Imputación (`median`)
  - Flag (True/False)
  - Transformación (`log1p`, `sqrt`)

### 🔗 Correlaciones (númericas)

- Matriz de correlaciones numéricas
- Detección de alta correlación (threshold configurable)
- Nota con recomendaciones (`eliminar`, `unir` o `filtrar`)

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

## ⚙️ Configuración vía YAML

Todo el comportamiento del EDA es **totalmente configurable** sin tocar el código.

### [config.yml](config/config.yml) (principal)

```yaml
path: 
  data: 'users_behavior.csv'
  overhead_percent: 1.8
  sample_data_percent: 0.1 

eda: 
  general_information: True
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
```

### [config_analysis_values.yml](config/config_analysis_values.yml) (decisiones ML)

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

> 🐥 Puedes ajustar umbrales, métodos y sugerencias según tu criterio.

---

## 🖥️ Uso actual (terminal)

```bash
# Run EDA con tu config
python main.py --config config.yml
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

## 🧱 Estructura del proyecto

```text
📂 data_alchemist/
├── 📂 config 
│   └── config_analysis_values.yml    # Configuración ML
│   └── config.yml                    # Configuración principal
├── 📂 data                           # Datasets
├── 📂 eda_analysis                   # Reportes por fechas
├── 📂 src/
│   ├── 📂 eda/
│   │   ├── eda_general_info.py       # Dimensiones, tipos, estadísticas
│   │   ├── eda_null_val.py           # Análisis de nulos
│   │   ├── eda_analysis_data.py      # Distribución, outliers, correlaciones, categóricas
│   │   └── pipeline_eda.py           # Orquestador del pipeline
│   ├── 📂 io/
│   │   └── folder_file_manager.py    # Gestión de outputs (JSON/TXT)
│   ├── 📂 strategies/
│   │   └── strategies.py                 # Enums para estrategias de validación
│   │   └── pre_processing_strategies.py  # Enums para estrategias de feature engineering
│   ├── 📂 validation/
|   |   ├── 📂 validation_analysis_values/
│   │   |   ├── validation.py                  # Validación de configuración para ML
│   │   └── eda_validation.py                  # Validación de configuración general
│   │   └── read_validation.py                 # Lectura de validaciones
│   │   └── validation.py                      # Orquestador de validaciones
│   └── get_frame.py                           # Carga de datos (eager)
├── .gitinore
├── LICENSE
├── README-ESP.md
├── README.md
├── main.py
└── requirements.txt
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
| **pathlib**	 | -           | built-in	Manejo de rutas                      |
| **psutil**	 | -	         | Monitoreo de recursos (futuro)                | 
| **datetime** | -           | built-in	Timestamps en reportes               |

---

## 🚀 Visión futura (dashboard)

```text
┌─────────────────────────────────────────────────────────────┐
│  🧙‍♂️ DATA ALCHEMIST                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. CARGA DE DATOS (Polars)                                 │
│     └── pl.read_csv() → detección de tipos, memoria         │
│                                                             │
│  2. EDA Y LIMPIEZA (Polars)                                 │
│     └── nulos, distribuciones, outliers (tu framework)      │
│                                                             │
│  3. PRE-PROCESAMIENTO (Polars → numpy)                      │
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

Haz fork del proyecto
Crea tu rama (git checkout -b feature/nueva-funcion)
Haz commit (git commit -m 'Añade nueva funcionalidad')
Haz push (git push origin feature/nueva-funcion)
Abre un Pull Request

> 💡🐥 ¿Ideas para la interfaz? ¿Sugerencias de usabilidad para no programadores? ¡Abierto a feedback!

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT
Eres libre de usarlo, modificarlo y compartirlo

---

## 📬 Contacto

🐥 **Data Alchemist** 
¿Preguntas o sugerencias? Abre un issue o contáctame directamente



