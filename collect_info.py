import paramiko
import json
import sys
import os
import time

HOST = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.1"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 222
PASSWORD = sys.argv[3] if len(sys.argv) > 3 else "keenetic"
USER = "root"

output = {}
OUTPUT_FILE = "nc1812_info.txt"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def run(cmd, timeout=30):
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode('utf-8', errors='replace')
        err = stderr.read().decode('utf-8', errors='replace')
        return out + err
    except Exception as e:
        return f"[ERROR] {e}"

def run_section(name, cmd, timeout=30):
    result = run(cmd, timeout)
    output[name] = result
    print(f"\n{'='*60}")
    print(f"=== {name}")
    print(f"{'='*60}")
    print(result[:5000])
    if len(result) > 5000:
        print(f"... (truncated, total {len(result)} chars)")

try:
    print(f"Connecting to {USER}@{HOST}:{PORT} ...")
    ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, look_for_keys=False, allow_agent=False, timeout=30)
    print("Connected successfully!")

    run_section("uname", "uname -a")
    run_section("cpuinfo", "cat /proc/cpuinfo")
    run_section("meminfo", "cat /proc/meminfo")
    run_section("version", "cat /proc/version")
    run_section("cmdline", "cat /proc/cmdline")
    run_section("mtd", "cat /proc/mtd")
    run_section("partitions", "cat /proc/partitions")
    run_section("dev_mtd", "ls -la /dev/mtd* 2>/dev/null; ls -la /dev/ubi* 2>/dev/null; ls -la /dev/mmc* 2>/dev/null")
    run_section("interrupts", "cat /proc/interrupts")
    run_section("iomem", "cat /proc/iomem")
    run_section("modules", "lsmod")
    run_section("network_interfaces", "ip addr 2>/dev/null || ifconfig")
    run_section("network_dev", "cat /proc/net/dev")

    # Wireless
    run_section("wireless", "iwinfo 2>/dev/null; iw dev 2>/dev/null; iw list 2>/dev/null || echo 'no iw/iwinfo'")
    run_section("wireless_proc", "cat /proc/net/wireless")

    # GPIO
    run_section("gpio_chips", "cat /sys/kernel/debug/gpio 2>/dev/null || echo 'debugfs not available'")
    run_section("gpio_base", "ls -la /sys/class/gpio/ 2>/dev/null || echo 'no /sys/class/gpio'")
    run_section("gpio_chip_labels", "for f in /sys/class/gpio/gpiochip*/label; do echo \"$f: $(cat $f 2>/dev/null)\"; done 2>/dev/null || echo 'no gpiochips'")
    run_section("gpio_chip_base", "for f in /sys/class/gpio/gpiochip*/base; do echo \"$f: $(cat $f 2>/dev/null)\"; done 2>/dev/null")
    run_section("gpio_chip_ngpio", "for f in /sys/class/gpio/gpiochip*/ngpio; do echo \"$f: $(cat $f 2>/dev/null)\"; done 2>/dev/null")

    # LEDs
    run_section("leds", "ls -la /sys/class/leds/ 2>/dev/null; for f in /sys/class/leds/*/trigger; do echo \"$f: $(cat $f 2>/dev/null)\"; done 2>/dev/null")
    run_section("leds_brightness", "for f in /sys/class/leds/*/brightness; do echo \"$f: $(cat $f 2>/dev/null)\"; done 2>/dev/null")

    # USB
    run_section("usb", "lsusb 2>/dev/null; ls -la /dev/usb* 2>/dev/null; cat /sys/kernel/debug/usb/devices 2>/dev/null || echo 'no usb debug'")
    run_section("usb_devices", "ls -la /dev/tty* 2>/dev/null")

    # Block devices
    run_section("block", "ls -la /sys/block/ 2>/dev/null")
    run_section("dmseg", "dmesg 2>/dev/null | head -500")
    run_section("dmseg_boot", "dmesg 2>/dev/null | grep -iE 'boot|uboot|bl2|bl31|atf|arm|mediatek|mt7988|mt7996' | head -200")

    # Device tree
    run_section("devicetree", "ls /sys/firmware/devicetree/base/ 2>/dev/null; ls /sys/firmware/devicetree/base/soc/ 2>/dev/null; cat /sys/firmware/devicetree/base/compatible 2>/dev/null; cat /sys/firmware/devicetree/base/model 2>/dev/null")
    run_section("dt_model", "for f in /sys/firmware/devicetree/base/*/device_type 2>/dev/null; do echo \"$f: $(cat $f)\"; done 2>/dev/null")

    # Flash info
    run_section("flash_info", "mtdinfo 2>/dev/null; ubinfo 2>/dev/null; cat /proc/mounts")
    run_section("mount", "mount")
    run_section("df", "df -h")

    # Packages/firmware version
    run_section("firmware_version", "cat /etc/version 2>/dev/null; cat /etc/openwrt_release 2>/dev/null; cat /etc/os-release 2>/dev/null; head -20 /etc/config/system 2>/dev/null")
    run_section("opkg", "opkg list-installed 2>/dev/null | head -100 || echo 'no opkg'")
    run_section("ndms_version", "ndms -v 2>/dev/null; ndmsVERSION 2>/dev/null; cat /etc/ndms_version 2>/dev/null; cat /etc/VERSION 2>/dev/null")

    # Process list
    run_section("ps", "ps 2>/dev/null || ps -ef 2>/dev/null || echo 'no ps'")

    # Switch info
    run_section("switch", "swconfig dev 2>/dev/null; swconfig list 2>/dev/null || echo 'no swconfig'")

    # I2C
    run_section("i2c", "i2cdetect -l 2>/dev/null; ls -la /dev/i2c* 2>/dev/null; ls -la /sys/bus/i2c/devices/ 2>/dev/null || echo 'no i2c'")

    # PWM
    run_section("pwm", "ls -la /sys/class/pwm/ 2>/dev/null; ls -la /sys/class/pwm/pwmchip*/ 2>/dev/null || echo 'no pwm'")

    # Serial ports
    run_section("serial", "setserial -g /dev/ttyS* 2>/dev/null; cat /proc/tty/drivers 2>/dev/null || echo 'no serial info'")

    # Thermal
    run_section("thermal", "cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null; ls -la /sys/class/thermal/ 2>/dev/null || echo 'no thermal'")

    # MAC addresses
    run_section("mac", "ip link 2>/dev/null | grep ether; ifconfig 2>/dev/null | grep HWaddr; cat /sys/class/net/*/address 2>/dev/null; cat /sys/class/net/*/addr_assign_type 2>/dev/null")

    # Write all to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("Netcraze Ultra NC-1812 System Information\n")
        f.write("=" * 60 + "\n")
        f.write(f"Host: {HOST}\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        for key, value in output.items():
            f.write(f"\n{'='*60}\n")
            f.write(f"=== {key}\n")
            f.write(f"{'='*60}\n")
            f.write(value)
            f.write("\n")

    print(f"\n\nAll information saved to: {OUTPUT_FILE}")
    print(f"File size: {os.path.getsize(OUTPUT_FILE)} bytes")

except paramiko.AuthenticationException:
    print("Authentication failed! Check password.")
except paramiko.SSHException as e:
    print(f"SSH error: {e}")
except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
