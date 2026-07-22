def numbers():
    yield 1
    print("After 1 was done")
    yield 2
    print("After 2 was done")
    yield 3
    print("After 3 was done")


gen = numbers()
print(next(gen))
print(next(gen))
print(next(gen))
print(next(gen))


class XYZ:

    def __init__(self, a, b, c, d) -> None:
        pass


class One:

    def __init__(self, a: XYZ, b, c, d) -> None:
        pass
    pass

class Two:

    def __init__(self, one: One) -> None:
        self.one = one

# two = Two(One(XYZ(1,2,4,5),2,3,4))