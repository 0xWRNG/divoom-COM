import enum


class Colors(enum.Enum):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_bytes(data):
    if isinstance(data, bytes | bytearray):
        for i in range(0, len(data), 16):
            chunk = data[i:i + 16]
            print(' '.join(f'{b:02X}' for b in chunk))
    elif isinstance(data, list):
        piece_ind = 0
        for piece in data:
            print(f'-- Chunk {piece_ind} --')
            piece_ind += 1
            print_bytes(piece)


def print_progress(sent, total):
    percent = (sent / total) * 100
    bar_len = 40
    filled = int(bar_len * sent // total)
    bar = '█' * filled + '-' * (bar_len - filled)
    if percent != 100:
        print(f'\r[{bar}] {percent:6.2f}% ({sent}/{total})', end='')
        return
    print(f'\r[{bar}] {percent:6.2f}% ({sent}/{total})')