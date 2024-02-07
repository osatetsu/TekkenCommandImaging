#! python

import sys
from PIL import Image
import aggdraw

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

forward_up = (
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

## arrows are orderd calculator-button.
arrows = (None,
          back_down_symbol, down_symbol, foward_down_symbol,
          back_symbol, None, foward_symbol,
          back_up_symbol, up_symbol, forward_up,
          )

def move_arrow(symbol, x):
    '''
    '''
    result = []
    is_x = True
    for p in symbol:
        if is_x:
            result.append(p + (base_width * x))
        else:
            result.append(p)
        is_x = not is_x

    return tuple(result)


arrow_count = 0
for a in arrows:
    if a:
        arrow_count += 1

im = Image.new('RGBA', (base_width * arrow_count, base_height), (0, 0, 0, 0))
draw = aggdraw.Draw(im)
draw_work = aggdraw.Draw(im)

pen = aggdraw.Pen((255, 64, 64), width=4)
brush = aggdraw.Brush((255, 255, 255))

#draw.ellipse((8, 8, 8+48, 8+48), brush, pen)

index = 0
for a in arrows:
    if a:
        a = move_arrow(a, index)
        draw.line(a, brush)
        index += 1

### Output
draw.flush()
im.save('hoge.png', quality=100)
