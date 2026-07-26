import paramiko, warnings, os, time, hashlib, base64
warnings.filterwarnings("ignore")

FW_FILE = r"E:\OpenWRT\openwrt-mediatek-filogic-netcraze_nc-1812-squashfs-factory.bin"
HOST, PORT, PASSWORD = "192.168.1.1", 222, "keenetic"

with open(FW_FILE, "rb") as f:
    fw_data = f.read()

fw_size = len(fw_data)
local_hash = hashlib.md5(fw_data).hexdigest()
b64 = base64.b64encode(fw_data).decode()

print(f"Firmware: {fw_size}B / {fw_size/1024/1024:.1f} MB")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username="root", password=PASSWORD,
            look_for_keys=False, allow_agent=False, timeout=30)

# Use a single channel with base64 piped through
transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command("tr -d '\n' | base64 -d > /tmp/fw.bin && echo OK || echo FAIL")

print("Sending base64 data via channel ...")
start = time.time()
buf = b64.encode()
pos = 0
while pos < len(buf):
    n = channel.send(buf[pos:pos+65536])
    if n == 0:
        print(f"ERROR: channel closed at byte {pos}/{len(buf)}")
        break
    pos += n

channel.shutdown_write()
output = b""
while True:
    chunk = channel.recv(1024)
    if not chunk:
        break
    output += chunk
channel.close()

elapsed = time.time() - start
print(f"Channel result: {output.decode().strip()}")
print(f"Time: {elapsed:.0f}s")

# Verify
stdin, stdout, stderr = ssh.exec_command("wc -c < /tmp/fw.bin; md5sum /tmp/fw.bin", timeout=15)
out = stdout.read().decode().strip().split()
remote_size, remote_hash = int(out[0]), out[1]
print(f"Remote: {remote_size}B MD5: {remote_hash}")
print(f"Local:  {fw_size}B MD5: {local_hash}")
print("OK!" if remote_size == fw_size and remote_hash == local_hash else "MISMATCH!")

ssh.close()
