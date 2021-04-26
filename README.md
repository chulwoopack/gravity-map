# Visual Domain Knowledge-based Multimodal Zoning Textual Region Localization in Noisy Historical Document Images
This repository contains the implementation of zoning solution based on multimodal approach using our novel visual representation, *Gravity-map*. The model predicts textual regions in a set of closed polygons on a document image. The underlying CNN model used in our solution is [dhSegment](https://dhsegment.readthedocs.io/en/latest/).

## Overview of Approach
![fusion_approach](/assets/fusion_approach.png)

## Gravity-map
Step 1: Oversegment image using Voronoi-tesselation |  Step 2: Compute geometric feature, *gravity* | Step 3: Construct *Gravity-map*     
:-------------------------:|:-------------------------:|:--------------------------:|
<img src="/assets/gravity_step_1.png" width="250" height="250">  |  <img src="/assets/gravity_step_2.png" width="250" height="250"> | <img src="/assets/gravity_step_3.png" width="250" height="250">





## Resultant Samples
![resultant_sample](/assets/resultant_sample.png)
