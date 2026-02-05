import time
import board
import digitalio
import usb_hid
import rotaryio
import keypad
import analogio
import neopixel
import busio
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.mouse import Mouse

# --- 1. CONFIGURATION ---

COMMAND = Keycode.GUI 

# Key Matrix Pins
ROW_PINS = (board.GP0, board.GP1, board.GP2, board.GP3, board.GP4)
COL_PINS = (board.GP9, board.GP8, board.GP7, board.GP6, board.GP5)

# Encoder Pins
ENC1_CLK, ENC1_DT, ENC1_SW = board.GP10, board.GP11, board.GP12
ENC2_CLK, ENC2_DT, ENC2_SW = board.GP13, board.GP14, board.GP15

# Joystick & Extra Buttons
JOY_X_PIN = board.GP27
JOY_Y_PIN = board.GP26
JOY_SW_PIN = board.GP22
BTN_EXTRA1_PIN = board.GP18
BTN_EXTRA2_PIN = board.GP19

# I2C (Space Mouse) & LED
I2C_SDA, I2C_SCL = board.GP16, board.GP17
LED_PIN = board.GP28
NUM_LEDS = 4

# SCROLL SETTINGS
SCROLL_SPEED = 20  # Set to 1 for default, 2 or 3 for faster scrolling

# LED COLOR CYCLE SETTINGS
# 4 Colors + OFF at the end
LED_COLORS = [
    (255, 100, 0),   # 1. Cyan
    (0, 0, 255),   # 2. Magenta
    (255, 255, 0),   # 3. Yellow
    (255, 255, 255), # 4. White
    (0, 0, 0)        # 5. OFF
]

# SPACE MOUSE SETTINGS (Fusion 360)
SM_DEADZONE = 100.0      
SM_SENSITIVITY = 15.0   
SM_Z_THRESHOLD = 100.0   

# --- 2. SETUP OBJECTS ---

kbd = Keyboard(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)
mouse = Mouse(usb_hid.devices)

# LED Setup
pixels = neopixel.NeoPixel(LED_PIN, NUM_LEDS, brightness=1.0)
pixels.fill((255, 255, 0)) # Startup Orange (Not in cycle, just for boot)

# Matrix Setup
keys = keypad.KeyMatrix(ROW_PINS, COL_PINS, columns_to_anodes=True)

# Direct Keys
# Index 0: Extra1, Index 1: Extra2, Index 2: Joystick Btn
direct_keys = keypad.Keys(
    (BTN_EXTRA1_PIN, BTN_EXTRA2_PIN, JOY_SW_PIN),
    value_when_pressed=False,
    pull=True
)

# Encoders
encoder1 = rotaryio.IncrementalEncoder(ENC1_CLK, ENC1_DT)
last_position1 = 0
encoder2 = rotaryio.IncrementalEncoder(ENC2_CLK, ENC2_DT)
last_position2 = 0

# Encoder Switches
encoder_switches = keypad.Keys(
    (ENC1_SW, ENC2_SW),
    value_when_pressed=False,
    pull=True
)

# Joystick Analog
joy_x = analogio.AnalogIn(JOY_X_PIN)
joy_y = analogio.AnalogIn(JOY_Y_PIN)

# Magnetometer Setup & Calibration
mlx = None
mlx_offsets = [0, 0, 0] 

try:
    import adafruit_mlx90393
    i2c = busio.I2C(I2C_SCL, I2C_SDA, frequency=400_000)
    mlx = adafruit_mlx90393.MLX90393(i2c)
    mlx.gain = adafruit_mlx90393.GAIN_1X 
    print("MLX90393 Found! Calibrating...")
    
    # Calibration Routine
    x_sum, y_sum, z_sum = 0, 0, 0
    for _ in range(20):
        mx, my, mz = mlx.magnetic
        x_sum += mx
        y_sum += my
        z_sum += mz
        time.sleep(0.01)
    
    mlx_offsets = [x_sum/20, y_sum/20, z_sum/20]
    print("Calibration Done:", mlx_offsets)
    pixels.fill((0, 255, 0)) # Green = Ready
    time.sleep(0.2)
    pixels.fill(LED_COLORS[0]) # Set to first color in cycle

except Exception as e:
    print("MLX90393 Init Failed:", e)
    pixels.fill((255, 0, 0)) # Red = Error

# --- 3. KEY MAPPING ---

KEYMAP = [
    [(COMMAND, Keycode.C), (COMMAND, Keycode.V), (COMMAND, Keycode.A), None, None],
    [(COMMAND, Keycode.ALT, Keycode.V), (COMMAND, Keycode.F), Keycode.ESCAPE, None, None],
    [Keycode.HOME, Keycode.E, (COMMAND, Keycode.Z), Keycode.SPACEBAR, Keycode.L],
    [Keycode.SHIFT, Keycode.COMMAND, Keycode.UP_ARROW, Keycode.TAB, Keycode.RIGHT_CONTROL],
    [None, Keycode.LEFT_ARROW, Keycode.DOWN_ARROW, Keycode.RIGHT_ARROW, (COMMAND, Keycode.S)]
]

# --- 4. HELPER FUNCTIONS ---

def read_joystick(pin_obj):
    val = pin_obj.value
    if abs(val - 32768) < 2000:
        return 0
    return int((val - 32768) / 1000)

def handle_keypress(key_item, pressed):
    if pressed:
        if isinstance(key_item, tuple):
            kbd.press(*key_item)
        else:
            kbd.press(key_item)
    else:
        if isinstance(key_item, tuple):
            kbd.release(*key_item)
        else:
            kbd.release(key_item)

# --- 5. MAIN LOOP ---

print("Ready")

last_sensor_read = 0
sensor_interval = 0.02

# State Variables
is_orbiting = False
led_index = 0 # Tracks current color in cycle

while True:
    now = time.monotonic()

    # A. HANDLE MATRIX
    event = keys.events.get()
    if event:
        row, col = event.key_number // 5, event.key_number % 5
        key_code = KEYMAP[row][col]
        if key_code:
            handle_keypress(key_code, event.pressed)

    # B. HANDLE DIRECT KEYS
    direct_event = direct_keys.events.get()
    if direct_event and direct_event.pressed:
        
        if direct_event.key_number == 0:   # Extra Btn 1 -> F6
            kbd.send(Keycode.F6)
            
        elif direct_event.key_number == 1: # Extra Btn 2 -> CYCLE LED COLORS
            # Increment index, wrap around if at end
            led_index = (led_index + 1) % len(LED_COLORS)
            pixels.fill(LED_COLORS[led_index])
            
        elif direct_event.key_number == 2: # Joystick Btn -> Click
            mouse.click(Mouse.LEFT_BUTTON)

    # C. HANDLE ENCODER SWITCHES
    enc_sw_event = encoder_switches.events.get()
    if enc_sw_event and enc_sw_event.pressed:
        if enc_sw_event.key_number == 0:   # Encoder 1 Switch -> Right Click
            mouse.click(Mouse.RIGHT_BUTTON)
        elif enc_sw_event.key_number == 1: # Encoder 2 Switch -> Home Key
            kbd.send(Keycode.HOME)
    
    # D. HANDLE ENCODERS
    
    # Encoder 1: HORIZONTAL SCROLL
    current_position1 = encoder1.position
    delta1 = current_position1 - last_position1
    
    if delta1 != 0:
        kbd.press(Keycode.SHIFT)
        # Use delta * SCROLL_SPEED to handle fast spins and multiplier
        mouse.move(wheel=delta1 * SCROLL_SPEED)
        kbd.release(Keycode.SHIFT)
        last_position1 = current_position1

    # Encoder 2: VERTICAL SCROLL
    current_position2 = encoder2.position
    delta2 = current_position2 - last_position2
    
    if delta2 != 0:
        # We invert delta2 because your original logic had 'current > last' (positive)
        # resulting in 'wheel=-1' (negative).
        mouse.move(wheel=-delta2 * SCROLL_SPEED)
        last_position2 = current_position2

    # E. HANDLE SENSORS
    if now - last_sensor_read > sensor_interval:
        
        # 1. Joystick
        jx = read_joystick(joy_x)
        jy = read_joystick(joy_y)
        if jx != 0 or jy != 0:
            mouse.move(x=jx, y=jy)

        # 2. Space Mouse
        if mlx:
            try:
                raw_x, raw_y, raw_z = mlx.magnetic
                
                dx = raw_x - mlx_offsets[0]
                dy = raw_y - mlx_offsets[1]
                dz = raw_z - mlx_offsets[2]
                
                # Orbit Logic
                if abs(dx) > SM_DEADZONE or abs(dy) > SM_DEADZONE:
                    if not is_orbiting:
                        kbd.press(Keycode.SHIFT)
                        mouse.press(Mouse.MIDDLE_BUTTON)
                        is_orbiting = True
                    
                    move_x = int(dx / SM_SENSITIVITY)
                    move_y = int(dy / SM_SENSITIVITY) * -1 
                    
                    move_x = max(-127, min(127, move_x))
                    move_y = max(-127, min(127, move_y))
                    
                    mouse.move(x=move_x, y=move_y)
                else:
                    if is_orbiting:
                        mouse.release(Mouse.MIDDLE_BUTTON)
                        kbd.release(Keycode.SHIFT)
                        is_orbiting = False

                # Zoom Logic
                if not is_orbiting and abs(dz) > SM_Z_THRESHOLD:
                    if dz > 0:
                        mouse.move(wheel=1)
                    else:
                        mouse.move(wheel=-1)

            except Exception:
                pass 
        
        last_sensor_read = now

    time.sleep(0.001)