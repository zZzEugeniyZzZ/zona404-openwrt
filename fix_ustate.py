import paramiko, warnings, time
warnings.filterwarnings("ignore")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.1.1", port=222, username="root", password="keenetic",
            look_for_keys=False, allow_agent=False, timeout=30)

print("Current U-State:")
stdin, stdout, stderr = ssh.exec_command("hexdump -C /dev/mtd11 | head -2", timeout=10)
print(stdout.read().decode().strip())

# The correct U-State: USTA + version=1 + slot=2 + try=2 + reserved=0
# Write using flash_erase + nandwrite
# Create correct U-State via base64 (avoids shell escaping issues with \x02)
import base64
ustate = b"\x55\x53\x54\x41\x01\x02\x02\x00"  # USTA + version=1 + slot=2 + try=2 + reserved=0
ustate_b64 = base64.b64encode(ustate).decode()

print("\nWriting correct U-State (slot 2) ...")
stdin, stdout, stderr = ssh.exec_command("flash_erase /dev/mtd11 0 0 2>/dev/null", timeout=60)
stdout.channel.recv_exit_status()

cmd = f"echo '{ustate_b64}' | base64 -d > /tmp/ustate.bin && " \
      f"nandwrite -p /dev/mtd11 /tmp/ustate.bin 2>/dev/null && echo OK || echo FAIL"
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
print(f"Result: {stdout.read().decode().strip()}")

print("\nNew U-State:")
stdin, stdout, stderr = ssh.exec_command("hexdump -C /dev/mtd11 | head -2", timeout=10)
print(stdout.read().decode().strip())

ssh.exec_command("rm /tmp/ustate.bin", timeout=10)

print("\nRebooting ...")
time.sleep(2)
ssh.exec_command("reboot", timeout=5)
ssh.close()
print("Done. Wait 3 min, then try: ssh root@192.168.1.1")
print("(OpenWrt uses port 22, not 222)")
