from values import MODES, VERSIONS


def new_doc(canvas, text_field, base, base2):
    canvas.delete("all")

    text_field.delete(1.0, "end")
    base.set(MODES[0])
    base2.set(VERSIONS[0])

