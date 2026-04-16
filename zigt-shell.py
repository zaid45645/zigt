import zigt
from fido2.hid import CtapHidDevice
import sys
import time
import os

key = next(CtapHidDevice.list_devices(), None)


def type_writer_effect(text, speed):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()

def start():
    type_writer_effect("welcome to zigt!", 0.07)
    while True:
        try:
            shell = input("zigt > ")
            if shell == "exit()":
                break

            if next(CtapHidDevice.list_devices(), None) is None:
                type_writer_effect("\nkey removed :(", 0.07)
                type_writer_effect("session terminated >:(", 0.07)
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
        type_writer_effect("access denied :(", 0.07)
        type_writer_effect("(pro tip: plug in key to use!)", 0.07)
        sys.exit(1)




