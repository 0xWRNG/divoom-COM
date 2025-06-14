from commands import Commands

header = b'\x01'
footer = b'\x02'

control_word_init = b'\x00'
control_word_continue = b'\x01'


def build_packet(command: Commands, payload: bytes) -> list[bytearray]:
    packet_seq = []
    if command == Commands.Animation:
        initial_packet = bytearray()

        length = 8
        initial_packet += length.to_bytes(2, byteorder='little')
        initial_packet += command.value
        initial_packet += control_word_init
        all_payload_size = len(payload).to_bytes(4, byteorder='little')
        initial_packet += all_payload_size
        initial_packet += calc_checksum(initial_packet)
        initial_packet = header + initial_packet + footer
        packet_seq.append(bytearray(initial_packet))

        segment_ind = 0
        for i in range(0, len(payload), 256):
            current_payload = payload[i:min(i + 256, len(payload))]
            packet = bytearray()
            length = len(current_payload) + 10
            packet += length.to_bytes(2, byteorder='little')
            packet += command.value
            packet += control_word_continue
            packet += all_payload_size
            packet += segment_ind.to_bytes(2, byteorder='little')
            packet += current_payload
            packet += calc_checksum(packet)
            packet = header + packet + footer
            packet_seq.append(bytearray(packet))
            segment_ind += 1
        return packet_seq

    packet = bytearray()
    length = len(payload) + 2 + len(command.value)
    packet += length.to_bytes(2, byteorder='little')
    packet += command.value
    packet += payload
    packet += calc_checksum(packet)
    full_packet = header + packet + footer
    return [bytearray(full_packet)]


def calc_checksum(byte_arr: bytes, length: int = 2, byteorder: str = 'little') -> bytes:
    max_value = 1 << (length * 8)
    checksum = 0
    for byte in byte_arr:
        checksum = (checksum + byte) % max_value
    return checksum.to_bytes(length, byteorder)
