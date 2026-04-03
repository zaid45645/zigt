import zigt

while True:
    shell = input("zigt > ")
    result, error = zigt.run(shell)

    if error:
        print(error.as_string())
    else:
        print(result)

