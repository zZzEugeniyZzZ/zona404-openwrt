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

# Install iptables packages
print("=== Install iptables ===")
out, err = run("apk add --force-broken-world iptables iptables-legacy iptables-nft 2>&1; echo EXIT:$?")
print(out[:400])

out, err = run("which iptables 2>&1; iptables --version 2>&1")
print("\n=== iptables check ===")
print(out[:200])

# Restart the service
print("\n=== Restart nfqws2 ===")
out, err = run("/etc/init.d/nfqws2-keenetic stop 2>&1; sleep 1; /etc/init.d/nfqws2-keenetic start 2>&1; echo EXIT:$?")
print(out[:500])

out, err = run("/etc/init.d/nfqws2-keenetic status 2>&1")
print("\n=== Status ===")
print(out[:200])

out, err = run("iptables-save 2>&1 | grep -i nfqws | head -15")
print("\n=== iptables rules ===")
print(out[:500])

out, err = run("nft list ruleset 2>&1 | grep -i nfqws | head -15")
print("\n=== nftables rules ===")
print(out[:300])

# Check logs
out, err = run("logread 2>&1 | grep -i nfqws | tail -10")
print("\n=== Logs ===")
print(out[:500])

ssh.close()
