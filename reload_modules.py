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

# Reload our modules
print("=== Reload modules ===")
out, err = run("ls /lib/modules/6.18.39/nfnetlink* /lib/modules/6.18.39/x_tables* /lib/modules/6.18.39/xt_NFQUEUE* 2>&1")
print(out[:300])

out, err = run("insmod /lib/modules/6.18.39/nfnetlink.ko 2>&1")
print("nfnetlink:", out[:100], err[:100])
out, err = run("insmod /lib/modules/6.18.39/nfnetlink_queue.ko 2>&1")
print("nfnetlink_queue:", out[:100], err[:100])
out, err = run("insmod /lib/modules/6.18.39/x_tables.ko 2>&1")
print("x_tables:", out[:100], err[:100])
out, err = run("insmod /lib/modules/6.18.39/xt_NFQUEUE.ko 2>&1")
print("xt_NFQUEUE:", out[:100], err[:100])

out, err = run("lsmod 2>&1 | grep -E 'nfnetlink|x_table|nfqueue'")
print("\n=== After insmod ===")
print(out[:200])

# Try nft queue rule again
out, err = run("nft add rule inet fw4 forward tcp dport 443 queue num 300 2>&1; echo EXIT:$?")
print("\n=== nft queue after reload ===")
print(out[:300])

# Check available nft queue modules
out, err = run("ls /lib/modules/6.18.39/nft_queue* 2>&1")
print("\n=== nft_queue module ===")
print(out[:100])

# Check our CI build for nft_queue module
out, err = run("find / -name 'nft_queue*' 2>/dev/null")
print("\n=== any nft_queue ===")
print(out[:100])

# Check nfqws2 config for listening mode
out, err = run("cat /etc/nfqws2/nfqws2.conf")
print("\n=== Full config ===")
print(out[:1000])

ssh.close()
