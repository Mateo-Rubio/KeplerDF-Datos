import pathlib


REPO = pathlib.Path(__file__).resolve().parent.parent
SALIDA = pathlib.Path(__file__).resolve().parent / 'output' / 'unificado.csv'
for f in REPO.glob('maquina_*/*/*/temp_*/rep_*/scenario_*/ollama_prompts_combined.json'):
    print(f.relative_to(REPO).parts[:6])
    break


CATEGORIAS = {'day': 'day_match', 'hour': 'hour_match', 'sensor': 'sensor_match', 'priority': 'priority_match'}
for c in CATEGORIAS: 
    print(c)
for c, campo in CATEGORIAS.items():
    print(c,campo)