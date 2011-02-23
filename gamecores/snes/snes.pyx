#!/usr/bin/cython

cdef extern from "stdint.h":
	ctypedef unsigned char uint8_t
	ctypedef unsigned short uint16_t
	ctypedef short int16_t
	ctypedef int bool

cdef extern from "libsnes.hpp":
	ctypedef void (*snes_video_refresh_t)(uint16_t *data, unsigned width, unsigned height)
	ctypedef void (*snes_audio_sample_t)(uint16_t left, uint16_t right)
	ctypedef void (*snes_input_poll_t)()
	ctypedef int16_t (*snes_input_state_t)(bool port, unsigned device, unsigned index, unsigned id)

	unsigned snes_library_revision_major()
	unsigned snes_library_revision_minor()

	void snes_set_video_refresh(snes_video_refresh_t)
	void snes_set_audio_sample(snes_audio_sample_t)
	void snes_set_input_poll(snes_input_poll_t)
	void snes_set_input_state(snes_input_state_t)

	void snes_set_controller_port_device(bool port, unsigned device)
	void snes_set_cartridge_basename(char* basename)

	void snes_init()
	void snes_term()
	void snes_power()
	void snes_reset()
	void snes_run()

	unsigned snes_serialize_size()
	bool snes_serialize(uint8_t *data, unsigned size)
	bool snes_unserialize(uint8_t *data, unsigned size)

	void snes_cheat_reset()
	void snes_cheat_set(unsigned index, bool enabled, char *code)

	bool snes_load_cartridge_normal(char* rom_xml, uint8_t* rom_data, unsigned rom_size)
	void snes_unload_cartridge()

	bool snes_get_region()
	uint8_t* snes_get_memory_data(unsigned id)
	unsigned snes_get_memory_size(unsigned id)

print snes_get_region()
import pygame
print pygame.ver
