def padbytes(arr: bytearray, alignment: int, fillchar: bytes = b"\x00", offset: int = 0) -> int:
    arrlen = len(arr)
    padlen = (alignment - ((arrlen + offset) % alignment)) % alignment
    if padlen > 0:
        arr.extend(padlen * fillchar)
        return arrlen + padlen
    return arrlen
