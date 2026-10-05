# KeplerDF-Datos

Contiene las solicitudes en lenguaje natural producidas por distintos modelos de lenguaje, estrategias de prompting y temperaturas, junto con su validación semántica. El código que genera estos datos está en el repositorio KeplerDF-Logica.

## Diseño experimental

| Factor | Niveles |
|---|---|
| Modelos | `gemma2:27b`, `llama3.1:8b`, `phi3.5:3.8b`, `phi4:14b`, `qwen2:7b` |
| Estrategias | `zero_shot`, `few_shot`, `chain_of_thought`, `chaining` |
| Escenarios | 34, de 15 tareas cada uno (510 tareas) |
| Temperaturas | 0.0, 0.2, 0.4, 0.6, 0.8, 1.0 |

Los escenarios son idénticos en todas las condiciones: misma semilla por escenario, TLE congelados, caché de geocodificación y fecha de referencia fija (ver KeplerDF-Logica).

## Máquinas y repeticiones

Cada máquina corre 2 repeticiones por temperatura. Cada combinación de máquina y repetición se trata como una repetición independiente del experimento.

| Temperatura | Máquinas | Repeticiones totales |
|---|---|---|
| 0.0 | A, B, C | 6 |
| 0.2 – 1.0 | A, B, C, D, E | 10 |

La temperatura 0.0 tiene menos repeticiones porque las repeticiones adicionales son prácticamente redundantes. Al comparar el texto generado tarea por tarea a temperatura 0.0, entre el 99,80 % y el 99,95 % de los textos fueron idénticos entre repeticiones de una misma máquina, y entre el 99,83 % y el 99,95 % entre máquinas distintas (`analysis/comparar_textos.py`). Es decir, la máquina no aporta variabilidad adicional a la propia de Ollama.

## Estructura

```
maquina_{x}/{modelo}/{estrategia}/temp_{T}/rep_{r}/scenario_{idx}/
├── ollama_prompt_TASK_GEN_001.txt … ollama_prompt_TASK_GEN_015.txt
├── ollama_prompts_combined.json
└── scenario_report.json
```

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

Para agregar la carpeta de análisis: `git sparse-checkout add analysis`. Los scripts de análisis que comparan máquinas requieren un clon completo.

## Análisis

La carpeta `analysis/` contiene los scripts de análisis. Todos importan primero `verificar_pull.py`, que comprueba si el repositorio local está al día con GitHub y, si no lo está, pregunta antes de continuar.

| Script | Descripción |
|---|---|
| `verificar_pull.py` | Comprobación de commits pendientes antes de cualquier análisis. |
| `comparar_textos.py` | Porcentaje de textos idénticos entre repeticiones y entre máquinas. |
| `hist_maquinas.py` | Histograma de la precisión por escenario para cada máquina. Guarda la figura en `analysis/output/maquinas/`. |
| `varianza_maquinas.py` | Compara la variabilidad entre máquinas con la variabilidad entre repeticiones de una misma máquina, por temperatura (excepto 0.0). Calcula el cociente `2 · varianza entre máquinas / varianza dentro de máquina` con un intervalo de confianza del 95 % por bootstrap; un valor cercano a 1 indica que la máquina no agrega variabilidad. Guarda la figura en `analysis/output/maquinas/varianza_maquinas.png`. |

Las respuestas de `chain_of_thought` que filtran su razonamiento en la salida se cuentan como fallo en todas las categorías.

Requieren `numpy`, `pandas` y `matplotlib`:

```
python -m pip install numpy pandas matplotlib
```
