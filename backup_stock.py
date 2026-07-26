import paramiko
import os
import base64
import warnings; warnings.filterwarnings("ignore")

HOST = "192.168.1.1"
PORT = 222
PASSWORD = "keenetic"
BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup")
os.makedirs(BACKUP_DIR, exist_ok=True)

PARTITIONS = {
    "preloader":  ("mtd1",  0x80000),
    "uboot":      ("mtd2",  0x200000),
    "u-config":   ("mtd3",  0x80000),
    "rf-eeprom":  ("mtd4",  0x400000),
    "firmware_1": ("mtd7",  0x3800000),
    "firmware_2": ("mtd14", 0x3800000),
}

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"Connecting to {HOST}:{PORT} ...")
    ssh.connect(HOST, port=PORT, username="root", password=PASSWORD,
                look_for_keys=False, allow_agent=False, timeout=30)

    for name, (mtd, size) in PARTITIONS.items():
        local = os.path.join(BACKUP_DIR, f"{name}.bin")
        print(f"\n[{name}] /dev/{mtd} ({size/1024/1024:.1f} MB) ...", end=" ", flush=True)

        # Read via base64 through SSH
        cmd = f"dd if=/dev/{mtd} bs=65536 2>/dev/null | base64"
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
        result = stdout.read()
        err = stderr.read().decode().strip()

        if err:
            print(f"STDERR: {err}")

        with open(local, "wb") as f:
            f.write(base64.b64decode(result))

        actual = os.path.getsize(local)
        print(f"saved {actual/1024/1024:.2f} MB")

    print(f"\nDone! Backup: {BACKUP_DIR}")

except Exception as e:
    print(f"\nError: {type(e).__name__}: {e}")
finally:
    try: ssh.close()
    except: pass
