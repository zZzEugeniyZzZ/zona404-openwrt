# TFTP server for Netcraze NC-1812 recovery
# Serves OpenWrt factory.bin for bootloader TFTP recovery
import socket, os, struct, time

FW_FILE = r"E:\OpenWRT\openwrt-mediatek-filogic-netcraze_nc-1812-squashfs-factory.bin"
BACKUP_DIR = r"E:\AI\Projects\Zona 404\backup"

# Try to load factory.bin, fall back to backup firmware
fw_path = None
for path in [FW_FILE, os.path.join(BACKUP_DIR, "firmware_1.bin")]:
    if os.path.exists(path):
        fw_path = path
        break

if not fw_path:
    print("ERROR: no firmware file found!")
    exit(1)

fw_size = os.path.getsize(fw_path)
fw_name = os.path.basename(fw_path)
print(f"Serving: {fw_path}")
print(f"Size: {fw_size / 1024 / 1024:.1f} MB")

# Common filenames the bootloader might request
fw_aliases = {
    fw_name.lower(): fw_path,
    "firmware.bin": fw_path,
    "recovery.bin": fw_path,
    "openwrt.bin": fw_path,
    "factory.bin": fw_path,
    "openwrt-mediatek-filogic-netcraze_nc-1812-squashfs-factory.bin": fw_path,
    "nc1812_firmware.bin": fw_path,
    "firmware_1.bin": os.path.join(BACKUP_DIR, "firmware_1.bin"),
    "firmware_2.bin": os.path.join(BACKUP_DIR, "firmware_2.bin"),
}

# Read files into cache
fw_cache = {}
for name, path in fw_aliases.items():
    if os.path.exists(path) and name not in fw_cache:
        with open(path, "rb") as f:
            fw_cache[name] = f.read()
        print(f"Cached: {name} ({len(fw_cache[name]) / 1024 / 1024:.1f} MB)")

# TFTP Server
def tftp_server(host="0.0.0.0", port=69):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.settimeout(1)
    print(f"\nTFTP server on udp/{port}")
    print("Waiting for bootloader request ...")
    
    start = time.time()
    while time.time() - start < 300:  # 5 minute timeout
        try:
            data, addr = sock.recvfrom(1024)
            print(f"\nReceived from {addr[0]}:{addr[1]}: {data.hex()[:60]}")
            
            if len(data) < 2:
                continue
                
            opcode = struct.unpack("!H", data[:2])[0]
            
            if opcode == 1:  # RRQ (Read Request)
                # Parse filename
                null_pos = data.find(b'\x00', 2)
                filename = data[2:null_pos].decode('ascii', errors='ignore').lower()
                mode = data[null_pos+1:data.find(b'\x00', null_pos+1)].decode('ascii', errors='ignore')
                
                print(f"RRQ: file='{filename}' mode='{mode}' from {addr[0]}")
                
                # Find matching cached file
                payload = None
                served_name = None
                for alias, cached_name in fw_aliases.items():
                    if filename == alias.lower() or filename.endswith(alias):
                        if cached_name in fw_cache:
                            payload = fw_cache[cached_name]
                            served_name = cached_name
                            break
                
                if payload is None and filename in fw_cache:
                    payload = fw_cache[filename]
                    served_name = filename
                
                if payload is None:
                    # Try direct file access
                    for cached_name, cached_payload in fw_cache.items():
                        if cached_name in filename or filename in cached_name:
                            payload = cached_payload
                            served_name = cached_name
                            break
                
                if payload:
                    print(f"Sending: {served_name} ({len(payload)} bytes)")
                    _tftp_send(sock, addr[0], addr[1], payload)
                else:
                    print(f"File not found: {filename}")
                    # Send error
                    err_pkt = struct.pack("!HH", 5, 1) + b"File not found" + b'\x00'
                    sock.sendto(err_pkt, addr)
                    
        except socket.timeout:
            pass
        except Exception as e:
            print(f"Error: {e}")
    
    print("TFTP server timeout (5 min)")
    sock.close()

def _tftp_send(sock, host, port, data):
    block_size = 512
    blocks = (len(data) + block_size - 1) // block_size
    
    print(f"Sending {blocks} blocks ...")
    start = time.time()
    
    for block_num in range(blocks):
        offset = block_num * block_size
        chunk = data[offset:offset + block_size]
        
        # Send DATA packet
        data_pkt = struct.pack("!HH", 3, (block_num + 1) % 65536) + chunk
        
        # Wait for ACK (with retries)
        for attempt in range(5):
            sock.sendto(data_pkt, (host, port))
            try:
                ack, _ = sock.recvfrom(1024)
                if len(ack) >= 4:
                    ack_op = struct.unpack("!HH", ack[:4])[0]
                    ack_num = struct.unpack("!HH", ack[:4])[1]
                    if ack_op == 4 and ack_num == ((block_num + 1) % 65536):
                        break
            except socket.timeout:
                if attempt == 4:
                    print(f"  Block {block_num+1}/{blocks} failed (no ACK)")
                    return False
        
        if (block_num + 1) % 100 == 0:
            elapsed = time.time() - start
            speed = offset / 1024 / 1024 / elapsed if elapsed > 0 else 0
            print(f"  {block_num+1}/{blocks} blocks ({speed:.1f} MB/s)")
    
    elapsed = time.time() - start
    print(f"Done! {blocks} blocks in {elapsed:.1f}s ({len(data)/1024/1024/elapsed:.1f} MB/s)")
    return True

if __name__ == "__main__":
    tftp_server()
