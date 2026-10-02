import verificar_pull
import json
import pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

REPO = pathlib.Path(__file__).resolve().parent.parent
SALIDA = pathlib.Path(__file__).resolve().parent / "output" / "maquinas"
MAQUINAS = {'A': 'maquina_a', 'B': 'maquina_b', 'C': 'maquina_c'}
TEMP = 'temp_0.0'
CATEGORIAS = ['day_match', 'hour_match', 'sensor_match', 'priority_match']
FUGA = ("stage 1 - reasoning", "stage 2 - final", "which exact string", "copy it verbatim")

filas = []
for maq, carpeta in MAQUINAS.items():
    raiz = REPO / carpeta
    for f in raiz.glob(f'*/*/{TEMP}/rep_*/scenario_*/ollama_prompts_combined.json'):
        modelo, estrategia, _, rep, escenario = f.relative_to(raiz).parts[:5]
        for t in json.loads(f.read_text(encoding='utf-8'))['tasks']:
            fuga = estrategia == 'chain_of_thought' and any(k in t['generated_output'].lower() for k in FUGA)
            filas.append({'maquina': maq, 'modelo': modelo, 'estrategia': estrategia, 'rep': rep,
                          'escenario': escenario, **{c: t['validation'][c] and not fuga for c in CATEGORIAS}})

clave = ['modelo', 'estrategia', 'escenario', 'rep']
p = pd.DataFrame(filas).groupby(['maquina'] + clave)[CATEGORIAS].mean().reset_index()
p = p[p.groupby(clave).maquina.transform('nunique') == len(MAQUINAS)]
prec = p.groupby(['maquina', 'modelo', 'estrategia', 'escenario'])[CATEGORIAS].mean().reset_index()

bins = np.arange(-1 / 60, 1 + 1 / 30, 1 / 30)
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
for cat, ax in zip(CATEGORIAS, axes.flat):
    for maq in MAQUINAS:
        x = prec.loc[prec.maquina == maq, cat]
        ax.hist(x, bins=bins, alpha=0.5, label=f'Máquina {maq} (media = {x.mean():.3f})')
    ax.set_title(cat)
    ax.set_xlabel('Precisión por escenario (promedio de repeticiones)')
    ax.set_ylabel('Frecuencia')
    ax.legend()
fig.suptitle(f'Distribución de la precisión por escenario entre máquinas — {TEMP}')
plt.tight_layout()
SALIDA.mkdir(parents=True, exist_ok=True)
plt.savefig(SALIDA / f'hist_precision_maquinas_{TEMP}.png', dpi=300, bbox_inches='tight')
plt.show()
