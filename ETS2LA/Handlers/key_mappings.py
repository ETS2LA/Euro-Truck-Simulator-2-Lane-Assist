from pynput import keyboard as pynput_keyboard


numpad_mapping = {
    12: "5",
    96: "Num 0",
    97: "Num 1",
    98: "Num 2",
    99: "Num 3",
    100: "Num 4",
    101: "Num 5",
    102: "Num 6",
    103: "Num 7",
    104: "Num 8",
    105: "Num 9",
    110: "Num ."
}

special_key_mapping = {
    pynput_keyboard.Key.esc: "ESC",
    pynput_keyboard.Key.enter: "Enter",
    pynput_keyboard.Key.space: "Space",
    pynput_keyboard.Key.shift: "Shift",
    pynput_keyboard.Key.shift_r: "Right Shift",
    pynput_keyboard.Key.ctrl_l: "Left Ctrl",
    pynput_keyboard.Key.ctrl_r: "Right Ctrl",
    pynput_keyboard.Key.alt_l: "Left Alt",
    pynput_keyboard.Key.alt_r: "Right Alt",
    pynput_keyboard.Key.cmd: "Win",
    pynput_keyboard.Key.cmd_r: "Right Win",
    pynput_keyboard.Key.menu: "Application Key",
    pynput_keyboard.Key.caps_lock: "CAPS LOCK",
    pynput_keyboard.Key.tab: "TAB",
    pynput_keyboard.Key.f1: "F1",
    pynput_keyboard.Key.f2: "F2",
    pynput_keyboard.Key.f3: "F3",
    pynput_keyboard.Key.f4: "F4",
    pynput_keyboard.Key.f5: "F5",
    pynput_keyboard.Key.f6: "F6",
    pynput_keyboard.Key.f7: "F7",
    pynput_keyboard.Key.f8: "F8",
    pynput_keyboard.Key.f9: "F9",
    pynput_keyboard.Key.f10: "F10",
    pynput_keyboard.Key.f11: "F11",
    pynput_keyboard.Key.f12: "F12",
    pynput_keyboard.Key.print_screen: "Print Screen",
    pynput_keyboard.Key.scroll_lock: "Scroll lock",
    pynput_keyboard.Key.pause: "Pause",
    pynput_keyboard.Key.insert: "Insert",
    pynput_keyboard.Key.delete: "Delete",
    pynput_keyboard.Key.home: "Home",
    pynput_keyboard.Key.end: "End",
    pynput_keyboard.Key.page_up: "Page Up",
    pynput_keyboard.Key.page_down: "Page Down",
    pynput_keyboard.Key.up: "↑",
    pynput_keyboard.Key.down: "↓",
    pynput_keyboard.Key.left: "←",
    pynput_keyboard.Key.right: "→",
    pynput_keyboard.Key.num_lock: "Num Lock",
    pynput_keyboard.Key.media_play_pause: "Media Play/Pause",
    pynput_keyboard.Key.media_previous: "Media Previous",
    pynput_keyboard.Key.media_next: "Media Next",
    pynput_keyboard.Key.media_volume_mute: "Media Volume Mute",
}


def key_to_str(key):
    if hasattr(key, 'vk') and key.vk in numpad_mapping:
        return numpad_mapping[key.vk]
    elif key in special_key_mapping:
        return special_key_mapping[key]
    elif hasattr(key, 'char') and key.char is not None:
        return key.char
    else:
        return str(key)
