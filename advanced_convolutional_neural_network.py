import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import time

max_steps = 3000
batch_size = 128
data_dir = 'cifar-10-batches-py/'


# 读取数据
def unpickle(file):
    import pickle
    with open(data_dir + file, 'rb') as fo:
        data = pickle.load(fo, encoding='bytes')
    return data


# 将数据存到list中
def load_train_data():
    cifar_data = []
    for i in range(5):
        filename = 'data_batch_' + str(i + 1)
        cifar_data.append(unpickle(filename))
    return cifar_data


# 读取test_data
def load_test_data():
    test_data = []
    filename = 'test_batch'
    test_data.append(unpickle(filename))
    return test_data


def variable_with_weight_loss(shape, stddev, wl):
    var = tf.Variable(tf.truncated_normal(shape, stddev=stddev))
    if wl is not None:
        weight_loss = tf.multiply(tf.nn.l2_loss(var), wl, name='weight_loss')
        tf.add_to_collection('losses', weight_loss)
    return var


train_data = load_train_data()  # 读取训练数据
images_train, labels_train = train_data[0][b'data'], train_data[0][b'labels']  # 图片信息与标签信息 暂时只使用batch_0
test_data = load_test_data()  # 读取测试数据
images_test, labels_test = test_data[0][b'data'], test_data[0][b'labels']  # 图片信息与标签信息

images_train = images_train.reshape(10000, 3, 32, 32)  # reshape维度
images_train = np.rollaxis(images_train, 1, 4)  # channel last
images_test = images_test.reshape(10000, 3, 32, 32)  # reshape维度
images_test = np.rollaxis(images_test, 1, 4)  # channel last

print(images_train.shape)  # (10000,32,32,3)
print(images_test.shape)  # (10000,32,32,3)

# 定义placeholder
image_holder = tf.placeholder(tf.float32, [batch_size, 32, 32, 3])
label_holder = tf.placeholder(tf.int32, [batch_size])

weights1 = variable_with_weight_loss(shape=[5, 5, 3, 64], stddev=5e-2, wl=0.0)  # kernel1权重
kernel1 = tf.nn.conv2d(image_holder, weights1, [1, 1, 1, 1], padding='SAME')