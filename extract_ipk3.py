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

# Check file type
out, err = run("head -c 20 /tmp/nfqws2_extract/data.tar.gz | xxd 2>&1")
print("=== data.tar.gz magic ===")
print(out[:100])

# Try different decompression methods
out, err = run("cd /tmp/nfqws2_extract && zcat data.tar.gz 2>/dev/null | tar tf - 2>/dev/null | head -20; echo ---; gzip -dc data.tar.gz 2>/dev/null | tar tf - 2>/dev/null | head -20; echo ---; tar tzf data.tar.gz 2>&1 | head -20")
print("\n=== Extract attempts ===")
print(out[:600])

# Try on the original ipk
out, err = run("cd /tmp/nfqws2_extract && tar xzf data.tar.gz 2>&1; find . -type f -not -name '*.tar.gz' -not -name 'debian-binary' 2>/dev/null")
print("\n=== tar xzf ===")
print(out[:500])

# Maybe data.tar.gz is actually data.tar.zst
out, err = run("which zstd 2>&1; which unzstd 2>&1")
print("\n=== zstd check ===")
print(out[:100])

ssh.close()
