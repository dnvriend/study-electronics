import click
import serial
import time
from tqdm import tqdm
from typing import Tuple

BAUD_RATE = 115200

def init_serial(serial_port: str) -> Tuple[str, serial.Serial]:
    """Initialize serial connection and wait for Arduino to start."""
    ser = serial.Serial(serial_port, BAUD_RATE)
    time.sleep(2)
    text = ser.readline().decode('utf-8').strip()
    return text, ser

@click.group()
@click.option('--serial-port', '-p', required=True, help="Serial port to use")
@click.pass_context
def cli(ctx, serial_port):
    """EEPROM Programmer CLI"""
    # Set the global serial_port in context so that commands can access it.
    ctx.ensure_object(dict)
    ctx.obj['serial_port'] = serial_port

@cli.command()
@click.argument('bytes_to_read', type=str, required=True)
@click.pass_context
def read(ctx, bytes_to_read: str):
    """Read contents of EEPROM with a limit eg. 0x7FFF or 32768"""
    serial_port = ctx.obj['serial_port']
    _, ser = init_serial(serial_port)
    ser.write(b'READ\n')
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
@click.pass_context
def erase(ctx, bytes_to_erase: str):
    """Erase EEPROM"""
    serial_port = ctx.obj['serial_port']
    _, ser = init_serial(serial_port)
    ser.write(b'ERASE\n')
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
    append it as is. This is due to the fact that Python reads big endian byte order from
    the file which means that the order in which the bytes are read is reversed.
    """
    result = bytearray()
    for i in range(0, len(binary_data), 2):
        if i + 1 < len(binary_data):
            result.extend([binary_data[i+1], binary_data[i]])
        else:
            result.append(binary_data[i])
    return bytes(result)

@cli.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--limit', '-l', type=str, default=None, help="Limit number of bytes to write (ex. 0xFF)")
@click.pass_context
def write(ctx, filename: str, limit: str):
    """Write binary file to EEPROM with an optional limit on the number of bytes to write (ex. 0xFF)"""
    serial_port = ctx.obj['serial_port']
    _, ser = init_serial(serial_port)
    ser.write(b'WRITE\n')
    
    with open(filename, 'rb') as f:
        read_data = f.read()

    # this is only necessary because python reads the binary data in big endian order
    binary_data = reverse_binary_words(read_data)

    # Determine the total length based on the limit option if provided.
    if limit is not None:
        limit_num = int(limit, 16) if limit.startswith("0x") else int(limit)
        total_length = min(len(binary_data), limit_num)
    else:
        total_length = len(binary_data)

    print("Length:", total_length)
    ser.write(f"{total_length}\n".encode())
    ser.flush()
    time.sleep(0.1)
    ser.reset_input_buffer()

    CHUNK_SIZE = 48
    from tqdm import tqdm
    with tqdm(total=total_length, unit='B', unit_scale=True, desc="Writing", ncols=80) as progress:
        for i in range(0, total_length, CHUNK_SIZE):
            chunk = binary_data[i:i+CHUNK_SIZE]
            ser.write(chunk)
            ser.flush()
            ack = ser.readline().decode('utf-8').strip()
            if ack != "ACK":
                print(f"Did not receive ACK after chunk at offset {i}. Received: {ack}")
                break
            progress.update(len(chunk))
    
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
@click.pass_context
def write_byte(ctx, address: str, data: str):
    """Write a single byte to EEPROM at the given address.
    
    ADDRESS and DATA can be given in hex (e.g., 0xFFFC) or decimal.
    """
    serial_port = ctx.obj['serial_port']
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
@click.pass_context
def read_byte(ctx, address: str):
    """Read a single byte from EEPROM at the given address.
    
    ADDRESS can be in hex (e.g., 0xFFFC) or decimal.
    """
    serial_port = ctx.obj['serial_port']
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
    cli(obj={})
