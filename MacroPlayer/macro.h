
/*
Input Recorder - Record and play back keyboard and mouse input.
Copyright (C) 2022  Zuzu_Typ

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

#pragma once

#include <chrono>
#include <thread>

#include "winput.h"

#define MACRO_INVALID_FORMAT -1
#define MACRO_NON_SINGLE -2
#define MACRO_INCOMPATIBLE -3
#define MACRO_EMPTY -4

#pragma pack(1)

enum class PlaybackMode {PLAY, EXPLAIN};

struct MacroConfig {

	static const byte VERSION = 1;
	
	byte version = VERSION;

	unsigned short screen_width;

	unsigned short screen_height;
};

struct MacroEvent {
	byte bytecode;
};

struct RawMousePositionEvent {
	byte bytecode = 'P';

	short x;

	short y;

};

struct MousePositionEvent {
	byte bytecode = 'P';

	MacroConfig config;

	short x;

	short y;

	MousePositionEvent(MacroConfig config, RawMousePositionEvent* bytes)
		: config{ config }, x{ bytes->x }, y{ bytes->y } {

	}

	void run() {
		set_mouse_pos(x, y);
	}

	void explain(char* buf, const size_t buf_size) {
		snprintf(buf, buf_size, "Set mouse position to (%d, %d)", (int)x, (int)y);
	}

};

struct MouseWheelMoveEvent {
	byte bytecode = 'V';

	char amount;

	void run() {
		move_mousewheel(amount);
	}

	void explain(char* buf, const size_t buf_size) {
		snprintf(buf, buf_size, "Move mousewheel by %d", (int)amount);
	}
};

struct MouseWheelHorizontalMoveEvent {
	byte bytecode = 'H';

	char amount;

	void run() {
		move_mousewheel_horizontal(amount);
	}

	void explain(char* buf, const size_t buf_size) {
		snprintf(buf, buf_size, "Move mousewheel horizontally by %d", (int)amount);
	}
};

struct MouseButtonPressEvent {
	byte bytecode = 'B';

	byte mouse_button;

	void run() {
		press_mouse_button(mouse_button);
	}

	void explain(char* buf, const size_t buf_size) {
		snprintf(buf, buf_size, "Press mouse button %d", (int)mouse_button);
	}
};

struct MouseButtonReleaseEvent {
	byte bytecode = 'b';

	byte mouse_button;

	void run() {
		release_mouse_button(mouse_button);
	}

	void explain(char* buf, const size_t buf_size) {
		snprintf(buf, buf_size, "Release mouse button %d", (int)mouse_button);
	}
};

struct KeyPressEvent {
	byte bytecode = 'K';

	WORD vk_code;

	void run() {
		press_key(vk_code);
	}

	void explain(char* buf, const size_t buf_size) {
		snprintf(buf, buf_size, "Press key %d", (int)vk_code);
	}
};

struct KeyReleaseEvent {
	byte bytecode = 'k';

	WORD vk_code;

	void run() {
		release_key(vk_code);
	}

	void explain(char* buf, const size_t buf_size) {
		snprintf(buf, buf_size, "Release key %d", (int)vk_code);
	}
};

int play_macro(unsigned int byte_count, byte* bytes, PlaybackMode mode) {
	if (byte_count < 1) {
		return MACRO_INVALID_FORMAT;
	}

	unsigned int index = 0;

	if (bytes[index] == (byte)'M') {
		return MACRO_NON_SINGLE;
	}

	if (bytes[index++] != (byte)'S') {
		return MACRO_INVALID_FORMAT;
	}

	if (index == byte_count) {
		return MACRO_INVALID_FORMAT;
	}

	// macro name
	byte name_length = bytes[index++];
	if (name_length <= 0 || index + name_length >= byte_count) {
		return MACRO_INVALID_FORMAT;
	}

	index += name_length;

	// macro config
	if (index + 1 + sizeof(MacroConfig) > byte_count || bytes[index] != sizeof(MacroConfig)) {
		return MACRO_INVALID_FORMAT;
	}
	index++;
	if (bytes[index] != MacroConfig::VERSION) {
		return MACRO_INCOMPATIBLE;
	}
	MacroConfig config = *(MacroConfig*)(bytes + index);

	index += sizeof(config);

	if (index == byte_count) {
		return MACRO_EMPTY;
	}

	auto start_time = std::chrono::high_resolution_clock::now();

	unsigned long long last_time_offset = 0;

	while (index < byte_count) {
		byte length = bytes[index++];
		if (index + length > byte_count) {
			return MACRO_INVALID_FORMAT;
		}

		unsigned long long time_offset = *(unsigned long long*)(bytes + index);
		index += sizeof(time_offset);
		byte bytecode = bytes[index];

		if (mode == PlaybackMode::PLAY) {
			long long diff;

			while ((diff = std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::high_resolution_clock::now() - start_time).count()) < (long long)time_offset) {
				long long time_to_wait = max(time_offset - diff - 1000000, 100000);
				std::this_thread::sleep_for(std::chrono::nanoseconds(time_to_wait));
			}
		}
		else if (mode == PlaybackMode::EXPLAIN) {
			unsigned long long diff = time_offset - last_time_offset;

			last_time_offset = time_offset;

			std::cout << "Wait " << diff / 1000000 << "ms" << std::endl;
		}
		

		char buffer[256];

		switch (bytecode) {
		case 'P':
			if (mode == PlaybackMode::PLAY)
				MousePositionEvent(config, reinterpret_cast<RawMousePositionEvent*>(bytes + index)).run();
			else if (mode == PlaybackMode::EXPLAIN)
				MousePositionEvent(config, reinterpret_cast<RawMousePositionEvent*>(bytes + index)).explain(buffer, sizeof(buffer));
			break;
		case 'V':
			if (mode == PlaybackMode::PLAY)
				reinterpret_cast<MouseWheelMoveEvent*>(bytes + index)->run();
			else if (mode == PlaybackMode::EXPLAIN)
				reinterpret_cast<MouseWheelMoveEvent*>(bytes + index)->explain(buffer, sizeof(buffer));
			break;
		case 'H':
			if (mode == PlaybackMode::PLAY)
				reinterpret_cast<MouseWheelHorizontalMoveEvent*>(bytes + index)->run();
			else if (mode == PlaybackMode::EXPLAIN)
				reinterpret_cast<MouseWheelHorizontalMoveEvent*>(bytes + index)->explain(buffer, sizeof(buffer));
			break;
		case 'B':
			if (mode == PlaybackMode::PLAY)
				reinterpret_cast<MouseButtonPressEvent*>(bytes + index)->run();
			else if (mode == PlaybackMode::EXPLAIN)
				reinterpret_cast<MouseButtonPressEvent*>(bytes + index)->explain(buffer, sizeof(buffer));
			break;
		case 'b':
			if (mode == PlaybackMode::PLAY)
				reinterpret_cast<MouseButtonReleaseEvent*>(bytes + index)->run();
			else if (mode == PlaybackMode::EXPLAIN)
				reinterpret_cast<MouseButtonReleaseEvent*>(bytes + index)->explain(buffer, sizeof(buffer));
			break;
		case 'K':
			if (mode == PlaybackMode::PLAY)
				reinterpret_cast<KeyPressEvent*>(bytes + index)->run();
			else if (mode == PlaybackMode::EXPLAIN)
				reinterpret_cast<KeyPressEvent*>(bytes + index)->explain(buffer, sizeof(buffer));
			break;
		case 'k':
			if (mode == PlaybackMode::PLAY)
				reinterpret_cast<KeyReleaseEvent*>(bytes + index)->run();
			else if (mode == PlaybackMode::EXPLAIN)
				reinterpret_cast<KeyReleaseEvent*>(bytes + index)->explain(buffer, sizeof(buffer));
			break;
		default:
			return MACRO_INVALID_FORMAT;
		}

		if (mode == PlaybackMode::EXPLAIN)
			std::cout << buffer << std::endl;

		index += length - sizeof(time_offset);
	}
	return 0;
}
