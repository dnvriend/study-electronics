#define SHIFT_DATA 2
#define SHIFT_CLOCK 3
#define SHIFT_LATCH 4
#define EEPROM_D0 5
#define EEPROM_D7 12
#define WRITE_EN 13

#define CHUNK_SIZE 48 // works: [16, 32] not: [64]
#define READ_TIMEOUT 5000  // timeout in milliseconds

/*
The 28C64 has 8kb of storage (8192 bytes) with an address range of 0x0000 to 0x1FFF
The 28C256 has 32kb of storage (32768 bytes) with a range of 0x0000 to 0x7FFF
*/

/*
https://www.arduino.cc/reference/tr/language/functions/advanced-io/shiftout/
shiftOut(dataPin: int, clockPin: int, bitOrder(MSBFIRST, LSBFIRST), value: byte): shifts out a byte of data, one bit at a time
*/

// Initialize the pins
void initialize() {
  pinMode(SHIFT_DATA, OUTPUT);
  pinMode(SHIFT_CLOCK, OUTPUT);
  pinMode(SHIFT_LATCH, OUTPUT);
  digitalWrite(SHIFT_LATCH, LOW);
  digitalWrite(WRITE_EN, HIGH);
  pinMode(WRITE_EN, OUTPUT);
}

// Toggle PIN(4) PIN(12) ST_CP on the 74HC595 
void toggleLatch() {
  digitalWrite(SHIFT_LATCH, LOW);
  digitalWrite(SHIFT_LATCH, HIGH);
  digitalWrite(SHIFT_LATCH, LOW);
}

/*
outputEnable means that the EEPROM is outputting its data. If true it will output
and if false it will not be outputting its data. Set false for programming.
*/
void setAddress(unsigned int address, bool outputEnable) {
  // shiftOut shifts 8 bits at a time (one byte)
  // AND we write MSBFIRST
  // AND we write 16 bits (2 bytes)
  // SO we need to know what the MSB bits are first and write that first
  // SO we first SHIFT 8 bits to the right THEN we have the MSB bits
  // THEN we just write the address and that writes ONLY the first 8 bits of the LSB
  shiftOut(SHIFT_DATA, SHIFT_CLOCK, MSBFIRST, (address >> 8) | (outputEnable ? 0x00 : 0x80)); // so for a number < 256 we get 8 zero's here
  shiftOut(SHIFT_DATA, SHIFT_CLOCK, MSBFIRST, address); // here we get the bits of the LSB as it writes the first byte only
  toggleLatch();
}

byte readEEPROM(unsigned int address) {
  for (unsigned int pin = EEPROM_D0; pin <= EEPROM_D7; pin += 1) {
    pinMode(pin, INPUT);
  }

  setAddress(address, /*outputEnable*/ true);
  byte data = 0;
  for(unsigned int pin=EEPROM_D7; pin >= EEPROM_D0; pin -= 1) {
    unsigned int bit = digitalRead(pin);    
    data = (data << 1) + bit;
  }
  return data;
}

void writeEEPROM(unsigned int address, byte data) {
  for (unsigned int pin = EEPROM_D0; pin <= EEPROM_D7; pin += 1) {
    pinMode(pin, OUTPUT);
  }

  setAddress(address, /*outputEnable*/ false);
  for (int pin = EEPROM_D0; pin <= EEPROM_D7; pin += 1) {
    digitalWrite(pin, data & 1);
    data = data >> 1;
  }

  digitalWrite(WRITE_EN, LOW);
  delayMicroseconds(1);
  digitalWrite(WRITE_EN, HIGH);
  delay(6); // milliseconds (for reliable writes, use a value 6 or higher)
}

void printContents(int max) {
  // first 256 bytes: 0xFF
  // 28C64:  0x1FFF
  // 28C256: 0x7FFF
  for (unsigned int base=0; base <= max; base += 16) {
    byte data[16];
    for(unsigned int offset = 0; offset <= 15; offset += 1) {
      data[offset] = readEEPROM(base + offset);
    }
    char buf[80];
    sprintf(buf, "%03x: %02x %02x %02x %02x %02x %02x %02x %02x   %02x %02x %02x %02x %02x %02x %02x %02x",
      base, data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], 
      data[8], data[9], data[10], data[11], data[12], data[13], data[14], data[15]
    );
    Serial.println(buf);
  }
}

void printReceivedData(byte data[], unsigned int length) {
  for (int base = 0; base < length; base += 16) {
    char buf[80];
    sprintf(buf, "%03x:", base);
    Serial.print(buf);
    
    // Print hex values
    for (unsigned int offset = 0; offset < 16 && (base + offset) < length; offset++) {
      sprintf(buf, " %02x", data[base + offset]);
      Serial.print(buf);
    }
    Serial.println();
  }
}

void eraseEEPROM(unsigned int max) {
  for (unsigned int address = 0; address <= max; address += 1) {
      writeEEPROM(address, 0xFF); // erase
    }
}

void writeDataToEEPROM(byte data[], unsigned int length) {
  for (unsigned int address = 0; address <= length; address += 1) {
      writeEEPROM(address, data[address]);
  }
}

void setup() {
  initialize();
  Serial.begin(115200);
  Serial.setTimeout(1000);
  Serial.println("EEPROM Programmer Ready");
}


void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.equalsIgnoreCase("READ")) {
      while (!Serial.available()) {}
      unsigned int address = Serial.parseInt();
      printContents(address);
      Serial.println("---END---");
    }
    else if (command.equalsIgnoreCase("ERASE")) {
      while (!Serial.available()) {}
      unsigned int address = Serial.parseInt();
      eraseEEPROM(address);
      Serial.println("---END---");     
    }
    else if (command.equalsIgnoreCase("WRITE")) {
      // Wait for the total length value
      while (!Serial.available()) {}  
      unsigned long lengthFromSerial = Serial.parseInt();
      unsigned int DO_NOT_USE = Serial.read();
      unsigned int totalLength = (unsigned int) lengthFromSerial;
      Serial.println(totalLength);
      
      unsigned int bytesWritten = 0;
      byte buffer[CHUNK_SIZE];
      
      while (bytesWritten < totalLength) {
        unsigned int bytesToRead = min(totalLength - bytesWritten, (unsigned int)CHUNK_SIZE);
        unsigned long startTime = millis();
        // Wait until the required number of bytes are available or timeout
        while (Serial.available() < bytesToRead && (millis() - startTime) < READ_TIMEOUT) {
          // Waiting for data
        }
        if (Serial.available() < bytesToRead) {
          Serial.print("Timeout waiting for bytes at address: ");
          Serial.println(bytesWritten, HEX);
          break;
        }
        int count = Serial.readBytes(buffer, bytesToRead);
        
        // Write each byte to EEPROM.
        for (unsigned int i = 0; i < (unsigned int)count; i++) {
          writeEEPROM(bytesWritten + i, buffer[i]);
        }
        bytesWritten += count;        
        // Signal the PC that we’re ready for the next chunk.
        Serial.println("ACK");
      }
      Serial.println("---END---");
    }
    else if (command.equalsIgnoreCase("WRITE_BYTE")) {
      // New command: expects an address then a data value (each terminated by newline)
      while (!Serial.available()) {}  
      unsigned int addr = Serial.parseInt();
      while (!Serial.available()) {}  
      int data = Serial.parseInt();
      writeEEPROM(addr, (byte)data);
      Serial.println("ACK");
    }
    else if (command.equalsIgnoreCase("READ_BYTE")) {
      // New command: expects an address, then returns the byte at that location.
      while (!Serial.available()) {}  
      unsigned int addr = Serial.parseInt();
      byte data = readEEPROM(addr);
      // Send back the data in hexadecimal format.
      Serial.println(data, HEX);
    }
    else {
      char buf[80];
      sprintf(buf, "Unknown command: '%s'. Use READ, WRITE, ERASE", command.c_str());      
      Serial.println(buf);
    }
  }
}
