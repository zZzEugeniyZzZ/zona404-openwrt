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

# Check if x_tables is built-in
out, err = run("cat /lib/modules/6.18.39/modules.builtin 2>&1 | grep -i x_tables")
print("x_tables builtin:", out[:200])

# List all modules.builtin
out, err = run("cat /lib/modules/6.18.39/modules.builtin 2>&1")
builtins = out.split("\n")
for m in builtins:
    if "table" in m or "nf" in m or "xt_" in m or "ip" in m:
        print("  builtin:", m)

# Check if x_tables.ko exists
out, err = run("ls /lib/modules/6.18.39/x_tables.ko 2>&1")
print("x_tables.ko:", out[:100])

# Check what modules.builtin says about nf and x_tables
out, err = run("grep -E '(table|nfnetlink|xt_)' /lib/modules/6.18.39/modules.builtin 2>&1")
print("builtin nf/xt:", out[:300])

# Also check modules.dep
out, err = run("ls /lib/modules/6.18.39/modules.dep 2>&1")
print("modules.dep exists:", out[:100])

# Try loading x_tables from the newly compiled module
out, err = run("find /lib/modules/6.18.39/ -name 'x_tables.ko' -o -name 'x_tables*' 2>&1")
print("find x_tables:", out[:100])

# Check if kernel has nfnetlink_queue builtin
out, err = run("cat /proc/net/netfilter/nfnetlink_queue 2>&1")
print("nfnetlink_queue proc:", out[:100])

ssh.close()
