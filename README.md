# auto-typir
Need to file transfer at least one-way and clipboard access is disabled? Try me!

## Install
Need to install pyautogui
```python
python3 -m install pyautogui
```

## Usage
Ever needed to transfer some files onto a remote machine and your host to RDP or VM clipboard access is disabled?
Convert whatever it is into base64, then run this script to have it typed into wherever you need it!

The script will warn you that you have 10 seconds to click into whatever window you want to be typed into.

```bash
# b64 encode Mac or Linux
base64 needme.zip > input.txt

# b64 encode Windows
certutil -encode needme.zip input.txt

# run script
python3 auto-typir.py input.txt
```


