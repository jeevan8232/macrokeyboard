# macrokeyboard
macro keyboard and space mouse using rpi pico. circuitpython code

Here is the complete, consolidated wiring list based on final code.

1. Power Distribution
* VBUS (Pin 40, 5V from USB): Connect LED Strip VCC here.
* 3V3 (Pin 36, 3.3V Out): Connect Joystick VCC, Magnetometer VCC, and Encoder (+) VCC here.
* GND (Any Ground Pin): Connect GND from all components (LEDs, Joystick, Magnetometer, Encoders, Extra Switches) here.

2. Signal Connections (GPIO)

A. Key Matrix (The Main Keyboard)
* Rows (R1 - R5):
    * Row 1 -> GP0
    * Row 2 -> GP1
    * Row 3 -> GP2
    * Row 4 -> GP3
    * Row 5 -> GP4
* Columns (C1 - C5): (Note: Based on your code, these are wired in reverse order)
    * Col 1 -> GP9
    * Col 2 -> GP8
    * Col 3 -> GP7
    * Col 4 -> GP6
    * Col 5 -> GP5

B. Rotary Encoders
* Encoder 1 (Left - Horizontal Scroll/Right Click):
    * CLK -> GP10
    * DT -> GP11
    * SW -> GP12
* Encoder 2 (Right - Vertical Scroll/Home):
    * CLK -> GP13
    * DT -> GP14
    * SW -> GP15

C. Space Mouse (Magnetometer - MLX90393)
* SDA -> GP16
* SCL -> GP17
    * Check: Ensure your breakout board is in I2C mode (usually the default).

D. Extra Buttons
* Extra Button 1 (F6 - Fit View): One leg to GP18, other leg to GND.
* Extra Button 2 (Mode/Color Cycle): One leg to GP19, other leg to GND.

E. Joystick Module
* VRx (X-Axis): -> GP27
* VRy (Y-Axis): -> GP26
* SW (Button): -> GP22

F. Lighting
* WS2812B Data In (DIN): -> GP28



