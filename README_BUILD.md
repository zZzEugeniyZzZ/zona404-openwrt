# OpenWrt for Netcraze NC-1812 / Keenetic KN-1812

> **Статус:** Полная поддержка уже есть в OpenWrt main (25.12+)

## OpenWrt референсы

| Компонент | Файл |
|---|---|
| Device Tree (NC-1812) | `target/linux/mediatek/dts/mt7988d-netcraze-nc-1812.dts` |
| Device Tree (KN-1812 shared) | `target/linux/mediatek/dts/mt7988d-keenetic-kn-1812.dtsi` |
| Build profile | `target/linux/mediatek/image/filogic.mk` → `netcraze_nc-1812` |
| BL2 | `mt7988-bl2 spim-nand-ubi-ddr4` |
| FIP | generic mt7988 BL31 + U-Boot |

## Прошивка: сток → OpenWrt

1. Собрать образ (`netcraze_nc-1812-factory.bin`)
2. Войти в веб-интерфейс стоковой прошивки
3. Загрузить `factory.bin` через раздел обновления ПО
4. После перезагрузки — SSH на 192.168.1.1

## Файлы в этой папке

- `build_openwrt.ps1` - установка WSL + сборка (Windows)
- `build.sh` - сборка (Linux/WSL)
- `nc1812_info.txt` - полный дамп заводской системы
- `collect_info.py` - скрипт сбора данных

## Сборка

### Способ 1: WSL (Windows, администратор)

```powershell
# Открыть PowerShell от Администратора
.\build_openwrt.ps1 -SetupWSL
# Перезагрузить Windows
.\build_openwrt.ps1 -Build
```

### Способ 2: Linux/WSL (пользователь)

```bash
bash build.sh
```

Готовые образы появятся в `openwrt/bin/targets/mediatek/filogic/`:
- `openwrt-mediatek-filogic-netcraze_nc-1812-sysupgrade.bin` — для обновления из OpenWrt
- `openwrt-mediatek-filogic-netcraze_nc-1812-factory.bin` — первичная прошивка
