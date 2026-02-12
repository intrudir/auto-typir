#!/usr/bin/env python3
"""
auto-typir - Type text into locked-down VDIs when clipboard is disabled.
Perfect for infil: passwords, base64 files, anything text-based.

Supports 1Password CLI integration for secure password retrieval.
"""

import argparse
import subprocess
import sys
from time import sleep

try:
    import pyautogui
except ImportError:
    print("ERROR: pyautogui not installed. Run: pip install pyautogui")
    sys.exit(1)


def read_from_1password(secret_ref: str, account: str = None) -> str:
    """
    Read a secret from 1Password using the CLI.
    
    Args:
        secret_ref: Secret reference (e.g., op://vault/item/field)
        account: Optional account shorthand for multi-account setups
    
    Returns:
        The secret value
    """
    cmd = ["op", "read", secret_ref]
    if account:
        cmd.extend(["--account", account])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except FileNotFoundError:
        print("ERROR: 1Password CLI (op) not found. Install with: brew install 1password-cli")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        if "not signed in" in e.stderr.lower():
            print("ERROR: Not signed in to 1Password. Run: op signin")
        elif "could not be found" in e.stderr.lower():
            print(f"ERROR: Secret not found: {secret_ref}")
        else:
            print(f"ERROR: 1Password CLI failed: {e.stderr.strip()}")
        sys.exit(1)

# Disable pyautogui's failsafe (move mouse to corner to abort)
# We'll handle our own abort logic
pyautogui.FAILSAFE = True


def countdown(seconds: int) -> bool:
    """Countdown with option to abort. Returns False if aborted."""
    print(f"\n⏱️  {seconds} seconds to click into target window...")
    print("   (Move mouse to top-left corner to abort)\n")
    
    for i in range(seconds, 0, -1):
        print(f"   {i}...", end=" ", flush=True)
        sleep(1)
    print("\n")
    return True


def type_text(text: str, interval: float = 0.0, chunk_size: int = 0, chunk_delay: float = 1.0):
    """
    Type text character by character.
    
    Args:
        text: Text to type
        interval: Delay between keystrokes in seconds (0 = fast as possible)
        chunk_size: If > 0, pause every N characters
        chunk_delay: Seconds to pause between chunks
    """
    total = len(text)
    typed = 0
    
    print(f"📝 Typing {total} characters...")
    
    for i, char in enumerate(text):
        # pyautogui.write() doesn't handle special chars well
        # Using press() for special keys and write() for regular chars
        if char == '\n':
            pyautogui.press('enter')
        elif char == '\t':
            pyautogui.press('tab')
        else:
            # write() with interval handles most chars including special ones
            pyautogui.write(char, interval=0)
        
        typed += 1
        
        # Progress update every 100 chars or at the end
        if typed % 100 == 0 or typed == total:
            pct = int((typed / total) * 100)
            print(f"\r   Progress: {typed}/{total} ({pct}%)", end="", flush=True)
        
        # Chunk delay for large files
        if chunk_size > 0 and typed % chunk_size == 0 and typed < total:
            print(f"\n   ⏸️  Chunk pause ({chunk_delay}s)...", end="", flush=True)
            sleep(chunk_delay)
        
        # Inter-keystroke delay
        if interval > 0:
            sleep(interval)
    
    print("\n\n✅ Done!")


def main():
    parser = argparse.ArgumentParser(
        description="Type text into locked-down VDIs when clipboard is disabled.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage - type contents of a file
  python3 auto-typir.py password.txt
  
  # Type a base64 file with chunking (good for large files)
  python3 auto-typir.py encoded.b64 --chunk 500 --chunk-delay 2
  
  # Slow typing for laggy VDIs (50ms between keys)
  python3 auto-typir.py input.txt --interval 0.05
  
  # Quick 3 second countdown
  python3 auto-typir.py input.txt --delay 3
  
  # Type literal text instead of from file
  python3 auto-typir.py --text "MyP@ssw0rd!"
  
  # Type whatever is in your clipboard
  python3 auto-typir.py --clipboard
  
  # 1Password integration - type password directly from vault
  python3 auto-typir.py --op "op://Personal/VDI Login/password"
  
  # 1Password with specific account (multi-account setups)
  python3 auto-typir.py --op "op://Work/Client VDI/password" --op-account work
        """
    )
    
    parser.add_argument("file", nargs="?", help="File containing text to type")
    parser.add_argument("--text", "-t", help="Type literal text instead of from file")
    parser.add_argument("--op", "-o", metavar="REF",
                        help="Read from 1Password (e.g., op://vault/item/password)")
    parser.add_argument("--op-account", metavar="ACCOUNT",
                        help="1Password account shorthand (for multi-account setups)")
    parser.add_argument("--clipboard", "-c", action="store_true",
                        help="Read text from clipboard and type it out")
    parser.add_argument("--delay", "-d", type=int, default=5,
                        help="Seconds before typing starts (default: 5)")
    parser.add_argument("--interval", "-i", type=float, default=0.0,
                        help="Delay between keystrokes in seconds (default: 0)")
    parser.add_argument("--chunk", type=int, default=0,
                        help="Pause every N characters (good for large files)")
    parser.add_argument("--chunk-delay", type=float, default=1.0,
                        help="Seconds to pause between chunks (default: 1)")
    parser.add_argument("--no-newline", "-n", action="store_true",
                        help="Don't add newline at end (default adds one)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be typed without typing")
    
    args = parser.parse_args()
    
    # Get text to type
    if args.op:
        print(f"🔐 Reading from 1Password: {args.op}")
        text = read_from_1password(args.op, args.op_account)
        print("   ✓ Secret retrieved")
    elif args.clipboard:
        try:
            import pyperclip
        except ImportError:
            print("ERROR: pyperclip not installed. Run: pip install pyperclip")
            sys.exit(1)
        text = pyperclip.paste()
        if not text:
            print("ERROR: Clipboard is empty")
            sys.exit(1)
        print(f"📋 Read {len(text)} characters from clipboard")
    elif args.text:
        text = args.text
    elif args.file:
        try:
            with open(args.file, "r") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"ERROR: File '{args.file}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Could not read file: {e}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)
    
    # Strip trailing whitespace but preserve internal structure
    text = text.rstrip()
    
    # Add newline at end unless disabled
    if not args.no_newline:
        text += "\n"
    
    # Dry run - just show what would happen
    if args.dry_run:
        print(f"\n🔍 DRY RUN - Would type {len(text)} characters:")
        print("-" * 40)
        if len(text) > 200:
            print(text[:100])
            print(f"... ({len(text) - 200} chars omitted) ...")
            print(text[-100:])
        else:
            print(text)
        print("-" * 40)
        return
    
    # Countdown
    print(f"\n🎯 Ready to type {len(text)} characters")
    print(f"   Mode: Typing (interval: {args.interval}s)")
    if args.chunk > 0:
        print(f"   Chunking: Every {args.chunk} chars, {args.chunk_delay}s pause")
    
    countdown(args.delay)
    
    # Do the thing
    try:
        type_text(text, args.interval, args.chunk, args.chunk_delay)
    except pyautogui.FailSafeException:
        print("\n\n⛔ ABORTED - Mouse moved to corner")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⛔ ABORTED - Ctrl+C")
        sys.exit(1)


if __name__ == "__main__":
    main()
