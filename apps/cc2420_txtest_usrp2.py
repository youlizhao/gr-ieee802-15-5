#!/usr/bin/env python

#
# Transmitter of IEEE 802.15.4 RADIO Packets.
#
# Modified by: Thomas Schmid, Sanna Leidelof, Bastian Bloessl
#

from gnuradio import gr, eng_notation
from gnuradio import uhd
from gnuradio import ucla
from gnuradio.ucla_blks import ieee802_15_4_pkt
from gnuradio.eng_option import eng_option
from optparse import OptionParser
import math, struct, time

def pick_subdevice(u):
    """
    The user didn't specify a subdevice on the command line.
    If there's a daughterboard on A, select A.
    If there's a daughterboard on B, select B.
    Otherwise, select A.
    """
    if u.db[0][0].dbid() >= 0:       # dbid is < 0 if there's no d'board or a problem
        return (0, 0)
    if u.db[1][0].dbid() >= 0:
        return (1, 0)
    return (0, 0)

class transmit_path(gr.top_block):
    def __init__(self, options):
        gr.top_block.__init__(self)
        
        self.samples_per_symbol = 2
        # chip rate?
        self.symbol_rate = 1e6
        
        #self.sample_rate = 10e6

        self.u = uhd.usrp_sink(device_addr="addr0=192.168.10.2",stream_args=uhd.stream_args(cpu_format="fc32", channels=range(1)))
        
        (self.sample_rate, self.samples_per_symbol) = self.set_sample_rate(self.symbol_rate, self.samples_per_symbol)
        
        self.chan_num = options.channel
        self.u.set_center_freq(ieee802_15_4_pkt.chan_802_15_4.chan_map[self.chan_num])

        if not options.gain:
            g = self.u.get_gain_range()
            options.gain = float(g.start() + g.stop()) / 2 + 5
            print "gain start:    " + str(g.start())
            print "gain end:      " + str(g.stop())
            print "current gain:  " + str(options.gain)

        self.u.set_gain(options.gain)

        print "cordic_freq = %s" % (eng_notation.num_to_str(ieee802_15_4_pkt.chan_802_15_4.chan_map[self.chan_num]))
        print "samples_per_symbol = ", eng_notation.num_to_str(self.samples_per_symbol)

        # transmitter
        self.packet_transmitter = ieee802_15_4_pkt.ieee802_15_4_mod_pkts(self,
                spb=int(self.samples_per_symbol), msgq_limit=2)

        self.gain = gr.multiply_const_cc (0.4)
        self.connect(self.packet_transmitter, self.gain, self.u)
       
        
    def set_sample_rate(self, sym_rate, req_sps):
        start_sps = req_sps
        while(True):
            asked_samp_rate = sym_rate * req_sps
            self.u.set_samp_rate(asked_samp_rate)
            actual_samp_rate = self.u.get_samp_rate()

            sps = actual_samp_rate/sym_rate
            if(sps < 2):
                req_sps +=1
            else:
                actual_sps = sps
                break

        print "\nSymbol Rate:         " + eng_notation.num_to_str(sym_rate)
        print "Requested sps:       " + eng_notation.num_to_str(start_sps)
        print "Given sample rate:   " + eng_notation.num_to_str(actual_samp_rate)
        print "Actual sps for rate: " + eng_notation.num_to_str(actual_sps)

        print "\nRequested sample rate:     " + eng_notation.num_to_str(asked_samp_rate)
        print "Actual sample rate:        " + eng_notation.num_to_str(actual_samp_rate)

        return (actual_samp_rate, actual_sps)

    def send_pkt(self, payload='', eof=False):
        return self.packet_transmitter.send_pkt(0xe5, struct.pack("HHHH", 0xFFFF, 0xFFFF, 0x10, 0x10), payload, eof)

def main ():


    parser = OptionParser (option_class=eng_option)
    parser.add_option("-T", "--tx-subdev-spec", type="subdev", default=None,
                      help="select USRP Tx side A or B (default=first one with a daughterboard)")
    parser.add_option ("-c", "--channel", type="eng_float", default=26,
                       help="Set 802.15.4 Channel to listen on", metavar="FREQ")
    parser.add_option ("-g", "--gain", type="eng_float", default=None,
            help="set TX gain. Default: midrange.")
    parser.add_option("-e", "--interface", type="string", default="eth0",
            help="select Ethernet interface, default is eth0")
    parser.add_option("-m", "--mac-addr", type="string", default="",
            help="select USRP by MAC address, default is auto-select")
    parser.add_option("-t", "--msg-interval", type="eng_float", default=1.0,
            help="inter-message interval")

    (options, args) = parser.parse_args ()

    tb = transmit_path(options)
    tb.start()

    i = 0
    while True:
        i+=1
        print "send message %d:"%(i+1,)
        #tb.send_pkt(struct.pack('9B', 0x1, 0x80, 0x80, 0xff, 0xff, 0x10, 0x0, 0x20, 0x0))
        #this is an other example packet we could send.
        #tb.send_pkt(struct.pack('BBBBBBBBBBBBBBBBBBBBBBBBBBB', 0x1, 0x8d, 0x8d, 0xff, 0xff, 0xbd, 0x0, 0x22, 0x12, 0xbd, 0x0, 0x1, 0x0, 0xff, 0xff, 0x8e, 0xff, 0xff, 0x0, 0x3, 0x3, 0xbd, 0x0, 0x1, 0x0, 0x0, 0x0))
        tb.send_pkt(struct.pack('46B', 0xe8, 0x41, 0x88, 0x28, 0xcd, 0xab, 0xff, 0xff, 0x40, 0xe8, 0x0, 0x18, 0x2b, 0x0, 0xe8, 0x40, 0x70, 0x69, 0x6e, 0x6b, 0x79, 0x20, 0x61, 0x6e, 0x64, 0x20, 0x62, 0x72, 0x61, 0x69, 0x6e, 0x21, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1, 0xe))

        time.sleep(options.msg_interval)

    tb.wait()

if __name__ == '__main__':
    main ()
