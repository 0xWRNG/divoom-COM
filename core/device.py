import serial
import time
import json

from utils.console_utils import *

class DitooDevice:
    def __init__(self, port='COM3', baudrate=128000, packet_timeout=0.01, debug_print=False, read_timeout=0.25):
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(self.port, self.baudrate, timeout=read_timeout)
        self.packet_timeout = packet_timeout
        self.debug = debug_print

    @classmethod
    def from_json(cls, json_path):
        with open(json_path, 'r') as f:
            config = json.load(f)
        return cls(
            port=config.get("port", 'COM3'),
            baudrate=config.get("baudrate", 128000),
            packet_timeout=config.get("packet_timeout", 0.01),
            read_timeout=config.get("read_timeout", 0.25),
            debug_print=config.get("debug_print", False),
        )

    def send_packet(self, packets: list[bytearray]):
        if isinstance(packets, bytes):
            if self.debug:
                print('- Sending raw bytes...')
                print_bytes(packets)
            self.ser.write(packets)
            return

        if len(packets) == 1:
            if self.debug:
                print('- Sending single packet...')
                print_bytes(packets)
            try:
                self.ser.write(packets[0])
            except serial.serialutil.SerialTimeoutException:
                print('- Sending single packet failed, skipping...')
            return

        total_size = sum(len(packet) for packet in packets)
        sent_size = 0



        first_packet = True
        for packet in packets:
            if self.debug:
                print(f'- Sending packet')
                print_bytes(packets)

            self.ser.write(packet)
            sent_size += len(packet)
            print_progress(sent_size, total_size)
            if first_packet:
                response = self.read_response()
                first_packet = False
                if response is None or len(response) == 0:
                    print('- Device is not responding, cancel sending')
                    return
                if response[5] == 0x55 and response[7] == 0x01:
                    if self.debug:
                        print("- Received ACK, continuing sending...")
                    continue
                else:
                    print(f'- Got error, cancel sending')
                    return
            else:
                time.sleep(self.packet_timeout)

    def read_response(self, size=64):
        data = self.ser.read(size)
        if self.debug:
            print('- Device response')
            print_bytes(data)
        return data

    def close(self):
        if self.debug:
            print('- Device closed')
        self.ser.close()
