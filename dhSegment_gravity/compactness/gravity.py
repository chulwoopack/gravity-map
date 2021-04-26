import json
import cv2
import numpy as np
import os
#import matplotlib.pyplot as plt
from tqdm import tqdm
#%matplotlib notebook
import pickle

from sklearn import preprocessing

import argparse

parser = argparse.ArgumentParser(description='Gravity-map')
# parser.add_argument('-oriimgpath', type=str, required=True,
#                    help='a path to the original input image')

parser.add_argument('-binimgpath', type=str, required=True,
                   help='a path to the binary input image')

parser.add_argument('-linepath', type=str, required=True,
                   help='a path to the linesegments')


parser.add_argument('-save', type=str, required=True,
                   help='a path to the output npy')

args = parser.parse_args()

# ORI_IMAGE_PATH = args.oriimgpath
BIN_IMAGE_PATH = args.binimgpath
LINE_PATH  = args.linepath
SAVE_PATH  = args.save


CONNECTIVITY = 4
MIN_CC_SIZE = 15
HEIGHT_RATIO = 0.8
WIDTH_RATIO = 0.2


def euclideanDistance(coordinate1, coordinate2):
    return pow(pow(coordinate1[0] - coordinate2[0], 2) + pow(coordinate1[1] - coordinate2[1], 2), .5)

"""Read binary image"""
img    = cv2.imread(BIN_IMAGE_PATH)
assert img is not None
h,w    = img.shape[0:2]

"""Read original image"""
# img_ori = cv2.imread(ORI_IMAGE_PATH)
# assert img_ori is not None


"""Read & Label linesegments based on overlapness on GT"""
img_voronoi_mask = np.ones([h,w]).astype(np.uint8)
vo_ridges = {}
img_voronoi_mask_test = 255*(np.ones([h,w]).astype(np.uint8))
img_cc_mask_test = -1*(np.ones([h,w]).astype(np.uint8))

with open(LINE_PATH, "r") as fp:
    for idx,line in enumerate(fp):
        vo_label = 0
        cs,ce,rs,re, lab1_cs,lab1_ce,lab1_rs,lab1_re, lab2_cs,lab2_ce,lab2_rs,lab2_re,lab1,lab2 = (int(x) for x in line.split())
        left,right,top,down = min(cs,ce),max(cs,ce),min(rs,re),max(rs,re)

        # draw voronoi-ridge
        cv2.line(img_voronoi_mask,(cs,rs),(ce,re),(0,0,0),2)
        
        # draw cc
        img_cc_mask_test[lab1_rs:lab1_re,lab1_cs:lab1_ce] = lab1
        img_cc_mask_test[lab1_rs:lab1_re,lab1_cs:lab1_ce] = lab2
        
        
        # Save voronoi-ridge info
        vo_ridges[idx] = {}
        vo_ridges[idx]['points'] = [cs,ce,rs,re, lab1_cs,lab1_ce,lab1_rs,lab1_re, lab2_cs,lab2_ce,lab2_rs,lab2_re]
        vo_ridges[idx]['ext_pts'] = [left,right,top,down]
        vo_ridges[idx]['label'] = vo_label
        
#print("Total {} voronoi-ridges are found.".format(idx+1))

# Show Voronoi_ridges
#plt.figure()
#plt.imshow(img_voronoi_mask,cmap='gray')
#plt.show()


###
# GRAVITY-MAP
###
cc_centroid_map = np.zeros((h,w)).astype(np.uint8)
cc_id_map       = np.zeros((h,w)).astype(int)
vo_centroid_map = np.zeros((h,w)).astype(np.uint8)

# CC centroid map
cc_map_roi  = img[:,:,0]
cc_num_labels, cc_labels, cc_stats, cc_centroids = cv2.connectedComponentsWithStats(np.invert(cc_map_roi), CONNECTIVITY, cv2.CV_32S)

for idx,cc_centroid in enumerate(cc_centroids):
    if(idx==0):
        continue
    if(cc_stats[idx,4]<MIN_CC_SIZE):
        #cc_labels[cc_labels==idx] = 0
        continue
    r,c = int(cc_centroid[0]),int(cc_centroid[1])
    cc_centroid_map[c,r] = 255
    cc_id_map[c,r] = idx

# Voronoi centroid map
vo_num_labels, vo_labels, vo_stats, vo_centroids = cv2.connectedComponentsWithStats(img_voronoi_mask, CONNECTIVITY, cv2.CV_32S)

for idx,vo_centroid in enumerate(vo_centroids):
    if(idx==0):
        continue
    r,c = int(vo_centroid[0]),int(vo_centroid[1])
    vo_centroid_map[c,r] = 255




"""OLD"""
"""ACTUAL GRAVITY CALCULATION"""
significant_cells = np.copy(vo_labels)
zone_cells = np.copy(vo_labels)
zone_cells[zone_cells==0] = -1  # Assign -1 to edges, which will be reverted to 255 later.
hog_cells = np.copy(vo_labels)
dists = []
for idx in tqdm(range(1,vo_num_labels)):
    #idx = 90

    # Find centroid of Voronoi-cell
    vo_coord = vo_centroids[idx][1].astype(int),vo_centroids[idx][0].astype(int)
    #print(vo_coord)
    
    # Set scope
    new_c,new_r,new_w,new_h = vo_stats[idx,0:4]
        
    # Find centroid of CC corresponding to Voronoi-cell
    canvas = np.zeros((new_h,new_w))+idx
    roi = (canvas == vo_labels[new_r:new_r+new_h,new_c:new_c+new_w]).astype(np.uint8)
    cc_coord_r,cc_coord_c = np.where(roi*cc_centroid_map[new_r:new_r+new_h,new_c:new_c+new_w]==255)
    # NOTE: This case handles when no CC is inside Voronoi-cell due to the size of CC is too small..
    if(cc_coord_r.size * cc_coord_c.size is 0):
        significant_cells[new_r:new_r+new_h,new_c:new_c+new_w][significant_cells[new_r:new_r+new_h,new_c:new_c+new_w]==idx] = 0
        zone_cells[new_r:new_r+new_h,new_c:new_c+new_w][zone_cells[new_r:new_r+new_h,new_c:new_c+new_w]==idx] = 0
        #hog_cells[new_r:new_r+new_h,new_c:new_c+new_w][hog_cells[new_r:new_r+new_h,new_c:new_c+new_w]==idx] = 0
        continue
    cc_coord = cc_coord_r+new_r,cc_coord_c+new_c
    #print(cc_coord)

    # NEW FEATURE
    ids = cc_id_map[cc_coord]
    #width_ratio = cc_stats[ids][0,2]/vo_stats[idx][2]
    #height_ratio = cc_stats[ids][0,3]/vo_stats[idx][3]
    area_ratio  = abs(cc_stats[ids][0,4]-vo_stats[idx][4])
    
    # Calculate distance
    #if(height_ratio>HEIGHT_RATIO):
    #    dist = 255
    #else:
    dist = min(np.mean(euclideanDistance(cc_coord,vo_coord)[0])*(area_ratio//4),4096)
    
    dists.append(dist)
    
    # Find significant Voronoi-cells based on gravity
    significant_cells[new_r:new_r+new_h,new_c:new_c+new_w][significant_cells[new_r:new_r+new_h,new_c:new_c+new_w]==idx] = dist
    zone_cells[new_r:new_r+new_h,new_c:new_c+new_w][zone_cells[new_r:new_r+new_h,new_c:new_c+new_w]==idx] = dist
    

min_max_scaler = preprocessing.MinMaxScaler()
significant_cells_minmax = min_max_scaler.fit_transform(significant_cells)

significant_cells_minmax = np.expand_dims(significant_cells_minmax,axis=2)
significant_cells_minmax = (255*significant_cells_minmax).astype(np.uint8)

# gravity = np.dstack((img_ori,significant_cells_minmax))

#np.save(SAVE_PATH, significant_cells_minmax)

cv2.imwrite(SAVE_PATH, significant_cells_minmax)

# with open(SAVE_PATH, "wb") as f_out:
#     pickle.dump(gravity, f_out)



