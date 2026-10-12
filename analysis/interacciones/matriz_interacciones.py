import pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import itertools

CARPETA = pathlib.Path(__file__).resolve().parent
UNIFICADO = CARPETA.parent / 'unificado.csv'
CATEGORIA = sys.argv[1]  # 'day', 'hour', 'sensor', 'priority' o 'global'
ESTADISTICO = 'media'  # 'media' o 'mediana'
CLAVE = ['temp', 'modelo', 'estrategia', 'maquina', 'rep', 'categoria']
FACTORES = ['modelo', 'temp', 'estrategia']
TAM_XLABEL = 7
TAM_YLABEL = 7
TAM_LEYENDA = 5
TAM_XTICK = 6
ETIQUETAS = {'gemma2_27b': 'gemma2\n27b', 'llama3_1_8b': 'llama3.1\n8b', 'phi3_5_3_8b': 'phi3.5\n3.8b',
             'phi4_14b': 'phi4\n14b', 'qwen2_7b': 'qwen2\n7b', 'chain_of_thought': 'chain of\nthought',
             'few_shot': 'few\nshot', 'zero_shot': 'zero\nshot'}
COLORES = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300']
centro = np.mean if ESTADISTICO == 'media' else np.median


def violines(ax, datos, posiciones, ancho, color, etiqueta):
    cuerpos = ax.violinplot(datos, positions=posiciones, widths=ancho, showextrema=False)['bodies']
    for c in cuerpos:
        c.set_facecolor(color)
        c.set_edgecolor(color)
        c.set_alpha(0.35)
    ax.scatter(posiciones, [centro(d) for d in datos], color=color, s=4, zorder=3, label=etiqueta)

def panel(ax, fi, fj):
    x = np.arange(len(niveles[fj]))
    if fi == fj:
        for k, n in enumerate(niveles[fi]):
            violines(ax, [prec.loc[prec[fi] == n, 'precision']], [k], 0.7, COLORES[k], str(n))
    else:
        ancho = 0.8 / len(niveles[fi])
        for k, n in enumerate(niveles[fi]):
            datos = [prec.loc[(prec[fi] == n) & (prec[fj] == m), 'precision'] for m in niveles[fj]]
            violines(ax, datos, x + (k - (len(niveles[fi]) - 1) / 2) * ancho, ancho * 0.9, COLORES[k], str(n))
    ax.set_xticks(x, [ETIQUETAS.get(str(n), str(n)) for n in niveles[fj]], fontsize=TAM_XTICK)
    ax.tick_params(axis='y', labelsize=TAM_YLABEL)
    ax.legend(title=fi, fontsize=TAM_LEYENDA, title_fontsize=TAM_LEYENDA, loc='best', ncol=2,
              markerscale=0.8, labelspacing=0.2, handletextpad=0.1, columnspacing=0.6,
              borderpad=0.3, framealpha=0.7)


def guardar(fig, sufijo):
    fig.savefig(CARPETA / f'matriz_interacciones_{CATEGORIA}_{sufijo}.png', dpi=300, bbox_inches='tight', pad_inches=0.02)


df = pd.read_csv(UNIFICADO)
df = df[df['categoria'] == CATEGORIA]
df = df.melt(id_vars=CLAVE, var_name='escenario', value_name='precision')
prec = df.groupby(['temp', 'modelo', 'estrategia', 'escenario', 'categoria'])['precision'].mean().dropna().reset_index()
niveles = {f: sorted(prec[f].unique()) for f in FACTORES}
fig, axes = plt.subplots(len(FACTORES), len(FACTORES), figsize=(9, 5.65), sharex='col', sharey=True)
for i, fi in enumerate(FACTORES):
    for j, fj in enumerate(FACTORES):
        ax = axes[i, j]
        panel(ax, fi, fj)
        if i == 0:
            ax.set_title(fj, fontsize=TAM_XLABEL)
        if j == 0:
            ax.set_ylabel(fi, fontsize=TAM_YLABEL)
        x = np.arange(len(niveles[fj]))
        if i == j:
            for k, n in enumerate(niveles[fi]):
                violines(ax, [prec.loc[prec[fi] == n, 'precision']], [k], 0.7, COLORES[k], str(n))
        else:
            ancho = 0.8 / len(niveles[fi])
            for k, n in enumerate(niveles[fi]):
                datos = [prec.loc[(prec[fi] == n) & (prec[fj] == m), 'precision'] for m in niveles[fj]]
                violines(ax, datos, x + (k - (len(niveles[fi]) - 1) / 2) * ancho, ancho * 0.9, COLORES[k], str(n))
        ax.set_xticks(x, [ETIQUETAS.get(str(n), str(n)) for n in niveles[fj]], fontsize=TAM_XTICK)
        ax.tick_params(axis='y', labelsize=TAM_YLABEL)
        ax.legend(title=fi, fontsize=TAM_LEYENDA, title_fontsize=TAM_LEYENDA, loc='best', ncol=2,
          markerscale=0.8, labelspacing=0.2, handletextpad=0.1, columnspacing=0.6,
          borderpad=0.3, framealpha=0.7)
        if i == 0:
            ax.set_title(fj, fontsize=TAM_XLABEL)
        if j == 0:
            ax.set_ylabel(fi, fontsize=TAM_YLABEL)
axes[0, 0].set_ylim(0, 1.02)
fig.suptitle(f'Matriz de Interacción para la categoria {CATEGORIA.capitalize()}', fontsize=TAM_XLABEL + 1)
plt.tight_layout()
plt.subplots_adjust(wspace=0.08, hspace=0.08)
guardar(fig, ESTADISTICO)
fig, axes = plt.subplots(1, len(FACTORES), figsize=(6.5, 2.2), sharey=True)
for ax, f in zip(axes, FACTORES):
    panel(ax, f, f)
    ax.set_xlabel(f, fontsize=TAM_XLABEL)
axes[0].set_ylim(0, 1.02)
axes[0].set_ylabel('precisión', fontsize=TAM_YLABEL)
plt.tight_layout()
guardar(fig, 'marginales')
plt.close(fig)

for a, b in itertools.combinations(sorted(FACTORES), 2):
    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.4), sharey=True)
    for ax, (fi, fj) in zip(axes, [(a, b), (b, a)]):
        panel(ax, fi, fj)
        ax.set_xlabel(fj, fontsize=TAM_XLABEL)
    axes[0].set_ylim(0, 1.02)
    axes[0].set_ylabel('precisión', fontsize=TAM_YLABEL)
    plt.tight_layout()
    guardar(fig, f'{a}_{b}')
    plt.close(fig)
plt.show()