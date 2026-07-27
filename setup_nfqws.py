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

# Copy the aarch64 binary to /usr/bin
print("=== Install binary ===")
out, err = run("cp /tmp/nfqws2_extract/tmp/nfqws2_binary/nfqws2-aarch64 /usr/bin/nfqws2 && chmod +x /usr/bin/nfqws2 && echo OK || echo FAIL")
print(out[:100])

# Verify
out, err = run("ls -la /usr/bin/nfqws2 2>&1; /usr/bin/nfqws2 --version 2>&1")
print("\n=== Binary check ===")
print(out[:300])

# Enable and start service
out, err = run("/etc/init.d/nfqws2-keenetic enable 2>&1; echo ENABLE:$?")
print("\n=== Service ===")
print(out[:200])

out, err = run("/etc/init.d/nfqws2-keenetic start 2>&1; echo START:$?")
print(out[:200])

# Check status
out, err = run("/etc/init.d/nfqws2-keenetic status 2>&1")
print("\n=== Status ===")
print(out[:300])

# Check iptables rules
out, err = run("iptables-save 2>&1 | grep -i nfqws | head -10")
print("\n=== iptables rules ===")
print(out[:500])

# Check logs
out, err = run("logread 2>&1 | grep -i nfqws | tail -10")
print("\n=== Logs ===")
print(out[:500])

ssh.close()
