import os
file_train = open('trainval.txt', 'w')
for xml_name in os.listdir('/home/data/19/*.xml'):
    file_train.write(xml_name[:-4] + '\n')
file_train.close()