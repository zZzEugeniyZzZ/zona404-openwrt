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

# Find iptables
out, err = run("find / -name 'iptables' -type f 2>/dev/null; find / -name 'iptables-nft' -type f 2>/dev/null; find / -name 'iptables-legacy' -type f 2>/dev/null")
print("=== iptables locations ===")
print(out[:300])

# Check nft rules
out, err = run("nft list ruleset 2>&1")
print("\n=== Full nft ruleset ===")
print(out[:1000])

# Check service running properly
out, err = run("ps 2>&1 | grep nfqws")
print("\n=== nfqws2 processes ===")
print(out[:300])

# Check if nfq queue handling
out, err = run("cat /proc/net/netfilter/nfnetlink_queue 2>&1")
print("\n=== nfqueue status ===")
print(out[:200])

# Test with a simple rule
print("\n=== Testing nft rule ===")
out, err = run("nft add chain inet fw4 nfqws_test '{ }' 2>&1; echo EXIT:$?")
print(out[:200])

out, err = run("nft add rule inet fw4 forward tcp dport 443 queue num 300 2>&1; echo EXIT:$?")
print(out[:200])

ssh.close()
