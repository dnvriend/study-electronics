def reverse_binary_words(binary_data: bytes) -> bytes:
    """
    Reverse the order of bytes in each 16-bit word from the binary data.
    
    For every two bytes, swap their order. If the last chunk is a single byte,
    append it as is.
    """
    result = bytearray()
    for i in range(0, len(binary_data), 2):
        # Check if two bytes are available
        if i + 1 < len(binary_data):
            result.extend([binary_data[i+1], binary_data[i]])
        else:
            # If odd number of bytes, just append the last one
            result.append(binary_data[i])
    return bytes(result)

####

rom = bytearray([0xea] * 32768)

rom[0x7FFC] = 0x00
rom[0x7FFD] = 0x80

with open("rom.bin", "wb") as f: 
    f.write(reverse_binary_words(rom))
