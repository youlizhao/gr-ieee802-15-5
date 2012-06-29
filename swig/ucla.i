/* -*- c++ -*- */

%feature("autodoc", "1");		// generate python docstrings

%include "exception.i"
%import "gnuradio.i"			// the common stuff

%{
#include "gnuradio_swig_bug_workaround.h"	// mandatory bug fix
#include "ucla_cc1k_correlator_cb.h"
#include "ucla_delay_cc.h"
#include "ucla_ieee802_15_4_packet_sink.h"
#include "ucla_manchester_ff.h"
#include "ucla_multichanneladd_cc.h"
#include "ucla_qpsk_modulator_cc.h"
#include "ucla_sos_packet_sink.h"
#include "ucla_symbols_to_chips_bi.h"
#include <gr_msg_queue.h>
#include <stdexcept>
%}

GR_SWIG_BLOCK_MAGIC(ucla,cc1k_correlator_cb);
%include "ucla_cc1k_correlator_cb.h"

GR_SWIG_BLOCK_MAGIC(ucla,sos_packet_sink);
%include "ucla_sos_packet_sink.h"

GR_SWIG_BLOCK_MAGIC(ucla,ieee802_15_4_packet_sink);
%include "ucla_ieee802_15_4_packet_sink.h"

GR_SWIG_BLOCK_MAGIC(ucla,qpsk_modulator_cc);
%include "ucla_qpsk_modulator_cc.h"

GR_SWIG_BLOCK_MAGIC(ucla,symbols_to_chips_bi);
%include "ucla_symbols_to_chips_bi.h"

GR_SWIG_BLOCK_MAGIC(ucla,manchester_ff);
%include "ucla_manchester_ff.h"

GR_SWIG_BLOCK_MAGIC(ucla,delay_cc);
%include "ucla_delay_cc.h"

GR_SWIG_BLOCK_MAGIC(ucla,multichanneladd_cc);
%include "ucla_multichanneladd_cc.h"
