import verificar_pull
import itertools
import json
import pathlib
import pandas as pd

REPO = pathlib.Path(__file__).resolve().parent.parent
MAQUINAS = {'A': 'maquina_a', 'B': 'maquina_b', 'C': 'maquina_c'}
TEMP = 'temp_0.0'

filas = []
for maq, carpeta in MAQUINAS.items():
    raiz = REPO / carpeta
    for f in raiz.glob(f'*/*/{TEMP}/rep_*/scenario_*/ollama_prompts_combined.json'):
        modelo, estrategia, _, rep, escenario = f.relative_to(raiz).parts[:5]
        for t in json.loads(f.read_text(encoding='utf-8'))['tasks']:
            filas.append({'maquina': maq, 'modelo': modelo, 'estrategia': estrategia, 'rep': rep,
                          'escenario': escenario, 'task_id': t['task_id'], 'texto': t['generated_output']})
df = pd.DataFrame(filas)

# Referencia: rep_1 vs rep_2 dentro de cada máquina
intra = df.pivot_table(index=['maquina', 'modelo', 'estrategia', 'escenario', 'task_id'],
                       columns='rep', values='texto', aggfunc='first').dropna()
intra['igual'] = intra['rep_1'] == intra['rep_2']
print('% de textos idénticos entre rep_1 y rep_2 (misma máquina):')
print((intra.groupby(['modelo', 'maquina'])['igual'].mean().unstack() * 100).round(2), '\n')

# Entre máquinas: misma repetición
entre = df.pivot_table(index=['modelo', 'estrategia', 'rep', 'escenario', 'task_id'],
                       columns='maquina', values='texto', aggfunc='first').dropna()
pares = pd.DataFrame({f'{a} vs {b}': entre[a] == entre[b] for a, b in itertools.combinations(MAQUINAS, 2)})
print('% de textos idénticos entre máquinas (misma repetición):')
print((pares.groupby(level='modelo').mean() * 100).round(2))