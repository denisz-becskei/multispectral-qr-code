WINDOW_SIZE_X = 1080
WINDOW_SIZE_Y = 512
WINDOW_SIZE_CONCAT = str(WINDOW_SIZE_X) + "x" + str(WINDOW_SIZE_Y)
SIDE_PANEL_SIZE = 256, 512
QR_CANVAS_SIZE = 370

MODES = ["Normal", "Multispectral"]
VERSIONS = list()
for i in range(1, 28):
    VERSIONS.append("Version " + str(i))
