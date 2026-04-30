# COBOT ROS2 Quick Start Guide

## 🚀 Быстрый старт

### Шаг 1: Подготовка окружения

```bash
# Перейти в рабочую директорию
cd ~/cobot_ws

# Установить переменные окружения (опционально)
export WHEEL_PORT=/dev/ttyCH341_motors
export LIDAR_PORT=/dev/ttyUSB0
export CAMERA_URL=http://192.168.1.100:81/stream

# Выдать права на порты (требуется sudo)
sudo chmod 666 /dev/ttyCH341_motors /dev/ttyCH341_servo /dev/ttyUSB0
```

### Шаг 2: Сборка проекта

```bash
# Первый раз
colcon build --symlink-install

# Последующие запуски
colcon build
```

### Шаг 3: Инициализация окружения

```bash
source install/setup.bash
```

### Шаг 4: Запуск всей системы

```bash
ros2 launch cobot_bringup robot.launch.py
```

## 🎮 Управление роботом

### Запустить отдельную ноду

#### Управление колёсами
```bash
ros2 run cobot_driver wheel_driver
```

#### Камера
```bash
ros2 run cobot_camera camera_driver
```

#### LiDAR
```bash
ros2 launch ldlidar_stl_ros2 stl27l.launch.py port_name:=/dev/ttyUSB0
```

#### Манипулятор
```bash
ros2 run cobot_driver servo_bridge
```

### Отправить команду движения

#### Из другого терминала:

```bash
# Движение вперёд
ros2 topic pub /cmd_vel geometry_msgs/Twist '
linear:
  x: 0.5
angular:
  z: 0.0'

# Поворот влево
ros2 topic pub /cmd_vel geometry_msgs/Twist '
linear:
  x: 0.0
angular:
  z: 0.5'

# Стоп
ros2 topic pub /cmd_vel geometry_msgs/Twist '
linear:
  x: 0.0
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0'
```

### Использовать Teleop (если установлен)

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Управление:
- **i/u/o** - Вперёд-влево/вперёд/вперёд-вправо
- **j/k/l** - Влево/стоп/вправо
- **m/,/.** - Назад-влево/назад/назад-вправо
- **q/z** - Увеличить/уменьшить скорость

## 📊 Мониторинг

### Просмотреть все ноды
```bash
ros2 node list
```

### Просмотреть все topics
```bash
ros2 topic list -t
```

### Посмотреть данные topic
```bash
# Данные от камеры (размер ~500KB/сек)
ros2 topic echo /camera/image_raw | head -20

# LiDAR скан
ros2 topic echo /scan | head -20

# Позиции суставов
ros2 topic echo /joint_states

# Команды движения
ros2 topic echo /cmd_vel
```

### Использовать RViz2 для визуализации

```bash
# Отдельный терминал
rviz2
```

В RViz2:
1. Установить Fixed Frame на `lidar`
2. Добавить LaserScan → `/scan`
3. Добавить Image → `/camera/image_raw`
4. Добавить TF для трансформаций

## 🔧 Конфигурирование

### Модифицировать параметры во время запуска

```bash
# Изменить URL камеры
ros2 run cobot_camera camera_driver --ros-args \
  -p camera_url:=http://192.168.1.50:81/stream

# Изменить скорость камеры
ros2 run cobot_camera camera_driver --ros-args \
  -p frame_rate:=15

# Изменить порт колёс
ros2 run cobot_driver wheel_driver --ros-args \
  -p port:=/dev/ttyUSB1 \
  -p baud:=115200
```

### Постоянные конфиги

**Камера:** `src/cobot_camera/config/camera_config.yaml`

```yaml
camera_driver:
  ros__parameters:
    camera_url: "http://192.168.1.100:81/stream"
    frame_rate: 30
    frame_id: "camera"
```

## 🧪 Тестирование

```bash
# Запустить тест всех компонентов
python3 src/cobot_driver/test_components.py all

# Тестировать только камеру
python3 src/cobot_driver/test_components.py camera

# Тестировать только LiDAR
python3 src/cobot_driver/test_components.py lidar
```

## 📝 Логирование

### Просмотреть логи конкретной ноды

```bash
# В процессе запуска (терминал виден в output)
ros2 run cobot_driver wheel_driver

# Задать уровень логирования
ros2 run cobot_driver wheel_driver --ros-args --log-level DEBUG
```

### Записать данные в файл

```bash
# Запустить роботу
ros2 launch cobot_bringup robot.launch.py > robot.log 2>&1 &

# Просмотреть логи в реальном времени
tail -f robot.log
```

## 🐛 Часто встречаемые проблемы

### Ошибка: "Cannot open port"
```bash
# Проверить доступность портов
ls -la /dev/ttyCH341* /dev/ttyUSB*

# Выдать права
sudo chmod 666 /dev/ttyCH341_motors /dev/ttyCH341_servo /dev/ttyUSB0
```

### Ошибка: "Camera connection failed"
```bash
# Проверить доступность камеры
curl http://192.168.1.100:81/stream

# Проверить IP адрес
ping 192.168.1.100

# Изменить URL камеры
ros2 run cobot_camera camera_driver --ros-args \
  -p camera_url:=http://192.168.1.YOUR_IP:81/stream
```

### Система зависает
```bash
# Завершить все ноды
pkill -f ros2

# Очистить ресурсы
source install/setup.bash
```

## 🎯 Часто используемые команды

```bash
# Полезные алиасы в ~/.bashrc
alias cobot_build="cd ~/cobot_ws && colcon build --symlink-install"
alias cobot_source="source ~/cobot_ws/install/setup.bash"
alias cobot_start="ros2 launch cobot_bringup robot.launch.py"
alias cobot_test="python3 ~/cobot_ws/src/cobot_driver/test_components.py"

# Использование
cobot_source
cobot_start
```

## 📚 Дополнительная информация

- Полная документация: `INTEGRATION.md`
- Конфиг камеры: `src/cobot_camera/config/camera_config.yaml`
- Launch файлы: `src/cobot_bringup/launch/`
- Примеры скриптов: `src/cobot_driver/`

## 🚨 Безопасность

⚠️ **ВАЖНО:**
1. **Всегда** останавливайте робота перед отключением питания
2. **Никогда** не выключайте питание ESP32 напрямую
3. **Проверяйте** ориентацию робота перед движением
4. **Используйте** достаточно длинный кабель USB для безопасности

```bash
# Безопасно остановить робота
ros2 topic pub /cmd_vel geometry_msgs/Twist 'linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}'
```
