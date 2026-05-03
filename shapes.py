#! python

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