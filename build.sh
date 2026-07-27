#!/bin/bash
set -e

# ===== OpenWrt build script for Netcraze NC-1812 =====
# Usage: bash build.sh
# Runs inside WSL Ubuntu

NC=$(nproc)
BUILD_DIR="$(cd "$(dirname "$0")" && pwd)"
OPENWRT_DIR="$BUILD_DIR/openwrt"

echo "=== OpenWrt build for Netcraze NC-1812 ==="
echo "Build dir: $BUILD_DIR"
echo "Cores: $NC"

# Install deps
if ! dpkg -l | grep -q build-essential; then
    echo "=== Installing dependencies ==="
    sudo apt update
    sudo apt install -y build-essential clang flex bison g++ gawk \
        gcc-multilib g++-multilib gettext git libncurses-dev libssl-dev \
        python3 python3-distutils python3-setuptools rsync unzip zlib1g-dev \
        file wget curl xz-utils device-tree-compiler
fi

# Clone
if [ ! -d "$OPENWRT_DIR" ]; then
    echo "=== Cloning OpenWrt main ==="
    git clone https://git.openwrt.org/openwrt/openwrt.git --depth=1 "$OPENWRT_DIR"
fi

cd "$OPENWRT_DIR"

# Apply FM25G01B/FM25G02B Quad I/O read dummy fix (PR #24007)
# This patch is NOT yet merged in main as of Jul 2026
echo "=== Applying FM25G01B/FM25G02B Quad I/O read dummy fix (PR #24007) ==="
KERNEL_DIR=$(find target/linux/generic -maxdepth 1 -type d -name 'pending-*' 2>/dev/null | head -1)
if [ -z "$KERNEL_DIR" ]; then
    echo "ERROR: No kernel pending directory found!"
    exit 1
fi
echo "Using kernel directory: $KERNEL_DIR"
cp "$BUILD_DIR/patches/403-mtd-spinand-fmsh-fix-FM25G01B-FM25G02B-quad-io-read-dummy.patch" \
   "$KERNEL_DIR/"

echo "=== Updating feeds ==="
./scripts/feeds update -a
./scripts/feeds install -a

echo "=== Configuring for NC-1812 ==="
cat > .config << 'EOF'
CONFIG_TARGET_mediatek=y
CONFIG_TARGET_mediatek_filogic=y
CONFIG_TARGET_mediatek_filogic_DEVICE_netcraze_nc-1812=y
CONFIG_TARGET_ALL_PROFILES=n
CONFIG_TARGET_MULTI_PROFILE=n
CONFIG_TARGET_PER_DEVICE_ROOTFS=y
CONFIG_LUCI=y
CONFIG_PACKAGE_luci-mod-status=y
CONFIG_PACKAGE_luci-mod-system=y
CONFIG_PACKAGE_luci-mod-network=y
CONFIG_PACKAGE_luci-app-statistics=y
CONFIG_PACKAGE_luci-i18n-base-ru=y
CONFIG_BTRFS_PROGS_ZSTD=y
CONFIG_ZSTD_OPTIMIZE_O3=y
CONFIG_OPENSSL_WITH_CHACHA20=y
CONFIG_OPENSSL_WITH_POLY1305=y
CONFIG_PACKAGE_kmod-ipt-nfqueue=y
CONFIG_PACKAGE_kmod-nfnetlink-queue=y
CONFIG_PACKAGE_kmod-nft-compat=y
CONFIG_PACKAGE_kmod-ipt-core=y
CONFIG_PACKAGE_kmod-ip6tables=y
CONFIG_PACKAGE_kmod-ipt-conntrack-extra=y
CONFIG_PACKAGE_kmod-ipt-extra=y
CONFIG_PACKAGE_kmod-ipt-filter=y
CONFIG_PACKAGE_kmod-ipt-ipopt=y
CONFIG_PACKAGE_kmod-ipt-nat6=y
CONFIG_PACKAGE_kmod-ip6tables-extra=y
EOF
make defconfig

echo "=== Downloading sources ==="
make download -j$NC

echo "=== Building (this will take 1-3 hours) ==="
make -j$NC V=s 2>&1 | tee "$BUILD_DIR/build.log"

echo "=== DONE ==="
ls -la bin/targets/mediatek/filogic/
