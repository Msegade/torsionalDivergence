import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

plt.rcParams.update({'text.usetex': True})
#dfCycler = mpl.cycler(color=['#332288', '#88CCEE', '#44AA99', '#117733', '#999933',
#                         '#DDCC77', '#CC6677', '#882255', '#AA4499'])
#
#mpl.rcParams['axes.prop_cycle'] = dfCycler
df = pd.read_csv('table.csv', names=['U', 'w', 'theta', 'Ucr'])

ax = sns.lineplot(x='U', y='Ucr', data=df, marker='.', markersize=12, label='$U_{cr}$',
                  legend=False)
ax.set_xlabel('Freestream velocity $U$ [m/s]')
ax.set_ylabel('Estimated critical velocity $U_{cr} [m/s]$')
ax2 = ax.twinx()
ax2._get_lines.prop_cycler = ax._get_lines.prop_cycler
ax2.plot(df['U'], df['w'], label='$w$')
ax2.set_ylabel('Vertical displacement $w$ [m]')

fig = ax.get_figure()
# Reduce the size of the figure to leave 25% space blank
fig.subplots_adjust(right=0.75)

ax3 = ax.twinx()
ax3._get_lines.prop_cycler = ax._get_lines.prop_cycler
ax3.plot(df['U'], df['theta'], label='$\\theta$')
ax3.spines['right'].set_position(('axes', +1.2))
ax3.set_ylabel('Tip torsional rotation $\\theta$ [$^{\circ}$]')
#ax3.spines['right'].set_visible(True)
#lines, labels = ax.get_legend_handles_labels()
#lines2, labels2 = ax2.get_legend_handles_labels()
#lines3, labels3 = ax3.get_legend_handles_labels()
#ax.legend(lines+lines2+lines3, labels + labels2 + labels3, loc=0)
fig.legend(loc='center left', bbox_to_anchor=(0.2, 0.5))

plt.savefig('U-Ucr.png', dpi=300)
plt.close()
