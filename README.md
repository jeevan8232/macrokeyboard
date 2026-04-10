# macrokeyboard
macro keyboard and space mouse using rpi pico. circuitpython code

https://www.thingiverse.com/thing:7293580

https://www.youtube.com/watch?v=AjmmTDKetks

# Hand-Wiring the Electronics

Since we are keeping this accessible, there is no custom PCB required—everything is hand-wired directly to the microcontroller!

Hand-wiring a project like this is incredibly rewarding. Take your time, trim your wires to length so they fit nicely inside the shell, and double-check your connections as you go.

Below is the complete wiring guide based on the Raspberry Pi Pico (RP2040) pinout used for this project.

1. Power Distribution (ALL components VCC (+) and GND (-))
First, let's establish our power and ground lines. It helps to daisy-chain your ground wires or create a small ground hub.

VBUS (Pin 40, 5V from USB): Connect your LED Strip VCC here.
3V3 (Pin 36, 3.3V Out): Connect the Joystick VCC, Magnetometer VCC, and Rotary Encoder VCCs here.
GND (Any Ground Pin): Connect the GND from all components (LEDs, Joystick, Magnetometer, Encoders, Extra Switches, etc.) to the microcontroller's ground.
2. The Key Matrix (Macro Keyboard)
To save pins, the mechanical switches are wired in a 5x5 matrix. You will need to solder diodes to your switches to prevent "ghosting" when pressing multiple keys.

🚨 CRITICAL DIODE NOTE: When soldering the 1N4148 diodes to the mechanical switches, the black line on the diode must face AWAY from the switch pin, Check the image.

* Rows (Solder to the diode tails):

Row 1 ➔ GP0
Row 2 ➔ GP1
Row 3 ➔ GP2
Row 4 ➔ GP3
Row 5 ➔ GP4
Columns (Solder to the other switch pin): (Note: These are wired in reverse order in the code! Don't worry we can always change the pin numbers in the code)
Col 1 ➔ GP9
Col 2 ➔ GP8
Col 3 ➔ GP7
Col 4 ➔ GP6
Col 5 ➔ GP5
3. The Space Mouse (Magnetometer & Joystick)
This is the core of our 3D navigation!

Magnetometer (MLX90393): This communicates via I2C. Ensure your breakout board is in I2C mode.
SDA ➔ GP16
SCL ➔ GP17

Analog Joystick Module:
VRx (X-Axis) ➔ GP27
VRy (Y-Axis) ➔ GP26
SW (Button) ➔ GP22

4. Rotary Encoders & Extra Buttons
These give you scroll and quick-action control.

Encoder 1 (Left - Horizontal Scroll / Right Click):
CLK ➔ GP10
DT ➔ GP11
SW ➔ GP12
Encoder 2 (Right - Vertical Scroll / Home):
CLK ➔ GP13
DT ➔ GP14
SW ➔ GP15
Extra Button 1 (F6 - Fit View): Wire one leg to GP18, the other to GND.
Extra Button 2 (Mode/Color Cycle): Wire one leg to GP19, the other to GND.
5. RGB Lighting
To give the macro pad that premium glow:

WS2812B Data In (DIN): ➔ GP28

