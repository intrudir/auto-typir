import sys
import pyautogui
from time import sleep


def help():
    msg = (
"""
Pass a path to your input file as the first arg to this script.

e.g. 'python3 auto-typir.py ./input.txt'

I will read it and give you 10 seconds to click into your desired area where I will type your text.
""")
    print(msg)


if len(sys.argv) <= 1:
    help()
    sys.exit(0)

input_file = sys.argv[1]
try:
    with open(input_file, "r") as inf:
        text = inf.read()
except FileNotFoundError:
    print(f"\nInput file '{input_file}' not found. Exiting...")
    sys.exit(1)

print("10 seconds to click into the textbox you want to type in...")
sleep(10)

pyautogui.typewrite(text+"\n")
