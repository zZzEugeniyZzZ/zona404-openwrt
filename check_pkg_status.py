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

# Check all installed packages
out, err = run("apk list-installed 2>&1 | head -30")
print("=== All installed (first 30) ===")
print(out[:1000])

# Check specifically nfqws2-keenetic
out, err = run("apk info -e nfqws2-keenetic 2>&1; echo EXIT:$?")
print("\n=== Is it installed? ===")
print(out[:200])

# Check repo contents (apk index)
out, err = run("apk list 2>&1 | grep nfqws")
print("\n=== In repo ===")
print(out[:500])

# Download and check the actual package file
out, err = run("wget -q -O /tmp/nfqws_check.txt https://nfqws.github.io/nfqws2-keenetic/openwrt/Packages 2>&1; head -50 /tmp/nfqws_check.txt 2>&1")
print("\n=== Package index ===")
print(out[:500])

# Check if there's a sub-package
out, err = run("apk list 2>&1 | grep -iE 'nfqws|zapret'")
print("\n=== All nfqws/zapret ===")
print(out[:500])

ssh.close()
