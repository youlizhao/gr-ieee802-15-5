/**
 * Copyright (C) 2011 Bastian Bloessl <bastian.bloessl@uibk.ac.at>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 */

#include "contiki.h"
#include "dev/leds.h"
#include "dev/button-sensor.h"
#include "net/rime.h"
#include <stdio.h>

#define RADIO_CHANNEL 129

// dummy information that is sent
struct Packet {
	char bla[20];
} knowledgeBase = {
	.bla = "pinky and brain!",
};

PROCESS(spam_process, "spam process");
PROCESS(button_process, "button process");

AUTOSTART_PROCESSES(&button_process);

static void update_leds() {
	static uint8_t i = 0;
	i++;
	leds_off(LEDS_ALL);
	switch(i % 3) {
	case 0:
		leds_on(LEDS_RED);
		break;
	case 1:
		leds_on(LEDS_GREEN);
		break;
	case 2:
		leds_on(LEDS_BLUE);
		break;
	}
}

static void broadcastSent(struct broadcast_conn *c, int status, int num_tx) {
	update_leds();
}

static void broadcastReceived(struct broadcast_conn *c, const rimeaddr_t *from) {
	struct Packet *pkt = packetbuf_dataptr();
	static uint8_t rssi;
	rssi = 128 + packetbuf_attr(PACKETBUF_ATTR_RSSI);

	printf("broadcast packet received from %d.%d with RSSI %d, LQI %u\n",
			from->u8[0], from->u8[1],
			rssi,
			packetbuf_attr(PACKETBUF_ATTR_LINK_QUALITY));

	printf("-------------------------------\n%s\n", pkt->bla);
	printf("-------------------------------\n");

}

static struct broadcast_conn broadcastConnection;
	static const struct broadcast_callbacks broadcastCallbacks = {
		broadcastReceived, broadcastSent
	};


/**
 * periodic dissemination of knowledge base.
 */
PROCESS_THREAD(spam_process, ev, data) {

	PROCESS_BEGIN();

	// init
	leds_off(LEDS_ALL);

	while(1) {
		// wait a little bit
		static struct etimer et;
		etimer_set(&et, 2 * CLOCK_SECOND);
		PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));
		// broadcast knowledge base
		packetbuf_copyfrom(&knowledgeBase, sizeof(struct Packet));
		broadcast_send(&broadcastConnection);
	}

	PROCESS_END();
}

PROCESS_THREAD(button_process, ev, data) {

	PROCESS_BEGIN();
	SENSORS_ACTIVATE(button_sensor);

	static int stopped = 1;

	broadcast_open(&broadcastConnection, RADIO_CHANNEL, &broadcastCallbacks);

	while(1) {
		leds_off(LEDS_ALL);

		// wait for button press
		PROCESS_WAIT_EVENT_UNTIL(ev == sensors_event &&
				data == &button_sensor);

		if(stopped) {
			stopped = 0;
			process_start(&spam_process, NULL);
		} else {
			stopped = 1;
			process_exit(&spam_process);
		}
	}

	PROCESS_END();
}
