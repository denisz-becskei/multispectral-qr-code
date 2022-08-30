import pyqrcode
import random

charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789$/'"


def make_string():
    output_string = ''
    for i in range(random.randint(10, 205)):
        character = random.randint(0, len(charset))
        output_string += str(character)
    return output_string


for i in range(0, 1000):
    qr = pyqrcode.create(make_string(), error="M")
    qr.png('normal_qr/train' + str(i + 1) + '.jpg', scale=random.randint(4, 10))
