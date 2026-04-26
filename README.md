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

## Raspberry Pi 5

### Терминал 1. Подтянуть изменения, собрать и запустить `bringup`

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

### Терминал 2. Проверить контроллеры

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

### Терминал 3. Быстрая проверка ROS 2 на Pi

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

### Терминал 2. Запустить обычный `MoveIt`

```bash
cd ~/cobot_ws
git status
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10
ros2 launch cobot_moveit_config moveit.launch.py
```

`moveit.launch.py` это основной ручной запуск. Внутри он просто подключает `move_group.launch.py`, так что дублирования логики между launch-файлами нет.

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
4. На `Raspberry Pi 5` в `Терминале 1` делаем `git pull`, сборку и запускаем `bringup`.
5. На `Raspberry Pi 5` в `Терминале 2` проверяем `ros2 control list_controllers`.
6. На `Huawei` в `Терминале 1` проверяем, что видны узлы и топики.
7. На `Huawei` выбираем один режим запуска:
   - обычный: `moveit.launch.py`
   - demo: `demo.launch.py`

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

## Короткое напоминание

- код и Git удобнее вести на `Huawei`
- `bringup` и работа с железом идут на `Raspberry Pi 5`
- `MoveIt` и `RViz` удобнее запускать на `Huawei`
- если после обновления что-то сломалось, сначала делай `git pull`, потом проверяй `ROS_DOMAIN_ID`, потом смотри `ros2 control list_controllers`
