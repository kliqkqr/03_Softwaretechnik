# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
from pathlib import Path

from Config.ConfigFile import ConfigFile
from Speichermedium.Speicher import Speicher


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Strg+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('World')

    cf = ConfigFile()
    cf.loadSettings()
    cf.saveSettings()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
