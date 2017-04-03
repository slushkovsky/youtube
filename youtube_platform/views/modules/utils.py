from base64 import b64encode
from itertools import zip_longest
import random


def file_as_url(arr):
    flattened = '\n'.join(arr).encode()
    base64 = b64encode(flattened)
    return 'data:application/octet-stream;charset=utf-16le;base64,' + base64.decode()


def create_social_bases(channels):
    youtube = [channel['channelUrl'] for channel in channels]
    vk = []
    ok = []
    inst = []
    fb = []
    for c in channels:
        socials = c['channelInfo']['socials']
        if 'VK' in socials:
            vk += [socials['VK']]
        if 'Facebook' in socials:
            fb += [socials['Facebook']]
        if 'Odnoklassniki' in socials:
            ok += [socials['Odnoklassniki']]
        if 'Instagram' in socials:
            inst += [socials['Instagram']]

    dbs = []
    if len(youtube) > 0:
        dbs += [
            {'name': 'youtube', 'db': file_as_url(youtube)}
        ]
    if len(vk) > 0:
        dbs += [
            {'name': 'vk', 'db': file_as_url(vk)}
        ]
    if len(fb) > 0:
        dbs += [
            {'name': 'facebook', 'db': file_as_url(fb)}
        ]
    if len(ok) > 0:
        dbs += [
            {'name': 'odnoklassniki', 'db': file_as_url(ok)}
        ]
    if len(inst) > 0:
        dbs += [
            {'name': 'instagram', 'db': file_as_url(inst)}
        ]

    return dbs


def grouper(iterable, n, fillvalue=None):
    """
    Collect data into fixed-length chunks or blocks
    """
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


##################################################
# RANDOM COLOR GENERATOR                         #
# Thx for https://gist.github.com/adewes/5884820 #
##################################################
def get_random_color(pastel_factor=0.5):
    return [(x + pastel_factor) / (1.0 + pastel_factor) for x in
            [random.uniform(0, 1.0) for i in [1, 2, 3]]]


def color_distance(c1, c2):
    return sum([abs(x[0] - x[1]) for x in zip(c1, c2)])


def generate_new_color(existing_colors, pastel_factor=0.5):
    max_distance = None
    best_color = None
    for i in range(0, 100):
        color = get_random_color(pastel_factor=pastel_factor)
        if not existing_colors:
            return color
        best_distance = min([color_distance(color, c) for c in existing_colors])
        if not max_distance or best_distance > max_distance:
            max_distance = best_distance
            best_color = color
    return best_color


def generate_colors(generate_hex=False, pastel_factor=0.5):
    colors = []
    while True:
        color = generate_new_color(colors, pastel_factor)
        if generate_hex:
            color = '#{:02x}{:02x}{:02x}'.format(
                *[int(c * 255) for c in color]
            )
        yield color
