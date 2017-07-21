# ||AUM||
import scipy.io
import scipy as sp
import numpy as np
from fmri_methods_sipi import rot_sub_data
from surfproc import view_patch_vtk, patch_color_attrib
from dfsio import readdfs
import os
import matplotlib.pyplot as plt
from brainsync import normalizeData, brainSync


p_dir = '/big_disk/ajoshi/HCP_data/data'
p_dir_ref = '/big_disk/ajoshi/HCP_data'
lst = os.listdir(p_dir)

r_factor = 3
ref_dir = os.path.join(p_dir_ref, 'reference')
nClusters = 30

ref = '196750'
print(ref + '.reduce' + str(r_factor) + '.LR_mask.mat')
fn1 = ref + '.reduce' + str(r_factor) + '.LR_mask.mat'
fname1 = os.path.join(ref_dir, fn1)
msk = scipy.io.loadmat(fname1)  # h5py.File(fname1);
dfs_left = readdfs(os.path.join(p_dir_ref, 'reference', ref + '.aparc.\
a2009s.32k_fs.reduce3.left.dfs'))
dfs_left_sm = readdfs(os.path.join(p_dir_ref, 'reference', ref + '.aparc.\
a2009s.32k_fs.reduce3.very_smooth.left.dfs'))

# view_patch_vtk(dfs_left_sm)
rho_rho = []
rho_all = []
#lst=lst[:1]
labs_all = sp.zeros((len(dfs_left.labels), len(lst)))
sub = lst[1]
data = scipy.io.loadmat(os.path.join(p_dir, sub, sub + '.rfMRI_REST1_LR.\
reduce3.ftdata.NLM_11N_hvar_25.mat'))
LR_flag = msk['LR_flag']
LR_flag = np.squeeze(LR_flag) != 0
data = data['ftdata_NLM']
temp = data[LR_flag, :]
d1 = temp.T

sub = lst[2]
data = scipy.io.loadmat(os.path.join(p_dir, sub, sub + '.rfMRI_REST1_LR.\
reduce3.ftdata.NLM_11N_hvar_25.mat'))
LR_flag = msk['LR_flag']
LR_flag = np.squeeze(LR_flag) != 0
data = data['ftdata_NLM']
temp = data[LR_flag, :]

d2 = temp.T

ind = 0
IntV = range(20, 1200, 10)
rms = sp.zeros(len(IntV))
for len1 in IntV:
    sub_data1, _, _ = normalizeData(d1[:len1, :])
    sub_data2, _, _ = normalizeData(d2[:len1, :])
    s = sp.std(sub_data2, axis=0)
    sub_data1 = sub_data1[:, s > 1e-2]
    sub_data2 = sub_data2[:, s > 1e-2]
    sub_data2_sync, Rot = brainSync(X=sub_data1, Y=sub_data2)
    rms[ind] = sp.linalg.norm(sub_data2_sync - sub_data1)/((sp.linalg.norm(
            sub_data2)**0.5)*(sp.linalg.norm(sub_data1)**0.5))
    ind += 1
    print len1

plt.plot(IntV, rms)
plt.ylim(ymax = 1, ymin = 0.45)
plt.savefig('sync_vs_len_diff_sub.pdf')
plt.show()

