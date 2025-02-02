## Retro Assembler Extension for VS Code
Retro Assembler is a multi-platform, lightweight but powerful macro assembler, capable of compiling code for multiple CPU types and has support for various output formats. This extension makes it easier to work with even large assembly projects.

## Retro Assembler User Guides
Make sure you look into the Retro Assembler Documentation which explains everything and contains information about file extension support regarding this extension, too.

Guide: Using Retro Assembler with Visual Studio Code

Guide: How to Install .NET on Linux and macOS

## Supported File Extensions
.asm
.s
.inc

## Code Snippets
The Directives like .macro can insert Code Snippets with the typically used parameters. After typing "." you can either press Ctrl+Space to bring up a list of the available directives, or start typing the directive you need. It will show a short description and examples for each. You can activate the auto-completion by hitting Tab.


## Build, Start and Debug Integration
The command Build is assigned to the keys Ctrl+Shift+B
The command Build & Start is assigned to the keys Shift+F5 and also to F6
The command Build & Debug is assigned to the key F5
You may assign different/additional keyboard shortcuts to these commands.
The active document is saved automatically upon launching any of the commands.
Build & Start utilizes the LaunchCommand setting entered into the source code file, by which you can launch the successfully compiled code file in an emulator. For example:

.setting "LaunchCommand", "C:\\Emulator\\emulator.exe {0}"

Build & Debug utilizes the DebugCommand setting entered into the source code file, by which you can launch the successfully compiled code file in a debugger. For example:

.setting "DebugCommand", "C:\\Emulator\\debugger.exe {0}"

Note: These paths are in the source code (or in Retro Assembler's default settings) and the execution is handled by the assembler, because of the vast array of CPU types it supports. They all need different emulators and debuggers to test the code with, and even different projects may require different emulators within the same CPU type.


## Extension Settings
This extension contributes the following settings that you can set up in your User Settings:

retroassembler.path: set the execution path or command for the assembler, for example "C:\Assembler\retroassembler.exe"
retroassembler.args: set command line arguments for the assembler, for example "-x"
retroassembler.mainfile: set the project's main file that should be compiled instead of the currently edited file, for example "[path]\main.6502.asm"
Note: When you edit the Settings in JSON mode, the path separators have to be escaped in Windows paths using "\\"


CPU Syntax Detection
Detecting the CPU type to choose the correct syntax for a source code file is not without errors in VS Code, but you can help it by following these guidelines:

Tag your source codes with the CPU type, like this...

MyCode.6502.asm
MyCode.65c02.asm (Use this tag for 65SC02, too)
MyCode.65816.asm
MyCode.4510.asm
MyCode.45gs02.asm
MyCode.mega65.asm (Same as 45GS02)
MyCode.4004.asm
MyCode.4040.asm
MyCode.8008.asm
MyCode.8080.asm
MyCode.8085.asm
MyCode.gameboy.asm
MyCode.z80.asm
If you are just starting out with a project, this is the easiest thing you can do to ensure that VS Code will choose the correct Syntax for your source code file.

You can associate your assembly extension(s) with a CPU Syntax in your User Settings. If you mostly work on one chosen CPU type (quite likely), you can just do this and call it a day...

"files.associations": { "*.asm": "retroasm_6502" }

MOS 6502: "retroasm_6502"
WDC 65C02 / 65SC02: "retroasm_65c02"
WDC 65816: "retroasm_65816"
CSC 4510: "retroasm_4510"
MEGA65 45GS02: "retroasm_45gs02"
Intel 4004: "retroasm_4004"
Intel 4040: "retroasm_4040"
Intel 8008: "retroasm_8008"
Intel 8080: "retroasm_8080"
Intel 8085: "retroasm_8085"
Nintendo Gameboy: "retroasm_gameboy"
Zilog Z80: "retroasm_z80"
The syntax for 6502 is selected by default. You can just choose the correct syntax for each loaded source code file on the bottom-right, in the status bar. It may become a bit tedious, but it's a workaround.

See the Retro Assembler section in Settings for comments and examples.


Release Notes for the Extension
1.3.6
Syntax added for these CPUs: CSC 4510, MEGA65 45GS02
The Stack Pointer register in 65816 source code can be written either as SP or S
1.3.5
Support for a new directive: .lib
1.3.4
Currently VS Code doesn't use word wrap in the formatting of Code Snippets. Previously I tried to solve that by formatting the descriptions with newline characters, but when the font size is changed, the text would break incorrectly. So I've given up on this approach and will wait for the VS Code team to eventually fix this issue.
1.3.3
Support for a new directive: .format
1.3.2
Fix for a file extension case sensitivity issue in the builder scripts.
1.3.1
Support for a new directive: .namespace
1.3.0
Code Snippets support implemented for all Directives like .macro, .segment, .byte etc
Each Directive has a short description and examples that the Code Snippet selector can display.
1.2.0
Syntax added for these Intel CPUs: 4004, 4040, 8008, 8080, 8085
Command Build & Debug added.
The Commands are all registered to standard keyboard shortcuts out of the box.
Upon launching any Command, the active document is saved automatically.
1.1.0
MainFile setting added to always start compiling a specific file in the project, instead of the currently edited file.
File paths that contain spaces are now handled correctly.
1.0.7
Smaller changes made in Light and Dark themes.
1.0.6
Blue theme added similar to classic DOS text editors for even more retro feels.
1.0.5
Support for new directives: .encoding, .textz, .ascii, .asciiz, .print, .error
1.0.4
The color of @Local and @@Regional labels changed from gray to a more distinctive brown. Colorization issues fixed.
1.0.3
Syntax for Z80 CPU added.
Color themes updated, Register color changed to be more distinct.
1.0.2
Build & Start no longer needs or uses the retroassembler.start user setting. It uses the -L command line switch for the assembler and utilizes the LaunchCommand setting entered into the source code file.
1.0.1
Syntax for 65816 CPU added.
Octal number format (0o17) and a new binary number format (0b11001010) is now supported.
Number separator '_' is supported in hexadecimal and binary numbers (0b11_00_10_10).
1.0.0
Initial release of the VS Code Extension.
Syntax for 6502, 65C02 / 65SC02, Gameboy CPUs.
Light and Dark themes.
Build and Build & Start command support using the built in Terminal.

## Resources
- https://enginedesigns.net/retroassembler