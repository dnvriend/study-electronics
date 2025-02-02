## Syntax

- '$' means hex number so $6002 means 0x6002 (hex), without the $ it means decimal.
- '#' means literally the value so lda #$FF means load FF into A, the literal value.

## Indentation
Assembly code must be indented. The indentation is used to determine the scope of a label.

## directives
- .org - sets the current address for the code that follows
- .word - sets the current address to the next word (16 bits)


# vasm compile


Download vasm source, then run it with:

```
make CPU=6502 SYNTAX=oldstyle
```