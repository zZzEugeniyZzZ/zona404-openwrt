# OpenWrt для Netcraze NC-1812 / Keenetic KN-1812

Роутер на MediaTek MT7988D (Filogic 860), 1024MB DDR4, 256MB SPI NAND (Fudan FM25G02B).

**Статус:** OpenWrt main (25.12+) уже включает полную поддержку:
- DTS: `target/linux/mediatek/dts/mt7988d-netcraze-nc-1812.dts`
- Профиль: `filogic.mk` → `netcraze_nc-1812`
- NAND: PR #23864 слит

## Сборка через GitHub Actions

1. Нажать **Actions** → **Build OpenWrt for Netcraze NC-1812** → **Run workflow**
2. Через ~2 часа скачать артефакты
3. Прошить `*factory.bin` через веб-интерфейс стоковой прошивки

## Локальная сборка (Linux/WSL)

```bash
bash build.sh
```

## Файлы

| Файл | Описание |
|---|---|
| `.github/workflows/build-openwrt.yml` | GitHub Actions workflow |
| `build.sh` | Скрипт сборки для Linux/WSL |
| `build_openwrt.ps1` | Скрипт сборки для Windows |
| `nc1812_info.txt` | Полный дамп заводской системы |
| `collect_info.py` | Сбор данных с роутера по SSH |
