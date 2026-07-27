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

# Extract to root
print("=== Extract to root ===")
out, err = run("cd / && gzip -dc /tmp/nfqws2_extract/data.tar.gz | tar xf - 2>&1; echo EXIT:$?")
print(out[:200])

# Check files
out, err = run("ls -la /etc/nfqws2/ 2>&1; ls -la /etc/init.d/nfqws2* 2>&1")
print("\n=== Config ===")
print(out[:500])

# Find binary (might be from iptables package)
out, err = run("which nfqws 2>&1; find /usr/sbin /usr/bin -name 'nfqws' 2>/dev/null")
print("\n=== Binary ===")
print(out[:200])

# Check iptables packages
out, err = run("apk list-installed 2>&1 | grep -iE 'iptable|xtable|xt_nfq'")
print("\n=== iptables packages ===")
print(out[:500])

# Check if xt_NFQUEUE is still loaded
out, err = run("lsmod 2>&1 | grep -E 'x_table|nfqueue|nfnetlink'")
print("\n=== Modules ===")
print(out[:200])

ssh.close()
