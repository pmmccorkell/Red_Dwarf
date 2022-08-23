![picture](https://github.com/pmmccorkell-usna/Red_Dwarf/blob/main/media/IMG_0964.jpg)

Run as sudo required to manipulate drivers for xbox controller.

Uses xbox-drv https://xboxdrv.gitlab.io/xboxdrv.html
sudo apt-get install xboxdrv
Uses xbox.py to interact with xbox-drv from FRC4564 Steven Jacobs https://github.com/FRC4564/Xbox

Uses Adafruit circuitpython bus libraries for i2c:
sudo apt-get install i2c-tools python3-smbus
sudo pip3 install adafruit-circuitpython-register
sudo pip3 install adafruit-circuitpython-busdevice

Uses Python API from 3-Space:
https://yostlabs.com/3-space-application-programming-interface/
move ThreeSpaceAPI.py and USB_ExampleClass.py to same directory as multi.py

Edit secrets.py with IP of QTM server.

Multiprocessing Only:
Requires pyqtgraph for plotting, which additionally requires qt5, pyqt5, etc.
  - raspi4 solution:
    - Have to cross-compile Qt5 (use wsl) to satisfy pyqtgraph version requirements:
      https://www.interelectronix.com/qt-515-cross-compilation-raspberry-compute-module-4-ubuntu-20-lts.html
    - If dependency and held package issues are raised at early steps, install aptitude  for smarter dependency handling than base apt or synaptic:
      apt-get install aptitude

  - wsl solution:
    https://github.com/Electron-Cash/Electron-Cash/issues/892
    sudo pip3 install --user -I PyQt5
    sudo pip3 install --user -I PyQt5-sip

