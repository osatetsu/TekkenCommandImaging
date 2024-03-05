#! python

import sys
from PIL import Image, ImageDraw, ImageFont
import aggdraw
import pyparsing as pp
import argparse
import collections

### Must be a multiple of 8.
base_width = 64
base_height = 64

margin = 4

back_down_symbol = (
    4, 60,
    48, 60,
    36, 48,
    60, 24,
    40, 4,
    16, 28,
    4, 16,
    4, 60,
    48, 60,
)

down_symbol = (
    32, 60,
    60, 32,
    48, 32,
    48, 4,
    16, 4,
    16, 32,
    4, 32,
    32, 60,
    60, 32,
)

foward_down_symbol = (
    60, 60,
    60, 16,
    48, 28,
    24, 4,
    4, 24,
    28, 48,
    16, 60,
    60, 60,
    60, 16,
)

back_symbol = (
    4, 32,
    32, 60,
    32, 44,
    60, 44,
    60, 20,
    32, 20,
    32, 4,
    4, 32,
    32, 60,
)

foward_symbol = (
    60, 32,
    32, 4,
    32, 20,
    4, 20,
    4, 44,
    32, 44,
    32, 60,
    60, 32,
    32, 4,
)

back_up_symbol = (
    4, 4,
    4, 48,
    16, 36,
    40, 60,
    60, 40,
    36, 16,
    48, 4,
    4, 4,
    4, 48,
)

up_symbol = (
    32, 4,
    4, 32,
    16, 32,
    16, 60,
    48, 60,
    48, 32,
    60, 32,
    32, 4,
    4, 32,
)

forward_up_symbol = (
    60, 4,
    16, 4,
    28, 16,
    4, 40,
    24, 60,
    48, 36,
    60, 48,
    60, 4,
    16, 4,
)

neutral_symbol = (
    32, 8,
    24, 20,
    12, 20,
    20, 32,
    12, 52,
    32, 40,
    52, 52,
    44, 32,
    52, 20,
    40, 20,
    32, 8,
    24, 20,
)

delimiter_symbol = (
    40, 32,
    28, 20,
    28, 44,
    40, 32,
    28, 20,
)

start_slip_symbol = (
    60, 4,
    48, 4,
    48, 60,
    60, 60,
)

end_slip_symbol = (
    4, 4,
    16, 4,
    16, 60,
    5, 60,
)

## arrows are orderd Tenkey.
arrows = (None,
          back_down_symbol, down_symbol, foward_down_symbol,
          back_symbol, None, foward_symbol,
          back_up_symbol, up_symbol, forward_up_symbol,
          )

def flatten(l):
    '''
    Thanks for:
    https://stackoverflow.com/questions/2158395/flatten-an-irregular-arbitrarily-nested-list-of-lists
    '''
    for el in l:
        if isinstance(el, collections.abc.Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el

def move_symbol(symbol, x):
    '''
    '''
    result = []
    is_x = True
    for p in symbol:
        if is_x:
            result.append(p + x)
        else:
            result.append(p)
        is_x = not is_x

    return tuple(result)

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
    box = draw.textbbox((base_x, margin), text, font=font)
    text_w = box[2] - box[0]
    if base_width < text_w:
        new_img = Image.new('RGBA', (w + text_w, base_height), (0, 0, 0, 0))
        new_img.paste(img, (0, 0))
        img = new_img
        draw = ImageDraw.Draw(img)

    draw.text((base_x, margin), text, fg_color, font=font)
    return (img, text_w)

def parse_command(cmd_str):
    directional_pattern = pp.Char("12346789nN")
    text = pp.quotedString.setParseAction( pp.removeQuotes )
    button_pattern = pp.Or([pp.CaselessLiteral('LP'), pp.CaselessLiteral('RP'), pp.CaselessLiteral('WP'),
                            pp.CaselessLiteral('LK'), pp.CaselessLiteral('RK'), pp.CaselessLiteral('WK')])
    slip_pattern = pp.Group(pp.Literal("[") + button_pattern * 2 + pp.Literal("]"))
    delimitor_pattern = pp.Or([pp.Literal('>'), pp.Literal(',')])
    sametime_op = pp.one_of('+')
    sametime_button = pp.Combine(button_pattern + (sametime_op + button_pattern)[1, ...]).ignore_whitespace(True)

    command_pattern = pp.OneOrMore(pp.Or([directional_pattern, button_pattern, slip_pattern, delimitor_pattern, sametime_button, text]))

    parsed_list = command_pattern.parse_string(cmd_str)
    # Nested list to flat list.
    result = flatten(parsed_list)
    return list(result)

def draw_command(output, ttf, font_size, ttc_index, command_list, fg_color):
    command_count = len(command_list)
    im = Image.new('RGBA', (base_width * command_count, base_height), (0, 0, 0, 0))
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
        draw_width = base_width
        if cmd in nums:
            symbol = arrows[int(cmd)]
            is_paint = True
        elif cmd == 'n' or cmd == 'N':
            symbol = neutral_symbol
            is_paint = True
        elif len(cmd) >= 2 and cmd[0:2] in buttons:
            draw_button(draw, base_x, pen, brush, pushed=cmd)
        elif cmd == '>' or cmd == ',':
            symbol = delimiter_symbol
            is_paint = True
        elif cmd == '[':
            symbol = start_slip_symbol
            is_outline = True
        elif cmd == ']':
            symbol = end_slip_symbol
            is_outline = True
        else:
            ### any text
            if font is None:
                font = ImageFont.truetype(ttf, font_size, index=ttc_index)
            draw.flush()
            (im, draw_width) = draw_text(im, base_x, cmd, font, fg_color)
            draw = aggdraw.Draw(im)

        if is_paint:
            a = move_symbol(symbol, base_x)
            draw.line(a, brush)
        elif is_outline:
            a = move_symbol(symbol, base_x)
            draw.line(a, pen)
        index += 1
        base_x += draw_width

    ### Output
    draw.flush()
    im.save(output, quality=100)

def main():
    desc = '''\
Generate png-image input Tekken command text.
Commands are supporting Tenkey-notation.
This notation corresponds as follows.

 7 8 9   LP RP (both 'WP')
 4 n 6 
 1 2 3   LK RK (both 'WK')

e.g. Fujin-ken is '6n23RP'.
'''

    ## Arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=desc)
    parser.add_argument("--debug", "-d", action='store_true', help="Enable debug message.")
    parser.add_argument("--output", "-o", required=True, type=str, help="Output png filename.")
    parser.add_argument("--truetype-font", type=str, default="YuGothR.ttc", help="TrueType font file for text drawing.")
    parser.add_argument("--font-size", type=int, default=48, help="TrueType font file for text drawing.")
    parser.add_argument("--ttc-index", type=int, default=1, help="TrueType Collection (*.TTC) index.")
    fg_group = parser.add_mutually_exclusive_group()
    fg_group.add_argument("--fg-white", action='store_true', help='Changed foreground color to White (default).')
    fg_group.add_argument("--fg-black", action='store_true', help='Changed foreground color to Black.')
    fg_group.add_argument("--fg-grey", action='store_true', help='Changed foreground color to Grey/Gray.')
    fg_group.add_argument("--fg-gray", action='store_true', help='Changed foreground color to Grey/Gray.')
    parser.add_argument("command", type=str, help="Tekken command.")
    args = parser.parse_args()

    fg_color = (255, 255, 255)
    if args.fg_white:
        pass
    elif args.fg_black:
        fg_color = (0, 0, 0)
    elif args.fg_grey or args.fg_gray:
        fg_color = (128, 128, 128)

    ## Tekken command.
    command = parse_command(args.command)
    if args.debug:
        print('parsed result:', command)
    
    ## Draw command.
    draw_command(args.output, args.truetype_font, args.font_size, args.ttc_index, command, fg_color)

if __name__ == '__main__':
    main()
