#!/usr/bin/env python

#
# Transmitter of IEEE 802.15.4 RADIO Packets.
#
# Modified by: Thomas Schmid, Sanna Leidelof, Bastian Bloessl
#

from gnuradio import gr, eng_notation
from gnuradio import uhd
from gnuradio.ucla_blks import ieee802_15_4_pkt
from gnuradio.eng_option import eng_option
from optparse import OptionParser
import struct, time

class transmit_path(gr.top_block):
    def __init__(self, options):
        gr.top_block.__init__(self)

        # chip rate (2e6 is defined in the standard)
        self.chip_rate = 2e6
        # half the symbols per QPSK symbol
        self.samples_per_chip = 2
        self.sample_rate = self.chip_rate * self.samples_per_chip

        ### setup the device
        self.u = uhd.usrp_sink(device_addr="addr0=192.168.10.2", stream_args=uhd.stream_args(cpu_format="fc32"))
        self.u.set_subdev_spec("A:0", 0)    # this should not be required
        self.u.set_antenna("TX/RX", 0)      # this should also no be required
               
        self.u.set_samp_rate(self.sample_rate)
        tmp = self.u.get_samp_rate()
        assert(tmp == self.sample_rate)     
        
        ### frequency
        self.chan_num = options.channel
        self.u.set_center_freq(ieee802_15_4_pkt.chan_802_15_4.chan_map[self.chan_num])

        ### gain
        if not options.gain:
            g = self.u.get_gain_range()
            options.gain = float(g.start() + g.stop()) / 2
            print "no gain specified!"
            print "min. gain:    " + str(g.start())
            print "max. gain:    " + str(g.stop())

        self.u.set_gain(options.gain)
        
        
        ### output active configuration
        print "\n### CONFIGURATION"
        print "gain:                " + str(options.gain)
        print "frequency:           " + str(eng_notation.num_to_str(ieee802_15_4_pkt.chan_802_15_4.chan_map[self.chan_num]))
        print "samples_per_chip:    " + eng_notation.num_to_str(self.samples_per_chip)      
        print "subdev:              " + self.u.get_subdev_spec(0)
        print "antenna(0):          " + str(self.u.get_antenna(0))
        print "###\n"

        ### transmitter
        self.packet_transmitter = ieee802_15_4_pkt.ieee802_15_4_mod_pkts(self,
                spb=int(self.samples_per_chip), msgq_limit=2)
     
        self.connect(self.packet_transmitter, self.u)

    def send_pkt(self, payload, seqno, eof=False):
        return self.packet_transmitter.send_pkt(seqno, '', payload, eof)

def main ():

    parser = OptionParser (option_class=eng_option)
    parser.add_option("-T", "--tx-subdev-spec", type="subdev", default=None,
                      help="select USRP Tx side A or B (default=first one with a daughterboard)")
    parser.add_option("-c", "--channel", type="eng_float", default=26,
                      help="Set 802.15.4 Channel to listen on", metavar="FREQ")
    parser.add_option("-g", "--gain", type="eng_float", default=None,
                      help="set TX gain. Default: midrange.")
    parser.add_option("-t", "--msg-interval", type="eng_float", default=2.0,
                      help="inter-message interval")

    (options, args) = parser.parse_args ()

    tb = transmit_path(options)
    tb.start()

    i = 0
    while True:
        i += 1
        print "sending message " + str(i)
        tb.send_pkt(struct.pack('38B', 0xcd, 0xab, 0xff, 0xff, 0x40, 0xe8, 0x81, 0x0, 0x2a, 0x17, 0x70, 0x69, 0x6e, 0x6b, 0x79, 0x20, 0x61, 0x6e, 0x64, 0x20, 0x62, 0x72, 0x61, 0x69, 0x6e, 0x21, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0), i)
        
        time.sleep(options.msg_interval)

    tb.wait()

if __name__ == '__main__':
    main ()
