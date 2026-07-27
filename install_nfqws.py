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

# Check repos
out, err = run("cat /etc/apk/repositories 2>&1")
print("=== Repos ===")
print(out[:500])

# Install nfqws2-keenetic
print("\n=== Installing nfqws2-keenetic ===")
out, err = run("apk add nfqws2-keenetic 2>&1; echo EXIT:$?")
print(out[:500])

# Check installed files
print("\n=== Installed files ===")
out, err = run("apk info -L nfqws2-keenetic 2>&1")
print(out[:500])

# Check config
print("\n=== Config ===")
out, err = run("ls -la /etc/nfqws/ 2>&1; cat /etc/nfqws/config 2>&1")
print(out[:500])

ssh.close()
