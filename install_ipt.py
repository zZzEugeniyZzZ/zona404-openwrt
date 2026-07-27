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

# Check what iptables packages are available
out, err = run("apk list 2>&1 | grep iptables")
print("=== iptables packages ===")
print(out[:800])

# Install iptables-legacy specifically
print("\n=== Install iptables-legacy ===")
out, err = run("apk add --force-broken-world iptables-legacy 2>&1; echo EXIT:$?")
print(out[:400])

out, err = run("apk add --force-broken-world iptables-nft 2>&1; echo EXIT:$?")
print(out[:400])

out, err = run("apk add --force-broken-world iptables-zz-legacy 2>&1; echo EXIT:$?")
print(out[:400])

out, err = run("find /usr/sbin /usr/bin /sbin /bin -name 'iptables*' -type f 2>/dev/null")
print("\n=== iptables binaries ===")
print(out[:300])

# Check the actual binary name
out, err = run("ls /usr/libexec/ 2>/dev/null; ls /usr/lib/iptables/ 2>/dev/null")
print("\n=== iptables libexec ===")
print(out[:200])

# Try installing xtables
out, err = run("apk add --force-broken-world xtables-legacy 2>&1; echo EXIT:$?")
print("\n=== xtables ===")
print(out[:300])

# Check what provides iptables binary
out, err = run("apk search --exact iptables 2>&1 | head -5")
print("\n=== exact iptables ===")
print(out[:200])

# Manually add the nft rule
print("\n=== Manual nft rule ===")
out, err = run("nft add rule inet fw4 forward tcp dport 443 queue num 300 2>&1; echo EXIT:$?")
print(out[:200])

# Check nfqueue module
out, err = run("lsmod 2>&1 | grep nfqueue; modinfo nf_queue 2>&1 | head -3")
print("\n=== nfqueue modules ===")
print(out[:200])

ssh.close()
