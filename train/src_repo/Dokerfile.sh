FROM uhub.service.ucloud.cn/eagle_nest/cuda10.0-cudnn7.4.2-dev-ubuntu16.04-opencv4.1.1-tensorflow1.13-openvino2020r1-workspace

# 创建默认目录，训练过程中生成的模型文件、日志、图必须保存在这些固定目录下，训练完成后这些文件将被保存
RUN mkdir -p /project/train/src_repo && mkdir -p /project/train/result-graphs && mkdir -p /project/train/log && mkdir -p /project/train/models && mkdir -p /project/train/src_repo/pre-trained-model
#RUN  mkdir -p /project/train/result-graphs && mkdir -p /project/train/log && mkdir -p /project/train/models


# 安装训练环境依赖端软件，请根据实际情况编写自己的代码
COPY . /project/train/src_repo/

# Download pretrained ssd inception v2 coco


# RUN wget -q http://eagle-nest-backend-service.default.svc.cluster.local/storage/pre-model/tensorflow_models/models/ssd_inception_v2_coco_2018_01_28.tar.gz -O /project/train/src_repo/pre-trained-model/ssd_inception_v2_coco_2018_01_28.tar.gz \
#     && cd /project/train/src_repo/pre-trained-model/ \
#     && mkdir -p ssd_inception_v2_coco \
#     && tar zxf ssd_inception_v2_coco_2018_01_28.tar.gz -C ./ \
#     && mv ssd_inception_v2_coco_2018_01_28/* ./ssd_inception_v2_coco/
# # Download pretrained ssd mobilenet v2 coco
# RUN wget -q http://eagle-nest-backend-service.default.svc.cluster.local/storage/pre-model/tensorflow_models/models/ssd_mobilenet_v2_coco_2018_03_29.tar.gz -O /project/train/src_repo/pre-trained-model/ssd_mobilenet_v2_coco_2018_03_29.tar.gz \
#     && cd /project/train/src_repo/pre-trained-model/ \
#     && mkdir -p ssd_mobilenet_v2_coco \
#     && tar zxf ssd_mobilenet_v2_coco_2018_03_29.tar.gz -C ./ \
#     && mv ssd_mobilenet_v2_coco_2018_03_29/* ./ssd_mobilenet_v2_coco/

#安装pd 和依赖
RUN python3.6 -m pip install paddlepaddle-gpu==1.8.3.post107 -i https://mirror.baidu.com/pypi/simple
RUN python3.6 -m pip install -i https://mirrors.aliyun.com/pypi/simple -r /project/train/src_repo/requirements.txt
RUN echo "paddepaddle install successfully" 





RUN mkdir /project/test \
	&& cd /project/test \
	&& wget http://10.9.0.146:8888/group1/M00/00/B8/CgkAkl8e5faELRpqAAAAAElJ4fw594.zip \
	&& unzip  CgkAkl8e5faELRpqAAAAAElJ4fw594.zip \
	&& rm  CgkAkl8e5faELRpqAAAAAElJ4fw594.zip \
	&& cd /project/test/PaddleDetection-release-0.3 \
	&& export CUDA_VISIBLE_DEVICES=0 \
	&& python dataset/fruit/download_fruit.py \
	&& echo "start intall X2paddle" \
	&& wget http://10.9.0.146:8888/group1/M00/00/CE/CgkAkl8n_2iEDthbAAAAAF9aS9A098.zip \
	&& unzip CgkAkl8n_2iEDthbAAAAAF9aS9A098.zip \
	&& rm CgkAkl8n_2iEDthbAAAAAF9aS9A098.zip \
	&& cd X2Paddle \
	&& git checkout develop \
	&& python setup.py install \
	&& echo "intall X2paddle done" \
	&& echo "wget pre_model " \
	&& cd /project/test \
	&& mkdir -p pre_model \
	&& cd pre_model \
	&& wget http://10.9.0.146:8888/group1/M00/00/1B/CgkAa18ovhyEFP0ZAAAAAFEkuHE500.tar \
	&& tar -xvf CgkAa18ovhyEFP0ZAAAAAFEkuHE500.tar \
	&& rm CgkAa18ovhyEFP0ZAAAAAFEkuHE500.tar \
	&& cd /project/test/pre_model \
	&& wget http://10.9.0.146:8888/group1/M00/00/08/CgkAa18g61eEUKaHAAAAADHYoQU618.tar \
	&& tar -xvf CgkAa18g61eEUKaHAAAAADHYoQU618.tar \
	&& rm CgkAa18g61eEUKaHAAAAADHYoQU618.tar \
	&& cd /project/test/pre_model \
	&& wget http://10.9.0.146:8888/group1/M00/00/CC/CgkAkl8mXHOEYliiAAAAAGoUbfo112.tar \
	&& tar -xvf CgkAkl8mXHOEYliiAAAAAGoUbfo112.tar \
	&& rm CgkAkl8mXHOEYliiAAAAAGoUbfo112.tar 


#安vi装cudacnn7.6
RUN echo "run  quick start cudacnn7.6"
RUN cat /usr/local/cuda/include/cudnn.h | grep CUDNN_MAJOR -A 2 \
	&& cd /project/test \
	&& wget http://10.9.0.146:8888/group1/M00/00/05/CgkAa18fv5iESKseAAAAACZb8dk7111.gz \
	&& tar -zxvf CgkAa18fv5iESKseAAAAACZb8dk7111.gz \
	&& rm  CgkAa18fv5iESKseAAAAACZb8dk7111.gz \
	&& sudo rm -rf /usr/local/cuda/include/cudnn.h \
	&& cd cuda \
	&& cp include/cudnn.h /usr/local/cuda/include/ \
	&& cp lib64/lib* /usr/local/cuda/lib64/ \
	&& cd /usr/local/cuda/lib64/ \
	&& chmod +r libcudnn.so.7.6.0  \
	&& ln -sf libcudnn.so.7.6.0 libcudnn.so.7 \
	&& ln -sf libcudnn.so.7 libcudnn.so    \
	&& ldconfig  

RUN cat /usr/local/cuda/include/cudnn.h | grep CUDNN_MAJOR -A 2
RUN echo "cudnn7.6.0 -cuda10 install successfully"



#	&& python -u tools/train.py -c configs/yolov3_mobilenet_v1_fruit.yml --eval



#修改测试代码输出模式路径

