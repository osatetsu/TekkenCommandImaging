#! python

from PIL import Image, ImageDraw, ImageFont
import aggdraw

import shapes
import utils

def draw_button(draw, base_x, pen, brush=None, **kwargs):
    '''
    kwargs:
        LP : Push Left-Punch. When exists this key painted by 'brush'.
        RP : Push Right-Punch.
        WP : LP and RP.
        LK : Push Left-Kick.
        RK : Push Right-Kick.
        WK : LK and RK.
        pushed : Accept all Punch and Kick notation. e.g. 'LP', 'LP+RK' etc...
    '''
    params = {
        'LP': [8, 4, 32, 28,],
        'LK': [8, 36, 32, 60,],
        'RP': [36, 4, 60, 28,],
        'RK': [36, 36, 60, 60,],
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
        b = None
        if key in push_buttons:
            b = brush
        draw.ellipse((base_x + params[key][0], params[key][1], base_x + params[key][2], params[key][3]), b, pen)

def draw_text(img, base_x, text, font, fg_color, **kwargs):
    '''
    params:
        img:
        base_x:
        font:
        pen:
        brush:
        kwargs:
    '''
    w, h = img.size
    draw = ImageDraw.Draw(img)
    box = draw.textbbox((base_x, shapes.margin), text, font=font)
    text_w = box[2] - box[0]
    if shapes.base_width < text_w:
        new_img = Image.new('RGBA', (w + text_w, shapes.base_height), (0, 0, 0, 0))
        new_img.paste(img, (0, 0))
        img = new_img
        draw = ImageDraw.Draw(img)

    draw.text((base_x, shapes.margin), text, fg_color, font=font)
    return (img, text_w)

def draw_command(output, ttf, font_size, ttc_index, command_list, fg_color):
    command_count = len(command_list)
    im = Image.new('RGBA', (shapes.base_width * command_count, shapes.base_height), (0, 0, 0, 0))
    draw = aggdraw.Draw(im)

    pen = aggdraw.Pen(fg_color, width=4)
    brush = aggdraw.Brush(fg_color)
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
            draw_button(draw, base_x, pen, brush, pushed=cmd)
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
                font = ImageFont.truetype(ttf, font_size, index=ttc_index)
            draw.flush()
            (im, draw_width) = draw_text(im, base_x, cmd, font, fg_color)
            draw = aggdraw.Draw(im)

        if is_paint:
            a = utils.move_symbol(symbol, base_x)
            draw.line(a, brush)
        elif is_outline:
            a = utils.move_symbol(symbol, base_x)
            draw.line(a, pen)
        index += 1
        base_x += draw_width

    ### Output
    draw.flush()
    im.save(output, quality=100)
