# OpenWrt для Netcraze NC-1812 / Keenetic KN-1812

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

1. Скачать `netcraze_nc-1812-factory.bin` из GitHub Actions артефактов
2. Войти в веб-интерфейс стоковой прошивки (192.168.1.1)
3. Обновление ПО → выбрать `factory.bin` → прошить
4. После перезагрузки — SSH на 192.168.1.1 (OpenWrt)

## Откат (если что-то пошло не так)

### До прошивки — сделайте бэкап

```bash
python backup_stock.py
```
Это сохранит preloader (BL2), U-Boot, RF-EEPROM и оба заводских firmware в `backup/`.

### Вариант 1 — Dual-boot recovery (автоматический, без UART)

NC-1812 имеет **два слота** прошивки: Firmware_1 и Firmware_2. Stock bootloader при трёх неудачных загрузках переключается на второй слот.

Если OpenWrt не загружается:
1. **Выключить питание**
2. **Зажать Reset** (на корпусе, за ушком)
3. **Включить питание**, держать Reset 10-15 секунд
4. Отпустить — роутер загрузится со второго слота (стоковая прошивка)

Если оба слота прошиты OpenWrt — этот вариант не поможет (нужен UART).

### Вариант 2 — Восстановление через UART (нужен адаптер USB-UART)

Пины на плате: GND, TX, RX (3.3V). Консоль: 115200 8n1.

В бутлоадере (нажать любую клавишу при загрузке):
```
setenv ipaddr 192.168.1.1
setenv serverip 192.168.1.100
tftp 0x46000000 firmware_1.bin
nand erase 0x700000 0x3800000
nand write 0x46000000 0x700000 0x3800000
reset
```

### Вариант 3 — Восстановление стоковой прошивки через SSH (если OpenWrt загрузился, но не работает как надо)

```bash
# Загрузить стоковую firmware_1.bin на роутер
scp -P 22 backup/firmware_1.bin root@192.168.1.1:/tmp/
ssh root@192.168.1.1
mtd write /tmp/firmware_1.bin firmware
reboot
```

## Сборка

### GitHub Actions (рекомендуется)

Перейти на https://github.com/PeaceDeath-ai/zona404-openwrt/actions → Run workflow.

### Локально (Linux/WSL)

```bash
bash build.sh
```

## Файлы в этой папке

| Файл | Описание |
|---|---|
| `backup/` | Бэкап стоковых разделов (preloader, uboot, rf-eeprom, firmware_1/2) |
| `backup_stock.py` | Скрипт бэкапа стоковой прошивки |
| `.github/workflows/build-openwrt.yml` | GitHub Actions workflow |
| `build.sh` | Скрипт сборки для Linux/WSL |
| `build_openwrt.ps1` | Скрипт сборки для Windows |
| `nc1812_info.txt` | Полный дамп заводской системы |
| `collect_info.py` | Сбор данных с роутера по SSH |
