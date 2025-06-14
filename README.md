Small Python project for controlling DivoomDitoo device over bluetooth by using COM port.
Contains such features as:
- Sending images to Divoom device
- Sending gifs
- Setting brightness

Also small features which were used during development and testing
- Creating binary files with gif content in Divoom compatible style
- Creating gifs from png strips

---
This project is fully inspired by this [project](https://github.com/andreas-mausch/divoom-ditoo-pro-controller), but it was using some unsupported Rust library only for Linux. Now it is using only pyserial for communication

### Setup
0. Connect your DivoomDitoo device over bluetooth. There is no matter which one you connect: Ditoo-Light or Ditoo-Audio.
1. Make a COM port assigned to this device. Select highest baudrate possible and remember COM port index
2. Goto config.json and write down parameters you previously selected
```json
{  
    "port": "COM3",  
    "baudrate": 128000,  
    "packet_timeout": 0.01,  
    "read_timeout": 0.25,  
    "debug_print": false  
}
```
3. Install requirements for this project using:
```shell
pip install -r requirements.txt
```

## CLI Usage
### sending .gif

This command will form packet sequence including packet-request, which will inform the device about packet sequence to be sended
```
python main.py send gif examples/fire.gif
```

You will see a progress bar showing how many bytes were sended
```
[████████████████████████████████████████] 100.00% (16676/16676 bytes)
```
if `debug_print` is enabled you will also see the contents of the packets

#### Sending pictures

It will form a packet  containing a content of a picture with some Divoom header, and send it to the device
```
python main.py send image examples/diamond.png
```

You will see a constant picture

if `debug_print` is true you will see packet content e.g:
```
- Sending single packet...
-- Chunk 0 --
01 AF 00 44 00 0A 0A 04 AA A8 00 00 00 00 0B FF
FF FF D5 FF F6 A1 FB E8 4A ED D9 2C E0 D8 20 C5
B5 1A AA A7 1C 91 9A 11 72 7A 14 5E 53 00 00 00
AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA AA
AA AA AA 88 88 AA AA AA AA AA 8A 00 10 A8 AA AA
AA AA 08 33 12 95 AA AA AA 8A 30 22 21 53 A9 AA
AA 8A 30 10 10 33 A9 AA AA 08 03 33 22 56 96 AA
AA 08 13 23 22 57 96 AA AA 08 50 22 32 67 96 AA
AA 18 33 66 66 55 97 AA AA 9A 63 55 55 56 A9 AA
AA 9A 64 55 55 26 A9 AA AA AA 79 33 22 95 AA AA
AA AA 9A 99 99 A9 AA AA AA AA AA AA AA AA AA AA
FE 53 02
```

#### Making .divoom16 file

If you don't what to create packet sequences every time, you can make a `.divoom16` file. This was inspired by project metioned in description. This file contains bytes of original gif in a Divoom format. May save some time for big gifs

```
python main.py make divoom16 examples/fire.gif examples/fire.divoom16
```
where first arg – original file, second – where file will be saved.

#### Sending .divoom16 file

If you previously created `.divoom16` file, you can send it to your device
```
(.venv) PS E:\divoom-COM> python main.py send divoom16 examples/rickroll.divoom16
[████████████████████████████████████████] 100.00% (24035/24035 bytes)
```
As it was with gif file, you will see a progress bar, and if debug_print is on – packets content

#### Making gifs out of png
This tool was created while developing this project just for fun. But if you have a .png representing an animation as minecraft saves their animations; base picture size: 16x16, animation 16x512, you can use this:
```
python main.py make gif_from_strip examples/soul_fire.gif examples/soul_fire.png 
```
You will get an output like this
```
Gif saved: examples\soul_fire.gif
```

#### Setting screen brightness
To control screen brightness use this:
```
python main.py set brightness 50  
```
where 50 – is brightness percentage

---
### Using pure code

If you want to create something by yourself, there is breif explanation how to:

#### Initialising device:
```python
from device import *
device = DitooDevice.from_json('config.json')
```
this will load config from project folder.

#### Sending content:
```python
from device import *  
from brightness import make_brightness_payload  
from packet import build_packet  
from commands import Commands  
from image import image_to_payload  
from animation import gif_to_payload, read_divoom16  
from gif_utils import create_gif_from_strip

# Initialisation
device = DitooDevice.from_json('config.json')

# Sendig gif
payload = gif_to_payload(Path('examples/seagrass.gif'))
packets = build_packet(Commands.Animation, payload)
device.send_packet(packets)

# Making .divoom16
gif_to_payload(  
    gif_path='examples/fire.gif',  
    save_path='examples/fire.divoom16'  
)

# Sending .divoom16
payload = read_divoom16(Path('examples/rickroll.divoom16'))
packets = build_packet(Commands.Animation, payload)
device.send_packet(packets)

# Sending image
payload = image_to_payload(Path('examples/diamond.png'))
packets = build_packet(Commands.Image, payload)
device.send_packet(packets)

# Setting brightness
payload = make_brightness_payload(50)
packets = build_packet(Commands.Brightness, payload)
device.send_packet(packets)
```
---
### Useful links
- https://github.com/andreas-mausch/divoom-ditoo-pro-controller
- https://docin.divoom-gz.com/web/#/5/146
- https://github.com/RomRider/node-divoom-timebox-evo/blob/master/PROTOCOL.md
