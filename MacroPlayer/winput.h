
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

#include <Windows.h>

#define LEFT_MOUSE_BUTTON    1
#define MIDDLE_MOUSE_BUTTON  2
#define RIGHT_MOUSE_BUTTON   4
#define EXTRA_MOUSE_BUTTON1  8
#define EXTRA_MOUSE_BUTTON2 16

inline void set_mouse_pos(int x, int y) {
	SetCursorPos(x, y);
}

inline void _issue_mouse_event(DWORD dwFlags, DWORD mouseData) {
	MOUSEINPUT mi = { 0, 0, mouseData, dwFlags };

	INPUT input = { INPUT_MOUSE, mi };

	SendInput(1, &input, sizeof(input));
}

inline void _issue_keyboard_event(WORD wVk, DWORD dwFlags) {
	KEYBDINPUT ki = { wVk, 0, dwFlags };

	INPUT input = { INPUT_KEYBOARD };

	input.ki = ki;

	SendInput(1, &input, sizeof(input));
}

inline void press_mouse_button(int mouse_button) {
	DWORD dwFlags;

	switch (mouse_button) {
	case LEFT_MOUSE_BUTTON:
		dwFlags = 0x02;
		break;
	case MIDDLE_MOUSE_BUTTON:
		dwFlags = 0x08;
		break;
	case RIGHT_MOUSE_BUTTON:
		dwFlags = 0x20;
		break;
	case EXTRA_MOUSE_BUTTON1:
	case EXTRA_MOUSE_BUTTON2:
		dwFlags = 0x80;
		break;

	default:
		dwFlags = 0;
		break;
	}

	DWORD mouseData;

	if (dwFlags == 0x80) {
		if (mouse_button == EXTRA_MOUSE_BUTTON1) {
			mouseData = 0x1;
		}
		else {
			mouseData = 0x2;
		}
	}
	else {
		mouseData = 0;
	}

	_issue_mouse_event(dwFlags, mouseData);
}

inline void release_mouse_button(int mouse_button) {
	DWORD dwFlags;

	switch (mouse_button) {
	case LEFT_MOUSE_BUTTON:
		dwFlags = 0x004;
		break;
	case MIDDLE_MOUSE_BUTTON:
		dwFlags = 0x010;
		break;
	case RIGHT_MOUSE_BUTTON:
		dwFlags = 0x040;
		break;
	case EXTRA_MOUSE_BUTTON1:
	case EXTRA_MOUSE_BUTTON2:
		dwFlags = 0x100;
		break;

	default:
		dwFlags = 0;
		break;
	}

	DWORD mouseData;

	if (dwFlags == 0x100) {
		if (mouse_button == EXTRA_MOUSE_BUTTON1) {
			mouseData = 0x1;
		}
		else {
			mouseData = 0x2;
		}
	}
	else {
		mouseData = 0;
	}

	_issue_mouse_event(dwFlags, mouseData);
}

inline void move_mousewheel(DWORD amount) {
	_issue_mouse_event(0x800, amount * 120);
}

inline void move_mousewheel_horizontal(DWORD amount) {
	_issue_mouse_event(0x1000, amount * 120);
}

inline void press_key(WORD vk_code) {
	_issue_keyboard_event(vk_code, 0);
}

inline void release_key(WORD vk_code) {
	_issue_keyboard_event(vk_code, KEYEVENTF_KEYUP);
}
