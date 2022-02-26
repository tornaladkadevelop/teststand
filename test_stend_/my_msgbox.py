#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__all__ = ["my_msg"]

import PySimpleGUI as sg


def my_msg(msg: str, bgcolor='#37474F'):
    #sg.theme('DarkAmber')   # Add a touch of color
    font = ('Arial', 15)
    # All the stuff inside your window.
    layout = [
            [sg.Text(msg, size=(60, 5), justification='center', font=font, background_color=bgcolor)],
            [sg.Button('Ok', font=font, size=16, button_color='#2D3D45', focus=True),
             sg.Button('Отмена', font=font, size=16, button_color='#2D3D45')]
        ]
    window = sg.Window('Внимание!', layout, element_justification='c', background_color=bgcolor,
                       keep_on_top=True, use_default_focus=True)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Ok' or event == 'Отмена':
            break

    window.close()

    if event == 'Ok':
        return True
    elif event == 'Отмена':
        return False
    elif event == sg.WIN_CLOSED:
        return False
