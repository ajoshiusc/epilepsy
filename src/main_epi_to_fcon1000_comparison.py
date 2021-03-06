# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 05:39:43 2016

@author: ajoshi
"""
import sys
sys.path.append('/big_disk/ajoshi/coding_ground/cortical_parcellation/src/')

import scipy.io
import scipy as sp
import os
import numpy as np
import nibabel as nib
from dfsio import readdfs, writedfs
from surfproc import view_patch, view_patch_vtk, smooth_surf_function, face_v_conn, patch_color_attrib
from fmri_methods_sipi import rot_sub_data, reorder_labels
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter
import glob

p_dir = '/big_disk/ajoshi/HCP_data'
p_dir_ref='/big_disk/ajoshi/HCP_data/'
lst = os.listdir(p_dir)
r_factor = 3
ref_dir = os.path.join(p_dir_ref, 'reference')
nClusters = 3

ref = '196750'
print(ref + '.reduce' + str(r_factor) + '.LR_mask.mat')
fn1 = ref + '.reduce' + str(r_factor) + '.LR_mask.mat'
dfs_right = readdfs(os.path.join(p_dir_ref, 'reference', ref + '.aparc\
.a2009s.32k_fs.reduce3.right.dfs'))
dfs_right_sm = readdfs(os.path.join(p_dir_ref, 'reference', ref + '.aparc\
.a2009s.32k_fs.reduce3.very_smooth.right.dfs'))

ind_subsample = sp.arange(start=0, stop=dfs_right.labels.shape[0], step=1)
ind_rois_orig = sp.in1d(dfs_right.labels,[46,3,4,28,29,68,69,70])
ind_rois = sp.full(ind_rois_orig.shape[0], False ,dtype=bool)
ind_rois = ind_rois_orig.copy()
ind_rois[ind_subsample] = True


surf1 = dfs_right_sm
X = surf1.vertices[:, 0]
Y = surf1.vertices[:, 1]
Z = surf1.vertices[:, 2]
NumTri = surf1.faces.shape[0]
#    NumVertx = X.shape[0]
vertx_1 = surf1.faces[:, 0]
vertx_2 = surf1.faces[:, 1]
vertx_3 = surf1.faces[:, 2]
V1 = np.column_stack((X[vertx_1], Y[vertx_1], Z[vertx_1]))
V2 = np.column_stack((X[vertx_2], Y[vertx_2], Z[vertx_2]))
V3 = np.column_stack((X[vertx_3], Y[vertx_3], Z[vertx_3]))
x1 = np.zeros((NumTri))
y1 = np.zeros((NumTri))
v2_v1temp = V2-V1
x2 = np.linalg.norm(v2_v1temp, axis=1)
y2 = np.zeros((NumTri))
x3 = np.einsum('ij,ij->i', (V3-V1),
               (v2_v1temp/np.column_stack((x2, x2, x2))))
mynorm = np.cross((v2_v1temp), V3-V1, axis=1)
yunit = np.cross(mynorm, v2_v1temp, axis=1)
y3 = np.einsum('ij,ij->i', yunit, (V3-V1))/np.linalg.norm(yunit, axis=1)
sqrt_DT = (np.abs((x1*y2 - y1*x2)+(x2*y3 - y2*x3)+(x3*y1 - y3*x1)))
Ar = 0.5*(np.abs((x1*y2 - y1*x2)+(x2*y3 - y2*x3)+(x3*y1 - y3*x1)))

TC = face_v_conn(surf1)
Wt = (1.0/3.0)*(TC)
# Wt = sp.sparse.spdiags(Wt*Ar, (0), NumTri, NumTri)
surf_weight = Wt*Ar
surf1.attributes = surf_weight
surf_weight = surf_weight[:, None]
# smooth_surf_function(dfs_right_sm, Wt*Ar*0.1, a1=0, a2=1)

surf1.attributes = ind_rois
surf1 = patch_color_attrib(surf1)
#view_patch_vtk(surf1, show=1)

# sub = '110411'
# p_dir = '/home/ajoshi/data/HCP_data'
lst = os.listdir('/big_disk/ajoshi/HCP5')
rho1 = 0; rho1rot = 0; rho2 = 0; rho2rot = 0;
# lst = [lst[0]]
diffbefore = 0
diffafter = 0

sub = lst[0]

vrest1 = scipy.io.loadmat('/big_disk/ajoshi/coding_ground/brainsync/data/\
NorthShoreLIJ/0019002/fmri_tnlm_5_reduce3_v2.mat')  # h5py.File(fname1);
data = vrest1['func_right']
indx = sp.isnan(data)
data[indx] = 0


vrest = data
vrest = vrest[ind_rois, ]
m = np.mean(vrest, 1)
vrest = vrest - m[:, None]
s = np.std(vrest, 1)+1e-116
vrest1 = vrest/s[:, None]

rho1 = 0
rhorot = 1
diffafter = 0
diffbefore = 0


lst = glob.glob('/big_disk/ajoshi/fcon_1000/Beijing/sub*')
nsub = 0

#
## rand sub
#sub=lst[1]
#vrest1 = scipy.io.loadmat(sub + '/fmri_tnlm_5_reduce3_v2.mat')  # h5py.File(fname1);
#data = vrest1['func_right']
#indx = sp.isnan(data)
#data[indx] = 0
#vrest = data
##vrest = vrest[ind_rois, :vrest1.shape[1]]
#m = np.mean(vrest, 1)
#vrest = vrest - m[:, None]
#s = np.std(vrest, 1)+1e-116
#vrest1 = vrest/s[:, None]

for sub in lst:
    if not os.path.exists(sub + '/fmri_tnlm_5_reduce3_v2.mat'):
        continue
        
    vrest2 = scipy.io.loadmat(sub + '/fmri_tnlm_5_reduce3_v2.mat')  # h5py.File(fname1);
    data = vrest2['func_right']
    indx = sp.isnan(data)
    data[indx] = 0
    vrest = data
    vrest = vrest[ind_rois, :vrest1.shape[1]]
    m = np.mean(vrest, 1)
    vrest = vrest - m[:, None]
    s = np.std(vrest, 1)+1e-116
    vrest2 = vrest/s[:, None]
    
    rho1 += sp.sum(vrest1*vrest2, axis=1)/vrest1.shape[1]
    diffbefore += vrest1 - vrest2
    
    vrest2, Rot, _ = rot_sub_data(ref=vrest1, sub=vrest2,
                                  area_weight=sp.sqrt(surf_weight[ind_rois]))
    

    rho1rot += sp.sum(vrest1*vrest2,
                     axis=1)/vrest1.shape[1]
    
    diffafter += vrest1 - vrest2
    nsub += 1
    print sub

rho1rot /= nsub
rho1 /= nsub
diffafter /= nsub
diffbefore /= nsub    
#diffbefore = gaussian_filter(diffbefore,[0,5]) 

plt.imshow(sp.absolute(diffbefore), aspect='auto', clim=(0, 2.0))
plt.colorbar()
plt.savefig('dist_epi_before_fcon1000_0019002_right.pdf', dpi=300)
plt.show()

#diffafter = gaussian_filter(diffafter, [0, 50])

plt.imshow(sp.absolute(diffafter), aspect='auto', clim=(0, 2.0))
plt.colorbar()
plt.savefig('dist_epi_after_fcon1000_0019002_right.pdf', dpi=300)
plt.show()


rho_full = sp.zeros((surf1.attributes.shape[0]))
rho_full[ind_rois] = rho1
dfs_right_sm.attributes = rho_full
dfs_right_sm = patch_color_attrib(dfs_right_sm, clim=[0, 1])
view_patch_vtk(dfs_right_sm, azimuth=90, elevation=180, roll=90,
               outfile='rest_before_rot_fcon1000_0019002_right.png', show=1)

   #dfs_right_sm.attributes = sp.absolute(diffafter[:,t])
#    dfs_right_sm=patch_color_attrib(dfs_right_sm,clim=[0,1])
#    view_patch_vtk(dfs_right_sm, azimuth=90, elevation=180, roll=90, outfile='rest1motrho_full=sp.zeros((surf1.attributes.shape[0]))
rho_full[ind_rois] = rho1rot
dfs_right_sm.attributes = rho_full
dfs_right_sm = patch_color_attrib(dfs_right_sm, clim=[0, 1])
view_patch_vtk(dfs_right_sm, azimuth=90, elevation=180, roll=90,
               outfile='rest_after_rot1_fcon1000_0019002_right.png', show=1)
view_patch_vtk(dfs_right_sm, azimuth=-90, elevation=180, roll=-90,
               outfile='rest_after_rot2_fcon1000_0019002_right.png', show=1)


#plt.plot(rho1)
#
#for t in sp.arange(15,32):
#    dfs_right_sm.attributes = sp.absolute(diffafter[:,t])
#    dfs_right_sm = patch_color_attrib(dfs_right_sm,clim=[0,.6])
#    view_patch_vtk(dfs_right_sm, azimuth=90, elevation=180, roll=90, show=1)
#    
#    
diff = sp.absolute(vrest1 - vrest2)
diff_s = gaussian_filter(diff,[0,10])
#
#
#for ind in sp.arange(vrest1.shape[1]):
#    dfs_right_sm.attributes = diff_s[:,ind]
#    fname1 = 'rest_vs_motor_after_rot_%d_d.png' % ind
#    fname2 = 'rest_vs_motor_after_rot_%d_m.png' % ind
#    dfs_right_sm = patch_color_attrib(dfs_right_sm, clim=[0, 1])
#    view_patch_vtk(dfs_right_sm, azimuth=90, elevation=180, roll=90,
#                   outfile=fname1, show=0)
#    view_patch_vtk(dfs_right_sm, azimuth=-90, elevation=180, roll=-90,
#                   outfile=fname2, show=0)
#    print ind, 

