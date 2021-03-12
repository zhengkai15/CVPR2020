#!/bin/bash
project_root_dir=/project/train/src_repo
dataset_dir=/home/data/19
log_file=/project/train/log/log.txt
mkdir -p  /project/train/log
touch /project/train/log/log.txt
mkdir -p /project/train/models/final
mkdir -p /project/train/result-graphs


echo "----------Preparing backup----------" 
mkdir -p /project/test/beckup
cp -r /project/test/models/faster_rcnn_r50_fpn_1x /project/test/beckup
cp -r /project/test/models/yolov4_cspdarknet_voc /project/test/beckup


echo "----------Preparing 恢复----------" 
rm -r ${project_root_dir}/dataset 
rm -r /project/test/models/


rm -r /project/test/faster_rcnn_r50_fpn_1x
rm -r /project/test/yolov4_cspdarknet_voc
rm /project/test/infer_output/*
rm -r  /project/train/src_repo/PaddleDetection-release-0.3/dataset/voc/VOCdevkit/VOC2007/Annotations
rm -r  /project/train/src_repo/PaddleDetection-release-0.3/dataset/voc/VOCdevkit/VOC2007/JPEGImages
# rm -r /project/test/fa
echo "----------Converting dataset----------" \
&& python3 -u ${project_root_dir}/convert_dataset.py  ${dataset_dir} | tee -a ${log_file} 

# 将数据移动到训练文件夹
echo "----------mkdir  and cp file starting----------" 
mkdir -p /project/train/src_repo/PaddleDetection-release-0.3/dataset/voc/VOCdevkit/VOC2007/JPEGImages \
&& mkdir -p /project/train/src_repo/PaddleDetection-release-0.3/dataset/voc/VOCdevkit/VOC2007/Annotations \
&& mkdir -p /project/train/src_repo/PaddleDetection-release-0.3/dataset/voc/VOCdevkit/VOC2007/ImageSets/Main \
&& cp /project/train/src_repo/dataset/annotations/*.xml   /project/train/src_repo/PaddleDetection-release-0.3/dataset/voc/VOCdevkit/VOC2007/Annotations 

# && cp ${dataset_dir}/*.jpg   /project/train/src_repo/PaddleDetection-release-0.3/dataset/voc/VOCdevkit/VOC2007/JPEGImages \
# 这里好像不能ln *.jpg
ln -s ${dataset_dir}/*   /project/train/src_repo/PaddleDetection-release-0.3/dataset/voc/VOCdevkit/VOC2007/JPEGImages 
echo "----------mkdir and cp file done----------"  
# 建立list_1
echo "----------getlist starting----------"  \
&& cd /project/train/src_repo/PaddleDetection-release-0.3/dataset/voc/VOCdevkit/VOC2007/ImageSets/Main/ \
&& python getlist.py 
rm -r /project/train/src_repo/dataset/images
# 建立list_2
echo "----------create_list starting----------"  \
&& cd  /project/train/src_repo/PaddleDetection-release-0.3 \
&& cd /project/train/src_repo/PaddleDetection-release-0.3/dataset/voc/ \
&& python create_list.py \
&& cd  /project/train/src_repo/PaddleDetection-release-0.3 \
&& echo "----------create_list done----------" \
&& echo "----------Start training----------" \
&& export CUDA_VISIBLE_DEVICES=0 
# && python -u tools/train.py -c configs/faster_rcnn_r50_fpn_1x.yml  \
# && echo "----------Training Done----------" \
# && echo "----------Start varlid----------" 
# cp -r /project/train/models/faster_rcnn_r50_fpn_1x /project/test/
# for i in `ls /project/train/src_repo/dataset/images/valid/*.jpg`
# do 
# python -u tools/infer.py -c configs/faster_rcnn_r50_fpn_1x.yml \
#               --infer_img=${i} \
#               --output_dir=/project/output/infer_output/
# done
# echo "----------Varlid Done----------"

# && echo "----------Start export_model----------" 
# python -u tools/export_model.py -c configs/faster_rcnn_r50_fpn_1x.yml \
#               --output_dir=/project/output/faster_rcnn_r50_fpn_1x/
# echo "----------export_model Done----------"


python -u tools/train.py -c configs/yolov4/yolov4_cspdarknet_voc.yml | tee -a ${log_file} 
echo "----------Training Done----------"
echo "----------Start export_model----------" 
python -u tools/export_model.py -c configs/yolov4/yolov4_cspdarknet_voc.yml \
              --output_dir=/project/output/
echo "----------export_model Done----------"
echo "----------Start to onnx ----------" 
x2paddle --framework=paddle2onnx --model=/project/output/yolov4_cspdarknet_voc/ --onnx_opset=11 --save_dir=/project/output/onnx_model  
echo "----------to onnx done----------" 
cp /project/output/onnx_model/* /project/train/models/final/
echo "----------cp to /project/train/models/final/ done----------" 
