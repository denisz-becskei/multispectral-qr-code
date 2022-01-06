from utils import is_cjk, is_alphanum


def decide_encoding(text: str):
    """
    Tests which encoding is the best for the written string.
    Source: https://www.thonky.com/qr-code-tutorial/

        >>>decide_encoding("255645")
        numeric
        >>>decide_encoding("IAMALPHANUMERIC")
        alphanumeric
        >>>decide_encoding("hi i am a byte string")
        binary

    :param text: The original input text
    :return: str
    """
    if text.isnumeric():
        return "numeric"
    elif is_alphanum(text):
        return "alphanumeric"
    else:
        for letter in text:
            if is_cjk(letter):
                return "kanji"
        return "binary"


def decide_smallest_available_version(encoding: str, text: str, multispectral: bool):
    """
    Returns the smallest available version of QR Code that can be made with the input string.
    The values are multiplied by 3 for multispectral modification, because the amount of data that can be stored
    in a multispectral QR Code is divided by 3 channels.

        >>>decide_smallest_available_version("numeric", "12321231", False)
        1
        >>>decide_smallest_available_version("numeric", "12321231", True)
        1
        >>>decide_smallest_available_version("binary", "never gonna give you UP, never gonna let you DOWN", False)
        4
        >>>decide_smallest_available_version("binary", "never gonna give you UP, never gonna let you DOWN", True)
        2

    :param encoding: Encoding used to encode the QR Code
    :param text: The input string
    :param multispectral: Is Multispectral option selected
    :return: int
    """
    version = 1
    if encoding == "numeric":
        numeric_capacities = [34, 63, 101, 149, 202, 255, 293, 365, 432, 513, 604, 691, 796, 871, 991, 1082, 1212, 1346,
                              1500, 1600, 1708, 1872, 2059, 2188, 1395, 2544, 2701]
        if multispectral:
            numeric_capacities = [x * 3 for x in numeric_capacities]
        for capacity in numeric_capacities:
            if len(text) <= capacity:
                return version
            version += 1
        # TODO: Throw error
    elif encoding == "alphanumeric":
        alphanumeric_capacities = [20, 38, 61, 90, 122, 154, 178, 221, 262, 311, 366, 419, 483, 528, 600, 656, 734, 816,
                                   909, 970, 1035, 1134, 1248, 1326, 1451, 1542, 1637]
        if multispectral:
            alphanumeric_capacities = [x * 3 for x in alphanumeric_capacities]
        for capacity in alphanumeric_capacities:
            if len(text) <= capacity:
                return version
            version += 1
        # TODO: Throw error
    elif encoding == "binary":
        byte_capacities = [14, 26, 42, 62, 84, 106, 122, 152, 180, 213, 251, 287, 331, 362, 412, 450, 504, 560, 624,
                           666, 711, 779, 857, 911, 997, 1059, 1125]
        if multispectral:
            byte_capacities = [x * 3 for x in byte_capacities]
        for capacity in byte_capacities:
            if len(text) <= capacity:
                return version
            version += 1
        # TODO: Throw error
    else:
        kanji_capacities = [8, 16, 26, 38, 52, 65, 75, 93, 111, 131, 155, 177, 204, 223, 254, 277, 310, 345, 384, 410,
                            438, 480, 528, 561, 614, 652, 692]
        if multispectral:
            kanji_capacities = [x * 3 for x in kanji_capacities]
        for capacity in kanji_capacities:
            if len(text) <= capacity:
                return version
            version += 1
        # TODO: Throw error
