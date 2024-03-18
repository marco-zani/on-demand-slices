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

def splitArray(arr):
    splitIndex = len(arr) // 2
    while splitIndex < len(arr) and (
        arr[splitIndex] != "\n" or arr[splitIndex + 1] != "\n"
    ):
        splitIndex += 1

    outLeft = arr[:splitIndex]
    outRight = arr[splitIndex + 2 :]

    return outLeft, outRight


def formatDevices(devices):
    out = ""
    for dev in devices:
        conn = devices[dev]
        out = out + "<b>@" + dev + "</b>\n"

        if type(conn) != list:
            conn = [conn]

        lastItem = conn[-1]

        for port, connDev in conn:
            if (port, connDev) == lastItem:
                out = out + "  └─ Eth" + port + " ── " + connDev + "\n\n"
            else:
                out = out + "  ├─ Eth" + port + " ── " + connDev + "\n"

    return out