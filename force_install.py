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

# Check if repo exists and add it
out, err = run("mkdir -p /etc/apk 2>&1")
print("mkdir:", out[:100])

# Add nfqws2 repo
out, err = run('echo "https://nfqws.github.io/nfqws2-keenetic/openwrt/packages.adb" > /etc/apk/repositories 2>&1; echo OK')
print("add repo:", out[:100])

# Update
out, err = run("apk update 2>&1; echo EXIT:$?")
print("apk update:", out[:500])

# Try force install
print("\n=== Force install nfqws2-keenetic ===")
out, err = run("apk add --no-deps nfqws2-keenetic 2>&1; echo EXIT:$?")
print(out[:500])

# Try with --force
print("\n=== Try with --force ===")
out, err = run("apk add --force nfqws2-keenetic 2>&1; echo EXIT:$?")
print(out[:500])

# Check apk help for force options
out, err = run("apk add --help 2>&1 | grep -i force")
print("force options:", out[:500])

ssh.close()
