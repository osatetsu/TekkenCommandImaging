#! python
#
# SVG ファイルは XML として扱う。
# 各エレメント(矢印などの図形)は、ローカル座標から transform で移動、回転させる。
# これらは、SVG ファイルを読み取って編集するライブラリが python に存在しないため、代替手段である。
#
# # 重要
# - 読み込むSVGファイル内の単位はすべて削除すること。例えばmm単位だと、メートルでもインチでも無いおかしな位置として計算されるため。
#

import copy
import sys
import xml.etree.ElementTree as ET
import svgelements as se
import pprint
from logging import getLogger, StreamHandler, DEBUG, ERROR

MARGIN_WIDTH = 16
EMPTY_SVG = """\
<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
</svg>
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
    shapes['root'] = ET.fromstring(EMPTY_SVG)

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
    if (is_debug):
        logger.debug(f"=== delimiter: x:{obj['box']['x']}, y:{obj['box']['y']}, w:{obj['box']['w']}, h:{obj['box']['h']}")

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

def draw_button(img, button_shapes, base_x, margin_width=MARGIN_WIDTH, push_color='#000000', **kwargs):
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
        new_transform = f"translate({draw_x}, 0)"
        btn.set('transform', new_transform)
        img.append(btn)

    return button_shapes['all_bbox']['x'] + button_shapes['all_bbox']['w']

def draw_shape(img, shape, base_x, margin_width=MARGIN_WIDTH, fill_color='#000000'):
    '''
    '''
    return draw_shape_rotate(img, shape, base_x, rotate_deg = 0, margin_width=margin_width, fill_color=fill_color)

def draw_shape_rotate(img, shape, base_x, rotate_deg, margin_width=MARGIN_WIDTH, fill_color='#000000'):
    '''
    '''

    draw_x = base_x + margin_width - shape['box']['x']
    box = shape['box']

    obj = copy.deepcopy(shape['element'])
    if (int(rotate_deg) == 0):
        new_transform = f"translate({draw_x}, 0)"
    else:
        new_transform = f" translate({draw_x}, 0) rotate({rotate_deg}, {box['cx']}, {box['cy']})"
    obj.set('transform', new_transform)
    img.append(obj)

    return shape['box']['w']

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
#    text = svgwrite.text.Text(text, base_x)
#    dwg.add(text)
    return None

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

    nums = {'1':True, '2':True, '3':True, '4':True, '6':True, '7':True, '8':True, '9':True, }
    buttons = {'LP':True, 'RP':True, 'LK':True, 'RK':True, 'WP':True, 'WK':True, }
    direction_to_deg = [None, 45 * 3, 45 * 2, 45 * 1, 45 * 4, None, 0, 45 * 5, 45 * 6, 45 * 7]

    ## Drawing.
    index = 0
    base_x = 0
    for cmd in command_list:
        symbol = None
        margin = MARGIN_WIDTH
        if cmd in nums:
            symbol = shapes['arrow']
            draw_width = draw_shape_rotate(dst, symbol, base_x, direction_to_deg[int(cmd)], margin_width=margin)
            logger.debug(f"{cmd}, {draw_width}, {symbol}")
        elif cmd == 'n' or cmd == 'N':
            symbol = shapes['neutral']
            draw_width = draw_shape(dst, symbol, base_x, margin_width=margin)
            logger.debug(f"{cmd}, {draw_width}, {symbol}")
        elif len(cmd) >= 2 and cmd[0:2] in buttons:
            draw_width = draw_button(dst, shapes['buttons'], base_x, margin_width=margin, pushed=cmd)
            logger.debug(f"{cmd}, {draw_width}, {symbol}")
        elif cmd == '>' or cmd == ',':
            symbol = shapes['delimiter']
            draw_width = draw_shape(dst, symbol, base_x, margin_width=margin)
            logger.debug(f"{cmd}, {draw_width}, {symbol}")
        elif cmd == '[':
            symbol = shapes['bracket']
            draw_width = draw_shape(dst, symbol, base_x, margin_width=margin)
            logger.debug(f"{cmd}, {draw_width}, {symbol}")
        elif cmd == ']':
            symbol = shapes['right_bracket']
            draw_width = draw_shape(dst, symbol, base_x, margin_width=margin)
            logger.debug(f"{cmd}, {draw_width}, {symbol}")
        else:
            ### any text
            if font is None:
                ######font = ImageFont.truetype(ttf, font_size, index=ttc_index)
                pass
            draw_text(dst, base_x, cmd, font, fg_color, margin_width=margin)
        if (is_debug):
            ## draw bounding box
            rect = ET.Element('rect')
            rect.set('x', str(base_x + MARGIN_WIDTH))
            rect.set('y', '0')
            rect.set('width', f"{draw_width}")
            rect.set('height', f"{ymax - 1}")
            rect.set('fill-opacity', '0%')
            rect.set('stroke', 'red')
            rect.set('stroke-width', '1')
            dst.append(rect)
        index += 1
        base_x += draw_width + margin

    ### Output
    view_w = base_x + MARGIN_WIDTH
    view_h = ymax + MARGIN_WIDTH
    dst.set('width', f"{view_w}")
    dst.set('height', f"{view_h}")
    dst.set('viewBox', f"{0} {0} {view_w} {view_h}")
    tree = ET.ElementTree(dst)
    tree.write(output, encoding='utf-8', xml_declaration=True)
