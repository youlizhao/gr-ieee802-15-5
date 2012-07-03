#!/usr/bin/env python

#
# Decoder of IEEE 802.15.4 RADIO Packets.
#
# Modified by: Thomas Schmid, Leslie Choong, Mikhail Tadjikov, Bastian Bloessl
#
  
from gnuradio import gr, eng_notation, uhd
from gnuradio.ucla_blks import ieee802_15_4_pkt
from gnuradio.eng_option import eng_option
from optparse import OptionParser
import struct, sys, time

class stats(object):
    def __init__(self):
        self.npkts = 0
        self.nright = 0
        
class oqpsk_rx_graph (gr.top_block):
    
    def __init__(self, options, rx_callback):
        self.sample_rate = 10e6
        
        gr.top_block.__init__(self)

        if options.infile is None:
            # Initialize USRP2 block
            u = uhd.usrp_source(device_addr="addr0=192.168.10.2",stream_args=uhd.stream_args(cpu_format="fc32", channels=range(1)))
            u.set_samp_rate(self.sample_rate)
            self.samples_per_symbol = 5
            self.chan_num = options.channel
            self.data_rate = int (self.sample_rate
                                  / self.samples_per_symbol)

            u.set_center_freq(ieee802_15_4_pkt.chan_802_15_4.chan_map[self.chan_num])
            #u.set_gain(options.gain)
            u.set_gain(1)

            print "cordic_freq = %s" % (eng_notation.num_to_str(ieee802_15_4_pkt.chan_802_15_4.chan_map[self.chan_num]))
            print "data_rate = ", eng_notation.num_to_str(self.data_rate)
            print "samples_per_symbol = ", self.samples_per_symbol

            self.src = u
        else:
            # TODO: test this
            self.src = gr.file_source(gr.sizeof_gr_complex, options.infile);
            self.samples_per_symbol = 2
            self.data_rate = 2000000

        self.packet_receiver = ieee802_15_4_pkt.ieee802_15_4_demod_pkts(self,
                                callback=rx_callback,
                                sps=self.samples_per_symbol,
                                symbol_rate=self.data_rate,
                                channel=self.chan_num,
                                threshold=options.threshold)

        #self.squelch = gr.pwr_squelch_cc(-65, gate=True)
        self.connect(self.src,
         #       self.squelch,
                self.packet_receiver)

def rx_callback_old(ok, payload, chan_num):
    
    ### record stats
    st.npkts += 1
    if ok:
        st.nright += 1
    
    ### extract data
    lqi    = struct.unpack('B', payload[0])
    seqno  = struct.unpack('B', payload[3])
    length = len(payload)
    crc   = 'correct' if ok else 'wrong'
    
    ### print output
    print "\n#### received packet"
    print "pktno = %4d  len = %4d  lqi = %4d  crc: %s (%d / %d) " % (seqno[0], length, lqi[0], crc, st.nright, st.npkts)
    print "payload:"
    print str(map(hex, map(ord, payload)))
    
    
def main ():

    parser = OptionParser (option_class=eng_option)
    parser.add_option("-R", "--rx-subdev-spec", type="subdev", default=None,
                      help="select USRP Rx side A or B (default=first one with a daughterboard)")
    parser.add_option ("-c", "--channel", type="eng_float", default=26,
                       help="Set 802.15.4 Channel to listen on")
    parser.add_option ("-f", "--filename", type="string",
                       default="rx.dat", help="write data to FILENAME")
    parser.add_option ("-i", "--infile", type="string",
                       default=None, help="Process from captured file")
    parser.add_option ("-g", "--gain", type="eng_float", default=35,
                       help="set Rx gain in dB [0,70]")
    parser.add_option ("-t", "--threshold", type="int", default=-1)

    (options, args) = parser.parse_args ()


    r= gr.enable_realtime_scheduling()
    if r == gr.RT_OK:
        print "Enabled Realtime"
    else:
        print "Failed to enable Realtime"

    tb = oqpsk_rx_graph(options, rx_callback_old)
    tb.start()
    tb.wait()

if __name__ == '__main__':
    st = stats()
    main ()
