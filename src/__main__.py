import sys


if __name__ == "__main__":
    print("Working")
    params = len(sys.argv)
    print(params)
    for x in range(params):
        print(sys.argv[x])
        if x == 0:
            continue
        if "--functions_definition" == sys.argv[x]:
            try:
                open(sys.argv[x + 1])
            except ValueError:
                raise ValueError("file not corresponding")
        elif "--input" == sys.argv[x]:
            input = sys.argv[x + 1]
        elif "--output" == sys.argv[x]:
            output = sys.argv[x + 1]
