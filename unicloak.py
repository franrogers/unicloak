#!/usr/bin/env python

"""
Functions to conceal data in invisible characters within Unicode text.

This module allows you to conceal data by hiding it as invisible characters
within Unicode text.

No cryptography is applied; you'll want to encrypt and decrypt it separately.
"""

from __future__ import division, print_function
import math

__all__ = ['unicloak', 'unidecloak']


invisible_chars = [u'\u200b', u'\u2060']  # , u'\u2063', u'\ufeff']


# Adapted from an ActiveState recipe.
def base_n(num, n):
    """Change a  to a base-n number.
    Up to base-36 is supported without special notation."""
    num_rep = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f',
               16: 'g', 17: 'h', 18: 'i', 19: 'j', 20: 'k', 21: 'l',
               22: 'm', 23: 'n', 24: 'o', 25: 'p', 26: 'q', 27: 'r',
               28: 's', 29: 't', 30: 'u', 31: 'v', 32: 'w', 33: 'x',
               34: 'y', 35: 'z'}
    new_num_string = ''
    current = num
    while current != 0:
        remainder = current % n
        if 36 > remainder > 9:
            remainder_string = num_rep[remainder]
        elif remainder >= 36:
            remainder_string = '({0})'.format(remainder)
        else:
            remainder_string = str(remainder)
        new_num_string = remainder_string + new_num_string
        current = current // n
    return new_num_string


def unicloak(covert_text, overt_text):
    """
    Conceal covert_text within overt_text.
    """

    base = len(invisible_chars)
    width = len(base_n(255, base))

    def each(ch):
        return base_n(ord(ch), base).zfill(width)

    digits = ''.join(map(each, covert_text))

    invisible = ''.join(map(lambda ch: invisible_chars[int(ch, base)], digits))

    overt_text = ''.join(filter(lambda ch: not ch in invisible_chars,
                                overt_text))

    spaces_at = []
    for i in range(len(overt_text)):
        if overt_text[i] == ' ':
            spaces_at.append(i)

    steg_text = ''
    invisible_pos, overt_pos, space_pos = 0, 0, 0
    chunk_size = int(math.floor(len(invisible) / len(spaces_at) *
                                len(invisible)))  # TODO: need better algorithm
    while space_pos < len(spaces_at):
        steg_text += overt_text[overt_pos:spaces_at[space_pos]]

        steg_text += invisible[invisible_pos:invisible_pos+chunk_size]
        invisible_pos += chunk_size

        steg_text += overt_text[spaces_at[space_pos]]
        overt_pos = spaces_at[space_pos] + 1
        space_pos += 1
    steg_text += overt_text[overt_pos:]

    return steg_text


def unidecloak(cloaked_text):
    """
    Reveal the concealed text within cloaked_text.
    """

    base = len(invisible_chars)
    width = len(base_n(255, base))

    invisible = filter(lambda ch: ch in invisible_chars, cloaked_text)

    covert_text = ''
    for i in range(0, len(invisible), width):
        invisible_ch = (invisible[i:i+width] +
                        invisible_chars[0] * (i + width - len(invisible)))
        ch_digits = ''.join(map(lambda ich: str(invisible_chars.index(ich)),
                            invisible_ch))
        ch = unichr(int(ch_digits, base))
        covert_text += ch

    return covert_text


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("""\
{0}: conceal data in invisible characters within Unicode text
Usage:
       {0} OVERT_TEXT_FILE
         Conceal stdin within OVERT_TEXT_FILE; resulting text goes to stdout.
       {0} -d
         Outputs the concealed text in stdin to stdout."""
              .format(sys.argv[0]))
        sys.exit(1)

    if sys.argv[1] == '-d':
        cloaked_text = sys.stdin.read().decode('utf-8')
        covert_text = unidecloak(cloaked_text)
        print(covert_text.encode('utf-8'), end='')
    else:
        covert_text = sys.stdin.read().decode('utf-8')
        overt_text = file(sys.argv[1]).read().decode('utf-8')
        cloaked_text = unicloak(covert_text, overt_text)
        print(cloaked_text.encode('utf-8'), end='')
