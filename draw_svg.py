#! python
#
# # 方針
# SVG ファイルは XML として扱う。
# 各エレメント(矢印などの図形)は、ローカル座標から transform で移動、回転させる。
# これらは、SVG ファイルを読み取って編集するライブラリが python に存在しないための代替手段である。
#
# # 重要
# - 読み込むSVGファイル内の単位はすべて削除するか、px単位にすること。DPI計算により意図しない結果になるため。
#

import copy
import sys
import xml.etree.ElementTree as ET
import pprint
from logging import getLogger, StreamHandler, DEBUG, ERROR

import svgelements as se
from PIL import ImageFont

MARGIN_WIDTH = 16
EMPTY_SVG = """\
<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
</svg>
"""
SVG_TEXT_FONT = 'NotoSans-Regular.ttf'
SVG_TEXT_FILL_COLOR = '#ffffff'
SVG_TEXT_STROKE_COLOR = '#808080'
SVG_TEXT_STROKE_WIDTH = 2
SVG_STYLE_CLASS = 'svg-text-normal'
SVG_STYLE = """\
.""" + SVG_STYLE_CLASS + """ {
  font-family: "Noto Sans", sans-serif;
  font-weight: 600;
}
"""

is_debug = False
logger = getLogger(__name__)
log_handler = StreamHandler()
if (is_debug):
    log_handler.setLevel(DEBUG)
    logger.setLevel(DEBUG)
else:
    log_handler.setLevel(ERROR)
    logger.setLevel(ERROR)
logger.propagate = False

ET.register_namespace("", "http://www.w3.org/2000/svg")

def get_text_bounding_box(text, font_path, font_size):
    '''
    任意のテキストに対しバウンディングボックスを得る。
    大きさはレンダラーによって異なるため、呼び出し側にて少し余裕を持つこと。

    text: 
    font_path: font file
    font_size: pixels

    return: (width, height)
    '''
    font = ImageFont.truetype(font_path, font_size)
    
    left, top, right, bottom = font.getbbox(text)
    
    width = right - left
    height = bottom - top
    
    return width, height

def debug_rect(dst, x, y, w, h, stroke_color='red', stroke_width=1):
    '''
    Draw a debug rectangle on the SVG.
    Maybe, you can see bounding box of the element.
    '''
    rect = ET.Element('rect')
    rect.set('x', str(x))
    rect.set('y', str(y))
    rect.set('width', str(w))
    rect.set('height', str(h))
    rect.set('fill-opacity', '0%')
    rect.set('stroke', stroke_color)
    rect.set('stroke-width', str(stroke_width))
    dst.append(rect)

def load_element(svg_path, target_id):
    tree = ET.parse(svg_path)
    root = tree.getroot()

    xml_element = root.find(f'.//*[@id="{target_id}"]')
    if xml_element is None:
        sys.stderr.write("ERROR: Could not find id:\"{0}\" in \"{1}\".\n".format(target_id, svg_path))
        return None
    xml_element.attrib.pop('id', None)

    svg_elements = se.SVG.parse(svg_path)
    se_obj = None
    for e in svg_elements.elements():
        eid = e.id if hasattr(e, 'id') else e.values.get('id')
        if eid == target_id:
            se_obj = e
            break

    cx = cy = 0
    xmin = ymin = xmax = ymax = 0
    if se_obj and se_obj.bbox():
        xmin, ymin, xmax, ymax = se_obj.bbox()
        cx = xmin + (xmax - xmin) / 2
        cy = ymin + (ymax - ymin) / 2

    obj = {}
    obj['element'] = xml_element
    obj['box'] = {}
    obj['box']['x'] = xmin
    obj['box']['y'] = ymin
    obj['box']['w'] = xmax - xmin
    obj['box']['h'] = ymax - ymin
    obj['box']['cx'] = cx
    obj['box']['cy'] = cy
    
    return obj

def load_buttons_element(svg_path):
    tree = ET.parse(svg_path)
    root = tree.getroot()

    ids = ['LP', 'RP', 'LK', 'RK']

    xml_buttons = {}
    boxes = {}
    all_xmin = float('inf')
    all_ymin = float('inf')
    all_xmax = float('-inf')
    all_ymax = float('-inf')

    for key in ids:
        xml_element = root.find(f'.//*[@id="{key}"]')
        if xml_element is None:
            sys.stderr.write("ERROR: Could not find id:\"{0}\" in \"{1}\".\n".format(key, svg_path))
            return None
        xml_element.attrib.pop('id', None)
        xml_buttons[key] = xml_element
    
        svg_elements = se.SVG.parse(svg_path)
        se_obj = None
        for e in svg_elements.elements():
            eid = e.id if hasattr(e, 'id') else e.values.get('id')
            if eid == key:
                se_obj = e
                break

        cx = cy = 0
        xmin = ymin = xmax = ymax = 0
        if se_obj and se_obj.bbox():
            xmin, ymin, xmax, ymax = se_obj.bbox()
            cx = xmin + (xmax - xmin) / 2
            cy = ymin + (ymax - ymin) / 2

        boxes[key] = {}
        boxes[key]['x'] = xmin
        boxes[key]['y'] = ymin
        boxes[key]['w'] = xmax - xmin
        boxes[key]['h'] = ymax - ymin
        boxes[key]['cx'] = cx
        boxes[key]['cy'] = cy

        if xmin < all_xmin:
            all_xmin = xmin
        if xmax > all_xmax:
            all_xmax = xmax
        if ymin < all_ymin:
            all_ymin = ymin
        if ymax > all_ymax:
            all_ymax = ymax
    
    obj = {}
    obj['elements'] = xml_buttons
    obj['boxes'] = boxes
    obj['all_bbox'] = {}
    obj['all_bbox']['x'] = xmin
    obj['all_bbox']['w'] = xmax - xmin
    obj['all_bbox']['y'] = ymin
    obj['all_bbox']['h'] = ymax - ymin

#    pprint.pprint(obj)
    return obj

def load_shapes():
    '''
    Currently using fixed filenames.
    - right_arrow.svg : Directory
    - star.svg : Neutral
    - 4buttons.svg : Buttuns
    - bracket.svg : Bracket
    - delimiter.svg : '>'
    '''

    shapes = {}
    ymax = MARGIN_WIDTH * 4

    ### XML root ###
    shapes['root'] = ET.fromstring(EMPTY_SVG)
    text = ET.Element('style')
    text.set('type', 'text/css')
    text.text = SVG_STYLE
    shapes['root'].append(text)

    ### Arrow ###
    obj = load_element('assets/right_arrow.svg', 'target')
    if obj is None:
        return None
    shapes['arrow'] = obj
    h = obj['box']['y'] + obj['box']['h']
    if ymax < h:
        ymax = h

    ### Neutral ###
    obj = load_element('assets/star.svg', 'target')
    if obj is None:
        return None
    shapes['neutral'] = obj
    h = obj['box']['y'] + obj['box']['h']
    if ymax < h:
        ymax = h

    ### Bracket ###
    obj = load_element('assets/bracket.svg', 'target')
    if obj is None:
        return None
    shapes['bracket'] = obj
    h = obj['box']['y'] + obj['box']['h']
    if ymax < h:
        ymax = h

    ### Delimiter ###
    obj = load_element('assets/delimiter.svg', 'target')
    if obj is None:
        return None
    shapes['delimiter'] = obj
    h = obj['box']['y'] + obj['box']['h']
    if ymax < h:
        ymax = h

    ### Buttuns ###
    obj = load_buttons_element('assets/4buttons.svg')
    if obj is None:
        return None
    shapes['buttons'] = obj
    h = obj['all_bbox']['y'] + obj['all_bbox']['h']
    if ymax < h:
        ymax = h

    return shapes, ymax

def replace_fill_style(element, fill_color):
    style = element.get('style', '')
    if 'fill:' in style:
        styles = [s for s in style.split(';') if not s.strip().startswith('fill')]
        styles.append(f"fill:{fill_color}")
        element.set('style', ';'.join(styles))
    return

def draw_button(img, button_shapes, base_x, base_y, margin_width=MARGIN_WIDTH, push_color='#000000', **kwargs):
    '''
    kwargs:
        LP : Push Left-Punch.
        RP : Push Right-Punch.
        WP : Both LP and RP.
        LK : Push Left-Kick.
        RK : Push Right-Kick.
        WK : Both LK and RK.
        pushed : Accept all Punch and Kick notation. e.g. 'LP', 'LP+RK' etc...
    '''
    params = {
        'LP': True,
        'LK': True,
        'RP': True,
        'RK': True,
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

    draw_x = base_x + margin_width
    for key in params:
        btn = copy.deepcopy(button_shapes['elements'][key])
        if key in push_buttons:
            btn.set('fill', push_color)
            replace_fill_style(btn, push_color)
        new_transform = f"translate({draw_x}, {base_y})"
        btn.set('transform', new_transform)
        img.append(btn)

    return button_shapes['all_bbox']['x'] + button_shapes['all_bbox']['w']

def draw_shape(img, shape, base_x, base_y, need_h_mirror=False, margin_width=MARGIN_WIDTH, fill_color='#000000', **kwargs):
    '''
    '''
    return draw_shape_rotate(img, shape, base_x, base_y, rotate_deg = 0, need_h_mirror=need_h_mirror, margin_width=margin_width, fill_color=fill_color)

def draw_shape_rotate(img, shape, base_x, base_y, rotate_deg, need_h_mirror=False, margin_width=MARGIN_WIDTH, fill_color='#000000', **kwargs):
    '''
    '''

    draw_x = base_x + margin_width - shape['box']['x']
    box = shape['box']

    obj = copy.deepcopy(shape['element'])
    translate = f"translate({draw_x}, {base_y})"
    rotate = ''
    mirror = ''

    if (int(rotate_deg) != 0):
        rotate = f"rotate({rotate_deg}, {box['cx']}, {box['cy']})"
    if (need_h_mirror):
        mirror = f"scale(-1, 1) translate({-box['cx'] * 2}, 0)"

    obj.set('transform', f"{translate} {rotate} {mirror}")
    img.append(obj)

    return shape['box']['w']

def draw_text(dst, base_x, ymax, text, font_size=32, margin_width=MARGIN_WIDTH, **kwargs):
    '''
    dst:
    base_x:
    text:
    ymax:
    font_size:
    margin_width:
    kwargs:
    '''

    render_y = int(ymax * 3 / 4)

    w, h = get_text_bounding_box(text, SVG_TEXT_FONT, font_size)
    logger.debug(f"draw_text: text:\"{text}\", font_size:{font_size}, w:{w}, h:{h}")
    # 表示する環境に依存するが、文字の描画は stroke の幅分だけ大きくなるため、余裕を持たせる。
    w += len(text) * (SVG_TEXT_STROKE_WIDTH + 4)

    e = ET.Element('text')
    e.set('class', SVG_STYLE_CLASS)
    e.set('x', str(base_x + margin_width))
    e.set('y', f"{render_y}")
    e.set('font-size', f"{font_size}px")
    e.set('style', f"stroke-width:{SVG_TEXT_STROKE_WIDTH}; stroke:{SVG_TEXT_STROKE_COLOR}; fill:{SVG_TEXT_FILL_COLOR};")
    e.text = text
    dst.append(e)

    return w

def draw_command(output, ttf, font_size, ttc_index, command_list, fg_color, **kwargs):
    global is_debug
    is_debug = kwargs['debug']
    if (is_debug):
        logger.removeHandler(log_handler)
        log_handler.setLevel(DEBUG)
        logger.setLevel(DEBUG)
        logger.addHandler(log_handler)

    shapes, ymax = load_shapes()
    if shapes is None:
        sys.stderr.write("Abort!\n")
        return

    dst = shapes['root']
    font = None

    nums = {'1':True, '2':True, '3':True, '4':True, '6':False, '7':True, '8':True, '9':True, }
    buttons = {'LP':True, 'RP':True, 'LK':True, 'RK':True, 'WP':True, 'WK':True, }
    direction_to_deg = [None, 45 * 3, 45 * 2, 45 * 1, 45 * 4, None, 0, 45 * 5, 45 * 6, 45 * 7]

    ## Drawing.
    index = 0
    base_x = 0
    base_y = MARGIN_WIDTH
    for cmd in command_list:
        symbol = None
        margin = MARGIN_WIDTH
        if cmd in nums:
            symbol = shapes['arrow']
            y = base_y
            draw_width = draw_shape_rotate(dst, symbol, base_x, y, direction_to_deg[int(cmd)], margin_width=margin)
            logger.debug(f"{cmd}, {draw_width}, {y}, {symbol}")
        elif cmd == 'n' or cmd == 'N':
            symbol = shapes['neutral']
            y = base_y #symbol['box']['y']
            draw_width = draw_shape(dst, symbol, base_x, y, margin_width=margin)
            logger.debug(f"{cmd}, {draw_width}, {symbol}")
        elif len(cmd) >= 2 and cmd[0:2] in buttons:
            draw_width = draw_button(dst, shapes['buttons'], base_x, base_y, margin_width=margin, pushed=cmd)
            logger.debug(f"{cmd}, {draw_width}, {symbol}")
        elif cmd == '>':
            symbol = shapes['delimiter']
            y = base_y #(symbol['box']['y'] + symbol['box']['h']) / 2
            draw_width = draw_shape(dst, symbol, base_x, y, margin_width=margin)
            logger.debug(f"{cmd}, {draw_width}, {symbol}")
        elif cmd == '[':
            symbol = shapes['bracket']
            y = base_y #(symbol['box']['y'] + symbol['box']['h']) / 2
            draw_width = draw_shape(dst, symbol, base_x, y, margin_width=margin)
            logger.debug(f"{cmd}, {draw_width}, {symbol}")
        elif cmd == ']':
            symbol = shapes['bracket']
            y = base_y #(symbol['box']['y'] + symbol['box']['h']) / 2
            draw_width = draw_shape(dst, symbol, base_x, y, need_h_mirror=True, margin_width=margin)
            logger.debug(f"{cmd}, {draw_width}, {symbol}")
        else:
            y = ymax + base_y
            draw_width = draw_text(dst, base_x, y, cmd, margin_width=margin)
            logger.debug(f"{cmd}, {draw_width}, {symbol}")
        if (is_debug):
            ## draw bounding box
            debug_rect(dst, base_x + margin, base_y, draw_width, ymax - 1, stroke_color='red', stroke_width=1)
        index += 1
        base_x += draw_width + margin

    ### Output
    view_w = base_x + MARGIN_WIDTH
    view_h = ymax + MARGIN_WIDTH * 2
    dst.set('width', f"{view_w}")
    dst.set('height', f"{view_h}")
    dst.set('viewBox', f"{0} {0} {view_w} {view_h}")
    tree = ET.ElementTree(dst)
    tree.write(output, encoding='utf-8', xml_declaration=True)
