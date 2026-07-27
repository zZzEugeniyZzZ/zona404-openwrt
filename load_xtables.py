import paramiko, warnings, os, time
warnings.filterwarnings("ignore")

ko_dir = os.path.join(os.environ["TEMP"], "opencode", "kmods2", "kmods")
dest = "/lib/modules/6.18.39/"
files = ["x_tables.ko"]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.1.1", port=22, username="root", password="!LoL-eSports",
            look_for_keys=False, allow_agent=False, timeout=15)

for f in files:
    local = os.path.join(ko_dir, f)
    remote = os.path.join(dest, f)
    with open(local, "rb") as fh:
        data = fh.read()
    transport = ssh.get_transport()
    chan = transport.open_session()
    chan.exec_command(f"dd bs=1024 of={remote} 2>/dev/null")
    for i in range(0, len(data), 1024):
        chunk = data[i:i+1024]
        chan.send(chunk)
        time.sleep(0.01)
    chan.shutdown_write()
    time.sleep(0.5)
    chan.close()
    print(f"  {f}: {len(data)}B uploaded")

# Now try loading in order
def run(cmd):
    _, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    return out, err

print("\n=== Loading modules ===")
cmds = [
    "insmod /lib/modules/6.18.39/x_tables.ko 2>&1; echo EXIT:$?",
    "insmod /lib/modules/6.18.39/xt_NFQUEUE.ko 2>&1; echo EXIT:$?",
    "lsmod | grep -E 'x_table|nfnetlink|NFQUEUE|nfqueue'",
]
for cmd in cmds:
    out, err = run(cmd)
    print(f"$ {cmd}")
    print(f"  {out[:200]}")

# Check nfqws repo
out, err = run("apk list 2>&1 | grep nfqws")
print("\nnfqws in repo:", out[:200] or "not found")

# Add repo if needed
out, err = run("cat /etc/apk/repositories 2>&1 | grep nfqws")
print("nfqws repo:", out[:200] or "not configured")

ssh.close()
