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

out, err = run("apk info -L nfqws2-keenetic 2>&1")
print("=== Package files ===")
print(out[:1000])

out, err = run("find / -name 'nfqws*' -o -name 'tpws*' 2>/dev/null")
print("\n=== Find nfqws/tpws binaries ===")
print(out[:500])

out, err = run("find /usr/sbin /usr/bin /sbin /bin -name '*nfq*' -o -name '*tpws*' 2>/dev/null; which zapret 2>&1; which nfqws 2>&1")
print("\n=== Binaries ===")
print(out[:500])

# Check if it installed somewhere else
out, err = run("find /opt /rom /overlay -name 'nfqws*' 2>/dev/null")
print("\n=== Other paths ===")
print(out[:500])

ssh.close()
