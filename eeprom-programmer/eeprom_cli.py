from typing import Optional, Tuple
import click
import serial
import time
from tqdm import tqdm

BAUD_RATE = 115200

def init_serial(serial_port: str) -> Tuple[str, serial.Serial]:
    ser = serial.Serial(serial_port, BAUD_RATE)
    time.sleep(2)
    text = ser.readline().decode('utf-8').strip()
    return text, ser

@click.group()
def cli():
    """EEPROM Programmer CLI"""
    pass

@cli.command()
@click.argument('bytes_to_read', type=str, required=True)
@click.argument('serial_port', type=str, required=True)
def read(bytes_to_read: str, serial_port: str):
    """Read contents of EEPROM"""
    _, ser = init_serial(serial_port)
    ser.write(f'READ\n'.encode())
    length = int(bytes_to_read, 16) if '0x' in bytes_to_read else int(bytes_to_read)

    ser.write(f"{length}\n".encode())
    while True:
        if ser.in_waiting:
            response = ser.readline().decode('utf-8').strip()
            if response == "---END---":
                break
            print(response)
    ser.close()

@cli.command()
@click.argument('bytes_to_erase', type=str, required=True)
@click.argument('serial_port', type=str, required=True)
def erase(bytes_to_erase: str, serial_port: str):
    """Erase EEPROM"""
    _, ser = init_serial(serial_port)
    ser.write(f'ERASE\n'.encode())
    length = int(bytes_to_erase, 16) if '0x' in bytes_to_erase else int(bytes_to_erase)
    
    ser.write(f"{length}\n".encode())
    while True:
        if ser.in_waiting:
            response = ser.readline().decode('utf-8').strip()
            if response == "---END---":
                break
            print(response)
    ser.close()

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

@cli.command()
@click.argument('filename', type=click.Path(exists=True))
@click.argument('serial_port', type=str, required=True)
def write(filename: str, serial_port: str):
    """Write binary file to EEPROM"""
    _, ser = init_serial(serial_port)
    ser.write(b'WRITE\n')
    
    with open(filename, 'rb') as f:
        read_data = f.read()

    # this is only necessary because python reads the binary data in big endian order
    binary_data = reverse_binary_words(read_data)

    total_length = len(binary_data)
    print("Length:", total_length)
    # Send total length with newline (to ensure Arduino's parseInt terminates correctly)
    ser.write(f"{total_length}\n".encode())
    ser.flush()
    time.sleep(0.1)

    # Optionally, clear any stray data from the input buffer.
    ser.reset_input_buffer()

    CHUNK_SIZE = 48
    # Create a tqdm progress bar based on total_length read
    with tqdm(total=total_length, unit='B', unit_scale=True, desc="Writing", ncols=80) as progress:
        # Process the binary_data in chunks
        for i in range(0, total_length, CHUNK_SIZE):
            chunk = binary_data[i:i+CHUNK_SIZE]
            ser.write(chunk)
            ser.flush()
            # Wait for ACK from Arduino before sending next chunk
            ack = ser.readline().decode('utf-8').strip()
            if ack != "ACK":
                print(f"Did not receive ACK after chunk at offset {i}. Received: {ack}")
                break
            else:
                progress.update(len(chunk))
    
    # Finally, wait for the "---END---" message.
    while True:
        if ser.in_waiting:
            response = ser.readline().decode('utf-8').strip()
            if response == "---END---":
                break
            print(response)
    ser.close()


@cli.command()
@click.argument('address', type=str, required=True)
@click.argument('data', type=str, required=True)
@click.argument('serial_port', type=str, required=True)
def write_byte(address: str, data: str, serial_port: str):
    """Write a single byte to EEPROM at the given address.
    
    ADDRESS and DATA can be given in hex (e.g., 0xFFFC) or decimal.
    """
    _, ser = init_serial(serial_port)
    ser.write(b'WRITE_BYTE\n')
    
    # Convert address and data to integer.
    addr = int(address, 16) if '0x' in address.lower() else int(address)
    dat = int(data, 16) if '0x' in data.lower() else int(data)
    
    # Send address and data, each terminated by a newline.
    ser.write(f"{addr}\n".encode())
    ser.write(f"{dat}\n".encode())
    ser.flush()
    
    # Wait for ACK from Arduino.
    while True:
        if ser.in_waiting:
            response = ser.readline().decode('utf-8').strip()
            if response == "ACK":
                print("Byte written.")
                break
            else:
                print("Received:", response)
    ser.close()

@cli.command()
@click.argument('address', type=str, required=True)
@click.argument('serial_port', type=str, required=True)
def read_byte(address: str, serial_port: str):
    """Read a single byte from EEPROM at the given address.
    
    ADDRESS can be in hex (e.g., 0xFFFC) or decimal.
    """
    _, ser = init_serial(serial_port)
    ser.write(b'READ_BYTE\n')
    
    # Convert address to integer (supports hex or decimal)
    addr = int(address, 16) if '0x' in address.lower() else int(address)
    ser.write(f"{addr}\n".encode())
    ser.flush()
    
    # Wait for the response from Arduino
    response = ser.readline().decode('utf-8').strip()
    print(response)
    ser.close()

if __name__ == '__main__':
    cli()
