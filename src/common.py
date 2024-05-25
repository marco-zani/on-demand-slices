from math import floor

UDP_IP = "127.0.0.1"
UDP_PORT = 53550
BUFFER_SIZE = 2048


def set_margin(obj, size):
    obj.set_margin_top(size)
    obj.set_margin_bottom(size)
    obj.set_margin_start(size)
    obj.set_margin_end(size)


def get_children(obj):
    out = []
    child = obj.get_first_child()

    while child != None:
        out.append(child)

        sibling = child.get_next_sibling()
        child = sibling

    return out

def splitArray(arr:str):
    newLines = floor((arr.count("\n")-4)/2) -1
    index = 0
    while index < len(arr) and newLines > 0:
        if arr[index] == "\n":
            newLines -= 1
        index += 1

    while index < len(arr) and (
        arr[index] != "\n" or arr[index + 1] != "\n"
    ):
        index += 1

    outLeft = arr[:index]
    outRight = arr[index + 2 :]

    return outLeft, outRight


def formatDevices(devices):
    out = ""
    for dev in devices:
        conn = devices[dev]
        out = out + "<b>@" + dev + "</b>\n"

        if type(conn) != list:
            conn = [conn]

        

        for port, connDev in conn:
            if len(conn) < 2 or (port, connDev) == conn[-1]:
                out = out + "  └─ Eth" + port + " ── " + connDev + "\n\n"
            else:
                out = out + "  ├─ Eth" + port + " ── " + connDev + "\n"

    return out