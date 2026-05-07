#! python

import svgwrite
import numpy as np

import shapes

def symbol_to_points(symbol, x):
    d = np.array(symbol).reshape(-1, 2) + [x, 0]
    point_list = []
    for b in d:
        point_list.append(tuple(b.tolist()))
    return point_list

def draw_button(dwg, base_x, pen, brush=None, **kwargs):
    '''
    kwargs:
        LP : Push Left-Punch. When exists this key painted by 'brush'.
        RP : Push Right-Punch.
        WP : Both LP and RP.
        LK : Push Left-Kick.
        RK : Push Right-Kick.
        WK : Both LK and RK.
        pushed : Accept all Punch and Kick notation. e.g. 'LP', 'LP+RK' etc...
    '''
    # [x, y, r]
    params = {
        'LP': [16, 16, 14],
        'LK': [16, 48, 14],
        'RP': [48, 16, 14],
        'RK': [48, 48, 14],
    }

    button_dic = {}
    if 'pushed' in kwargs:
        b = kwargs['pushed']
        button_dic = {button_name: True for button_name in b.split('+')}
    else:
        button_dic = kwargs

    push_buttons = []
    for key in button_dic:
        if key in params:
            push_buttons.append(key)
        elif key == 'WP':
            push_buttons.append('LP')
            push_buttons.append('RP')
        elif key == 'WK':
            push_buttons.append('LK')
            push_buttons.append('RK')
        else:
            ### Unknown
            pass

    for key in params:
        b = 'none'
        if key in push_buttons:
            b = brush
        circle = dwg.circle(
            center=(base_x + params[key][0], params[key][1]),
            r=params[key][2],
            fill=b,
            stroke=pen,
            stroke_width=4
        )
        dwg.add(circle)

def draw_text(dwg, base_x, text, font, fg_color, **kwargs):
    '''
    params:
        img:
        base_x:
        font:
        pen:
        brush:
        kwargs:
    '''
    text = svgwrite.text.Text(text, base_x)
    dwg.add(text)
    return None

def draw_command(output, ttf, font_size, ttc_index, command_list, fg_color):
    command_count = len(command_list)
    dwg = svgwrite.Drawing(output, size=("{}px".format(shapes.base_width * command_count), "{}px".format(shapes.base_height)))

    pen = svgwrite.utils.rgb(r=fg_color[0], g=fg_color[1], b=fg_color[2], mode='RGB')
    brush = svgwrite.utils.rgb(r=fg_color[0], g=fg_color[1], b=fg_color[2], mode='RGB')
    font = None

    nums = {'1':True, '2':True, '3':True, '4':True, '6':True, '7':True, '8':True, '9':True, }
    buttons = {'LP':True, 'RP':True, 'LK':True, 'RK':True, 'WP':True, 'WK':True, }

    ## Drawing.
    index = 0
    base_x = 0
    for cmd in command_list:
        symbol = None
        is_paint = False
        is_outline = False
        draw_width = shapes.base_width
        if cmd in nums:
            symbol = shapes.arrows[int(cmd)]
            is_paint = True
        elif cmd == 'n' or cmd == 'N':
            symbol = shapes.neutral_symbol
            is_paint = True
        elif len(cmd) >= 2 and cmd[0:2] in buttons:
            draw_button(dwg, base_x, pen, brush, pushed=cmd)
        elif cmd == '>' or cmd == ',':
            symbol = shapes.delimiter_symbol
            is_paint = True
        elif cmd == '[':
            symbol = shapes.start_slip_symbol
            is_outline = True
        elif cmd == ']':
            symbol = shapes.end_slip_symbol
            is_outline = True
        else:
            ### any text
            if font is None:
                ######font = ImageFont.truetype(ttf, font_size, index=ttc_index)
                pass
            draw_text(dwg, base_x, cmd, font, fg_color)

        if is_paint:
            a = symbol_to_points(symbol, base_x)
            poly = dwg.polygon(a, fill=brush, stroke=pen, stroke_width=4)
            dwg.add(poly)
        elif is_outline:
            a = symbol_to_points(symbol, base_x)
            poly = dwg.polygon(a, fill='none', stroke=pen, stroke_width=4)
            dwg.add(poly)
        index += 1
        base_x += draw_width

    ### Output
    dwg.save()
