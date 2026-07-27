import paramiko, warnings
warnings.filterwarnings("ignore")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("192.168.1.1", port=22, username="root", password="!LoL-eSports",
            look_for_keys=False, allow_agent=False, timeout=15)

def run(cmd):
    _, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    return out, err

# Check all modules
out, err = run("lsmod 2>&1")
print("=== lsmod ===")
print(out[:500])

# Check nft_queue module availability
out, err = run("find /lib/modules -name 'nft_queue*' 2>/dev/null; find /lib/modules -name 'xt_NFQUEUE*' 2>/dev/null")
print("\n=== Queue modules ===")
print(out[:200])

# Install iptables-legacy CONCRETELY
out, err = run("apk info iptables-zz-legacy 2>&1")
print("\n=== iptables-zz-legacy info ===")
print(out[:300])

# List files in iptables-zz-legacy
out, err = run("apk manifest iptables-zz-legacy 2>&1 | head -30")
print("\n=== iptables-zz-legacy files ===")
print(out[:500])

# Check xtables-legacy
out, err = run("apk manifest xtables-legacy 2>&1 | head -20")
print("\n=== xtables-legacy files ===")
print(out[:300])

# Actually check what is installed
out, err = run("apk list-installed 2>&1 | grep -E 'iptables|xtables|nfqueue'")
print("\n=== Installed packages ===")
print(out[:500])

ssh.close()
