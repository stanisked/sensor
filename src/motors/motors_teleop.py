#!/usr/bin/env python3
import sys
import termios
import tty
import serial
import time

PORT = "/dev/ttyCH341_motors"
BAUD = 115200

SPEED_STEP = 10
SPEED_MIN = 0
SPEED_MAX = 255


def getch():
    """Читаем один символ с клавиатуры без Enter."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        # Стрелки приходят как ESC [ A/B/C/D (3 байта)
        if ch == "\x1b":
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            return ch + ch2 + ch3
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def send_cmd(ser, cmd, speed=None):
    """Отправка команды на ESP32 в твоём текстовом протоколе."""
    if speed is not None:
        line = f"V {speed}\n"
        ser.write(line.encode("ascii"))
        ser.flush()
    line = cmd + "\n"
    ser.write(line.encode("ascii"))
    ser.flush()
    print(f"TX: {line.strip()}")


def main():
    print(f"Открываем {PORT} @ {BAUD}")
    ser = serial.Serial(PORT, BAUD, timeout=0.1)

    speed = 180  # стартовая скорость
    send_cmd(ser, "s")  # стоп на всякий случай
    print("Управление:")
    print("  W / стрелка вверх    - вперёд")
    print("  S / стрелка вниз     - назад")
    print("  A / стрелка влево    - влево")
    print("  D / стрелка вправо   - вправо")
    print("  Пробел               - стоп")
    print("  Q / Z                - скорость -")
    print("  E / C                - скорость +")
    print("  X                    - выход")
    print(f"Текущая скорость: {speed}")

    try:
        while True:
            key = getch()

            if key in ("x", "X"):
                send_cmd(ser, "s")
                print("Выход.")
                break

            elif key in ("w", "W", "\x1b[A"):  # up
                send_cmd(ser, "f", speed)

            elif key in ("s", "S", "\x1b[B"):  # down
                send_cmd(ser, "b", speed)

            elif key in ("a", "A", "\x1b[D"):  # left
                send_cmd(ser, "l", speed)

            elif key in ("d", "D", "\x1b[C"):  # right
                send_cmd(ser, "r", speed)

            elif key == " ":
                send_cmd(ser, "s")

            elif key in ("q", "Q", "z", "Z"):
                speed = max(SPEED_MIN, speed - SPEED_STEP)
                print(f"Скорость: {speed}")

            elif key in ("e", "E", "c", "C"):
                speed = min(SPEED_MAX, speed + SPEED_STEP)
                print(f"Скорость: {speed}")

            # читаем ответы прошивки (необязательно)
            try:
                line = ser.readline().decode(errors="ignore").strip()
                if line:
                    print(f"RX: {line}")
            except Exception:
                pass

            time.sleep(0.01)

    finally:
        ser.close()


if __name__ == "__main__":
    main()
