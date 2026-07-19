#! python

import pyparsing as pp
import argparse
import collections

import draw_svg

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

def parse_command(cmd_str):
    directional_pattern = pp.Char("12346789nN")
    text = pp.quotedString.set_parse_action( pp.removeQuotes )
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

def main():
    desc = '''\
Generate SVG-image input Tekken command text.
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
    parser.add_argument("--output", "-o", required=True, type=str, help="Output svg filename.")

    # @not implemented yet
    parser.add_argument("--truetype-font", type=str, default="NotoSans-Regular.ttf", help="TrueType font file for text drawing.")

    # @not implemented yet
    parser.add_argument("--font-size", type=int, default=48, help="TrueType font file for text drawing.")

    parser.add_argument("command", type=str, help="Tekken command.")
    args = parser.parse_args()

    ## Tekken command.
    command = parse_command(args.command)
    if args.debug:
        print('parsed result:', command)
    
    ## Draw command.
    draw_svg.draw_command(args.output, args.truetype_font, args.font_size, command, debug=args.debug)

if __name__ == '__main__':
    main()
