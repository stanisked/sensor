# cobot_ws

## Сначала про Git

Это самое важное в повседневной работе.

Изменения в коде обычно делаются на `Huawei`, а потом уже подтягиваются на `Raspberry Pi 5`.

Порядок такой:

1. На `Huawei` меняем код, конфиги, launch-файлы.
2. На `Huawei` проверяем, что всё собирается.
3. На `Huawei` делаем `git add`, `git commit`, `git push`.
4. На `Raspberry Pi 5` заходим в тот же workspace и делаем `git pull`.
5. На `Raspberry Pi 5` пересобираем workspace и проверяем работу с железом.

### Типичный цикл работы на `Huawei`

```bash
cd ~/cobot_ws
git status
colcon build
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
git add .
git commit -m "описание изменений"
git push
```

### Типичный цикл работы на `Raspberry Pi 5`

```bash
cd ~/cobot_ws
git pull
colcon build
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
```

### Если после `git pull` всё ведёт себя странно

Иногда остаются старые артефакты сборки. Тогда проще пересобрать workspace начисто.

```bash
cd ~/cobot_ws
rm -rf build install log
colcon build
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
```

## Что где делается

В проекте используются два устройства:

- `Huawei` с `Ubuntu 24.04 LTS Desktop` и `ROS 2 Jazzy`
- `Raspberry Pi 5` с `Ubuntu 24.04 LTS Server` и `ROS 2 Jazzy`

### `Huawei`

Основная машина для разработки:

- редактирование кода
- настройка конфигов
- локальная сборка
- работа с Git
- запуск `MoveIt` и `RViz`

### `Raspberry Pi 5`

Машина, подключенная к железу:

- запуск `bringup`
- работа с `ros2_control`
- запуск драйверов
- проверка сервомоторов `STS3215`
- финальная проверка на реальном роботе

## Важно перед запуском

На обоих устройствах должен быть одинаковый `ROS_DOMAIN_ID`.

Пример:

```bash
export ROS_DOMAIN_ID=10
```

Если на `Huawei` и `Raspberry Pi 5` стоят разные значения, устройства не увидят друг друга.

## Пошаговый запуск по терминалам

Ниже всё расписано так, чтобы можно было просто открыть нужный терминал и выполнить команды сверху вниз.

Команды намеренно повторяются. Это нормально. Так меньше шансов забыть `source` или `export`.

## 🚗 Управление мобильной базой (Wheels + Camera + LiDAR)

**НОВОЕ в этой версии:** Интеграция управления колёсами, камеры ESP32-CAM и лидара LDROBOT D500.

### Быстрый старт — запуск ВСЕ компонентов одной командой

На `Raspberry Pi 5`:

```bash
cd ~/cobot_ws
git pull
colcon build
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10
ros2 launch cobot_bringup robot.launch.py
```

Это запустит **одновременно**:
- Управление колёсами (wheel_driver)
- Камеру ESP32-CAM (camera_driver)
- LiDAR (ldlidar_driver)
- Манипулятор (servo_bridge)

### Управление колёсами из другого терминала

На `Raspberry Pi 5` (новый терминал):

```bash
cd ~/cobot_ws
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10

# Движение вперёд со скоростью 50%
ros2 topic pub /cmd_vel geometry_msgs/Twist 'linear: {x: 0.5}'

# Поворот влево
ros2 topic pub /cmd_vel geometry_msgs/Twist 'angular: {z: 0.5}'

# Полная остановка
ros2 topic pub /cmd_vel geometry_msgs/Twist '{}'
```

На `Huawei` можно отправлять команды тому же `/cmd_vel`:

```bash
cd ~/cobot_ws
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10

# Управление движением
ros2 topic pub /cmd_vel geometry_msgs/Twist 'linear: {x: 0.3} angular: {z: -0.2}'
```

### Просмотр данных от камеры

На `Huawei`:

```bash
cd ~/cobot_ws
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10

# Просмотр информации об изображении
ros2 topic echo /camera/image_raw | head -20

# Или в RViz:
rviz2
# Добавить Image → /camera/image_raw
```

### Просмотр данных от LiDAR

На `Huawei`:

```bash
cd ~/cobot_ws
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10

# Просмотр сканов
ros2 topic echo /scan | head -20

# Или в RViz:
rviz2
# Добавить LaserScan → /scan
```

### Как это было раньше vs как теперь

**Старый способ:**
```bash
cd ~/robot_ws/motors
python3 motors_teleop.py
```

**Новый способ через ROS2:**
```bash
ros2 launch cobot_bringup robot.launch.py
# или только колёса:
ros2 run cobot_driver wheel_driver
```

### Конфигурация портов

Если порты отличаются от стандартных, отредактируйте переменные окружения или `launch/robot.launch.py`:

```bash
export WHEEL_PORT=/dev/ttyCH341_motors
export LIDAR_PORT=/dev/ttyUSB0
export CAMERA_URL=http://192.168.1.100:81/stream
```

### ROS2 Topics для управления и сенсоров

| Topic | Тип | Назначение |
|-------|-----|-----------|
| `/cmd_vel` | `geometry_msgs/Twist` | **Вход**: команды движения |
| `/camera/image_raw` | `sensor_msgs/Image` | **Выход**: видеопоток с камеры |
| `/scan` | `sensor_msgs/LaserScan` | **Выход**: данные LiDAR |
| `/joint_states` | `sensor_msgs/JointState` | **Выход**: позиции суставов манипулятора |

---

## Raspberry Pi 5

### Терминал 1. Подтянуть изменения, собрать и запустить полный `bringup` (с колёсами, камерой, LiDAR)

```bash
cd ~/cobot_ws
git pull
colcon build
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10
ros2 launch cobot_bringup robot.launch.py
```

**ИЛИ**, если нужен только старый bringup (без управления колёсами):

```bash
cd ~/cobot_ws
git pull
colcon build
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10
ros2 launch cobot_bringup bringup.launch.py
```

После запуска этот терминал лучше оставить в покое. В нём должен продолжать работать `bringup`.

### Терминал 2. Управление колёсами (тележка)

```bash
cd ~/cobot_ws
git status
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10

# Движение вперёд с половинной скоростью
ros2 topic pub /cmd_vel geometry_msgs/Twist 'linear: {x: 0.5}'

# Или движение с поворотом
ros2 topic pub /cmd_vel geometry_msgs/Twist 'linear: {x: 0.3} angular: {z: 0.2}'

# Остановка
ros2 topic pub /cmd_vel geometry_msgs/Twist '{}'
```

### Терминал 3. Проверить данные от камеры

```bash
cd ~/cobot_ws
git status
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10

# Просмотр информации о кадрах
ros2 topic echo /camera/image_raw | head -10
```

### Терминал 4. Проверить данные от LiDAR

```bash
cd ~/cobot_ws
git status
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10

# Просмотр сканов
ros2 topic echo /scan | head -10
```

### Терминал 5. Проверить контроллеры манипулятора

```bash
cd ~/cobot_ws
git pull
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10
ros2 control list_controllers
```

Если видишь, что `joint_state_broadcaster` и `arm_controller` в состоянии `active`, значит всё ок.

Если они не активны, можно руками выполнить:

```bash
cd ~/cobot_ws
git pull
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10
ros2 control load_controller joint_state_broadcaster
ros2 control load_controller arm_controller
ros2 control set_controller_state joint_state_broadcaster active
ros2 control set_controller_state arm_controller active
ros2 control list_controllers
```

### Терминал 6. Быстрая проверка ROS 2 на Pi

```bash
cd ~/cobot_ws
git pull
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10
ros2 node list
ros2 topic list
```

## Huawei

### Терминал 1. Собрать workspace и проверить, что видны узлы

```bash
cd ~/cobot_ws
git status
colcon build
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10
ros2 node list
ros2 topic list
```

Если список узлов и топиков приходит, значит `Huawei` видит `Raspberry Pi 5`.

### Терминал 2. Управление колёсами (тележка) с Huawei

```bash
cd ~/cobot_ws
git status
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10

# Движение вперёд
ros2 topic pub /cmd_vel geometry_msgs/Twist 'linear: {x: 0.5}'

# Движение с поворотом (вперёд-влево)
ros2 topic pub /cmd_vel geometry_msgs/Twist 'linear: {x: 0.3} angular: {z: 0.2}'

# Только поворот на месте
ros2 topic pub /cmd_vel geometry_msgs/Twist 'angular: {z: 0.5}'

# Остановка
ros2 topic pub /cmd_vel geometry_msgs/Twist '{}'
```

### Терминал 3. Просмотр видео с камеры

```bash
cd ~/cobot_ws
git status
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10

# Просмотр информации о кадрах
ros2 topic echo /camera/image_raw | head -5
```

### Терминал 4. Просмотр данных LiDAR

```bash
cd ~/cobot_ws
git status
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10

# Просмотр сканов
ros2 topic echo /scan | head -5
```

### Терминал 5. Запустить MoveIt для манипулятора

```bash
cd ~/cobot_ws
git status
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10
ros2 launch cobot_moveit_config moveit.launch.py
```

### Терминал 6. Визуализация всего в RViz

```bash
cd ~/cobot_ws
git status
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10
rviz2
```

В RViz добавьте:
1. **LaserScan** → `/scan` (красные точки с лидара)
2. **Image** → `/camera/image_raw` (видео с камеры)
3. **TF** (трансформации)
4. **RobotModel** (модель робота)
5. **MotionPlanning** (для управления манипулятором через MoveIt)

---

### Альтернатива: `demo.launch.py` вместо обычного запуска

`demo.launch.py` не нужно запускать вместе с `moveit.launch.py`.

Это отдельный demo-режим, который сам поднимает `move_group`, `RViz`, `robot_state_publisher`, fake `ros2_control` и спавнеры контроллеров.

```bash
cd ~/cobot_ws
git status
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10
ros2 launch cobot_moveit_config demo.launch.py
```

## Короткий сценарий целиком

1. На `Huawei` вносим изменения.
2. На `Huawei` собираем проект.
3. На `Huawei` делаем `git add`, `git commit`, `git push`.
4. На `Raspberry Pi 5` в `Терминале 1` делаем `git pull`, сборку и запускаем **новый** `robot.launch.py`:
   ```bash
   ros2 launch cobot_bringup robot.launch.py
   ```
   Это запустит одновременно: колёса, камеру, LiDAR, манипулятор.
5. На `Raspberry Pi 5` в остальных терминалах проверяем компоненты:
   - `Терминал 2`: управление колёсами `ros2 topic pub /cmd_vel ...`
   - `Терминал 3`: проверка камеры `ros2 topic echo /camera/image_raw`
   - `Терминал 4`: проверка LiDAR `ros2 topic echo /scan`
   - `Терминал 5`: проверка манипулятора `ros2 control list_controllers`
6. На `Huawei` в `Терминале 1` проверяем, что видны узлы и топики:
   ```bash
   ros2 node list
   ros2 topic list
   ```
7. На `Huawei` управляем:
   - `Терминал 2`: управление колёсами `ros2 topic pub /cmd_vel ...`
   - `Терминал 3`: просмотр видео `ros2 topic echo /camera/image_raw`
   - `Терминал 4`: просмотр LiDAR `ros2 topic echo /scan`
   - `Терминал 5`: запускаем MoveIt `ros2 launch cobot_moveit_config moveit.launch.py`
   - `Терминал 6`: запускаем RViz для визуализации всего

## Краткая справка по новым командам

### Запуск

| Команда | Описание |
|---------|----------|
| `ros2 launch cobot_bringup robot.launch.py` | ✅ **НОВОЕ**: запуск всех компонентов (колёса + камера + LiDAR + манипулятор) |
| `ros2 launch cobot_bringup bringup.launch.py` | Старый способ: только манипулятор |
| `ros2 run cobot_driver wheel_driver` | Только управление колёсами |
| `ros2 run cobot_camera camera_driver` | Только камера |

### Управление

| Команда | Описание |
|---------|----------|
| `ros2 topic pub /cmd_vel geometry_msgs/Twist 'linear: {x: 0.5}'` | Движение вперёд на 50% скорости |
| `ros2 topic pub /cmd_vel geometry_msgs/Twist 'linear: {x: 0.3} angular: {z: 0.2}'` | Движение вперёд с поворотом |
| `ros2 topic pub /cmd_vel geometry_msgs/Twist 'angular: {z: 0.5}'` | Поворот на месте |
| `ros2 topic pub /cmd_vel geometry_msgs/Twist '{}'` | ⛔ Остановка |

### Проверка данных

| Команда | Описание |
|---------|----------|
| `ros2 topic echo /camera/image_raw \| head -5` | Просмотр видео с камеры |
| `ros2 topic echo /scan \| head -5` | Просмотр сканов LiDAR |
| `ros2 topic echo /joint_states` | Просмотр позиций суставов |
| `ros2 topic list` | Список всех topics |
| `ros2 node list` | Список всех узлов |

### Визуализация

| Команда | Описание |
|---------|----------|
| `rviz2` | Запуск RViz (добавить LaserScan `/scan` и Image `/camera/image_raw`) |
| `ros2 launch cobot_moveit_config moveit.launch.py` | Запуск MoveIt для управления манипулятором |

---

## Что проверить, если что-то не работает

### 1. Совпадает ли `ROS_DOMAIN_ID`

На `Raspberry Pi 5`:

```bash
cd ~/cobot_ws
git pull
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
echo $ROS_DOMAIN_ID
```

На `Huawei`:

```bash
cd ~/cobot_ws
git status
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
echo $ROS_DOMAIN_ID
```

Значение должно быть одинаковым.

### 2. Видны ли узлы

На `Raspberry Pi 5`:

```bash
cd ~/cobot_ws
git pull
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10
ros2 node list
```

На `Huawei`:

```bash
cd ~/cobot_ws
git status
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10
ros2 node list
```

Обычно полезно увидеть хотя бы такие узлы:

- `robot_state_publisher`
- `controller_manager`

### 3. Видны ли топики

На `Huawei`:

```bash
cd ~/cobot_ws
git status
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10
ros2 topic list
```

Обычно стоит проверить, есть ли:

- `/joint_states`
- `/robot_description`
- `/tf`
- `/tf_static`

### 4. Идут ли данные в `/joint_states`

На `Huawei`:

```bash
cd ~/cobot_ws
git status
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10
ros2 topic echo /joint_states
```

### 5. Диагностика колёс (Wheel Driver)

Если колёса не двигаются:

```bash
# Проверить, что ноды запустились
ros2 node list | grep wheel_driver

# Проверить, что топик /cmd_vel создан
ros2 topic list | grep cmd_vel

# Проверить доступ к порту
ls -la /dev/ttyCH341_motors

# Если нет прав доступа
sudo chmod 666 /dev/ttyCH341_motors

# Проверить логи
ros2 run cobot_driver wheel_driver --ros-args --log-level DEBUG
```

### 6. Диагностика камеры (ESP32-CAM)

Если камера не работает:

```bash
# Проверить доступность камеры с Raspberry Pi 5
curl http://192.168.1.100:81/stream

# Проверить, что ноды запустились
ros2 node list | grep camera_driver

# Проверить топик камеры
ros2 topic list | grep camera

# Проверить логи
ros2 run cobot_camera camera_driver --ros-args --log-level DEBUG

# Проверить IP адрес ESP32-CAM в сети
ping 192.168.1.100
```

Если IP другой, отредактируйте:
- Переменную окружения: `export CAMERA_URL=http://ВАШ_IP:81/stream`
- Или конфиг: `src/cobot_camera/config/camera_config.yaml`

### 7. Диагностика LiDAR

Если LiDAR не работает:

```bash
# Проверить, что ноды запустились
ros2 node list | grep ldlidar

# Проверить доступ к порту
ls -la /dev/ttyUSB0

# Если нет прав доступа
sudo chmod 666 /dev/ttyUSB0

# Проверить топик LiDAR
ros2 topic list | grep scan

# Просмотреть данные
ros2 topic echo /scan | head -20
```

Если порт отличается, используйте:
```bash
export LIDAR_PORT=/dev/ttyUSB1
# или отредактируйте src/cobot_bringup/launch/robot.launch.py
```

---

## Короткое напоминание

- код и Git удобнее вести на `Huawei`
- `bringup` и работа с железом идут на `Raspberry Pi 5`
- `MoveIt` и `RViz` удобнее запускать на `Huawei`
- если после обновления что-то сломалось, сначала делай `git pull`, потом проверяй `ROS_DOMAIN_ID`, потом смотри `ros2 control list_controllers`
- **NEW:** если колёса не двигаются, проверь порт `/dev/ttyCH341_motors` и логи `wheel_driver`
- **NEW:** если камера не работает, проверь доступность IP и конфиг `camera_config.yaml`
- **NEW:** если LiDAR не работает, проверь порт `/dev/ttyUSB0` и логи `ldlidar_driver`
