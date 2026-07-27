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

# Extract ipk manually (ipk = tar.gz)
print("=== Extract ipk ===")
out, err = run("cd /tmp && mkdir -p nfqws2_extract && cd nfqws2_extract && tar xzf /tmp/nfqws2.ipk 2>&1; echo ---; ls -la 2>&1")
print(out[:300])

# Check contents
out, err = run("ls -la /tmp/nfqws2_extract/ 2>&1")
print("\n=== Root ===")
print(out[:200])

# Check for data.tar or control.tar
out, err = run("ls -la /tmp/nfqws2_extract/*.tar* /tmp/nfqws2_extract/*.gz 2>&1")
print("\n=== Tarballs ===")
print(out[:300])

# Extract data tarball
out, err = run("cd /tmp/nfqws2_extract && for f in *.tar*; do [ -f \"$f\" ] && tar xf \"$f\" 2>&1; done; echo ---; find . -type f 2>/dev/null | head -30")
print("\n=== Extracted files ===")
print(out[:800])

# Check for nfqws binary
out, err = run("find /tmp/nfqws2_extract -name 'nfqws*' -o -name 'S51*' 2>/dev/null")
print("\n=== nfqws files ===")
print(out[:300])

ssh.close()
