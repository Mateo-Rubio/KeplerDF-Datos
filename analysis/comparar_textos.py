import itertools
import json
import pathlib
import pandas as pd

REPO = pathlib.Path(__file__).resolve().parent.parent
MAQUINAS = {'A': 'maquina_a', 'B': 'maquina_b', 'C': 'maquina_c', 'D': 'maquina_d', 'E': 'maquina_e'}
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

# Referencia: todos los pares de repeticiones dentro de cada máquina (B y D tienen además rep_3)
intra = df.pivot_table(index=['maquina', 'modelo', 'estrategia', 'escenario', 'task_id'],
                       columns='rep', values='texto', aggfunc='first')
pares_rep = pd.concat([(intra[a] == intra[b]).astype(float).where(intra[a].notna() & intra[b].notna())
                       for a, b in itertools.combinations(sorted(intra.columns), 2)])
print('% de textos idénticos entre repeticiones (misma máquina):')
print((pares_rep.groupby(['modelo', 'maquina']).mean().unstack() * 100).round(2), '\n')

# Entre máquinas: misma repetición, solo tareas presentes en ambas máquinas del par (rep_3 solo cuenta en B vs D)
entre = df.pivot_table(index=['modelo', 'estrategia', 'rep', 'escenario', 'task_id'],
                       columns='maquina', values='texto', aggfunc='first')
pares = pd.DataFrame({f'{a} vs {b}': (entre[a] == entre[b]).astype(float).where(entre[a].notna() & entre[b].notna())
                      for a, b in itertools.combinations(MAQUINAS, 2)})
print('% de textos idénticos entre máquinas (misma repetición):')
print((pares.groupby(level='modelo').mean() * 100).round(2).to_string())