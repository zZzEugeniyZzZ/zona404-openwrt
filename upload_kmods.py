import paramiko, base64, warnings, os, time
warnings.filterwarnings("ignore")

HOST = "192.168.1.1"
PORT = 22
PASSWORD = "!LoL-eSports"

ko_dir = os.path.join(os.environ["TEMP"], "opencode", "kmods", "kmods")
files = ["nfnetlink.ko", "nfnetlink_queue.ko", "xt_NFQUEUE.ko",
         "xt_connbytes.ko", "xt_connmark.ko", "xt_conntrack.ko"]
dest = "/lib/modules/6.18.39/"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username="root", password=PASSWORD,
            look_for_keys=False, allow_agent=False, timeout=15)
print("SSH OK")

# Create dest dir
_, stdout, _ = ssh.exec_command(f"mkdir -p {dest}")
stdout.read()

for f in files:
    local = os.path.join(ko_dir, f)
    remote = os.path.join(dest, f)
    with open(local, "rb") as fh:
        raw = fh.read()
    # Use printf with hex escape to write bytes
    hex_str = "".join(f"\\x{b:02x}" for b in raw)
    remote_esc = remote.replace("'", "'\\''")
    cmd = f"printf '{hex_str}' > '{remote_esc}' && echo OK:{f} || echo FAIL:{f}"
    _, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    result = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if err:
        print(f"  {f}: {result} (err: {err[:100]})")
    else:
        print(f"  {f}: {result} ({len(raw)}B)")
    time.sleep(0.2)

# Verify
print("\n=== Verify ===")
_, stdout, _ = ssh.exec_command(f"ls -la {dest}*.ko 2>&1")
print(stdout.read().decode().strip())

ssh.close()
print("Done")
