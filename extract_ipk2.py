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

# Extract with gunzip + tar pipe
print("=== Extract data.tar.gz ===")
out, err = run("cd /tmp/nfqws2_extract && gunzip -c data.tar.gz | tar xf - 2>&1; find . -type f -not -name '*.tar.gz' -not -name 'debian-binary' 2>/dev/null | head -30")
print(out[:1000])

# List files
out, err = run("find /tmp/nfqws2_extract -type f -not -name '*.tar.gz' -not -name 'debian-binary' 2>/dev/null")
print("\n=== All files ===")
print(out[:800])

# Check for nfqws binary
out, err = run("find /tmp/nfqws2_extract -name 'nfqws' -o -name 'S51*' -o -name '*.sh' 2>/dev/null")
print("\n=== Binaries ===")
print(out[:500])

ssh.close()
