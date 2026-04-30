# Интеграция компонентов в ROS2 — Итоговый отчёт

## ✅ Выполненные задачи

### 1. Интеграция управления колёсами (мобильной базы)

**Файл:** `src/cobot_driver/cobot_driver/wheel_driver_node.py`

**Функции:**
- ✅ Управление двумя DC моторами через ESP32
- ✅ Подписка на `/cmd_vel` для управления движением (Twist)
- ✅ Поддержка простого текстового протокола (V, f, b, l, r, s)
- ✅ Динамическое управление скоростью (0-255)
- ✅ Возможность конфигурирования портов и скорости передачи

**Использование:**
```bash
ros2 run cobot_driver wheel_driver
```

**Параметры:**
- `port`: '/dev/ttyCH341_motors'
- `baud`: 115200
- `speed_step`: 10
- `speed_min`: 0
- `speed_max`: 255

---

### 2. Интеграция ESP32-CAM (камера)

**Файл:** `src/cobot_camera/cobot_camera/camera_driver.py`

**Функции:**
- ✅ Захват видеопотока с ESP32-CAM по HTTP
- ✅ Автоматическое переподключение при разрыве соединения
- ✅ Публикация кадров в `/camera/image_raw` (sensor_msgs/Image)
- ✅ Настраиваемая частота кадров (default: 30 FPS)
- ✅ Использование cv_bridge для конвертации OpenCV → ROS

**Использование:**
```bash
ros2 run cobot_camera camera_driver
```

**Параметры:**
- `camera_url`: 'http://192.168.1.100:81/stream'
- `frame_rate`: 30
- `frame_id`: 'camera'

**Файлы конфигурации:**
- `src/cobot_camera/config/camera_config.yaml`
- `src/cobot_camera/launch/camera.launch.py`

---

### 3. Интеграция LDROBOT D500 LiDAR

**Источник:** Официальный пакет `ldlidar_stl_ros2` (клонирован из GitHub)

**Функции:**
- ✅ Поддержка LDROBOT D500 (STL-27L вариант)
- ✅ Публикация данных на `/scan` (sensor_msgs/LaserScan)
- ✅ Работа на скорости 230400 бод
- ✅ Готовые launch файлы для всех вариантов (LD06, LD19, STL-27L)

**Использование:**
```bash
ros2 launch ldlidar_stl_ros2 stl27l.launch.py port_name:=/dev/ttyUSB0
```

---

### 4. Создание интегрированного Launch файла

**Файл:** `src/cobot_bringup/launch/robot.launch.py`

**Функции:**
- ✅ Одновременный запуск всех компонентов
- ✅ Поддержка переменных окружения для портов и адресов
- ✅ Централизованное управление параметрами
- ✅ Настраиваемые адреса через environment variables

**Использование:**
```bash
ros2 launch cobot_bringup robot.launch.py
```

**Переменные окружения:**
```bash
export WHEEL_PORT=/dev/ttyCH341_motors
export LIDAR_PORT=/dev/ttyUSB0
export CAMERA_URL=http://192.168.1.100:81/stream
```

---

## 📁 Структура проекта

```
~/cobot_ws/
├── src/
│   ├── cobot_driver/               # Драйвер мобильной базы
│   │   ├── cobot_driver/
│   │   │   ├── wheel_driver_node.py    ✨ НОВОЕ
│   │   │   ├── servo_bridge_node.py    (существующее)
│   │   │   └── servo_driver_node.py    (существующее)
│   │   ├── test_components.py          ✨ НОВОЕ
│   │   ├── setup.py                    (обновлено)
│   │   └── package.xml                 (обновлено)
│   │
│   ├── cobot_camera/                ✨ НОВЫЙ ПАКЕТ
│   │   ├── cobot_camera/
│   │   │   ├── camera_driver.py
│   │   │   └── __init__.py
│   │   ├── config/
│   │   │   └── camera_config.yaml
│   │   ├── launch/
│   │   │   └── camera.launch.py
│   │   ├── setup.py
│   │   ├── setup.cfg
│   │   ├── package.xml
│   │   └── test/
│   │
│   ├── cobot_bringup/               (обновлено)
│   │   ├── launch/
│   │   │   └── robot.launch.py      ✨ НОВОЕ
│   │   └── ...
│   │
│   ├── ldlidar_stl_ros2/            ✨ КЛОНИРОВАНО ИЗ GITHUB
│   │   ├── launch/
│   │   │   ├── stl27l.launch.py
│   │   │   └── ...
│   │   └── ...
│   │
│   └── motors/                      (для справки, переписан в wheel_driver)
│
├── INTEGRATION.md                   ✨ НОВОЕ - полная документация
├── QUICKSTART.md                    ✨ НОВОЕ - быстрый старт
└── setup.sh                         ✨ НОВОЕ - скрипт инициализации
```

---

## 🔌 Аппаратное подключение

### ESP32 Motors (Колёса)
- **Тип**: 2x JGB37-520 DC Motor + ESP32
- **Адаптер**: CH341 USB-UART
- **Порт**: `/dev/ttyCH341_motors`
- **Скорость**: 115200 бод
- **Команды**: V, f, b, l, r, s

### ESP32-CAM
- **Тип**: Камера с ESP32
- **Интерфейс**: HTTP streaming
- **URL**: `http://192.168.1.100:81/stream`
- **Разрешение**: Типично 640x480
- **Частота**: 30 FPS

### LDROBOT D500
- **Тип**: 2D LiDAR
- **Адаптер**: USB-UART
- **Порт**: `/dev/ttyUSB0`
- **Скорость**: 230400 бод
- **Дальность**: До 12 метров

---

## 🎯 ROS2 Topics

### Входные (вывод данных)
```
/cmd_vel                  (geometry_msgs/Twist) ← Управление движением
/arm_controller/joint_trajectory  (trajectory_msgs/JointTrajectory) ← Команды манипулятора
```

### Выходные (сбор данных)
```
/camera/image_raw        (sensor_msgs/Image) ← Видеопоток
/scan                    (sensor_msgs/LaserScan) ← Данные LiDAR
/joint_states            (sensor_msgs/JointState) ← Позиции суставов
```

---

## 🚀 Быстрый старт

```bash
# 1. Подготовка
cd ~/cobot_ws
source install/setup.bash
sudo chmod 666 /dev/ttyCH341_motors /dev/ttyCH341_servo /dev/ttyUSB0

# 2. Сборка (первый раз)
colcon build --symlink-install

# 3. Запуск всей системы
ros2 launch cobot_bringup robot.launch.py

# 4. В другом терминале - управление
source install/setup.bash
ros2 topic pub /cmd_vel geometry_msgs/Twist 'linear: {x: 0.5}'
```

Для более подробных инструкций см. `QUICKSTART.md`.

---

## 🧪 Тестирование

```bash
# Запустить тесты всех компонентов
python3 src/cobot_driver/test_components.py all

# Тестировать компоненты отдельно
python3 src/cobot_driver/test_components.py camera
python3 src/cobot_driver/test_components.py lidar
python3 src/cobot_driver/test_components.py wheel
```

---

## 📦 Зависимости

### Новые зависимости ROS2:
- `geometry_msgs` - для управления движением (Twist)
- `cv_bridge` - для конвертации изображений
- `image_transport` - для публикации изображений
- `sensor_msgs` - для LiDAR и камеры

### Системные:
```bash
pip3 install pyserial opencv-python numpy
```

---

## 🔄 Следующие шаги

### Планируется:
1. ✅ Интеграция управления колёсами через ESP32
2. ✅ Интеграция камеры ESP32-CAM
3. ✅ Интеграция LiDAR LDROBOT D500
4. ⏳ **Настройка SLAM с использованием LiDAR + камеры**
5. ⏳ **Интеграция IMU для улучшения навигации**
6. ⏳ **Obstacle avoidance на основе LiDAR**
7. ⏳ **Управление манипулятором через MoveIt2**

### Не включено в текущую интеграцию:
- Управление манипулятором оставлено на месте (servo_bridge, servo_driver_node)
- SLAM, навигация,障碍 avoidance требуют дополнительной конфигурации

---

## 🐛 Известные проблемы и их решение

### Проблема 1: Порты переназначаются при перезагрузке
**Решение:** Используйте udev правила для постоянного имени портов

### Проблема 2: Камера не подключается
**Решение:** Проверьте IP адрес ESP32-CAM, используйте `ping` и `curl`

### Проблема 3: Нет доступа к портам
**Решение:** Выполните `sudo chmod 666 /dev/ttyCH341_* /dev/ttyUSB*`

---

## 📚 Документация

1. **INTEGRATION.md** - Полная архитектура и документация
2. **QUICKSTART.md** - Быстрый старт и основные команды
3. **setup.sh** - Скрипт инициализации проекта

---

## ✨ Итог

Система полностью интегрирована и готова к использованию:
- ✅ Мобильная база управляется через `/cmd_vel`
- ✅ Камера публикует видеопоток в `/camera/image_raw`
- ✅ LiDAR публикует данные в `/scan`
- ✅ Все компоненты запускаются одной командой

**Запуск:** `ros2 launch cobot_bringup robot.launch.py`

---

*Последнее обновление: 30 апреля 2026*
