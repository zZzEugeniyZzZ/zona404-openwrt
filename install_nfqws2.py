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

# Install with --force-broken-world (kmod deps already satisfied manually)
print("=== Installing nfqws2-keenetic ===")
out, err = run("apk add --force-broken-world nfqws2-keenetic 2>&1; echo EXIT:$?")
print(out[:800])

# Check what was installed
print("\n=== Installed ===")
out, err = run("apk info nfqws2-keenetic 2>&1")
print(out[:200])

out, err = run("which nfqws2 2>&1; nfqws2 --version 2>&1")
print("binary:", out[:200])

out, err = run("ls -la /etc/init.d/nfqws* 2>&1; ls -la /etc/nfqws* 2>&1")
print("config:", out[:200])

# Check default config
out, err = run("find /etc -name '*nfqws*' -type f 2>&1")
print("config files:", out[:500])

ssh.close()
