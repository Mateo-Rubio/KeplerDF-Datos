import verificar_pull
import json
import pathlib
from collections import Counter
import numpy as np
import pandas as pd

REPO = pathlib.Path(__file__).resolve().parent.parent
SALIDA = pathlib.Path(__file__).resolve().parent / 'output' / 'unificado.csv'
TOTAL = 5 * 4 * 34
TEMPS = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
REPS = ['rep_1', 'rep_2']
CATEGORIAS = {'day': 'day_match', 'hour': 'hour_match', 'sensor': 'sensor_match', 'priority': 'priority_match'}
FUGA = ("stage 1 - reasoning", "stage 2 - final", "which exact string", "copy it verbatim")
CLAVE = ['temp', 'modelo', 'estrategia', 'maquina', 'rep', 'categoria']

conteo = Counter()
filas = []
for f in REPO.glob('maquina_*/*/*/temp_*/rep_*/scenario_*/ollama_prompts_combined.json'):
    maquina, modelo, estrategia, temp, rep, escenario = f.relative_to(REPO).parts[:6]
    t = float(temp.split('_')[1])
    conteo[(maquina, t, rep)] += 1
    aciertos = {c: [] for c in CATEGORIAS}
    for tarea in json.loads(f.read_text(encoding='utf-8'))['tasks']:
        fuga = estrategia == 'chain_of_thought' and any(k in tarea['generated_output'].lower() for k in FUGA)
        for c, campo in CATEGORIAS.items():
            aciertos[c].append(tarea['validation'][campo] and not fuga)
    precisiones = {c: np.mean(v) for c, v in aciertos.items()}
    precisiones['global'] = np.mean(list(precisiones.values()))
    for c, p in precisiones.items():
        filas.append({'temp': t, 'modelo': modelo, 'estrategia': estrategia, 'maquina': maquina, 'rep': rep,
                      'categoria': c, 'escenario': int(escenario.split('_')[1]), 'precision': p})

maquinas = sorted(p.name for p in REPO.glob('maquina_*'))
tabla = pd.DataFrame({f'T{t} {r}': [f'{conteo[(m, t, r)]}/{TOTAL}' for m in maquinas]
                      for t in TEMPS for r in REPS}, index=maquinas)
print(tabla.to_string())

unificado = pd.DataFrame(filas).pivot(index=CLAVE, columns='escenario', values='precision').reset_index()
SALIDA.parent.mkdir(parents=True, exist_ok=True)
unificado.to_csv(SALIDA, index=False)