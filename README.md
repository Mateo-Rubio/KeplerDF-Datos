# KeplerDF-Datos

Repositorio de datos del experimento KeplerDF. Contiene las solicitudes en lenguaje natural producidas por distintos modelos de lenguaje, estrategias de prompting y temperaturas, junto con su validación semántica, y los scripts que analizan esos resultados. El código que genera los datos (Data Collector, Physics Engine, generación con Ollama y validación) está en el repositorio KeplerDF-Logica.

En resumen, el repositorio cumple tres funciones:

1. **Almacenar los resultados crudos** de cada máquina que ejecutó el experimento (`maquina_a/` … `maquina_e/`).
2. **Recibir los resultados a medida que se generan:** cada máquina publica sus escenarios terminados mediante commits automáticos (`maquina_{x}: N escenarios completos`).
3. **Analizar los resultados** con los scripts de `analysis/`, que consolidan la precisión de todas las condiciones en una única tabla (`analysis/unificado.csv`) y generan las figuras.

## Diseño experimental

| Factor | Niveles |
|---|---|
| Modelos | `gemma2:27b`, `llama3.1:8b`, `phi3.5:3.8b`, `phi4:14b`, `qwen2:7b` |
| Estrategias | `zero_shot`, `few_shot`, `chain_of_thought`, `chaining` |
| Escenarios | 34, de 15 tareas cada uno (510 tareas) |
| Temperaturas | 0.0, 0.2, 0.4, 0.6, 0.8, 1.0 |

Los escenarios son idénticos en todas las condiciones: misma semilla por escenario, TLE congelados, caché de geocodificación y fecha de referencia fija (ver KeplerDF-Logica).

Cada combinación de modelo y estrategia tiene 34 escenarios, por lo que una repetición completa de una temperatura en una máquina suma 5 × 4 × 34 = 680 escenarios.

### Validación

Cada tarea generada se valida en cuatro categorías, que se registran en `ollama_prompts_combined.json`:

| Categoría | Campo | Qué se comprueba |
|---|---|---|
| `day` | `day_match` | El día de la solicitud coincide con el del `ground_truth`. |
| `hour` | `hour_match` | La hora coincide. |
| `sensor` | `sensor_match` | El sensor coincide. |
| `priority` | `priority_match` | La prioridad coincide. |

En el análisis, la precisión de un escenario en una categoría es la proporción de sus 15 tareas que aciertan; la precisión `global` es el promedio de las cuatro categorías. Las respuestas de `chain_of_thought` que filtran su razonamiento en la salida (por ejemplo, incluyen `stage 1 - reasoning` o `copy it verbatim`) se cuentan como fallo en todas las categorías.

## Máquinas y repeticiones

Cada máquina corre 2 repeticiones por temperatura. Cada combinación de máquina y repetición se trata como una repetición independiente del experimento.

| Temperatura | Máquinas | Repeticiones totales |
|---|---|---|
| 0.0 – 1.0 | A, B, C, D | 8 |

Las máquinas A a D tienen las 8 repeticiones completas en todas las temperaturas, incluida la 0.0. Al comparar el texto generado tarea por tarea a temperatura 0.0 en las máquinas A, B y C, entre el 99,80 % y el 99,95 % de los textos fueron idénticos entre repeticiones de una misma máquina, y entre el 99,83 % y el 99,95 % entre máquinas distintas (`analysis/comparar_textos.py`). Es decir, la máquina no aporta variabilidad adicional a la propia de Ollama, lo que justifica agrupar las repeticiones de todas las máquinas como repeticiones equivalentes del experimento.

La máquina E (`maquina_e`) se ejecutó en un entorno distinto al de las demás, y sus repeticiones a temperatura 0.0 resultaron completamente discordantes. En ella no se cumple el supuesto de que la influencia de la máquina sobre la inferencia es mínima, por lo que sus resultados se conservan en el repositorio pero se excluyen del análisis (lista `EXCLUIDAS` en `generar_unificado.py`).

## Estructura del repositorio

```
KeplerDF-Datos/
├── README.md
├── .gitignore
├── maquina_a/ … maquina_e/        Resultados crudos de cada máquina
│   └── {modelo}/{estrategia}/temp_{T}/rep_{r}/scenario_{idx}/
└── analysis/                      Scripts de análisis y figuras
    ├── progreso.py
    ├── generar_unificado.py
    ├── unificado.csv
    ├── comparar_textos.py
    ├── distribuciones/
    ├── interacciones/
    └── repeticiones/
```

### Datos de cada máquina

```
maquina_{x}/{modelo}/{estrategia}/temp_{T}/rep_{r}/scenario_{idx}/
├── ollama_prompt_TASK_GEN_001.txt … ollama_prompt_TASK_GEN_015.txt
├── ollama_prompts_combined.json
└── scenario_report.json
```

Los nombres de los modelos usan `_` en lugar de `:` y `.` (por ejemplo, `llama3.1:8b` → `llama3_1_8b`).

| Archivo | Contenido |
|---|---|
| `ollama_prompt_TASK_GEN_XXX.txt` | Solicitud generada para cada tarea. |
| `ollama_prompts_combined.json` | Las 15 tareas del escenario con su `ground_truth`, el texto generado (`generated_output`) y la validación (`validation`: `day_match`, `hour_match`, `sensor_match`, `priority_match`). Es el archivo que usa el análisis. |
| `scenario_report.json` | Escenario generado por el Data Collector (satélites con sus TLE, estaciones terrenas y tareas). |

Un escenario solo se publica cuando su `ollama_prompts_combined.json` registra las 15 tareas. Los reportes del Physics Engine (`physics_passes_report.json`) no se incluyen porque el análisis no los usa.

## Procedencia

- **Temperatura 0.0:** generada originalmente en las ramas `maquina-a`, `maquina-b` y `maquina-c` del repositorio `Kepler-Copia` y copiadas a este repositorio.
- **Temperaturas 0.2 a 1.0:** publicadas directamente por `auto_commit.py` desde cada máquina. Los commits están firmados como `maquina_{x}`.

## Clonar solo una máquina

Para trabajar con los datos de una sola máquina sin descargar el resto:

```
git clone --filter=blob:none --sparse https://github.com/Mateo-Rubio/KeplerDF-Datos.git
cd KeplerDF-Datos
git sparse-checkout set maquina_a
```

Para agregar la carpeta de análisis: `git sparse-checkout add analysis`. Los scripts que leen los JSON de varias máquinas (`progreso.py`, `generar_unificado.py`, `comparar_textos.py`) requieren un clon completo; los que solo leen `unificado.csv` funcionan con la carpeta `analysis/`.

## Análisis

La carpeta `analysis/` sigue un flujo en dos pasos:

1. `generar_unificado.py` recorre todos los `ollama_prompts_combined.json`, calcula la precisión por escenario y categoría y la guarda en `analysis/unificado.csv`.
2. Los scripts de las subcarpetas leen `unificado.csv` (no los JSON) y guardan sus figuras en su propia carpeta.

Cuando llegan datos nuevos de las máquinas, hay que volver a ejecutar `generar_unificado.py` antes de regenerar las figuras.

### `unificado.csv`

Una fila por combinación de `temp`, `modelo`, `estrategia`, `maquina`, `rep` y `categoria` (`day`, `hour`, `sensor`, `priority`, `global`), con una columna por escenario (`1` … `34`) que contiene la precisión de ese escenario (proporción de las 15 tareas acertadas). Las celdas vacías corresponden a escenarios que todavía no se publicaron.

Los scripts de figuras promedian (o calculan el desvío de) las repeticiones de todas las máquinas para cada combinación de temperatura, modelo, estrategia, escenario y categoría.

### Scripts

| Script | Descripción | Salida |
|---|---|---|
| `progreso.py` | Muestra cuántos escenarios de los 680 tiene cada máquina para cada temperatura y repetición. Sirve para seguir el avance del experimento. | Tabla por consola. |
| `generar_unificado.py` | Calcula la precisión por escenario y categoría (aplicando la regla de fuga de `chain_of_thought`) y genera la tabla unificada. También imprime la tabla de progreso. Las máquinas de la lista `EXCLUIDAS` (actualmente `maquina_e`) no se incluyen. | `analysis/unificado.csv` |
| `comparar_textos.py` | Porcentaje de textos idénticos a temperatura 0.0 entre `rep_1` y `rep_2` de una misma máquina, y entre pares de máquinas, por modelo. | Tablas por consola. |
| `distribuciones/distribucion_variable.py` | Histogramas de la precisión por escenario para cada categoría, separados por los niveles de una variable que se pasa como argumento (`temp`, `modelo` o `estrategia`). Ejemplo: `python analysis/distribuciones/distribucion_variable.py modelo`. | `distribuciones/hist_{variable}.png` |
| `interacciones/matriz_interacciones.py` | Matriz de gráficos de violín que cruza los factores `modelo`, `temp`, `estrategia` y `categoria` (solo `day` y `hour`): en la diagonal, la distribución por nivel de cada factor; fuera de ella, la interacción entre dos factores. El punto marca la media o la mediana según la constante `ESTADISTICO`. | `interacciones/matriz_interacciones_{media\|mediana}.png` |
| `repeticiones/dispersion_repeticiones.py` | Diagramas de caja de la desviación estándar de la precisión entre repeticiones, por temperatura y categoría. Muestra cuánto varía el resultado de un mismo escenario al repetirlo. | `repeticiones/dispersion_repeticiones.png` |

### Requisitos

Requieren Python 3 con `numpy`, `pandas` y `matplotlib`:

```
python -m pip install numpy pandas matplotlib
```

Los scripts se pueden ejecutar desde cualquier directorio, ya que construyen las rutas a partir de su propia ubicación.
