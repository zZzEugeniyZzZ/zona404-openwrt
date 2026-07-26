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
PATCH_FILE="target/linux/generic/pending-6.18/403-mtd-spinand-fmsh-fix-FM25G01B-FM25G02B-quad-io-read-dummy.patch"
if [ ! -f "$PATCH_FILE" ]; then
    echo "=== Applying FM25G01B/FM25G02B Quad I/O read dummy fix (PR #24007) ==="
    mkdir -p "$(dirname "$PATCH_FILE")"
    cat > "$PATCH_FILE" << 'PATCH'
--- a/drivers/mtd/nand/spi/fmsh.c
+++ b/drivers/mtd/nand/spi/fmsh.c
@@ -44,6 +44,14 @@ static SPINAND_OP_VARIANTS(update_cache_
 		SPINAND_PROG_LOAD_1S_1S_4S_OP(false, 0, NULL, 0),
 		SPINAND_PROG_LOAD_1S_1S_1S_OP(false, 0, NULL, 0));
 
+static SPINAND_OP_VARIANTS(fm25g_read_cache_variants,
+		SPINAND_PAGE_READ_FROM_CACHE_1S_4S_4S_OP(0, 1, NULL, 0, 0),
+		SPINAND_PAGE_READ_FROM_CACHE_1S_1S_4S_OP(0, 1, NULL, 0, 0),
+		SPINAND_PAGE_READ_FROM_CACHE_1S_2S_2S_OP(0, 1, NULL, 0, 0),
+		SPINAND_PAGE_READ_FROM_CACHE_1S_1S_2S_OP(0, 1, NULL, 0, 0),
+		SPINAND_PAGE_READ_FROM_CACHE_FAST_1S_1S_1S_OP(0, 1, NULL, 0, 0),
+		SPINAND_PAGE_READ_FROM_CACHE_1S_1S_1S_OP(0, 1, NULL, 0, 0));
+
 static int fm25g01b_ooblayout_ecc(struct mtd_info *mtd, int section,
 				  struct mtd_oob_region *region)
 {
@@ -192,7 +200,7 @@ static const struct spinand_info fmsh_sp
 		     SPINAND_ID(SPINAND_READID_METHOD_OPCODE_DUMMY, 0xd1),
 		     NAND_MEMORG(1, 2048, 128, 64, 1024, 21, 1, 1, 1),
 		     NAND_ECCREQ(8, 528),
-		     SPINAND_INFO_OP_VARIANTS(&read_cache_variants,
+		     SPINAND_INFO_OP_VARIANTS(&fm25g_read_cache_variants,
 					      &write_cache_variants,
 					      &update_cache_variants),
 		     SPINAND_HAS_QE_BIT,
@@ -202,7 +210,7 @@ static const struct spinand_info fmsh_sp
 		     SPINAND_ID(SPINAND_READID_METHOD_OPCODE_DUMMY, 0xd2),
 		     NAND_MEMORG(1, 2048, 128, 64, 2048, 41, 1, 1, 1),
 		     NAND_ECCREQ(8, 528),
-		     SPINAND_INFO_OP_VARIANTS(&read_cache_variants,
+		     SPINAND_INFO_OP_VARIANTS(&fm25g_read_cache_variants,
 					      &write_cache_variants,
 					      &update_cache_variants),
 		     SPINAND_HAS_QE_BIT,
PATCH
    echo "Patch applied."
fi

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
EOF
make defconfig

echo "=== Downloading sources ==="
make download -j$NC

echo "=== Building (this will take 1-3 hours) ==="
make -j$NC V=s 2>&1 | tee "$BUILD_DIR/build.log"

echo "=== DONE ==="
ls -la bin/targets/mediatek/filogic/
