# EEPROM Programmer

## Overview
This project is a custom EEPROM programmer based on the 28C64 and 28C256 EEPROMs. It is inspired by [Ben Eater's EEPROM programmer](https://www.youtube.com/watch?v=K88pgWhEb1M) but extends its capabilities with a Python-based CLI for reading, writing, and erasing EEPROM contents. The project is built using an Arduino Nano as the controller and a Python client for handling serial communication and machine code transfer.

## What I Learned

### Hardware Components:
- **D-Latches and Clock Generator**: Used for shifting bits into the D-latches to control address lines.
- **HC595 Shift Register**: An 8-bit shift register requiring three wires (data, clock, storage register) for address manipulation.
- **28C64 and 28C256 EEPROMs**: Pin-compatible EEPROMs, requiring only two additional address bits on the HC595.

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

## Arduino Source Code
The Arduino code handles:
- Parsing serial commands (`READ`, `WRITE`, `ERASE`).
- Controlling the EEPROM’s address and data lines via shift registers.
- Writing and reading EEPROM contents.
- Handling byte-by-byte data transfer and verification.

## Python CLI Client
The Python CLI provides an interface to:
- Read EEPROM contents.
- Erase EEPROM memory.
- Write machine code from a binary file (e.g., `a.out`) to the EEPROM.
- Handle serial communication with proper command parsing and data transfer validation.

## Future Improvements
- Implement a GUI for better usability.
- Optimize performance with batch writes instead of single-byte writes.
- Improve debugging by adding real-time feedback and verification reads.
- Expand compatibility to support additional EEPROM types.

This project has been a deep dive into both hardware (EEPROM programming, shift registers) and software (serial communication, Python scripting), making it a valuable learning experience in embedded systems development.

## Resources
- [Atmel 28C64 Datasheet](https://ww1.microchip.com/downloads/en/devicedoc/doc0001h.pdf)
- [Atmel 28C256 Datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/doc0006.pdf)
- [Ben Eater's EEPROM programmer](https://www.youtube.com/watch?v=K88pgWhEb1M)
- [Ben Eater's Using an EEPROM to replace combinational logic](https://www.youtube.com/watch?v=BA12Z7gQ4P0)