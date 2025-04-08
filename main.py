from time import sleep
from ili9341 import Display, color565
from machine import Pin, SPI, ADC
from xglcd_font import m64time, m64date, titelfont
from ustrftime import strftime
import utime
from DIYables_MicroPython_Joystick import Joystick
import gc



VRX_PIN = 39 # The ESP32 pin GPIO39 (ADC3) connected to VRX pin of joystick
VRY_PIN = 36 # The ESP32 pin GPIO36 (ADC0) connected to VRY pin of joystick
SW_PIN = 17  # The ESP32 pin GPIO17 connected to SW pin of joystick

gc.collect()

spi = SPI(1, baudrate=40000000, sck=Pin(18), mosi=Pin(23))
display = Display(spi, dc=Pin(2), cs=Pin(5), rst=Pin(4))

frame_folder = "images/sleepymario"

adc_vrx = ADC(Pin(VRX_PIN))
adc_vry = ADC(Pin(VRY_PIN))
# Set the ADC width (resolution) to 12 bits
adc_vrx.width(ADC.WIDTH_12BIT)
adc_vry.width(ADC.WIDTH_12BIT)
# Set the attenuation to 11 dB, allowing input range up to ~3.3V
adc_vrx.atten(ADC.ATTN_11DB)
adc_vry.atten(ADC.ATTN_11DB)

joystick = Joystick(pin_x=VRX_PIN, pin_y=VRY_PIN, pin_button=SW_PIN)

LEFT_THRESHOLD = 1000
RIGHT_THRESHOLD = 3000
UP_THRESHOLD = 1000
DOWN_THRESHOLD = 3000

# Define states
STATE_SLEEPYMARIO = 0
STATE_MENU = 1

app_state = STATE_SLEEPYMARIO  # Start in sleepymario state

joystick.set_debounce_time(100)
COMMAND_NO = 0x00
COMMAND_LEFT = 0x01
COMMAND_RIGHT = 0x02
COMMAND_UP = 0x04
COMMAND_DOWN = 0x08

def set_theme():
    display.clear()
    display.draw_text(90, 250, "Set``Theme", menufont, color565(255, 255, 255), landscape=True, rotate_180=True, spacing=3)
    display.draw_image('images/goclock70x50.raw', 5, 3, 70, 50)

def set_alarm():
    display.clear()
    display.draw_text(90, 250, "Set``Alarm", menufont, color565(255, 255, 255), landscape=True, rotate_180=True, spacing=3)
    display.draw_image('images/goclock70x50.raw', 5, 3, 70, 50)
    

menuindex = 0
    
menuoptions = {
    1: set_theme,
    2: set_alarm}

menu_list = list(menuoptions.keys())

def check_commands(x_value, y_value):
    command = COMMAND_NO

    # Check for left/right commands
    if x_value < LEFT_THRESHOLD:
        command |= COMMAND_LEFT
    elif x_value > RIGHT_THRESHOLD:
        command |= COMMAND_RIGHT

    # Check for up/down commands
    if y_value < UP_THRESHOLD:
        command |= COMMAND_UP
    elif y_value > DOWN_THRESHOLD:
        command |= COMMAND_DOWN

    return command

def sleepymario(folder, frame_count, delay=0.1):
    """Play frames stored as raw images sequentially."""
    global app_state
    while app_state == STATE_SLEEPYMARIO:
        for i in range(frame_count):
            if app_state != STATE_SLEEPYMARIO:
                break
            x_value = adc_vrx.read()
            y_value = adc_vry.read()
            command = check_commands(x_value, y_value)
            frame_file = f"{folder}/frame{i}.raw"  # Adjust based on naming
            # Draw the frame at (0, 0) with full screen resolution (240x320)
            display.draw_image(frame_file, 5, 70, 110, 180)
            process_input(command)
            sleep(delay)  # Maintain frame delay

def process_input(command):
    global app_state
    if command & COMMAND_UP:
        display.clear()
        app_state = STATE_MENU  # Transition to menu state

def menu():
    global app_state
    display.clear()
    display.draw_text(90, 250, "Set``Theme", menufont, color565(255, 255, 255), landscape=True, rotate_180=True, spacing=3)
    display.draw_image('images/goclock70x50.raw', 5, 3, 70, 50)
                
    while app_state == STATE_MENU:
        x_value = adc_vrx.read()
        y_value = adc_vry.read()
        command = check_commands(x_value, y_value)

        if command & COMMAND_DOWN:  # Exit menu
            app_state = STATE_SLEEPYMARIO
            display.clear()
            return
        if command & COMMAND_RIGHT:
            current_index = (current_index + 1) % len(menu_list)
           
            

timefont = m64time('fonts/Mario64.c', 48, 48)
datefont = m64date('fonts/Mario64Date.c', 24, 25)
menufont = titelfont('fonts/nintendofont.c', 26, 26)

def currenttimem64():
    # venstre y-akse højre x-akse
    localtime = utime.time()
    timenow = strftime("%H:%M", utime.localtime(localtime))
    datenow = strftime("%d/%m", utime.localtime(localtime))
    timenowfunc = f"{timenow}"
    datenowfunc = f"{datenow}"
    display.draw_image('images/wifi.raw', 180, 15, 55, 41)
    display.draw_text(120, 260, f"{timenowfunc}", timefont, color565(255, 255, 255),
                      landscape=True, rotate_180=True, spacing=5)
    display.draw_image('images/star20x20.raw', 210, 290, 20, 20)
    display.draw_image('images/border.raw', 190, 90, 37, 145)
    display.draw_text(200, 220, f"{datenow}", datefont, color565(255, 255, 255),
                      landscape=True, rotate_180=True, spacing=5)

while True:
    gc.collect()
    if app_state == STATE_SLEEPYMARIO:
        gc.collect()
        currenttimem64()
        sleepymario(frame_folder, frame_count=15, delay=0)
    elif app_state == STATE_MENU:
        menu()
        gc.collect()
