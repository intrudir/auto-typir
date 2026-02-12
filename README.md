# auto-typir

Type text into locked-down VDIs when clipboard is disabled. Perfect for infil: passwords, base64-encoded files, anything text-based.

## Install

```bash
pip install pyautogui pyperclip
brew install 1password-cli  # optional, for 1Password integration
```

## Quick Start

```bash
# Type a password from file
python3 auto-typir.py password.txt

# Type literal text
python3 auto-typir.py --text "MyP@ssw0rd!"

# Pull directly from 1Password (no files needed)
python3 auto-typir.py --op "op://Personal/VDI Login/password"

# Type whatever's in your clipboard
python3 auto-typir.py -c
```

## 1Password Integration

Pull secrets directly from your vault — no temp files, no clipboard history.

```bash
# Type a password
python3 auto-typir.py --op "op://Vault/Item/password"

# Type a TOTP code
python3 auto-typir.py --op "op://Vault/Item/one-time password"

# Multi-account setup (work vs personal)
python3 auto-typir.py --op "op://Work Vault/Client VDI/password" --op-account work
```

**Finding your secret reference:**
1. Open 1Password desktop app
2. Right-click the field you want → **Copy Secret Reference**
3. Use that `op://...` string with `--op`

**Requirements:**
- 1Password CLI: `brew install 1password-cli`
- 1Password desktop app must be unlocked (Touch ID prompt on use)
- Enable CLI integration: 1Password → Settings → Developer → "Integrate with 1Password CLI"

## Options

| Flag | Short | Description |
|------|-------|-------------|
| `--text` | `-t` | Type literal text instead of from file |
| `--op` | `-o` | Read secret from 1Password (`op://vault/item/field`) |
| `--op-account` | | 1Password account shorthand (multi-account) |
| `--clipboard` | `-c` | Read from clipboard and type it out |
| `--delay` | `-d` | Seconds before typing starts (default: 5) |
| `--interval` | `-i` | Delay between keystrokes in seconds (default: 0) |
| `--chunk` | | Pause every N characters (large files) |
| `--chunk-delay` | | Seconds to pause between chunks (default: 1) |
| `--no-newline` | `-n` | Don't add newline at end |
| `--dry-run` | | Preview without typing |

## Examples

### Password Infil

```bash
# From 1Password (recommended)
python3 auto-typir.py --op "op://Work/Client Portal/password"

# From clipboard
python3 auto-typir.py -c

# From file
python3 auto-typir.py client_pass.txt

# Literal (not recommended - shows in shell history)
python3 auto-typir.py --text "hunter2"
```

### File Transfer

```bash
# On your machine - encode the file
base64 payload.zip > payload.b64

# Type into notepad/terminal on VDI (click in within 5 seconds)
python3 auto-typir.py payload.b64 --chunk 1000 --interval 0.01

# On the VDI - decode
base64 -d payload.b64 > payload.zip        # Linux/Mac
certutil -decode payload.b64 payload.zip   # Windows
```

### Laggy VDI Tuning

```bash
# Slow typing (50ms between keystrokes)
python3 auto-typir.py input.txt --interval 0.05

# Chunked typing (pause every 500 chars)
python3 auto-typir.py large.b64 --chunk 500 --chunk-delay 2

# Both (very slow VDI)
python3 auto-typir.py large.b64 --interval 0.02 --chunk 500 --chunk-delay 3
```

## Aborting

- **Move mouse to top-left corner** — pyautogui failsafe, instant abort
- **Ctrl+C** — keyboard interrupt

## Tips

- **Laggy VDI?** Start with `--interval 0.05`, increase if still dropping chars
- **Large files?** Use `--chunk 500` to avoid buffer overflows
- **Testing?** Always `--dry-run` first
- **Special chars?** Fully supported (`!@#$%^&*` etc.)
- **Faster countdown?** `--delay 3` for 3 seconds instead of 5
