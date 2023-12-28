import random

from HttpResponse import body


class ByteRanges:
    def __init__(self, length: int, boundary: str = ''.join(random.choices('0123456789abcdef', k=16))):
        if length <= 0:
            raise ValueError('Length must be positive.')
        if not boundary:
            raise ValueError('Boundary must be non-empty.')

        self._length = length
        self._boundary = boundary
        self._ranges = []

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, value: int):
        if value <= 0:
            raise ValueError('Length must be positive.')
        self._length = value

    @property
    def boundary(self):
        return self._boundary

    @boundary.setter
    def boundary(self, value: str):
        if not value:
            raise ValueError('Boundary must be non-empty.')
        self._boundary = value

    def append(self, obj, start):
        raw, body_type = body(obj)
        end = start + len(raw) - 1
        if not 0 <= start <= end < self._length:
            raise ValueError('Range out of bounds.')
        self._ranges.append({
            'type': body_type,
            'start': start,
            'end': end,
            'raw': raw
        })

    def __str__(self):
        return f'\r\n--{self._boundary}\r\n'.join([
            '',
            *[
                f'Content-Type: {x["type"]}\r\nContent-Range: bytes {x["start"]}-{x["end"]}/{self._length}\r\n\r\n{x["raw"].decode("utf-8")}'
                for x in self._ranges],
            '',
        ]).strip()

    def to_bytes(self):
        return f'\r\n--{self._boundary}\r\n'.encode('utf-8').join([
            b'',
            *[
                f'Content-Type: {x["type"]}\r\nContent-Range: bytes {x["start"]}-{x["end"]}/{self._length}\r\n\r\n'.encode(
                    'utf-8') + x['raw']
                for x in self._ranges],
            b'',
        ]).strip()
