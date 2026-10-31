# Ripple Glasses

Code for ripple glasses electronics (microcontroller and embedded system)

## Setup with PlatformIO

1. Download VS Code and enable the WSL distro. Follow [these](https://code.visualstudio.com/docs/remote/wsl) instructions for more information.
2. Add the extension Remote Development, which will allow you to connect to WSL on your system. 
3. Download python using the following:
```
sudo apt update
sudo apt install python3 python3-pip python3-venv
```
4. Add the Platform IO extension. [These](https://docs.platformio.org/en/latest/integration/ide/vscode.html#quick-start) instructions can give you more detail if needed.
5. Navigate to the revision you would like to update/explore on your terminal
6. Execute the command `code {folder to open}`. If the revision does not exist yet, navigate to Platform IO home and add your project by Creating New Project. Make sure you add it to the github repository in `~/crocker_fellowship/platformio`
7. Link the device to your project. Refer to the header __Linking to WSL__ for more information.
8. Ensure that the baud rate in the `src/` folder matches the `platformio.ini` file. If unsure, explicitly define it in `platformio.ini` to match what is in `src/`:
```
monitor_speed = {BAUD_RATE}
```
9. Try uploading it. Everything should work now! After uploading, you can access the serial monitor on the PlatformIO terminal "Monitor" tab.
10. If you have issues with PSRAM allocation, follow this:
	- In `platformio.ini`, add 
```
board_build.arduino.memory_type = qio_qspi
build_flags =
    -DBOARD_HAS_PSRAM
```
	- Run `rm -rf .pio`
	- Run `pio run --target clean`
	- Run `pio run`
	- PSRAM should allocate correctly now
11. If you have issues running `pio` commands from the VS terminal, follow this:
	- Run `find ~/.platformio -iname "pio" 2>/dev/null`
	- Take the output from that command and use it here: 
```
echo 'export PATH=$PATH:{path you found minus last pio folder}' >> ~/.bashrc
source ~/.bashrc
which pio
pio --version
```
	- You should now be able to use `pio` commands in the terminal

## Linking to WSL

Since WSL2 can't access the device scanner within Windows, we must manually bind the new device to WSL for PlatformIO to use. I wrote
a PowerShell script - with the help of AI - that should bind an already-registered device to WSL when connected/reconnected. That script
is found within the main directory of this repo at `Scripts/usbipd-auto-attach`. To get it to work on your computer, run the following
command within PowerShell as an administrator:
	1. Add the directory `Scripts/usbipd-auto-attach` to a local location on
your Windows environment. Make sure to note the full file path. 
	2. Connect the microcontroller via USB
	3. Execute `usbipd list` on the command line and search for your MCU.
It should say something like `Silicon Labs CP210x USB to UART Bridge` followed
by the port number. Store for later use the number under the column `VID:PID`.
	4. Run the following commands:
```
$action  = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"C:\path\to\file\Scripts\usbipd-auto-attach.ps1`" -HardwareId <VID:PID>"
$trigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -TaskName "usbipd-auto-attach-<VID:PID>" -Action $action -Trigger $trigger -RunLevel Limited -Force
```
This task should now run in the background whenever you log into Windows. 
	5. Confirm that the task was generated correctly by running `(Get-ScheduledTask -TaskName "usbipd-auto-attach").Actions | Select-Object Execute, Arguments`,
verifying that the arguments and flags are all correct (especially the VID:PID)
	6. Log off and back on and verify that the task is running by executing `Get-ScheduledTask -TaskName "usbipd-auto-attach*"`.
The status should be `Running` or `Ready`. You can also run `Get-ScheduledTask -TaskName "usbipd-auto-attach" | Get-ScheduledTaskInfo`
to ensure everything is working correctly. 
	
When adding a new device, repeat steps 3-6, which essentially creates a new process
for the new device. Your last check should be uploading to the device on PlatformIO. If it uploads successfully, you're done! If not, you might have to do some more debugging. If you don't want to have extra processes running
on your system, follow the steps below for a one-time bind to WSL:
        - `winget install usbipd`
        - `usbipd list`
        - Find your board on the list (should be something like "Silicon Labs CP210x USB to UART Bridge") and note its BUSID
        - Bind the board `usbipd bind --busid <BUSID>`
        - Attach it to WSL `usbipd attach --wsl --busid <BUSID>`
        - Verify that it exists in WSL (move to a WSL terminal) `ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null`

## Set up with Windows

This repo has been mostly developed in Linux, meaning it's implementation in Windows is a little tricky. I've decided to start developing a little more in Windows to test the new microphone array we have, the UMA-8 miniDSP microphone array. To set up this repo, follow these instructions:
1. Download the [Git Bash terminal for windows](https://git-scm.com/install/windows). Its configuration should be straight forward.
2. Navigate to `windows_streaming\audio_stream` or whatever sub directory of `windows_streaming\` you want to use. 
3. Since this section of the repo uses python, we will install python3 and the pip installer. Install python3 with the windows download and run `py -m pip --version` to ensure the pip installer works. 
4. Install a virtual environment `python3 -m venv .venv`.
5. Activate the virtual environment `.\.venv\Scripts\Activate.ps1`. This step may require that you change the ExecutionPolicy of your computer. Change this by running `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force`.
6. Run `py -m pip install -r .\requirements.txt`. `requirements.txt` holds the necessary modules that the specific subdirectory needs. Without these, the py scripts will not run correctly. 
7. You can now run the scripts successfully! Once done, make sure to run `deactivate` to deactivate the virtual environment. 

## Changelog

- 1/13/2026 Arduino MKR WiFi 1010 was received
- 1/14/2026 Arduino MKR WiFi 1010 was configured
- 1/15/2026 Arduino MKR WiFi 1010 is able to sent digital pulses to L>
- 1/16/2026 Arduino MKR WiFi 1010 connected successfully to the inter>
- 1/17/2026 Arduino MKR WiFi 1010 is battery-powered and disconnected>
- 1/20/2026 Arduino MKR WiFi 1010 successfully outputted voltage to v>
- 1/21/2026 Implemented button logic to light up an LED
- 1/23/2026 Attached Thing to ESP32S3
- 1/27/2026 ESP32S3 added battery functionality
- 1/27/2026 Put in housing for further testing
- 1/30/2026 Added LED_PIN functionality for led blink
- 2/2/2026 Made Thing unique to prototype (Rev 6)
- 2/13/2026 Added App functionality and global variable
- 2/26/2026 Made Revision 7, making device smaller with smaller batte>
- 3/4/2026 Made Revision 8, connecting device to Firebase
- 3/16/2026 Made Revision 9, connecting device to App and creating ap>
- 3/18/2026 Finished defining finite states for app and microcontroll>
- 3/20/2026 Shifted to new prototype (Ripple Glasses)
- 4/8/2026 Completed Rev 1.3, able to capture sound bites 5 seconds i>
- 7/28/2026 Migrated to platformIO and updated git repo
- 8/4/2026: Updated I2S config for deprecated libraries
- 8/4/2026: Added script for binding devices to platformio running in WSL
- 10/30/2026: Configure new directory for beamform testing and audio streaming
- 10/31/2026: Add instructions for `audio_streaming` use
