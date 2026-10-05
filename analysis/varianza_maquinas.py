import verificar_pull
import json
import pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

REPO = pathlib.Path(__file__).resolve().parent.parent
SALIDA = pathlib.Path(__file__).resolve().parent / "output" / "maquinas"
CATEGORIAS = ['day_match', 'hour_match', 'sensor_match', 'priority_match']
FUGA = ("stage 1 - reasoning", "stage 2 - final", "which exact string", "copy it verbatim")
N_BOOT = 2000
rng = np.random.default_rng(0)

filas = []
for f in REPO.glob('maquina_*/*/*/temp_*/rep_*/scenario_*/ollama_prompts_combined.json'):
    maquina, modelo, estrategia, temp, rep, escenario = f.relative_to(REPO).parts[:6]
    if float(temp.split('_')[1]) == 0:
        continue
    aciertos = []
    for t in json.loads(f.read_text(encoding='utf-8'))['tasks']:
        fuga = estrategia == 'chain_of_thought' and any(k in t['generated_output'].lower() for k in FUGA)
        aciertos.append(np.mean([t['validation'][c] and not fuga for c in CATEGORIAS]))
    filas.append({'temp': float(temp.split('_')[1]), 'modelo': modelo, 'estrategia': estrategia,
                  'escenario': escenario, 'maquina': maquina, 'precision': np.mean(aciertos)})
df = pd.DataFrame(filas)

celda = ['temp', 'modelo', 'estrategia', 'escenario']
pm = df.groupby(celda + ['maquina'])['precision'].agg(['mean', 'var', 'count']).reset_index()
pm = pm[pm['count'] == 2]
pm = pm[pm.groupby(celda)['maquina'].transform('nunique') == pm.groupby('temp')['maquina'].transform('nunique')]
cel = pm.groupby(celda).agg(s_w2=('var', 'mean'), s_b2=('mean', 'var')).reset_index()

filas_res = []
for T, g in cel.groupby('temp'):
    w, b = g['s_w2'].to_numpy(), g['s_b2'].to_numpy()
    idx = rng.integers(0, len(g), (N_BOOT, len(g)))
    boot = 2 * b[idx].mean(axis=1) / w[idx].mean(axis=1)
    filas_res.append({'temp': T, 'celdas': len(g), 'var_dentro': w.mean(), 'var_entre': b.mean(),
                      'cociente': 2 * b.mean() / w.mean(),
                      'ic_inf': np.percentile(boot, 2.5), 'ic_sup': np.percentile(boot, 97.5)})
res = pd.DataFrame(filas_res)
print(res.round(4).to_string(index=False))

fig, ax = plt.subplots(figsize=(8, 5))
ax.errorbar(res['temp'], res['cociente'],
            yerr=[res['cociente'] - res['ic_inf'], res['ic_sup'] - res['cociente']],
            fmt='o', capsize=5, label='Cociente (IC 95 % bootstrap)')
ax.axhline(1, color='r', ls='--', label='Sin efecto de máquina (= 1)')
ax.set_xticks(res['temp'])
ax.set_xlabel('Temperatura')
ax.set_ylabel('2 · varianza entre máquinas / varianza dentro de máquina')
ax.set_title('Variabilidad entre máquinas frente a variabilidad entre repeticiones')
ax.legend()
plt.tight_layout()
SALIDA.mkdir(parents=True, exist_ok=True)
plt.savefig(SALIDA / 'varianza_maquinas.png', dpi=300, bbox_inches='tight')
plt.show()