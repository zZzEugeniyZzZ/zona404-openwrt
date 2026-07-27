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

# List all files in data.tar.gz
print("=== ALL files in package ===")
out, err = run("cd /tmp/nfqws2_extract && tar tzf data.tar.gz 2>&1 | grep -v '/$'")
print(out[:1500])

# Check control file for any hints
print("\n=== Control files ===")
out, err = run("cd /tmp/nfqws2_extract && gunzip -c control.tar.gz | tar xf - -O ./control 2>/dev/null; echo ---; gunzip -c control.tar.gz | tar xf - -O ./postinst 2>/dev/null")
print(out[:500])

# Check the init script for binary path
print("\n=== Init script ===")
out, err = run("head -30 /etc/init.d/nfqws2-keenetic 2>&1")
print(out[:500])

# Check config for binary path
print("\n=== Config ===")
out, err = run("grep -E 'NFQWS|PROG|BIN|binary' /etc/nfqws2/nfqws2.conf 2>&1 | head -10")
print(out[:300])

ssh.close()
