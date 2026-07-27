param(
    [switch]$SetupWSL,
    [switch]$Build
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "`n=== $Message ===" -ForegroundColor Green
}

function Check-Admin {
    $id = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    $p = New-Object System.Security.Principal.WindowsPrincipal($id)
    return $p.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)
}

if ($SetupWSL) {
    if (-not (Check-Admin)) {
        Write-Host "ERROR: Setup WSL requires Administrator. Run as Admin!" -ForegroundColor Red
        exit 1
    }
    Write-Step "Installing WSL with Ubuntu"
    wsl --install -d Ubuntu
    if ($?) {
        Write-Host "WSL installed. Reboot and run: .\build_openwrt.ps1 -Build" -ForegroundColor Yellow
    }
    exit
}

if (-not (Get-Command wsl -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: WSL not found. Run as Admin: .\build_openwrt.ps1 -SetupWSL" -ForegroundColor Red
    exit 1
}

Write-Step "Checking WSL distros"
$distros = wsl -l -q
if ($distros -notmatch "Ubuntu") {
    Write-Host "ERROR: Ubuntu not installed. Run as Admin: .\build_openwrt.ps1 -SetupWSL" -ForegroundColor Red
    exit 1
}

if ($Build) {
    $buildDir = Resolve-Path "."
    Write-Step "Starting OpenWrt build for Netcraze NC-1812"
    Write-Host "Build dir: $buildDir"

    $wslScript = @'
set -e
echo "=== Updating packages ==="
sudo apt update && sudo apt install -y build-essential clang flex bison g++ gawk \
    gcc-multilib g++-multilib gettext git libncurses-dev libssl-dev \
    python3 python3-distutils python3-setuptools rsync unzip zlib1g-dev \
    file wget curl xz-utils device-tree-compiler

echo "=== Cloning OpenWrt main ==="
cd /mnt/e/AI/Projects/Zona404
[ -d openwrt ] || git clone https://git.openwrt.org/openwrt/openwrt.git --depth=1
cd openwrt

echo "=== Updating feeds ==="
./scripts/feeds update -a
./scripts/feeds install -a

echo "=== Configuring ==="
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
make download -j$(nproc)

echo "=== Building (this will take a long time!) ==="
make -j$(nproc) V=s 2>&1 | tee build.log

echo "=== Done! ==="
ls -la bin/targets/mediatek/filogic/
'@

    $tmpScript = [System.IO.Path]::GetTempFileName() + ".sh"
    Set-Content -Path $tmpScript -Value $wslScript -Encoding UTF8
    wsl -d Ubuntu -u root bash -c "bash /mnt/c/Users/$env:USERNAME/AppData/Local/Temp/$(Split-Path $tmpScript -Leaf)"
    Remove-Item $tmpScript
}
