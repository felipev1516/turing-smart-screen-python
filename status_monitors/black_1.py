import os
import signal
import sys
import time
import datetime


sys.path.append('../')

from library.lcd.lcd_comm_rev_a import LcdCommRevA, Orientation
from library.lcd.lcd_simulated import LcdSimulated
from library.log import logger
from PIL import ImageFont

COM_PORT = "AUTO"  # Set your COM port e.g. COM3 for Windows, /dev/ttyACM0 for Linux, etc. or "AUTO" for auto-discovery
REVISION = "A"  # Display revision: A for Turing 3.5" and UsbPCMonitor 3.5"/5"
WIDTH, HEIGHT = 320, 480  # Display width & height in pixels for portrait
FONT_PATH = "./../res/fonts/Ubuntu/Ubuntu-Bold.ttf"  # Path to the font file
#FONT_PATH = "./../res/fonts/roboto/Roboto-Bold.ttf"
#FONT_PATH = "Ubuntu-Bold.ttf"
assert WIDTH <= HEIGHT, "Indicate display width/height for PORTRAIT orientation: width <= height"
stop = False

if __name__ == "__main__":
  def sighandler(signum, frame):
    global stop
    stop = True

  # Set the signal handlers, to send a complete frame to the LCD before exit
  signal.signal(signal.SIGINT, sighandler)
  signal.signal(signal.SIGTERM, sighandler)
  is_posix = os.name == 'posix'
  if is_posix:
    signal.signal(signal.SIGQUIT, sighandler)
  #Print OS Name in logger
  logger.info(f"Running on {os.name} system")

  # Build your LcdComm object based on the HW revision
  lcd_comm = None
  if REVISION == "A":
    logger.info("Selected Hardware Revision A (Turing Smart Screen 3.5\" & UsbPCMonitor 3.5\"/5\")")
    lcd_comm = LcdCommRevA(com_port=COM_PORT, display_width=WIDTH, display_height=HEIGHT)
  else:
    logger.error(f"Unsupported hardware revision: {REVISION}")
    sys.exit(1)

  # Reset screen in case it was in an unstable state (screen is also cleared)
  lcd_comm.Reset()
  
  # Initialize the LCD communication
  lcd_comm.InitializeComm()

  # Set backlight brightness
  lcd_comm.SetBrightness(level=10)

  #Set orientation (screen starts in Portrait)
  lcd_comm.SetOrientation(orientation=Orientation.REVERSE_LANDSCAPE)

  # Define background picture
  background = f"death_star_{lcd_comm.get_width()}x{lcd_comm.get_height()}.png"

  # Display Background image
  logger.debug("setting background picture")
  start = time.perf_counter()
  lcd_comm.DisplayBitmap(background)
  end = time.perf_counter()
  logger.debug(f"background picture set (took {end - start:.3f} s)")

  #Display current date and time
  current_time = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
  logger.info(f"Current time: {current_time}")
  lcd_comm.DisplayText(text=current_time,
                       x=21, y=30,
                       font=FONT_PATH,
                       font_size=20,
                       font_color=(255, 255, 255),
                       background_image=background)
 
  #Display IP address
  ip_address = "0.0.0.0"  # Default IP address
  lcd_comm.DisplayText(text=f"IP: {ip_address}",
                       x=260, y=30,
                       font=FONT_PATH,
                       font_size=20,
                       font_color=(255, 255, 255),
                       background_image=background)
  #Display CPU Usage Text
  logger.info("Displaying CPU temperature and RAM usage")
  lcd_comm.DisplayText(text=f"CPU\nUsage:",
                       x=21, y=75,
                       font=FONT_PATH,
                       font_size=25,
                       font_color=(255, 255, 255),
                       background_image=background)
  
  # Display CPU Usage Radial Progress Bar
  lcd_comm.DisplayRadialProgressBar(155,105,40,4,
      angle_start=135, angle_end=405,
      min_value=0, max_value=100, value=50,angle_sep=0,
      background_image=background,
      bar_color=(255, 255, 255),
      clockwise=True,
      text=f"50%",
      font=FONT_PATH,
      font_size=25,
      font_color=(255, 255, 255),
      with_text=True,
  )

  #Display CPU Temperature
  logger.info("Displaying CPU temperature and RAM usage")
  lcd_comm.DisplayText(text="CPU\nTemp:",
                       x=21, y=160,
                       font=FONT_PATH,
                       font_size=25,
                       font_color=(255, 255, 255),
                       background_image=background)
  
  # Display CPU Temperature Radial Progress Bar
  lcd_comm.DisplayRadialProgressBar(155,200,40,8,
      angle_start=135, angle_end=405,
      min_value=0, max_value=100, value=50,
      background_image=background,
      bar_color=(255, 255, 255),
      clockwise=True,
      text=f"50°C",
      font=FONT_PATH,
      font_size=25,
      font_color=(255, 255, 255),
      with_text=True,
  )
  # Display RAM usage Text
  lcd_comm.DisplayText(text="RAM\nUsage:",
                       x=260, y=75,
                       font=FONT_PATH,
                       font_size=25,
                       font_color=(255, 255, 255),
                       background_image=background)
  # Display RAM Usage Radial Progress Bar
  lcd_comm.DisplayRadialProgressBar(395,105,40,4,
      angle_start=135, angle_end=405,
      min_value=0, max_value=100, value=50,angle_sep=0,
      background_image=background,
      bar_color=(255, 255, 255),
      clockwise=True,
      text=f"50%",
      font=FONT_PATH,
      font_size=25,
      font_color=(255, 255, 255),
      with_text=True,
  )
  # Display Status Circle
  logger.info("Displaying Status Circle")
  lcd_comm.DisplayStatusCircle(21,255, 30, 30, 15, status=True,
                               background_image=background)
  #display small image
  lcd_comm.DisplayBitmap("./docker_logo_50x50.png", x=60, y=245, width=50, height=50)
  '''
  if os.name == 'posix':
    logger.info("Running on a POSIX-compliant system (Linux, macOS, etc.)")
    tempature = os.system("cat /sys/class/thermal/thermal_zone0/temp")
    if tempature != 0:
        logger.error("Failed to read temperature from thermal zone")
    else:
        tempature = tempature / 1000.0  # Convert to Celsius
        logger.info(f"Temperature: {tempature}°C")
    
    ram = os.popen("free -m").readlines()[1].split()[1:4]
    total_ram = int(ram[0])  # Total RAM in MB
    used_ram = int(ram[1])   # Used RAM in MB
    free_ram = int(ram[2])   # Free RAM in MB
    logger.info(f"RAM: Total: {total_ram}MB, Used: {used_ram}MB, Free: {free_ram}MB")

    #CPU usage
    cpu_usage = os.popen("top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\([0-9.]*\)%* id.*/\1/' | awk '{print 100 - $1}'").read().strip()
    logger.info(f"CPU Usage: {cpu_usage}%")
  elif os.name == 'nt':
    logger.info("Running on a Windows system")
    import psutil
    tempature = psutil.sensors_temperatures()
    if 'coretemp' in tempature:
        tempature = tempature['coretemp'][0].current
        logger.info(f"Temperature: {tempature}°C")
    else:
        logger.error("Temperature sensor not found")

    ram = psutil.virtual_memory()
    total_ram = ram.total // (1024 * 1024)  # Convert to MB
    used_ram = ram.used // (1024 * 1024)     # Convert to MB
    free_ram = ram.free // (1024 * 1024)     # Convert to MB
    logger.info(f"RAM: Total: {total_ram}MB, Used: {used_ram}MB, Free: {free_ram}MB")
  else:
    logger.error("Unsupported operating system. This script is designed for POSIX-compliant systems or Windows.")
    sys.exit(1)
    '''
   # Close serial connection at exit
  lcd_comm.closeSerial()