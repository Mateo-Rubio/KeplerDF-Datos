import sys
import pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ANALISIS = pathlib.Path(__file__).resolve().parent
UNIFICADO = ANALISIS / 'output' / 'unificado.csv'
SALIDA = ANALISIS / 'output' / 'distribuciones'
VARIABLE = sys.argv[1]
CATEGORIAS = ['day', 'hour', 'sensor', 'priority', 'global']
CLAVE = ['temp', 'modelo', 'estrategia', 'maquina', 'rep', 'categoria']

df = pd.read_csv(UNIFICADO).melt(id_vars=CLAVE, var_name='escenario', value_name='precision')
prec = df.groupby(['temp', 'modelo', 'estrategia', 'escenario', 'categoria'])['precision'].mean().dropna().reset_index()

bins = np.arange(-1 / 60, 1 + 1 / 30, 1 / 30)
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for cat, ax in zip(CATEGORIAS, axes.flat):
    for nivel, g in prec[prec['categoria'] == cat].groupby(VARIABLE):
        ax.hist(g['precision'], bins=bins, alpha=0.5, label=f'{nivel} (media = {g["precision"].mean():.3f})')
    ax.set_title(cat)
    ax.set_xlabel('Precisión por escenario (promedio de repeticiones)')
    ax.set_ylabel('Frecuencia')
    ax.legend()
axes.flat[-1].axis('off')
fig.suptitle(f'Distribución de la precisión por escenario según {VARIABLE}')
plt.tight_layout()
SALIDA.mkdir(parents=True, exist_ok=True)
plt.savefig(SALIDA / f'hist_{VARIABLE}.png', dpi=300, bbox_inches='tight')
plt.show()