import verificar_pull
import pathlib
from collections import Counter
import pandas as pd

REPO = pathlib.Path(__file__).resolve().parent.parent
TOTAL = 5 * 4 * 34
TEMPS = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
REPS = ['rep_1', 'rep_2']

conteo = Counter()
for f in REPO.glob('maquina_*/*/*/temp_*/rep_*/scenario_*/ollama_prompts_combined.json'):
    maquina, _, _, temp, rep = f.relative_to(REPO).parts[:5]
    conteo[(maquina, float(temp.split('_')[1]), rep)] += 1

maquinas = sorted(p.name for p in REPO.glob('maquina_*'))
tabla = pd.DataFrame({f'T{t} {r}': [f'{conteo[(m, t, r)]}/{TOTAL}' for m in maquinas]
                      for t in TEMPS for r in REPS}, index=maquinas)
print(tabla.to_string())