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

# Check all nfqws packages in repo
out, err = run("apk search nfqws 2>&1")
print("=== nfqws packages ===")
print(out[:500])

# Check what packages were installed with nfqws2
out, err = run("apk list-installed 2>&1 | grep -i nfqws")
print("\n=== Installed nfqws ===")
print(out[:500])

# Check files of the nfqws2-keenetic package again
out, err = run("apk manifest nfqws2-keenetic 2>&1")
print("\n=== Manifest ===")
print(out[:500])

# Check if there's a different package name
out, err = run("apk list 2>&1 | grep -i nfqws2")
print("\n=== All nfqws2 packages ===")
print(out[:500])

# Check the init script
out, err = run("ls -la /etc/init.d/ 2>&1 | grep -i nfqws")
print("\n=== Init scripts ===")
print(out[:200])

# Find binary
out, err = run("find /usr /opt /etc -name 'nfqws*' -not -path '*apk*' 2>/dev/null")
print("\n=== nfqws files ===")
print(out[:500])

ssh.close()
