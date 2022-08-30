from PIL import Image
import pyqrcode
import os


def is_cjk(character):
    """"
    Checks whether character is CJK.

        >>> is_cjk(u'\u33fe')
        True
        >>> is_cjk(u'\uFE5F')
        False

    :param character: The character that needs to be checked.
    :type character: char
    :return: bool
    """
    return any([start <= ord(character) <= end for start, end in
                [(4352, 4607), (11904, 42191), (43072, 43135), (44032, 55215),
                 (63744, 64255), (65072, 65103), (65381, 65500),
                 (131072, 196607)]
                ])


def is_alphanum(text: str):
    """
    Checks whether text is alphanumerical.

        >>> is_alphanum("AB12C4")
        True
        >>> is_alphanum("Hello World!")
        False

    :param text: The text that needs to be checked.
    :return: bool
    """

    for letter in text:
        if not (65 <= ord(letter) <= 90 or 48 <= ord(letter) <= 57):
            return False
    return True


def get_hard_limit(version: int, encoding: str):
    """
    Every QR Code has a character limit, aka an amount of characters a QR Code can store. These limits are hard coded
    depending on version and encoding. This function gives the amount of storable characters for a specific version QR
    Code with a specific encoding.

        >>>get_hard_limit(1, "numeric")
        34
        >>>get_hard_limit(4, "binary")
        62

    :param version: The version of the QR Code we need the storage capacity for
    :param encoding: The encoding of the QR Code we need the storage capacity for
    :return: int
    """
    if encoding == "numeric":
        return [34, 63, 101, 149, 202, 255, 293, 365, 432, 513, 604, 691, 796, 871, 991, 1082, 1212, 1346,
                1500, 1600, 1708, 1872, 2059, 2188, 1395, 2544, 2701][version - 1]
    if encoding == "alphanumeric":
        return [20, 38, 61, 90, 122, 154, 178, 221, 262, 311, 366, 419, 483, 528, 600, 656, 734, 816,
                909, 970, 1035, 1134, 1248, 1326, 1451, 1542, 1637][version - 1]
    if encoding == "binary":
        return [14, 26, 42, 62, 84, 106, 122, 152, 180, 213, 251, 287, 331, 362, 412, 450, 504, 560, 624,
                666, 711, 779, 857, 911, 997, 1059, 1125][version - 1]
    return [8, 16, 26, 38, 52, 65, 75, 93, 111, 131, 155, 177, 204, 223, 254, 277, 310, 345, 384, 410,
            438, 480, 528, 561, 614, 652, 692][version - 1]


def create_qr_code(text: str, version: int, encoding: str):
    """
    Creates the QR Code. Function to avoid repeating code.
    :param text: Text to encode
    :param version: Version to encode the text in
    :param encoding: Encoding to use for the QR Code
    :return: pyqrcode.QRCode
    """
    qr = pyqrcode.create(text, error="M", mode=encoding, version=version)
    return qr


def merge_color_channels(version: int, img1: Image, img2: Image, img3: Image = None):
    """
    Merging 2 or 3 QR Codes by color. The premise is simple. We check every single pixel on the 3 QR Codes (which should
    be Red, Green and Blue if we are using the Multispectral setting) and adds the RGB color values together with some
    exceptions so we remain in the 0-255 color range.

        >>>merge_color_channels(1, img1, img2, img3)
        A new QR Code where the color channels are merged together for all 3 QR Codes
        >>>merge_color_channels(2, img1, img2)
        A new QR Code where the color channels are merged together with an additional blank image as a dummy for the
        missing image (needed when the text is not long enough to use all 3 channels).

    :param version: The version of the encoded QR Codes - needed for output image size calculation
    :param img1: The first generated QR Code - RED
    :param img2: The second generated QR Code - GREEN
    :param img3: The third generated QR Code - BLUE
    :return: void
    """
    output_size = 200 + version * 32
    if img3 is None:
        dummy_img3 = Image.new("RGB", (output_size, output_size), color="black")
    else:
        dummy_img3 = img3

    output = Image.new("RGB", (output_size, output_size), color="white")
    output_pixel_map = output.load()

    for i in range(0, output_size):
        for j in range(0, output_size):
            img1_current_pixel = img1.getpixel((i, j))
            img2_current_pixel = img2.getpixel((i, j))
            img3_current_pixel = dummy_img3.getpixel((i, j))

            r = 0
            g = 0
            b = 0

            if img1_current_pixel != (255, 255, 255):
                r += img1_current_pixel[0]
                g += img1_current_pixel[1]
                b += img1_current_pixel[2]
            if img2_current_pixel != (255, 255, 255):
                r += img2_current_pixel[0]
                g += img2_current_pixel[1]
                b += img2_current_pixel[2]
            if img3_current_pixel != (255, 255, 255):
                r += img3_current_pixel[0]
                g += img3_current_pixel[1]
                b += img3_current_pixel[2]

            output_pixel_map[i, j] = (r, g, b)

    for i in range(0, output_size):
        for j in range(0, output_size):
            if output_pixel_map[i, j] == (255, 255, 255):
                output_pixel_map[i, j] = (0, 0, 0)
            elif output_pixel_map[i, j] == (0, 0, 0):
                output_pixel_map[i, j] = (255, 255, 255)

    output.save("qr_to_show.png")
    if os.path.exists("./qr1.png"):
        if os.path.exists("./qr3.png"):
            end = 4
        else:
            end = 3
        for i in range(1, end):
            os.remove("./qr" + str(i) + ".png")

