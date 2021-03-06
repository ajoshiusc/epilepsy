"""
Created on Thu Aug  4 05:39:43 2016

@author: ajoshi
"""
import scipy.io as spio
import scipy as sp
import os
import numpy as np
import nibabel as nib
from dfsio import readdfs, writedfs
from surfproc import view_patch, view_patch_vtk, smooth_surf_function, face_v_conn, patch_color_attrib
from fmri_methods_sipi import rot_sub_data, reorder_labels
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter
from brainsync import brainSync, normalizeData
from scipy.ndimage.filters import gaussian_filter

p_dir = '/big_disk/ajoshi/HCP_data'
p_dir_ref = '/big_disk/ajoshi/HCP_data/'
lst = os.listdir(p_dir)
r_factor = 3
ref_dir = os.path.join(p_dir_ref, 'reference')
nClusters = 3

ref = '196750'  # '100307'
print(ref + '.reduce' + str(r_factor) + '.LR_mask.mat')
fn1 = ref + '.reduce' + str(r_factor) + '.LR_mask.mat'
fname1 = os.path.join(ref_dir, fn1)

msk = spio.loadmat(fname1)  # h5py.File(fname1);

dfs_right = readdfs(os.path.join(p_dir_ref, 'reference', ref + '.aparc\
.a2009s.32k_fs.reduce3.right.dfs'))

dfs_right_sm = readdfs(os.path.join(p_dir_ref, 'reference', ref + '.aparc\
.a2009s.32k_fs.reduce3.very_smooth.right.dfs'))

sub = lst[0]

# dat = scipy.io.loadmat('/big_disk/ajoshi/with_andrew/100307/100307.\
# tfMRI_MOTOR_LR.reduce3.ftdata.NLM_11N_hvar_5.mat')
#fmotor = dat['ftdata_NLM'].T
# fmotor,_,_=normalizeData(fmotor)

dat = spio.loadmat('/big_disk/ajoshi/with_andrew/100307/100307.\
rfMRI_REST1_RL.reduce3.ftdata.NLM_11N_hvar_5.mat')
fmotor = dat['ftdata_NLM'].T
fmotor = fmotor[:284, :]
fmotor, _, _ = normalizeData(fmotor)


dat = spio.loadmat('/big_disk/ajoshi/with_andrew/100307/100307.\
rfMRI_REST1_LR.reduce3.ftdata.NLM_11N_hvar_5.mat')
frest = dat['ftdata_NLM'].T
frest = frest[:fmotor.shape[0], :]
frest, _, _ = normalizeData(frest)

diffbefore = fmotor - frest

fmotor, _ = brainSync(frest, fmotor)

diffafter = fmotor - frest

plt.imshow(sp.absolute(diffbefore), aspect='auto', clim=(0, 0.1))

plt.colorbar()
plt.savefig('dist_motor_before.pdf', dpi=300)
plt.show()
plt.figure()
plt.imshow(sp.absolute(diffafter), aspect='auto', clim=(0, .1))
plt.colorbar()
plt.savefig('dist_motor_after.pdf', dpi=300)
plt.show()
#diffafter = gaussian_filter(diffafter, [2, 0])
nV = len(dfs_right_sm.vertices)
dfs_right_sm.attributes = np.sum(frest*fmotor,axis=0)
dfs_right_sm.attributes=dfs_right_sm.attributes[nV:]
fname1 = 'rest_after_1.png'
fname2 = 'rest_after_2.png'
dfs_right_sm = patch_color_attrib(dfs_right_sm, clim=[0.8, 1])
view_patch_vtk(dfs_right_sm, azimuth=90, elevation=180, roll=90,
               outfile=fname1, show=0)
view_patch_vtk(dfs_right_sm, azimuth=-90, elevation=180, roll=-90,
               outfile=fname2, show=0)

for ind in sp.arange(frest.shape[0]):
    dfs_right_sm.attributes = sp.absolute(diffafter[ind, (nV):])
    fname1 = 'rest_after_rot_right_%d_d.png' % ind
    fname2 = 'rest_after_rot_right_%d_m.png' % ind
    dfs_right_sm = patch_color_attrib(dfs_right_sm, clim=[0.8, 1])
    view_patch_vtk(dfs_right_sm, azimuth=90, elevation=180, roll=90,
                   outfile=fname1, show=0)
    view_patch_vtk(dfs_right_sm, azimuth=-90, elevation=180, roll=-90,
                   outfile=fname2, show=0)
    print(ind,)
#
