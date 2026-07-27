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

# Check nft_compat and all modules
out, err = run("lsmod 2>&1")
print("=== lsmod ===")
print(out)

# Check if nft_compat is available
out, err = run("find /lib/modules -name 'nft_compat*' 2>/dev/null")
print("\n=== nft_compat ===")
print(out[:200])

# Try to use xt_NFQUEUE via nft (with nft_compat)
out, err = run("nft add rule inet fw4 forward tcp dport 443 counter queue num 300 2>&1")
print("\n=== nft with queue ===")
print(out[:200])

# Try using 'jump' or 'goto' with NFQUEUE target via nft_compat
out, err = run("nft add rule inet fw4 forward tcp dport 443 counter 2>&1")
print("\n=== simple counter ===")
print(out[:200])

# Check nftables match/target list
out, err = run("nft list matches 2>&1 | head -20")
print("\n=== nft matches ===")
print(out[:400])

ssh.close()
