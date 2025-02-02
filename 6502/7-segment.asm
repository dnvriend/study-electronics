;
; for driving a 7-segment display with an 28C64 EEPROM and a common cathode display
;
; vasm -Fbin -dotdir 7-segment.asm -o 7-segment.bin
;
  .word $7744 ; 0, 1
  .word $6B6E ; 2, 3
  .word $5C3E ; 4, 5
  .word $3F64 ; 6, 7
  .word $7F7E ; 8, 9
  .word $7D1F ; A, B
  .word $334F ; C, D
  .word $3B39 ; E, F
