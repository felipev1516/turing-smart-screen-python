import os
import signal
import sys
import time
import datetime
import psutil


sys.path.append('./$(pwd)/../')

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
  
  while not stop:
    # Update the current time every second
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    lcd_comm.DisplayText(text=current_time,
                         x=21, y=30,
                         font=FONT_PATH,
                         font_size=20,
                         font_color=(255, 255, 255),
                         background_image=background)
    if os.name == 'posix':
      # Post IP address
      try:
        # Thanks to DougieLAwson @ https://forums.raspberrypi.com/viewtopic.php?t=79936
        import socket
        gw = os.popen("ip -4 route show default").read().split()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((gw[2],0))
        ip_address = s.getsockname()[0] # Get the local IP address
        logger.info(f"IP Address: {ip_address}")
        lcd_comm.DisplayText(text=f"IP: {ip_address}", 
                              x=260, y=30,
                              font=FONT_PATH,
                              font_size=20,
                              font_color=(255, 255, 255),
                              background_image=background)
      except Exception as e:
        logger.error(f"Failed to get IP address: {e}")
        ip_address = "0.0.0.0"  # Default IP address
        lcd_comm.DisplayText(text=f"IP: {ip_address}", 
                              x=260, y=30, 
                              font=FONT_PATH,
                              font_size=20,
                              font_color=(255, 255, 255),
                              background_image=background)

      # CPU Usage and RAM usage for POSIX-compliant systems
      logger.info("Running on a POSIX-compliant system (Linux, macOS, etc.)")
      CPU_Usage = psutil.cpu_percent(interval=1)
      logger.info(f"CPU Usage: {CPU_Usage}%")
      
      # Print CPU Usage in the radial progress bar
      lcd_comm.DisplayRadialProgressBar(155,105,40,4,
          angle_start=135, angle_end=405,
          min_value=0, max_value=100, value=CPU_Usage,angle_sep=0,
          background_image=background,
          bar_color=(255, 255, 255),
          clockwise=True,
          text=f"{CPU_Usage}%",
          font=FONT_PATH,
          font_size=25,
          font_color=(255, 255, 255),
          with_text=True,
      )
      # Get CPU temperature
      logger.info("Reading CPU temperature")
      tempature = os.popen("cat /sys/class/thermal/thermal_zone0/temp").read()
      try:
          tempature = int(tempature.strip())  # Read temperature from the file 
      except ValueError:
          logger.error("Failed to convert CPU temperature to integer")
          tempature = None
      # Check if temperature is None or 0
      # If temperature is None or 0, set it to 0
      # This is to avoid displaying an incorrect temperature value
      # If temperature is 0, it means the temperature could not be read
      if tempature is None or tempature == 0:
          logger.error("Failed to read CPU temperature")
          tempature = 0
      else:
          tempature = tempature / 1000.0  # Convert to Celsius
      
      logger.info(f"Temperature: {tempature}°C")  
      
      # Print CPU Temperature in the radial progress bar
      lcd_comm.DisplayRadialProgressBar(155,200,40,8,
          angle_start=135, angle_end=405,
          min_value=0, max_value=100, value=tempature,
          background_image=background,
          bar_color=(255, 255, 255),
          clockwise=True,
          text=f"{tempature:.1f}°C",
          font=FONT_PATH,
          font_size=20,
          font_color=(255, 255, 255),
          with_text=True,
      )

      #RAM usage
      ram = psutil.virtual_memory()
      total_ram = ram.total // (1024 * 1024)
      used_ram = ram.used // (1024 * 1024)
      free_ram = ram.free // (1024 * 1024)
      logger.info(f"RAM: Total: {total_ram}MB, Used: {used_ram}MB, Free: {free_ram}MB")
      # Print RAM Usage in the radial progress bar
      ram_usage = ram.percent
      lcd_comm.DisplayRadialProgressBar(395,105,40,4,
          angle_start=135, angle_end=405,
          min_value=0, max_value=100, value=ram_usage,angle_sep=0,
          background_image=background,
          bar_color=(255, 255, 255),
          clockwise=True,
          text=f"{ram_usage}%",
          font=FONT_PATH,
          font_size=20,
          font_color=(255, 255, 255),
          with_text=True,
      )
      # Determine if docker is running with a active container
      docker_running = os.system("docker ps -q") != 0
      if docker_running:
          logger.info("Docker is running with active containers")
          lcd_comm.DisplayStatusCircle(21,255, 30, 30, 15, status=True,
                                       background_image=background)
      else:
          logger.info("Docker is not running or has no active containers")
          lcd_comm.DisplayStatusCircle(21,255, 30, 30, 15, status=False,
                                       background_image=background)
    elif os.name == 'nt':
      # CPU Usage and RAM usage for Windows systems
      logger.info("Running on a Windows system")
      CPU_Usage = psutil.cpu_percent(interval=1)
      logger.info(f"CPU Usage: {CPU_Usage}%")
      # Print CPU Usage in the radial progress bar
      lcd_comm.DisplayRadialProgressBar(155,105,40,4,
          angle_start=135, angle_end=405,
          min_value=0, max_value=100, value=CPU_Usage,angle_sep=0,
          background_image=background,
          bar_color=(255, 255, 255),
          clockwise=True,
          text=f"{CPU_Usage}%",
          font=FONT_PATH,
          font_size=25,
          font_color=(255, 255, 255),
          with_text=True,
      )
      # Get CPU temperature
      logger.info("Reading CPU temperature")
      try:
          import wmi
          c = wmi.WMI(namespace="root\\wmi")
          temperature_info = c.MSAcpi_ThermalZoneTemperature()[0]
          tempature = (temperature_info.CurrentTemperature / 10.0) - 273.15  # Convert to Celsius
          logger.info(f"Temperature: {tempature}°C")
      except Exception as e:
          logger.error(f"Failed to read CPU temperature: {e}")
          tempature = 0.0
      # Print CPU Temperature in the radial progress bar
      lcd_comm.DisplayRadialProgressBar(155,200,40,8,
          angle_start=135, angle_end=405,
          min_value=0, max_value=100, value=tempature,
          background_image=background,
          bar_color=(255, 255, 255),
          clockwise=True,
          text=f"{tempature}°C",
          font=FONT_PATH,
          font_size=25,
          font_color=(255, 255, 255),
          with_text=True,
      )
      # RAM usage
      ram = psutil.virtual_memory()
      total_ram = ram.total // (1024 * 1024)
      used_ram = ram.used // (1024 * 1024)
      free_ram = ram.free // (1024 * 1024)
      logger.info(f"RAM: Total: {total_ram}MB, Used: {used_ram}MB, Free: {free_ram}MB")
      # Print RAM Usage in the radial progress bar
      ram_usage = ram.percent
      lcd_comm.DisplayRadialProgressBar(395,105,40,4,
          angle_start=135, angle_end=405,
          min_value=0, max_value=100, value=ram_usage,angle_sep=0,
          background_image=background,
          bar_color=(255, 255, 255),
          clockwise=True,
          text=f"{ram_usage}%",
          font=FONT_PATH,
          font_size=25,
          font_color=(255, 255, 255),
          with_text=True,
      )
      # Determine if docker is running with a active container
      docker_running = os.system("docker ps -q") != 0
      if docker_running:
          logger.info("Docker is running with active containers")
          lcd_comm.DisplayStatusCircle(21,255, 30, 30, 15, status=True,
                                       background_image=background)
      else:
          logger.info("Docker is not running or has no active containers")
          lcd_comm.DisplayStatusCircle(21,255, 30, 30, 15, status=False,
                                       background_image=background)
    else:
      logger.error(f"Unsupported OS: {os.name}. Only POSIX-compliant systems and Windows are supported.")
      sys.exit(1)
      break
    # Sleep for a second before the next update
    logger.debug("Sleeping for 1 second before next update")
    time.sleep(1)

   # Close serial connection at exit
  lcd_comm.closeSerial()
