import pathlib
import pandas as pd
import matplotlib.pyplot as plt

CARPETA = pathlib.Path(__file__).resolve().parent
UNIFICADO = CARPETA.parent / 'unificado.csv'
CLAVE = ['temp', 'modelo', 'estrategia', 'maquina', 'rep', 'categoria']
CATEGORIAS = ['day', 'hour', 'sensor', 'priority', 'global']

df = pd.read_csv(UNIFICADO)
df = df[df['categoria'].isin(CATEGORIAS)]
df = df.melt(id_vars=CLAVE, var_name='escenario', value_name='precision')
de = df.groupby(['temp', 'modelo', 'estrategia', 'escenario', 'categoria'])['precision'].std().dropna().reset_index()
temps = sorted(de['temp'].unique())

fig, axes = plt.subplots(3, 2, figsize=(10, 7), sharey=True)
axes.flat[-1].remove()
for cat, ax in zip(CATEGORIAS, axes.flat):
    ax.boxplot([de.loc[(de['categoria'] == cat) & (de['temp'] == t), 'precision'] for t in temps],
               positions=range(len(temps)), patch_artist=True,
               boxprops={'facecolor': '#2a78d6'}, medianprops={'color': 'black'})
    ax.set_xticks(range(len(temps)), [str(t) for t in temps])
    ax.set_title(cat)
    ax.set_xlabel('Temperatura')
plt.tight_layout()
plt.savefig(CARPETA / 'dispersion_repeticiones.png', dpi=300, bbox_inches='tight')
plt.show()