from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
import os
import sys
import shutil
import pathlib
import random
import cv2 as cv

from lxml import etree
import PIL
from PIL import Image
import xml.etree.ElementTree as ET
import pandas as pd
import tensorflow as tf
import io
from collections import namedtuple, OrderedDict

from global_config import *
from object_detection.utils import dataset_util
# from GEN_Annotations import *

train_data_dir = os.path.join(project_root, 'dataset/images/train/')
valid_data_dir = os.path.join(project_root, 'dataset/images/valid')
annotations_dir = os.path.join(project_root, 'dataset/annotations')
supported_fmt = ['.jpg', '.JPG']

class GEN_Annotations:
    def __init__(self, filename):
        self.root = etree.Element("annotation")
 
        child1 = etree.SubElement(self.root, "folder")
        child1.text = "VOC2007"
 
        child2 = etree.SubElement(self.root, "filename")
        child2.text = filename
 
        child3 = etree.SubElement(self.root, "source")
 
        child4 = etree.SubElement(child3, "annotation")
        child4.text = "PASCAL VOC2007"
        child5 = etree.SubElement(child3, "database")
        child5.text = "Unknown"
 
        child6 = etree.SubElement(child3, "image")
        child6.text = "flickr"
        child7 = etree.SubElement(child3, "flickrid")
        child7.text = "35435"
 
 
    def set_size(self,witdh,height):
        size = etree.SubElement(self.root, "size")
        widthn = etree.SubElement(size, "width")
        widthn.text = str(witdh)
        heightn = etree.SubElement(size, "height")
        heightn.text = str(height)

    def savefile(self,filename):
        tree = etree.ElementTree(self.root)
        tree.write(filename, pretty_print=True, xml_declaration=False, encoding='utf-8')
    def add_pic_attr(self,label,xmin,ymin,xmax,ymax):
        object = etree.SubElement(self.root, "object")
        namen = etree.SubElement(object, "name")
        namen.text = label
        bndbox = etree.SubElement(object, "bndbox")
        difficult = etree.SubElement(object, "difficult")
        difficult.text = "0"
        xminn = etree.SubElement(bndbox, "xmin")
        xminn.text = str(xmin)
        yminn = etree.SubElement(bndbox, "ymin")
        yminn.text = str(ymin)
        xmaxn = etree.SubElement(bndbox, "xmax")
        xmaxn.text = str(xmax)
        ymaxn = etree.SubElement(bndbox, "ymax")
        ymaxn.text = str(ymax)
def class_text_to_int(row_label):
    if row_label == 'fall':  # ?????????????????????????????????
        return 1
    else:
        return 0


def split(df, group):
    data = namedtuple('data', ['filename', 'object'])
    gb = df.groupby(group)
    return [data(filename, gb.get_group(x)) for filename, x in zip(gb.groups.keys(), gb.groups)]


def create_tf_example(group, path):
    with tf.gfile.GFile(os.path.join(path, '{}'.format(group.filename)), 'rb') as fid:
        encoded_jpg = fid.read()
    encoded_jpg_io = io.BytesIO(encoded_jpg)
    image = Image.open(encoded_jpg_io)
    width, height = image.size

    filename = group.filename.encode('utf8')
    image_format = b'jpg'
    xmins = []
    xmaxs = []
    ymins = []
    ymaxs = []
    classes_text = []
    classes = []

    for index, row in group.object.iterrows():
        xmins.append(row['xmin'] / width)
        xmaxs.append(row['xmax'] / width)
        ymins.append(row['ymin'] / height)
        ymaxs.append(row['ymax'] / height)
        classes_text.append(row['class'].encode('utf8'))
        classes.append(class_text_to_int(row['class']))

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_jpg),
        'image/format': dataset_util.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_example


def csv_to_record(output_path, img_path, csv_input):
    writer = tf.python_io.TFRecordWriter(output_path)
    path = os.path.join(os.getcwd(), img_path)
    examples = pd.read_csv(csv_input)
    grouped = split(examples, 'filename')
    for group in grouped:
        tf_example = create_tf_example(group, path)
        writer.write(tf_example.SerializeToString())

    writer.close()
    output_path = os.path.join(os.getcwd(), output_path)
    print('Successfully created the TFRecords: {}'.format(output_path))


def xml_to_csv(data_list):
    """???data_list?????????(??????, ??????)????????????pandas.Dataframe??????
    """
    xml_list = []
    for data in data_list:
        tree = ET.parse(data['label'])
        root = tree.getroot()
        try:
            img = Image.open(data['image'])
        except (FileNotFoundError, PIL.UnidentifiedImageError):
            print(f'??????{data["image"]}??????!')
            continue
        width, height = img.size
        img.close()
        for member in root.findall('object'):
            bndbox = member.find('bndbox')
            value = (data['image'],
                     width,
                     height,
                     member[0].text,
                     int(float(bndbox[0].text)),
                     int(float(bndbox[1].text)),
                     int(float(bndbox[2].text)),
                     int(float(bndbox[3].text))
                     )
            xml_list.append(value)
    column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df


 

 

def converge_pathes(data_path, dst_path):
    """
    ??????????????????????????????????????????????????????????????????dst_path?????????
    """
    video_files = os.listdir(data_path)
    video_files = [video_file for video_file in video_files if video_file.endswith('.mp4')]
    video_ids = [video_file.split('.')[0] for video_file in video_files]
    for video_id in video_ids:
        labeled_path = os.path.join(data_path, video_id)
        labeled_files = os.listdir(labeled_path)
        for labeled_file in labeled_files:
            src_file = os.path.join(labeled_path, labeled_file)
            dst_file = os.path.join(dst_path, video_id + '_' + labeled_file)
            shutil.copy(src_file, dst_file)
            # os.symlink(src_file, dst_file)

 
def xml_to_xml(data_list,annotations_dir):
    """???data_list?????????(??????, ??????)????????????pandas.Dataframe??????
    """
    xml_list = []
    for data in data_list:
        tree = ET.parse(data['label'])
        root = tree.getroot()
        try:
            img = Image.open(data['image'])
        except (FileNotFoundError, PIL.UnidentifiedImageError):
            print(f'??????{data["image"]}??????!')
            continue
        width, height = img.size
        img.close()
        for member in root.findall('object'):
            bndbox = member.find('bndbox')
            value = (data['image'],
                     width,
                     height,
                     member[0].text,
                     int(float(bndbox[0].text)),
                     int(float(bndbox[1].text)),
                     int(float(bndbox[2].text)),
                     int(float(bndbox[3].text))
                     )
            print("")
            filename=value[0]
            anno= GEN_Annotations(filename)
            anno.set_size(value[1],value[2])
            xmin=value[4]
            ymin=value[5]
            xmax=value[6]
            ymax=value[7]
            anno.add_pic_attr(member[0].text,xmin,ymin,xmax,ymax)
            tmp= xml_list.data['image']+".xml"
            print(tmp)
            anno.savefile(os.path.join(annotations_dir, tmp))
    #         xml_list.append(value)
    # column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
    # xml_df = pd.DataFrame(xml_list, columns=column_name)
    # return xml_df


if __name__ == '__main__':
    os.makedirs(project_root, exist_ok=True)
    os.makedirs(train_data_dir, exist_ok=True)
    os.makedirs(valid_data_dir, exist_ok=True)
    os.makedirs(annotations_dir, exist_ok=True)
    if not os.path.exists(sys.argv[1]):
        print(f'{sys.argv[1]} ?????????!')
        exit(-1)

    # ??????????????????????????????xml????????????????????????
    dataset_path = pathlib.Path(sys.argv[1])
    # ?????????????????????????????????images_labels????????????????????????????????????????????????(jpg)??????????????????(xml)
    dst_images_labels_path = os.path.join(dataset_path, 'images_labels')
    os.makedirs(dst_images_labels_path, exist_ok=True)
    # converge_pathes(dataset_path, dst_images_labels_path)

    
    # dataset_path = pathlib.Path(dst_images_labels_path)
    found_data_list = []
    for xml_file in dataset_path.glob('**/*.xml'):
        possible_images = [xml_file.with_suffix(suffix) for suffix in supported_fmt]
        supported_images = list(filter(lambda p: p.is_file(), possible_images))
        if len(supported_images) == 0:
            print(f'?????????????????????????????????`{xml_file.as_posix()}`')
            continue
        found_data_list.append({'image': supported_images[0], 'label': xml_file})

    # ????????????????????????????????????????????????????????????????????????????????????/project/train/src_repo/dataset???
    random.shuffle(found_data_list)
    train_data_count = len(found_data_list) * 4 / 5
    train_data_list = []
    valid_data_list = []
    for i, data in enumerate(found_data_list):
        if i < train_data_count:  # ?????????
            dst = train_data_dir
            data_list = train_data_list
        else:  # ?????????
            dst = valid_data_dir
            data_list = valid_data_list
        image_dst = (pathlib.Path(dst) / data['image'].name).as_posix()
        label_dst = (pathlib.Path(dst) / data['label'].name).as_posix()
#         shutil.copy(data['image'].as_posix(), image_dst)
#         shutil.copy(data['label'].as_posix(), label_dst)
        os.symlink(data['image'].as_posix(), image_dst)
        os.symlink(data['label'].as_posix(), label_dst)
        data_list.append({'image': image_dst, 'label': label_dst})

    # ???XML?????????CSV??????
    train_xml_df = xml_to_csv(train_data_list)
    train_xml_df.to_csv(os.path.join(annotations_dir, 'train_labels.csv'), index=False)
    valid_xml_df = xml_to_csv(valid_data_list)
    valid_xml_df.to_csv(os.path.join(annotations_dir, 'valid_labels.csv'), index=False)
    print('Successfully converted xml to csv.')


    # ???XML?????????xml??????
    train_xml_df = xml_to_xml(train_data_list,annotations_dir)
    valid_xml_df = xml_to_xml(valid_data_list,annotations_dir)
    print('Successfully converted xml to xml.')


    # ?????????????????????tf record??????
    csv_to_record(os.path.join(annotations_dir, 'train.record'), train_data_dir,
                  os.path.join(annotations_dir, 'train_labels.csv'))
    csv_to_record(os.path.join(annotations_dir, 'valid.record'), valid_data_dir,
                  os.path.join(annotations_dir, 'valid_labels.csv'))

    #
    with open(os.path.join(annotations_dir, 'label_map.pbtxt'), 'w') as f:
        label_map = """
item {
    id: 1
    name: "fire"
}
        """
        f.write(label_map)
