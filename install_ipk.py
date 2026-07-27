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

# Download the .ipk directly
print("=== Downloading nfqws2-keenetic.ipk ===")
out, err = run("cd /tmp && wget -q 'https://nfqws.github.io/nfqws2-keenetic/openwrt/nfqws2-keenetic_1.2.4_all.ipk' -O nfqws2.ipk 2>&1; ls -la nfqws2.ipk 2>&1")
print(out[:200])

# Force install it
print("\n=== Force install .ipk ===")
out, err = run("apk add --force-broken-world --allow-untrusted /tmp/nfqws2.ipk 2>&1; echo EXIT:$?")
print(out[:500])

# Check if installed now
out, err = run("apk info -e nfqws2-keenetic 2>&1; echo EXIT:$?")
print("\n=== Installed check ===")
print(out[:200])

# Find files
out, err = run("find / -name 'nfqws*' -not -path '*apk*' 2>/dev/null")
print("\n=== Files ===")
print(out[:500])

# Check binary
out, err = run("which nfqws 2>&1; nfqws --version 2>&1")
print("\n=== Binary ===")
print(out[:300])

# Check config
out, err = run("ls -la /etc/nfqws*/ 2>&1; cat /etc/nfqws*/nfqws*.conf 2>&1 | head -30")
print("\n=== Config ===")
print(out[:500])

ssh.close()
