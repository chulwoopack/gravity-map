# Voronoi-based Document Layout Analysis
This repo contains Voronoi-based Document Layout Analysis code (originally worked by K. Kise and modified by Faisal Shafait). 

## Installation
This program requires `libtiff`.
To install this program, please run `make`. You will find `be` in the current directory if the compilation is successful.

## How to Use
This program requires a single argument is required:
an input binary image (with sunraster or TIFF format).
```console
user@local:~$ ./be <input image>
```
**Note** For more optional arguments (e.g., sampling rate), please simply enter `be`.
```console
user@local:~$ ./be

Usage : be <input_file>
input_file  : a binary doc. image (sun raster or tiff format)
options : [-<argument> (<data type>)] : <meaning>:<<default value>>
[-sr (int)]  : sampling rate  :<13>
[-nm (int)]  : max size (area) of noise CC  :<15>
[-fr (float)]: threshold setting param. for Td2 :<0.340>
[-ta (int)]  : threshold value for area ratio :<40>
[-sw (int)]  : size of smoothing window of distance :<2>
[-dparam]  : display parameters :<NO>
[-ddetail] : display detailed outputs :<NO>
[-djson] : display json format outputs  :<NO>
```
Once the program runs successfully, you will find an output file (a list of coordinates of line segments) under `data/linesegments`.

For visualizing the segmentation result, you should run the following:
```console
user@local:~$ ./drawing/dl -i <input image> -l <line segment> -o <output file>
```
**Note** Similarly as above, for more optional arguments (e.g., line width), please simply enter `dl`.

## References
[1] Voronoi page segmentation algorithm:
       K.Kise, A.Sato and M.Iwata,
       Segmentation of Page Images Using the Area Voronoi Diagram,
       Computer Vision and Image Understanding,
       Vol.70, No.3, pp.370-382, Academic Press, 1998.6.

[2] Color coding format and evaluation of Voronoi algorithm:
       F. Shafait, D. Keysers, T.M. Breuel,
       Performance Evaluation and Benchmarking of Six Page Segmentation Algorithms
       IEEE Transactions on Pattern Analysis and Machine Intelligence
       Vol.30, No.6, pp.941-954, June 2008

## Comments, Bug Reports
Please send them to [chulwoo.pack@huskers.unl.edu](mailto:chulwoo.pack@huskers.unl.edu)

## Note

This program contains the following public domain code as its parts:

(1) Voronoi page segmentation code by K. Kise.
  www.science.uva.nl/research/dlia/software/kise

   The note in Kise's Voronoi page segmentation code's README file is as follows:

   "The authors of this software are Akinori Sato, Motoi Iwata
   and Koichi Kise except for the parts listed in (2).
   Copyright (c) 1999 Akinori Sato, Motoi Iwata and Koichi Kise.
   Permission to use, copy, modify, and distribute this software for any
   purpose without fee is hereby granted, provided that this entire notice
   is included in all copies of any software which is or includes a copy
   or modification of this software and in all copies of the supporting
   documentation for such software.
   THIS SOFTWARE IS BEING PROVIDED "AS IS",
   WITHOUT ANY EXPRESS OR IMPLIED WARRANTY. "

(2) Steve Fortune's Voronoi program: sweep2
  
  http://netlib.bell-labs.com/netlib/voronoi/index.html

   
