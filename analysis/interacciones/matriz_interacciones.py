import pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

CARPETA = pathlib.Path(__file__).resolve().parent
UNIFICADO = CARPETA.parent / 'unificado.csv'
ESTADISTICO = 'media'  # 'media' o 'mediana'
CLAVE = ['temp', 'modelo', 'estrategia', 'maquina', 'rep', 'categoria']
FACTORES = ['modelo', 'temp', 'estrategia', 'categoria']
COLORES = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300']
centro = np.mean if ESTADISTICO == 'media' else np.median


def violines(ax, datos, posiciones, ancho, color, etiqueta):
    cuerpos = ax.violinplot(datos, positions=posiciones, widths=ancho, showextrema=False)['bodies']
    for c in cuerpos:
        c.set_facecolor(color)
        c.set_edgecolor(color)
        c.set_alpha(0.35)
    ax.scatter(posiciones, [centro(d) for d in datos], color=color, s=18, zorder=3, label=etiqueta)


df = pd.read_csv(UNIFICADO)
df = df[df['categoria'].isin(['day', 'hour'])]
df = df.melt(id_vars=CLAVE, var_name='escenario', value_name='precision')
prec = df.groupby(['temp', 'modelo', 'estrategia', 'escenario', 'categoria'])['precision'].mean().dropna().reset_index()
niveles = {f: sorted(prec[f].unique()) for f in FACTORES}

fig, axes = plt.subplots(len(FACTORES), len(FACTORES), figsize=(22, 18), sharey=True)
for i, fi in enumerate(FACTORES):
    for j, fj in enumerate(FACTORES):
        ax = axes[i, j]
        x = np.arange(len(niveles[fj]))
        if i == j:
            for k, n in enumerate(niveles[fi]):
                violines(ax, [prec.loc[prec[fi] == n, 'precision']], [k], 0.7, COLORES[k], str(n))
        else:
            ancho = 0.8 / len(niveles[fi])
            for k, n in enumerate(niveles[fi]):
                datos = [prec.loc[(prec[fi] == n) & (prec[fj] == m), 'precision'] for m in niveles[fj]]
                violines(ax, datos, x + (k - (len(niveles[fi]) - 1) / 2) * ancho, ancho * 0.9, COLORES[k], str(n))
        ax.set_xticks(x, [str(n) for n in niveles[fj]], rotation=45)
        if i == 0:
            ax.set_title(fj)
        if j == 0:
            ax.set_ylabel(f'{fi}\nprecisión')
    axes[i, -1].legend(*axes[i, 1 if i == 0 else 0].get_legend_handles_labels(), title=fi,
                       bbox_to_anchor=(1.02, 1), loc='upper left')
axes[0, 0].set_ylim(0, 1.02)
plt.tight_layout()
plt.savefig(CARPETA / f'matriz_interacciones_{ESTADISTICO}.png', dpi=300, bbox_inches='tight')
plt.show()