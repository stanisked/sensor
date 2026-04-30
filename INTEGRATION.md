# Интеграция мобильной платформы с ROS2

## Архитектура системы

```
┌─────────────────────────────────────────────────────────┐
│                      ROS2 Master                        │
├──────────┬───────────────┬──────────────┬───────────────┤
│          │               │              │               │
▼          ▼               ▼              ▼               ▼
┌──────┐  ┌──────┐      ┌──────┐     ┌────────┐    ┌─────────┐
│Wheels│  │Camera│      │LiDAR │     │Arm     │    │Hardware │
│Driver│  │Driver│      │Driver│     │Driver  │    │Interface│
└──┬───┘  └──┬───┘      └──┬───┘     └────┬───┘    └────┬────┘
   │         │             │              │             │
   ▼         ▼             ▼              ▼             ▼
┌──────┐  ┌──────┐      ┌──────┐     ┌────────┐    ┌─────────┐
│ESP32 │  │ESP32 │      │LDROBOT│    │Servos  │    │STS Servo│
│Motors│  │CAM   │      │D500   │    │Control │    │Bus      │
└──────┘  └──────┘      └──────┘     └────────┘    └─────────┘
```

## Аппаратное обеспечение

### 1. Мобильная база (Wheels)
- **Моторы**: 2x JGB37-520 DC Motor
- **Контроллер**: ESP32 с CH341 USB-UART адаптером
- **Порт**: `/dev/ttyCH341_motors`
- **Скорость**: 115200 бод
- **Протокол**: Текстовый (простые команды)

### 2. Камера
- **Модель**: ESP32-CAM
- **Интерфейс**: HTTP stream
- **URL**: `http://192.168.1.100:81/stream`
- **Частота кадров**: 30 FPS

### 3. LiDAR
- **Модель**: LDROBOT D500 (STL-27L)
- **Интерфейс**: UART (USB-CH341)
- **Порт**: `/dev/ttyUSB0`
- **Скорость**: 230400 бод

### 4. Манипулятор
- **Сервомоторы**: 3x STS servo (шина управления)
- **Порт**: `/dev/ttyCH341_servo`

## ROS2 Пакеты

### cobot_driver
Основной пакет для управления мобильной базой.

**Ноды:**
- `wheel_driver`: Управление двумя колёсами через ESP32
- `servo_bridge`: Управление сервомоторами манипулятора

**Topics:**
- `/cmd_vel` (input): Geometry/Twist для управления движением
- `/joint_states` (output): Позиции суставов
- `/arm_controller/joint_trajectory` (input): Траектория манипулятора

### cobot_camera
Драйвер для ESP32-CAM.

**Ноды:**
- `camera_driver`: Захват и публикация видеопотока

**Topics:**
- `/camera/image_raw` (output): Raw RGB/8 изображения

### ldlidar_stl_ros2
Официальный драйвер LDROBOT для ROS2 (скопирован из репозитория).

**Topics:**
- `/scan` (output): Данные LiDAR (sensor_msgs/LaserScan)

## Установка и настройка

### 1. Подготовка портов

```bash
# Проверить доступные устройства
ls -la /dev/tty*

# Выдать права доступа (требуется sudo)
sudo chmod 666 /dev/ttyCH341_motors
sudo chmod 666 /dev/ttyCH341_servo
sudo chmod 666 /dev/ttyUSB0
```

### 2. Сборка проекта

```bash
cd ~/cobot_ws
colcon build --symlink-install
source install/setup.bash
```

### 3. Конфигурирование адресов

Создать файл `~/.env` или экспортировать переменные:

```bash
export WHEEL_PORT="/dev/ttyCH341_motors"
export LIDAR_PORT="/dev/ttyUSB0"
export CAMERA_URL="http://192.168.1.100:81/stream"
```

Для постоянной конфигурации добавить в `~/.bashrc` или `~/.zshrc`:
```bash
source ~/.env
```

## Запуск

### Вариант 1: Запуск всей системы
```bash
ros2 launch cobot_bringup robot.launch.py
```

### Вариант 2: Запуск отдельных компонентов

**Управление колёсами:**
```bash
ros2 run cobot_driver wheel_driver
```

**Камера:**
```bash
ros2 run cobot_camera camera_driver
```

**LiDAR:**
```bash
ros2 launch ldlidar_stl_ros2 stl27l.launch.py port_name:=/dev/ttyUSB0
```

**Сервомоторы:**
```bash
ros2 run cobot_driver servo_bridge
```

## Управление движением

### Через Teleop

```bash
# Если установлен teleop_twist_keyboard
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### Через Python скрипт

```python
import rclpy
from geometry_msgs.msg import Twist

rclpy.init()
node = rclpy.create_node('test_cmd_vel')
pub = node.create_publisher(Twist, '/cmd_vel', 10)

# Движение вперёд
msg = Twist()
msg.linear.x = 0.5  # 50% скорости
pub.publish(msg)

rclpy.spin_once(node)
rclpy.shutdown()
```

## Мониторинг и диагностика

### Проверить все активные ноды
```bash
ros2 node list
```

### Посмотреть все topics
```bash
ros2 topic list -t
```

### Просмотр данных конкретного topic
```bash
# Изображение с камеры (требует специальной визуализации)
ros2 topic echo /camera/image_raw

# LiDAR скан
ros2 topic echo /scan

# Позиции суставов
ros2 topic echo /joint_states
```

### Использовать RViz2 для визуализации

```bash
rviz2
```

Добавить:
- LaserScan (`/scan`)
- Camera (`/camera/image_raw`)
- TF (для трансформаций)

## Конфигурационные файлы

### Камера (`cobot_camera/config/camera_config.yaml`)
```yaml
camera_driver:
  ros__parameters:
    camera_url: "http://192.168.1.100:81/stream"
    frame_rate: 30
    frame_id: "camera"
```

### Модификация параметров во время запуска

```bash
ros2 run cobot_camera camera_driver --ros-args \
  -p camera_url:=http://192.168.1.50:81/stream \
  -p frame_rate:=15
```

## Устранение неполадок

### Нет соединения с ESP32
```bash
# Проверить порт
lsusb
ls -la /dev/ttyUSB* /dev/ttyCH341*

# Проверить права доступа
sudo chmod 666 /dev/ttyCH341_motors

# Проверить подключение
cat /dev/ttyCH341_motors  # Ctrl+C для выхода
```

### Камера не подключается
```bash
# Проверить доступность
curl http://192.168.1.100:81/stream

# Проверить IP адрес ESP32-CAM
ping 192.168.1.100

# Проверить конфигурацию в Arduino IDE / ESP-IDF
```

### LiDAR не работает
```bash
# Проверить порт
ls -la /dev/ttyUSB*

# Тест передачи данных
ros2 run ldlidar_stl_ros2 ldlidar_driver --ros-args \
  -p port_name:=/dev/ttyUSB0
```

## ESP32 Протоколы управления

### Колёса (Motor Controller)
```
V <speed>   - Установить скорость (0-255)
f           - Вперёд
b           - Назад (Backward)
l           - Влево (Left)
r           - Вправо (Right)
s           - Стоп (Stop)
```

Пример:
```
V 180       # Скорость 180/255
f           # Вперёд с текущей скоростью
s           # Стоп
```

### ARM (Servo Controller)
```
Протокол STS (Serial Servo Transport)
- Адрес сервы: 1-6
- Команды: Position, Speed, Acceleration
- Скорость: 115200 бод
- Формат: Двоичный
```

## Дополнительные инструменты

### Запись rosbag
```bash
ros2 bag record /camera/image_raw /scan /cmd_vel -o my_recording
```

### Воспроизведение rosbag
```bash
ros2 bag play my_recording
```

### Проверка синхронизации
```bash
ros2 topic echo /tf --once
```

## Примечания и знаемые проблемы

1. **Асинхронность портов**: Убедитесь, что все USB адаптеры имеют уникальные идентификаторы, иначе порты могут переназначиться при перезагрузке.

2. **Производительность камеры**: Высокое разрешение может замедлить систему. Используйте 30 FPS как базовую частоту.

3. **Питание**: При одновременном использовании всех компонентов убедитесь в достаточной мощности источника питания.

4. **Коллизии тем управления**: Проверьте, что только один источник управления отправляет команды на `/cmd_vel`.

## Список TODO

- [ ] Добавить управление манипулятором через MoveIt2
- [ ] Интегрировать IMU для навигации
- [ ] Добавить障碍 avoidance с использованием LiDAR
- [ ] Создать URDF модель полной системы
- [ ] Добавить SLAM навигацию
