# ARM64 Chromedriver Fix for undetected-chromedriver

## Problem

`undetected-chromedriver` v3.5.5 auto-downloads chromedriver from
Google's repos. On Linux, it always downloads the x86_64 binary,
even on ARM64/aarch64 systems. This causes:

```
OSError: [Errno 8] Exec format error:
'/root/.local/share/undetected_chromedriver/undetected_chromedriver'
```

The library re-downloads on every import if the binary is missing or
unpatched, so simply copying an ARM64 binary to the default path
gets overwritten.

## Fix

1. Find the system's ARM64 chromedriver:

```bash
find /snap /usr -name "chromedriver" -type f 2>/dev/null
# Typical locations:
# /snap/chromium/<build>/usr/lib/chromium-browser/chromedriver
# /usr/lib/chromium-browser/chromedriver
```

2. Verify it is ARM64:

```bash
file /snap/chromium/3478/usr/lib/chromium-browser/chromedriver
# Should show: ELF 64-bit LSB pie executable, ARM aarch64
```

3. Copy to a writable location:

```bash
mkdir -p /root/.local/share/uc-chromedriver/
cp /snap/chromium/3478/usr/lib/chromium-browser/chromedriver \
   /root/.local/share/uc-chromedriver/chromedriver
chmod +x /root/.local/share/uc-chromedriver/chromedriver
```

4. Use in code:

```python
import undetected_chromedriver as uc

driver = uc.Chrome(
    options=options,
    use_subprocess=True,
    browser_executable_path="/snap/bin/chromium",
    driver_executable_path="/root/.local/share/uc-chromedriver/chromedriver"
)
```

## Why the destination must be writable

The patcher modifies the chromedriver binary in-place (removes
automation signatures). Snap filesystems are read-only, so the
copy target must be on a writable filesystem (ext4, tmpfs, etc.).

## Verified on

- Oracle Cloud ARM64 (aarch64)
- Chromium 149.0.7827.200 (snap)
- undetected-chromedriver 3.5.5
- Python 3.11.15
