import paramiko, warnings, time, hashlib, base64, os
warnings.filterwarnings("ignore")

FW_FILE = r"E:\OpenWRT\openwrt-mediatek-filogic-netcraze_nc-1812-squashfs-factory.bin"
HOST, PORT, PASSWORD = "192.168.1.1", 222, "keenetic"

with open(FW_FILE, "rb") as f:
    fw_data = f.read()
fw_size = len(fw_data)
b64 = base64.b64encode(fw_data).decode()
local_md5 = hashlib.md5(fw_data).hexdigest()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username="root", password=PASSWORD,
            look_for_keys=False, allow_agent=False, timeout=30)

# Check if /tmp/fw.bin already exists
stdin, stdout, stderr = ssh.exec_command("wc -c < /tmp/fw.bin 2>/dev/null || echo 0", timeout=10)
existing = int(stdout.read().decode().strip())
print(f"Existing /tmp/fw.bin: {existing}B (need {fw_size}B)")

if existing != fw_size:
    print("\n=== Uploading firmware ===")
    transport = ssh.get_transport()
    channel = transport.open_session()
    channel.exec_command("cat | tr -d '\n' | base64 -d > /tmp/fw.bin && echo OK || echo FAIL")
    pos = 0
    buf = b64.encode()
    while pos < len(buf):
        n = channel.send(buf[pos:pos+65536])
        if n == 0: break
        pos += n
    channel.shutdown_write()
    result = b""
    while True:
        chunk = channel.recv(1024)
        if not chunk: break
        result += chunk
    print(f"Upload: {result.decode().strip()} ({pos}B)")

# Verify
stdin, stdout, stderr = ssh.exec_command("wc -c < /tmp/fw.bin; md5sum /tmp/fw.bin", timeout=15)
out = stdout.read().decode().strip().split()
remote_size, remote_md5 = int(out[0]), out[1]
print(f"Remote: {remote_size}B MD5: {remote_md5}")

if remote_size != fw_size or remote_md5 != local_md5:
    print("ERROR: file verification failed!")
    ssh.close()
    exit(1)

# Step 1: Erase Firmware_2
print("\n=== Step 1: Erasing Firmware_2 (mtd14) ===")
stdin, stdout, stderr = ssh.exec_command(
    "flash_erase /dev/mtd14 0 0 2>&1 && echo ERASE_OK || echo ERASE_FAIL",
    timeout=300)
out = stdout.read().decode().strip()
err = stderr.read().decode().strip()
print(f"Erase: {out}")
if err: print(f"  err: {err[:200]}")

# Step 2: Write firmware
print("\n=== Step 2: Writing firmware ===")
start = time.time()
stdin, stdout, stderr = ssh.exec_command(
    "nandwrite -p /dev/mtd14 /tmp/fw.bin 2>&1 && echo WRITE_OK || echo WRITE_FAIL",
    timeout=300)
out = stdout.read().decode().strip()
err = stderr.read().decode().strip()
elapsed = time.time() - start
print(f"Write ({elapsed:.0f}s): {out[:300]}")
if err: print(f"  err: {err[:300]}")

# Verify flash
print("\n=== Verify ===")
stdin, stdout, stderr = ssh.exec_command(
    "nanddump -l 64 -f - /dev/mtd14 2>/dev/null | hexdump -C | head -3",
    timeout=15)
print(stdout.read().decode().strip())

# Step 3: Update U-State to boot from slot 2
print("\n=== Step 3: Update U-State ===")
stdin, stdout, stderr = ssh.exec_command(
    "printf '\\x55\\x53\\x54\\x41\\x01\\x02\\x02\\x00' > /dev/mtd11 2>&1 && echo OK || echo FAIL",
    timeout=15)
print(f"U-State: {stdout.read().decode().strip()}")

# Verify
stdin, stdout, stderr = ssh.exec_command("hexdump -C /dev/mtd11 | head -2", timeout=10)
print("New U-State:")
print(stdout.read().decode().strip())

# Clean up
ssh.exec_command("rm /tmp/fw.bin", timeout=10)

# Step 4: Reboot
print("\n=== Step 4: Rebooting into OpenWrt ===")
print("This will disconnect SSH. Wait 3 min, then connect:")
print("  ssh root@192.168.1.1")
print()
time.sleep(2)
ssh.exec_command("sync; sleep 1; reboot", timeout=5)

ssh.close()
