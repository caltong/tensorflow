from datetime import datetime
import math
import time
import tensorflow as tf

batch_size = 32
num_batches = 100


# 显示网络每层结构函数
def print_activations(t):
    print(t.op.name, ' ', t.get_shape().as_list())


# 结构
def inference(images):
    parameters = []

    with tf.name_scope('conv1') as scope:
        kernel = tf.Variable(tf.truncated_normal([11, 11, 3, 64], dtype=tf.float32, stddev=1e-1), name='weights')
        conv = tf.nn.conv2d(images, kernel, [1, 4, 4, 1], padding='SAME')
        biases = tf.Variable(tf.constant(0.0, shape=[64], dtype=tf.float32), trainable=True, name='biases')
        bias = tf.nn.bias_add(conv, biases)
        conv1 = tf.nn.relu(bias, name=scope)
        print_activations(conv1)  # 输出conv1结构
        parameters = parameters + [kernel, biases]  # 存入parameters list

    lrn1 = tf.nn.lrn(conv1, 4, bias=1.0, alpha=0.001 / 9, beta=0.75, name='lrn1')
    pool1 = tf.nn.max_pool(lrn1, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding='VALID', name='pool1')
    print_activations(pool1)  # 输出pool1结构

    with tf.name_scope('conv2') as scope:
        kernel = tf.Variable(tf.truncated_normal([5, 5, 64, 192], dtype=tf.float32, stddev=1e-1), name='weights')
        conv = tf.nn.conv2d(pool1, kernel, [1, 1, 1, 1], padding='SAME')
        biases = tf.Variable(tf.constant(0.0, shape=[192], dtype=tf.float32), trainable=True, name='biases')
        bias = tf.nn.bias_add(conv, biases)
        conv2 = tf.nn.relu(bias, name=scope)
        print_activations(conv2)
        parameters = parameters + [kernel, biases]

    lrn2 = tf.nn.lrn(conv2, 4, bias=1.0, alpha=0.001 / 9, beta=0.75, name='lrn2')
    pool2 = tf.nn.max_pool(lrn2, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding='VALID', name='pool2')
    print_activations(pool2)

    with tf.name_scope('conv3') as scope:
        kernel = tf.Variable(tf.truncated_normal([3, 3, 192, 384], dtype=tf.float32, stddev=1e-1), name='weights')
        conv = tf.nn.conv2d(pool2, kernel, [1, 1, 1, 1], padding='SAME')
        biases = tf.Variable(tf.constant(0.0, shape=[384], dtype=tf.float32), trainable=True, name='biases')
        bias = tf.nn.bias_add(conv, biases)
        conv3 = tf.nn.relu(bias, name=scope)
        parameters = parameters + [kernel, biases]
        print_activations(conv3)

    with tf.name_scope('conv4') as scope:
        kernel = tf.Variable(tf.truncated_normal([3, 3, 384, 256], dtype=tf.float32, stddev=1e-1), name='weights')
        conv = tf.nn.conv2d(conv3, kernel, [1, 1, 1, 1], padding='SAME')
        biases = tf.Variable(tf.constant(0.0, shape=[256], dtype=tf.float32), trainable=True, name='biases')
        bias = tf.nn.bias_add(conv, biases)
        conv4 = tf.nn.relu(bias, name=scope)
        parameters = parameters + [kernel, biases]
        print_activations(conv4)

    with tf.name_scope('conv5') as scope:
        kernel = tf.Variable(tf.truncated_normal([3, 3, 256, 256], dtype=tf.float32), trainable=True, name='biases')
        conv = tf.nn.conv2d(conv4, kernel, [1, 1, 1, 1], padding='SAME')
        biases = tf.Variable(tf.constant(0.0, shape=[256], dtype=tf.float32), trainable=True)
        bias = tf.nn.bias_add(conv, biases)
        conv5 = tf.nn.relu(bias, name=scope)
        parameters = parameters + [kernel, biases]
        print_activations(conv5)

    pool5 = tf.nn.max_pool(conv5, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding='VALID', name='pool5')
    print_activations(pool5)

    return pool5, parameters


# 评估运算时间
def time_tensorflow_run(session, target, info_string):
    num_steps_burn_in = 10  # 预热
    total_duration = 0.0
    total_duration_squared = 0.0

    for i in range(num_batches + num_steps_burn_in):
        start_time = time.time()
        _ = session.run(target)
        duration = time.time() - start_time
        if i >= num_steps_burn_in:  # 预热 排除显存加载 cache命中问题
            if not i % 10:
                print('%s: step %d, duration = %.3f' % (datetime.now(), i - num_steps_burn_in, duration))
            total_duration = total_duration + duration
            total_duration_squared = total_duration_squared + duration * duration

    mn = total_duration / num_batches
    vr = total_duration_squared / num_batches - mn * mn
    sd = math.sqrt(vr)

    print('%s:%s across %d steps, %.3f +/- %.3f sec / batch' % (datetime.now(), info_string, num_batches, mn, sd))


def run_benchmark():
    with tf.Graph().as_default():
        image_size = 224  # 图片尺寸
        images = tf.Variable(
            tf.random_normal([batch_size, image_size, image_size, 3], dtype=tf.float32, stddev=1e-1))  # 随机生成数据

        pool5, parameters = inference(images)

        init = tf.global_variables_initializer()
        sess = tf.Session()
        sess.run(init)

        time_tensorflow_run(sess, pool5, "Forward")  # 前向预测耗时

        objective = tf.nn.l2_loss(pool5)  # 模拟pool5 的 L2 损失为优化目标
        grad = tf.gradients(objective, parameters)  # 求这个优化目标各参数的梯度，以此来模拟训练时的耗时
        time_tensorflow_run(sess, grad, "Forward-backward")  # 模拟训练时耗时


run_benchmark()
