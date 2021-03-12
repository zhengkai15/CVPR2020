for i in `ls /project/train/src_repo/dataset/images/valid/*.jpg`
do 
python -u tools/infer.py -c configs/yolov4/yolov4_cspdarknet_voc.yml \
              --infer_img=${i} \
              --output_dir=/project/output/infer_output
done