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

# Check nftables version and capabilities
out, err = run("nft --version 2>&1")
print("nft version:", out)

# Check if nft_queue is built into kernel
out, err = run("grep NFT_QUEUE /boot/config-* 2>/dev/null; grep NFT_QUEUE /proc/config.gz 2>/dev/null || zcat /proc/config.gz 2>/dev/null | grep NFT_QUEUE")
print("\nkernel NFT_QUEUE:", out[:200])

# Check what nft actions are available
out, err = run("nft list ruleset 2>&1 | head -5")
print("\nruleset head:", out[:200])

# Try simpler nft queue syntax
out, err = run("nft add rule inet fw4 forward tcp dport 443 queue 2>&1")
print("\nnft queue simple:", out[:200])

out, err = run("nft add rule ip fw4 forward tcp dport 443 queue num 300 2>&1")
print("\nnft ip queue:", out[:200])

# Check ip family
out, err = run("nft list tables 2>&1")
print("\ntables:", out[:200])
out, err = run("nft list table inet fw4 2>&1 | head -30")
print("\ninet fw4:", out[:500])

# Check iptables-legacy xtables match
out, err = run("ls /lib/modules/*/xt_* 2>&1")
print("\nxt modules:", out[:300])

ssh.close()
