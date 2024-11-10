import time
import board
import adafruit_dht
import gpiod
import tkinter as tk
from tkinter import font

# GPIO pin setup
BUZZER_PIN = 17         # GPIO pin for Buzzer
MQ135_PIN = 27          # GPIO pin for MQ135 digital output
MQ9_PIN = 22            # GPIO pin for MQ9 digital output

# Initialize the DHT sensor (DHT11)
sensor = adafruit_dht.DHT11(board.D18)

# Initialize the GPIO chip and lines
chip = gpiod.Chip('gpiochip4')
buzzer_line = chip.get_line(BUZZER_PIN)
mq135_line = chip.get_line(MQ135_PIN)
mq9_line = chip.get_line(MQ9_PIN)

# Request lines for the Buzzer, MQ135, and MQ9 sensors
buzzer_line.request(consumer="Buzzer", type=gpiod.LINE_REQ_DIR_OUT)
mq135_line.request(consumer="MQ135", type=gpiod.LINE_REQ_DIR_IN)
mq9_line.request(consumer="MQ9", type=gpiod.LINE_REQ_DIR_IN)

# Tkinter GUI setup
root = tk.Tk()
root.title("Sensor Dashboard")

# Configure window size and background color
root.geometry("600x400")
root.configure(bg="lightgrey")

# Set custom font for the labels
label_font = font.Font(family="Helvetica", size=12, weight="bold")

# Create frames and labels for each sensor reading with specified colors and alignment
# Temperature on the left, half width
temp_frame = tk.Frame(root, bg="lightblue", padx=10, pady=10)
temp_frame.place(relwidth=0.5, relheight=0.3, x=0, y=0)
temp_label_c = tk.Label(temp_frame, text="Temperature (C): -- *C", font=label_font, bg="lightblue")
temp_label_c.pack()
temp_label_f = tk.Label(temp_frame, text="Temperature (F): -- *F", font=label_font, bg="lightblue")
temp_label_f.pack()

# Humidity on the right, half width
humidity_frame = tk.Frame(root, bg="lightgreen", padx=10, pady=10)
humidity_frame.place(relwidth=0.5, relheight=0.3, relx=0.5, y=0)
humidity_label = tk.Label(humidity_frame, text="Humidity: -- %", font=label_font, bg="lightgreen")
humidity_label.pack()

# MQ135 on the left, one-third width
mq135_frame = tk.Frame(root, bg="lightcoral", padx=10, pady=10)
mq135_frame.place(relwidth=0.33, relheight=0.3, rely=0.3)
mq135_status_label = tk.Label(mq135_frame, text="MQ135 Status: No Gas Detected", font=label_font, bg="lightcoral")
mq135_status_label.pack()

# MQ9 in the center, one-third width
mq9_frame = tk.Frame(root, bg="lightyellow", padx=10, pady=10)
mq9_frame.place(relwidth=0.33, relheight=0.3, relx=0.33, rely=0.3)
mq9_status_label = tk.Label(mq9_frame, text="MQ9 Status: No Gas Detected", font=label_font, bg="lightyellow")
mq9_status_label.pack()

# Buzzer Control Toggle Button on the right, one-third width
buzzer_state = False  # Initial state of the buzzer (off)
def toggle_buzzer():
    global buzzer_state
    buzzer_state = not buzzer_state  # Toggle the state
    buzzer_line.set_value(1 if buzzer_state else 0)  # Turn buzzer on or off
    buzzer_button.config(text="Turn Buzzer Off" if buzzer_state else "Turn Buzzer On")

buzzer_button = tk.Button(root, text="Turn Buzzer On", font=label_font, command=toggle_buzzer, bg="orange")
buzzer_button.place(relwidth=0.34, relheight=0.3, relx=0.66, rely=0.3)

# Function to update the readings
def update_readings():
    try:
        # Read temperature and humidity from the DHT sensor
        temperature_c = sensor.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = sensor.humidity

        # Update label values for DHT sensor
        temp_label_c.config(text=f"Temperature (C): {temperature_c:0.1f} *C")
        temp_label_f.config(text=f"Temperature (F): {temperature_f:0.1f} *F")
        humidity_label.config(text=f"Humidity: {humidity:0.1f}%")
        
        # Read the digital output from MQ135 and MQ9 (assuming LOW indicates gas presence)
        mq135_state = mq135_line.get_value()
        mq9_state = mq9_line.get_value()

        if mq135_state == 0:
            mq135_status_label.config(text="MQ135 Status: Gas Detected!", bg="red" if mq135_state == 0 else "lightcoral")
        else:
            mq135_status_label.config(text="MQ135 Status: No Gas Detected", bg="lightcoral")
            
            
        if mq9_state == 0:
            mq9_status_label.config(text="MQ9 Status: Gas Detected!", bg="orange" if mq9_state == 0 else "lightyellow")
        else:
            mq9_status_label.config(text="MQ9 Status: No Gas Detected", bg="lightyellow")
        
            
        # Check if either sensor is in a LOW state and turn on buzzer if needed
        if mq135_state == 0 or mq9_state == 0:
            if not buzzer_state:  # Only activate buzzer if the toggle button is off
                buzzer_line.set_value(1)  # Turn on buzzer  
        else:
            if not buzzer_state:  # Ensure buzzer is off if the toggle button is off
                buzzer_line.set_value(0)
            
    except RuntimeError as error:
        # In case of a DHT reading error
        print(error.args[0])
    except Exception as error:
        sensor.exit()
        raise error

    # Schedule the function to update after 3 seconds
    root.after(1000, update_readings)

# Start updating readings
update_readings()

# Run the Tkinter event loop
try:
    root.mainloop()
finally:
    # Release the GPIO lines
    buzzer_line.release()
    mq135_line.release()
    mq9_line.release()
