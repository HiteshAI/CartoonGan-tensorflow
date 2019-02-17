import logging
import tensorflow as tf
from net_base import NetBase
from modules import coupled_conv, batch_norm, conv


class Generator(NetBase):

    def __init__(self, input_size=224, base_chs=64, init_param=None, inf_only=False):
        super(Generator, self).__init__(
                input_size, base_chs, init_param, inf_only)
        self.graph_prefix = "Generator"

    def build_graph(self, x, reuse=False):
        with tf.variable_scope(self.graph_prefix, reuse=reuse):
            chs = self.base_chs
            logging.debug("initial conv: 3, %d" % chs)
            # Init conv
            x = conv(x, 3, chs, 5, 1, 2, 0, False, self.get_par(0))
            x = tf.nn.relu(batch_norm(
                x, chs, 1, 1e-5,
                *self.get_par(1, 3)))
            prev_chs = chs
            par_pos = 3
            mcnt = 2
            # Downsample
            with tf.variable_scope("Downsample", reuse=reuse):
                for i in range(4):
                    if i % 2 == 0:
                        chs *= 2
                        stride = 2
                    else:
                        stride = 1
                    logging.debug("downsample conv: %d, %d" % (prev_chs, chs))
                    x = coupled_conv(x, prev_chs, chs, 3, stride, True, mcnt,
                                     *self.get_par(par_pos, par_pos+6))
                    prev_chs = chs
                    par_pos += 6
                    mcnt += 1
            # ResBlock
            with tf.variable_scope("ResBlock", reuse=reuse):
                for _ in range(8):
                    x1 = x
                    logging.debug("res conv: %d, %d" % (prev_chs, chs))
                    x = coupled_conv(x, prev_chs, chs, 3, 1, True, mcnt,
                                     *self.get_par(par_pos, par_pos+6))
                    x = coupled_conv(x, prev_chs, chs, 3, 1, False, mcnt+1,
                                     *self.get_par(par_pos+6, par_pos+12))
                    x += x1  # no relu as suggested by Sam Gross and Michael Wilber
                    mcnt += 2
                    par_pos += 12
            # Upsample
            with tf.variable_scope("Upsample", reuse=reuse):
                cur_size = self.input_size // 4
                for i in range(4):
                    if i % 2 == 0:
                        cur_size *= 2
                        chs /= 2
                        x = tf.image.resize_bilinear(x, (cur_size, cur_size))
                    logging.debug("upsample conv: %d, %d, size: %d" % (prev_chs, chs, cur_size))
                    x = coupled_conv(x, prev_chs, chs, 3, 1, True, mcnt,
                                     *self.get_par(par_pos, par_pos+6))
                    par_pos += 6
                    mcnt += 1
                    prev_chs = chs
            # Final conv
            logging.debug("final conv: %d, %d" % (prev_chs, chs))
            x = conv(x, prev_chs, 3, 5, 1, 2, mcnt, True, *self.get_par(par_pos, par_pos+2))
            par_pos += 2
            logging.debug("%d param tensors traversed" % par_pos)
        self.to_save_vars = [
            v for v in tf.global_variables() if v.name.startswith(self.graph_prefix)]
        assert len(self.to_save_vars) == par_pos
        self.saver = None if reuse else tf.train.Saver(self.to_save_vars)
        self.has_graph = True
        return x


def _test():
    import os
    import numpy as np
    logging.basicConfig(level=logging.DEBUG)
    size = 224
    x = tf.placeholder(tf.float32, [2, size, size, 3])
    net = Generator(input_size=size)
    nx = np.random.rand(2, size, size, 3).astype(np.float32)
    out_op = net.build_graph(x)
    out_op2 = net.build_graph(x, True)
    writer = tf.summary.FileWriter(os.path.join("tmp", "gruns"), tf.get_default_graph())
    writer.close()
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        out = sess.run(out_op, {x: nx})
        out2 = sess.run(out_op2, {x: nx})
    logging.debug(out.shape)
    logging.debug(out2.shape)
    logging.debug(np.sqrt(np.mean((out-out2)**2)))


if __name__ == '__main__':
    _test()