import tensorflow as tf
from config import *
from ambientGAN import *


def train(args, sess, model):
    #optimizer
    g_optimizer = tf.train.AdamOptimizer(args.learning_rate, beta1=args.momentum, name="AdamOptimizer_G").minimize(model.g_loss, var_list=model.g_vars)
    d_optimizer = tf.train.AdamOptimizer(args.learning_rate, beta1=args.momentum, name="AdamOptimizer_D").minimize(model.d_loss, var_list=model.d_vars)

    epoch = 0
    step = 0

    #saver
    saver = tf.train.Saver()        
    if args.continue_training:
        last_ckpt = tf.train.latest_checkpoint(args.checkpoints_path)
        saver.restore(sess, last_ckpt)
        ckpt_name = str(last_ckpt)
        print "Loaded model file from " + ckpt_name
        step = int(ckpt_name.split('-')[-1])
        tf.local_variables_initializer().run()
    else:
        tf.global_variables_initializer().run()
        tf.local_variables_initializer().run()


    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(sess=sess, coord=coord)


    all_summary = tf.summary.merge([model.images_sum,
                                    model.genX_sum, 
                                    model.d_loss_sum,
                                    model.g_loss_sum])

    writer = tf.summary.FileWriter(args.graph_path, sess.graph)

    while epoch < args.epochs:
        #Update Discriminator
        summary, d_loss, _ = sess.run([all_summary, model.d_loss, d_optimizer])
        writer.add_summary(summary, step)

        #Update Generator
        summary, g_loss, _ = sess.run([all_summary, model.g_loss, g_optimizer])
        writer.add_summary(summary, step)
        #Update Generator Again
        summary, g_loss, _ = sess.run([all_summary, model.g_loss, g_optimizer])
        writer.add_summary(summary, step)


        print "Epoch [%d] Step [%d] G Loss: [%.4f] D Loss: [%.4f]" % (epoch, step, g_loss, d_loss)

        if step*args.batch_size >= model.data_count:
            saver.save(sess, args.checkpoints_path + "model", global_step=epoch)

            res_img = sess.run([model.genX])

            img_tile(epoch, args, res_img)
            step = 0
            epoch += 1 

        step += 1



    coord.request_stop()
    coord.join(threads)
    sess.close()            
    print("Done.")


def main(_):
    run_config = tf.ConfigProto()
    run_config.gpu_options.allow_growth = True
    
    with tf.Session(config=run_config) as sess:
        model = ambientGAN(args)

        #create graph and checkpoints folder if they don't exist
        if not os.path.exists(args.checkpoints_path):
            os.makedirs(args.checkpoints_path)
        if not os.path.exists(args.graph_path):
            os.makedirs(args.graph_path)
            
        print 'Start Training...'
        train(args, sess, model)

main(args)

#Still Working....