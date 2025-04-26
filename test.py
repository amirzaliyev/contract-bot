def encode_to_zw(text: str) -> str:
    # Binary to zero-width mapping
    zw_map = {'0': '\u200B', '1': '\u200C'}  # ZWSP and ZWNJ
    binary = ''.join(f'{ord(c):08b}' for c in text)  # Convert to binary
    return ''.join(zw_map[b] for b in binary)



def decode_from_zw(zw_text: str) -> str:
    zw_map = {'\u200B': '0', '\u200C': '1'}
    binary = ''.join(zw_map[c] for c in zw_text if c in zw_map)
    chars = [chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8)]
    return ''.join(chars)

# Encode secret
secret = "hello123"
hidden = encode_to_zw(secret)

# Append to visible message
message = f"This is a normal message.{hidden}"
print(message) # You will see invisible characters at the end

# Later... extract the secret
extracted_zw = message[len("This is a normal message."):]
revealed = decode_from_zw(extracted_zw)
print("Hidden message:", revealed)
