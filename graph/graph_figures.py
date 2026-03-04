
from GraphInspector import GraphInspector
import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np
import warnings
from matplotlib.colors import LinearSegmentedColormap

# Suppress RuntimeWarnings from Shapely
warnings.filterwarnings("ignore", category=RuntimeWarning)

path_to_graph = 'graph10.3.pt'

graph = GraphInspector(path_to_graph, grid_key = 'data', hidden_key = 'hidden', coords_key='x')
xlim = (-30,60)
ylim=(50,90)

mesh_edge_lons = np.array(graph.mesh_edge_list[1], dtype=object)
mesh_edge_lats = np.array(graph.mesh_edge_list[0], dtype=object)

n_lines = graph.graph_data[graph.h2h_key]['edge_index'].shape[1]
edge_weights = graph.mesh_edge_weights

# Function to apply the thresholds
def apply_threshold(value, lower_threshold, upper_threshold):
    if value is None:  # If the value is None, leave it as is
        return None
    if value < lower_threshold or value > upper_threshold:  # Apply threshold
        return None
    return value

# Use np.vectorize to apply the function element-wise
mesh_edge_lons_large = mesh_edge_lons
mesh_edge_lons_large = np.vectorize(apply_threshold)(mesh_edge_lons_large, -14, 25)
mesh_edge_lats_large = mesh_edge_lats
mesh_edge_lats_large = np.vectorize(apply_threshold)(mesh_edge_lats_large, 57, 71)
mesh_edge_lons_small = mesh_edge_lons
mesh_edge_lons_small = np.vectorize(apply_threshold)(mesh_edge_lons_small, -2, 2)
mesh_edge_lats_small = mesh_edge_lats
mesh_edge_lats_small = np.vectorize(apply_threshold)(mesh_edge_lats_small, 64.5, 66.5)

def get_color(weight, cmap):
    #print(weight)
    if weight > 30:
        return cmap[0], 10, 1
    elif weight <= 30 and weight > 15:
        return cmap[1], 6, 2
    elif weight <= 15 and weight > 7:
        return cmap[2], 3, 3
    elif weight <= 7 and weight > 3.5:
        return cmap[3], 20, 4
    elif weight <= 3.5 and weight > 2.25:
        return cmap[4], 12 ,5
    elif weight <= 2.25 and weight > 1:
        return cmap[5], 6, 6
    else:
        return cmap[6], 1, 7 

fig, ax = plt.subplots(figsize=(10,10), dpi=200, subplot_kw={'projection':ccrs.NorthPolarStereo()})
ax.scatter(graph.mesh_lons, graph.mesh_lats, marker='.', s=10, color='grey', label = 'Hidden mesh', zorder=50, alpha=0.4, transform=ccrs.PlateCarree())
#ax.set_ylim(65.5, 67)
#ax.set_xlim(-2,2)
#cmap = ['#FFFFFF', '#FFFFFF', '#FFFFFF', '#9C27B0', "#004DC0", "#D13F35", "#252525"]
cmap = ['#FFFFFF', '#FFFFFF', '#FFFFFF', "#BC2AD6", "#0558D3", "#E4473B", "#252525"]
cmap = ['#FFFFFF', '#FFFFFF', '#FFFFFF', '#1A237E', '#0288D1', '#4CAF50', "#252525"]
for i in range(n_lines):
    if edge_weights[i] > 8:
        pass
    else:
        color, lw, zorder = get_color(edge_weights[i], cmap=cmap)
        ax.plot(mesh_edge_lons_small[3*i:3*i+2], mesh_edge_lats_small[3*i:3*i+2], lw=lw, zorder=zorder, color=color, transform=ccrs.PlateCarree())

custom_cmap = LinearSegmentedColormap.from_list("CustomCmap", cmap, N=7)
norm = mcolors.Normalize(vmin=1, vmax=8)

sm = cm.ScalarMappable(cmap=custom_cmap, norm=norm)
cax = fig.add_axes([ax.get_position().x1+0.07,ax.get_position().y0+0.06,0.02,ax.get_position().height-0.12])
cbar = fig.colorbar(sm, cax=cax, ticks=[1.5,2.5,3.5,4.5,5.5,6.5,7.5], label='Refinement level')
cbar.ax.set_yticklabels(["4", "5", "6", "7", "8", "9", "10"])
ax.set_extent([-1,1,65.2,65.9])

legend = ax.legend(loc='upper right', fontsize=12, framealpha=0.9)
legend.set_zorder(150)
for handle in legend.legend_handles:
    handle.set_sizes([50])

label_style = {'size': 12, 'color': 'gray'}
gl = ax.gridlines(crs=ccrs.PlateCarree(), color='black', draw_labels=True, dms=True, x_inline=False, y_inline=False, zorder=200)
gl.top_labels = gl.right_labels = False
gl.xlabel_style = label_style
gl.ylabel_style = label_style
gl.rotate_labels = False
gl.xlines = gl.ylines = None
ax.gridlines(crs=ccrs.PlateCarree(), color='grey', draw_labels=False, x_inline=False, y_inline=False, zorder=0)
plt.savefig('processor_inner.png')