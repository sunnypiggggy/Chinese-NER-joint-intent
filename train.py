# import os
# os.environ['CUDA_DEVICE-ORDER'] = 'PCI_BUS_ID'


# os.environ['CUDA_VISIBLE_DEVICES'] = '6'


import time
import helper
import argparse
import tensorflow as tf
from BILSTM_CRF import BILSTM_CRF

# python train.py train.in model -v validation.in -c char_emb -e 10 -g 2

parser = argparse.ArgumentParser()
parser.add_argument("--train_path", default="process_process_data/final_test_BME",help="the path of the train file")
parser.add_argument("--train_tag_path",default="processed_data/test_char_label", help="the path of the train tag file")
parser.add_argument("--train_intent_path", default="process_process_data/intent_test", help="the path of the train intent file")
parser.add_argument("--save_path", default="predict_output", help="the path of the saved model")
parser.add_argument("--val_path", help="the path of the validation file", default="process_process_data/final_test_BME")
parser.add_argument("--val_tag_path", help="the path of the valid tag file", default="processed_data/test_char_label")
parser.add_argument("--val_intent_path", help="the path of the valid intent file", default="process_process_data/intent_test")
parser.add_argument("--epoch", help="the number of epoch", default=20, type=int)
parser.add_argument("--char_emb", help="the char embedding file", default="vectors.txt")
# parser.add_argument("--gpu", help="the id of gpu, the default is 0", default=0, type=int)

args = parser.parse_args()

train_path = args.train_path
save_path = args.save_path
val_path = args.val_path
val_tag_path = args.val_tag_path
num_epochs = args.epoch
emb_path = args.char_emb
# gpu_config = "/gpu:"+str(args.gpu)
num_steps = 30 # it must consist with the test

start_time = time.time()
print("preparing train and validation data")

pathin_tag = args.train_tag_path
pathin_intent =  args.train_intent_path
pathval_intent =  args.val_intent_path
X_train, y_train, X_val, y_val, X_tag_train, X_tag_val, y_intent_train, y_intent_val = helper.get_train(train_path=train_path, val_path=val_path, input_tag_path=pathin_tag, val_tag_path=val_tag_path, input_intent_path=pathin_intent, valid_intent_path=pathval_intent, seq_max_len=num_steps)

char2id, id2char = helper.loadMap("meta_data/char2id")
label2id, id2label = helper.loadMap("meta_data/label2id")
intentlabel2id, id2intentlabel = helper.loadMap("meta_data/intentlabel2id")
num_chars = len(id2char.keys())
num_classes = len(id2label.keys())
num_intent_classes = len(id2intentlabel.keys())
if emb_path != None:
    embedding_matrix = helper.getEmbedding(emb_path)
else:
    embedding_matrix = None

#pathin_tag = "./song_train_char.100"
#input_tag = get_input_tag(in_tag)

print(save_path)

print("building model")
import os
# config = tf.ConfigProto(allow_soft_placement=True)
tf.reset_default_graph()
with tf.Graph().as_default():
    # with tf.Session(config=config) as sess:
    # with tf.device(gpu_config):
        initializer = tf.random_uniform_initializer(-0.1, 0.1)
        with tf.variable_scope("model", reuse=None, initializer=initializer):
            model = BILSTM_CRF(num_chars=num_chars, num_classes=num_classes, num_intent_classes=num_intent_classes,
                               num_steps=num_steps, num_epochs=num_epochs, embedding_matrix=embedding_matrix,
                               is_training=True) #TODO is_training

        with tf.variable_scope("model", reuse=tf.AUTO_REUSE, initializer=initializer):
            model_dev = BILSTM_CRF(num_chars=num_chars, num_classes=num_classes, num_intent_classes=num_intent_classes,
                               num_steps=num_steps, num_epochs=num_epochs, embedding_matrix=embedding_matrix,
                               is_training=False) #TODO is_training

        if os.path.exists("predict_output"):
            test_value = tf.Variable(0, name='test_value', trainable=False)
        else:
            test_value = tf.Variable(1, name='test_value', trainable=False)
        saver = tf.train.Saver()
        print("training model")
        sess = tf.Session()
        sess.run(tf.global_variables_initializer())
        # tf.global_variables_initializer().run()
        if os.path.exists("predict_output"):
            saver.restore(sess, "predict_output/model")
        print(sess.run(test_value))
        model.train(sess, saver, save_path, X_train, y_train, X_val, y_val, X_tag_train, X_tag_val, y_intent_train, y_intent_val, model_dev)
        # print("final best f1 is: %f" % (model.max_f1))

        end_time = time.time()
        print("time used %f(hour)" % ((end_time - start_time) / 3600))


