import zigt
from fido2.hid import CtapHidDevice

key = next(CtapHidDevice.list_devices(), None)

def start():
    while True:
        shell = input("zigt > ")
        result, error = zigt.run('<stdin>', shell)

        if error:
            print(error.as_string())
        else:
            print(result)

if key:
    start()
else:
    print("access denied :(")
    exit()




