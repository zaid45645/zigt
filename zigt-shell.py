import zigt
from fido2.hid import CtapHidDevice
import sys

key = next(CtapHidDevice.list_devices(), None)

def start():
    while True:
        try:
            shell = input("zigt > ")
            if next(CtapHidDevice.list_devices(), None) is None:
                print("\nsession terminated >:(")
                break

            result, error = zigt.run('<stdin>', shell)

            if error:
                print(error.as_string())
            else:
                print(result)
        except (EOFError, KeyboardInterrupt):
            break

if __name__ == "__main__":
    if key:
        start()
    else:
        print("access denied :(")
        sys.exit(1)




