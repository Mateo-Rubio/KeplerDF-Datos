import sys
import pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ANALISIS = pathlib.Path(__file__).resolve().parent
UNIFICADO = ANALISIS / 'output' / 'unificado.csv'
SALIDA = ANALISIS / 'output' / 'distribuciones'
VARIABLE = sys.argv[1]
CATEGORIAS = ['day', 'hour']
CLAVE = ['temp', 'modelo', 'estrategia', 'maquina', 'rep', 'categoria']

df = pd.read_csv(UNIFICADO).melt(id_vars=CLAVE, var_name='escenario', value_name='precision')
df = df[df['categoria'].isin(CATEGORIAS)]
prec = df.groupby(['temp', 'modelo', 'estrategia', 'escenario', 'categoria'])['precision'].mean().dropna().reset_index()

niveles = sorted(prec[VARIABLE].unique())
bins = np.arange(-1 / 60, 1 + 1 / 30, 1 / 30)
fig, axes = plt.subplots(len(CATEGORIAS), len(niveles), figsize=(4 * len(niveles), 7), sharex=True, sharey=True)
for i, cat in enumerate(CATEGORIAS):
    for j, nivel in enumerate(niveles):
        x = prec.loc[(prec['categoria'] == cat) & (prec[VARIABLE] == nivel), 'precision']
        ax = axes[i, j]
        ax.hist(x, bins=bins)
        ax.set_title(f'{cat} — {nivel} (media = {x.mean():.3f})')
        ax.set_xlabel('Precisión por escenario (promedio de repeticiones)')
        ax.set_ylabel('Frecuencia')
fig.suptitle(f'Distribución de la precisión por escenario según {VARIABLE}')
plt.tight_layout()
SALIDA.mkdir(parents=True, exist_ok=True)
plt.savefig(SALIDA / f'hist_{VARIABLE}_separado.png', dpi=300, bbox_inches='tight')
plt.show()