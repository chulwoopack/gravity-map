# Your location should be at /compactness

# otsu binarization
jpg_files=$(find /home/toor/Documents/jiyoungl/jupyter/MAKE/dataset/PRImA_Layout_Analysis_Dataset/images_bin -iname "*.jpg")

num=0
total=$(echo "$jpg_files" | wc -l)
echo "There are $total files to be converted."

for f in $jpg_files; do file_name="${f##*/}";num=`expr $num + 1`;echo "Converting $f, $num/$total";python otsu.py -imgpath "$f" -save "/home/toor/Documents/jiyoungl/jupyter/MAKE/dataset/PRImA_Layout_Analysis_Dataset/images_bin/${file_name%.*}.tif";done


# convert to tiff
tif_files=$(find /home/toor/Documents/jiyoungl/jupyter/MAKE/dataset/PRImA_Layout_Analysis_Dataset/images_bin -iname "*.tif")

num=0
total=$(echo "$tif_files" | wc -l)
echo "There are $total files to be converted."

for f in $tif_files; do file_name="${f##*/}";num=`expr $num + 1`;echo "Converting $f, $num/$total";convert "$f" "/home/toor/Documents/jiyoungl/jupyter/MAKE/dataset/PRImA_Layout_Analysis_Dataset/images_bin/${file_name%.*}.tiff";done


# Voronoi-segmentation
tif_files=$(find /home/toor/Documents/jiyoungl/jupyter/MAKE/dataset/PRImA_Layout_Analysis_Dataset/images_bin -iname "*.tiff")

num=0
total=$(echo "$tif_files" | wc -l)
echo "There are $total files to be converted."

for f in $tif_files; do file_name="${f##*/}";num=`expr $num + 1`;echo "Converting $f, $num/$total";./be "$f";cp ./data/linesegments/line "/home/toor/Documents/jiyoungl/jupyter/MAKE/dataset/PRImA_Layout_Analysis_Dataset/images_line/${file_name%.*}_line";done



# Gravity
tif_files=$(find /home/toor/Documents/jiyoungl/jupyter/MAKE/dataset/PRImA_Layout_Analysis_Dataset/images_bin -iname "*.tiff")

num=0
total=$(echo "$tif_files" | wc -l)
echo "There are $total binary image files."

for f in $tif_files; do file_name="${f##*/}";num=`expr $num + 1`;echo "Converting $f, $num/$total";python gravity.py -binimgpath "$f" -linepath "/home/toor/Documents/jiyoungl/jupyter/MAKE/dataset/PRImA_Layout_Analysis_Dataset/images_line/${file_name%.*}_line" -save "/home/toor/Documents/jiyoungl/jupyter/MAKE/dataset/PRImA_Layout_Analysis_Dataset/images_gravity/${file_name%.*}.png";done