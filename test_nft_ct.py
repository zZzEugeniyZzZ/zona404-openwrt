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

# Test ct expressions in nft
tests = [
    "nft add rule inet fw4 forward ct original packets 1-15 queue num 300 2>&1",
    "nft add rule inet fw4 forward ct original packets 1-15 log 2>&1",
    "nft add rule inet fw4 forward ct original packets 1 2>&1",
    "nft describe ct original 2>&1",
    "nft add rule inet fw4 forward ct state new,established tcp dport 443 log 2>&1",
    "nft add rule inet fw4 forward ct state new tcp dport 443 log 2>&1",
    "nft add rule inet fw4 forward tcp dport 443 log prefix test 2>&1",
    # Test if xt_connbytes works via nft
    "nft add rule inet fw4 forward meta mark 0 tcp dport 443 log 2>&1",
]

for cmd in tests:
    out, err = run(cmd)
    print(f"$ {cmd}")
    if out: print(f"out: {out[:100]}")
    if err: print(f"err: {err[:100]}")
    print()

ssh.close()
