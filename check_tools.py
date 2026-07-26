import paramiko, warnings
warnings.filterwarnings("ignore")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.1.1", port=222, username="root", password="keenetic",
            look_for_keys=False, allow_agent=False, timeout=30)

# Try installing nand-utils which contains nandwrite and flash_erase
print("Installing nand-utils via opkg ...")
stdin, stdout, stderr = ssh.exec_command("opkg install nand-utils 2>&1", timeout=120)
out = stdout.read().decode().strip()
err = stderr.read().decode().strip()
print(out[:1000])
if err: print(f"ERR: {err[:300]}")

# Check if tools are now available
print("\nChecking installed tools:")
stdin, stdout, stderr = ssh.exec_command(
    "which nandwrite flash_erase nanddump 2>/dev/null; nandwrite --version 2>&1 | head -2",
    timeout=10)
print(stdout.read().decode().strip())

ssh.close()
