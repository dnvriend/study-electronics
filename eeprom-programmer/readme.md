# EEPROM Programmer for 28Cxxx Series

This project implements a custom EEPROM programmer based on the 28C64 and 28C256 EEPROMs. It is inspired by [Ben Eater's EEPROM programmer](https://www.youtube.com/watch?v=K88pgWhEb1M) but extends its capabilities with a Python-based CLI for reading, writing, and erasing EEPROM contents. The project is built using an Arduino Nano as the controller and a Python client for handling serial communication and machine code transfer.
## What I Learned

**Hardware:**  
  - Arduino Nano (limited SRAM, ~2 KB)  
  - 74HC595 shift registers to drive the EEPROM address lines  
  - 28C256 EEPROM (32 KB capacity, native address range 0x0000–0x7FFF)
  - Latches and Clock Generator: Used for shifting bits into the D-latches to control address lines.

**Software:**  
  - Arduino firmware that processes commands: `READ`, `ERASE`, `WRITE`, `WRITE_BYTE`, and `READ_BYTE`  
  - Python CLI (using Click) for sending commands and transferring data over USB  
  - Use of tqdm for progress feedback during bulk transfers

### Software and Communication:
- **Arduino Serial Behavior**: The `setup()` function runs on every serial invocation.
- **Python Serial Communication**:
    - Sending and receiving commands over serial.
    - Handling responses from the Arduino.
    - Sending complete files like `a.out` from the VASM assembler.
- **Parsing and Transmitting Data**:
    - Implementing a Python CLI to interact with the EEPROM programmer.
    - Ensuring correct data transfer using hex dumps for debugging.

## The 0A Bug (Newline Issue)
During development, an issue arose where an unexpected `0A` (newline) byte was appearing at the beginning of the data sent to the Arduino. This was due to Python adding a newline when sending the EEPROM size over serial. The bug was fixed by ensuring that Python does not append a newline after sending the size parameter.

## Key Concepts & Limitations

1. **USB Interaction and Firmware Initialization:**  
   Every time the Arduino Nano is connected or reset over USB, its `setup()` function runs again. This resets any internal state. The firmware is written to immediately listen for commands from the serial interface.

2. **Limited Memory:**  
   The Arduino Nano has limited SRAM (~2 KB). To avoid memory exhaustion when programming the 32 KB EEPROM, data is transferred in small chunks (16–48 bytes). The firmware waits for each chunk to be received and processed before requesting the next.

3. **Chunked Data Transfers:**  
   Due to the Nano’s small serial buffer (typically 64 bytes) and the need to avoid overflowing memory, the PC sends data in chunks. The Arduino firmware writes the chunk and then sends an acknowledgment (ACK) so that the PC can send the next chunk. This handshake ensures reliable transfers despite the Nano’s limitations.

4. **EEPROM Write Speed:**  
   - **Byte Write:** Each byte write cycle takes approximately 10 ms, resulting in an overall programming time of about 3–3.5 minutes for 32 KB.  
   - **Page Write:** Although the AT28C256 supports page writes (allowing 1 to 64 bytes to be written in one programming cycle), the current hardware setup (with the 74HC595 shift registers and wiring) does not support page writes. In the future, reworking the control sequence could take advantage of page writes to increase throughput.
   - The firmware currently uses a 6 ms delay after each byte write for reliable operation, which has been tuned (from 10 ms) to balance speed and reliability.

5. **Extra Functions in the CLI:**  
   In addition to bulk EEPROM operations, the project supports commands to read or write a single byte (`READ_BYTE` and `WRITE_BYTE`). This functionality allows for:
   - Changing the reset vector (addresses 0xFFFC and 0xFFFD) without rewriting the entire EEPROM.
   - Programming smaller programs faster by writing only the required number of bytes (e.g., if the program is only 2048 bytes).

6. **Workflow & Knowledge Transfer:**  
   - The firmware demonstrates how to build an embedded command interpreter that processes serial commands and performs hardware-level operations.
   - The Python CLI shows how to create a user-friendly command-line tool that communicates with the firmware, handles chunked transfers, and provides additional functionality like progress indication.
   - Together, they form a complete workflow for programming and testing 32 KB EEPROM devices using an Arduino Nano on a breadboard.

## Commands Overview

### Arduino Commands

- **READ**  
  Reads the EEPROM contents up to a specified address and prints the data in a hexdump format.

- **ERASE**  
  Writes `0xFF` to every byte up to a specified address, effectively erasing that portion of the EEPROM.

- **WRITE**  
  Receives a total length (number of bytes) and then data in chunks. After processing each chunk, the firmware sends an `ACK` to signal the PC that it is ready for the next chunk.

- **WRITE_BYTE**  
  Receives an address and a data value, writes that single byte, and sends an `ACK`.

- **READ_BYTE**  
  Receives an address, reads the byte at that location, and returns the data (prefixed with `DATA:`).

### PC (Python CLI) Commands

- **read**  
  Sends the `READ` command and displays a hexdump of the EEPROM data.

- **erase**  
  Sends the `ERASE` command and erases the EEPROM up to the given address.

- **write**  
  Sends the `WRITE` command along with a binary file. Data is sent in chunks, and the PC waits for an `ACK` after each chunk before proceeding.

- **write-byte**  
  Sends the `WRITE_BYTE` command, followed by an address and a byte value to program a single location.

- **read-byte**  
  Sends the `READ_BYTE` command, followed by an address, and prints the returned byte.

## Performance

- Bulk programming of 32 KB using byte writes takes approximately 3–3.5 minutes.
- Using chunk sizes between 16 and 48 bytes has been found to be reliable on the breadboard setup.
- Future improvements may include reworking the firmware to support page writes for significantly faster programming speeds.

## Conclusion

This project demonstrates a complete solution for programming 28Cxxx EEPROMs using an Arduino Nano and a Python CLI. It covers challenges such as limited memory, slow write cycles, and the need for reliable data transfer over a constrained serial connection. The extra commands (`WRITE_BYTE` and `READ_BYTE`) allow for fine-tuning and efficient updates to critical addresses (like the reset vector), providing a flexible workflow for various programming needs.

This project has been a deep dive into both hardware (EEPROM programming, shift registers) and software (serial communication, Python scripting), making it a valuable learning experience in embedded systems development.

## Resources
- [Atmel 28C64 Datasheet](https://ww1.microchip.com/downloads/en/devicedoc/doc0001h.pdf)
- [Atmel 28C256 Datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/doc0006.pdf)
- [Ben Eater's EEPROM programmer](https://www.youtube.com/watch?v=K88pgWhEb1M)
- [Ben Eater's Using an EEPROM to replace combinational logic](https://www.youtube.com/watch?v=BA12Z7gQ4P0)
