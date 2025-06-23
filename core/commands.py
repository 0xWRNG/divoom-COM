import enum


class Commands(enum.Enum):
    Animation = b'\x8b'
    Brightness = b'\x74'
    Image = b'\x44\x00\x0A\x0A\x04'
