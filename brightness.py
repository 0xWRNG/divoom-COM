def make_brightness_payload(brightness):
    if 100 < brightness < 0:
        raise ValueError("Brightness should be between 0 and 100")
    return bytes([brightness])
