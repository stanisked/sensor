# cobot_ws

## Рабочий контекст

В проекте используются два устройства:

- `Huawei` с `Ubuntu 24.04 LTS Desktop` и `ROS 2 Jazzy`
- `Raspberry Pi 5` с `Ubuntu 24.04 LTS Server` и `ROS 2 Jazzy`

На обоих устройствах используется одно и то же рабочее пространство: `cobot_ws`.

## Роли устройств

### 1. Десктоп `Huawei`

Основная машина для разработки:

- редактирование кода
- настройка конфигов
- локальная сборка и проверка
- работа с Git

### 2. `Raspberry Pi 5`

Машина, подключенная к реальному железу:

- подключение к роботам
- работа с сервомоторами `STS3215`
- запуск на целевой системе
- проверка взаимодействия с железом

## Git workflow

Обычный порядок работы такой:

1. Изменения вносятся на десктопе `Huawei`
2. Затем выполняется `git push`
3. На `Raspberry Pi 5` выполняется `git pull`
4. После этого изменения проверяются уже на машине, подключенной к роботам

## Важно

При изменениях в `ros2_control`, драйверах, launch-файлах и конфигурации MoveIt нужно учитывать, что:

- на десктопе удобно разрабатывать и отлаживать конфиги
- итоговая проверка работы с моторами и реальным роботом делается на `Raspberry Pi 5`

## Типовые команды

### Синхронизация на `Raspberry Pi 5`

```bash
cd ~/cobot_ws
git pull
colcon build
source install/setup.bash
```

### Очистка старой сборки на `Raspberry Pi 5`

Если после `git pull` или смены конфигов сборка ведёт себя странно, можно очистить старые артефакты сборки и собрать workspace заново:

```bash
cd ~/cobot_ws
rm -rf build install log
colcon build
source install/setup.bash
```

### Сборка после изменений на десктопе

```bash
cd ~/cobot_ws
colcon build
source install/setup.bash
```

### Запуск bringup

```bash
ros2 launch cobot_bringup bringup.launch.py
```

### Запуск MoveIt

```bash
ros2 launch cobot_moveit_config moveit.launch.py
```

### Demo-запуск MoveIt

```bash
ros2 launch cobot_moveit_config demo.launch.py
```

## Пошаговый запуск на двух устройствах

### Важно про `ROS_DOMAIN_ID`

Перед запуском на обоих устройствах нужно выставить один и тот же `ROS_DOMAIN_ID`.

Пример:

```bash
export ROS_DOMAIN_ID=10
```

Если на одном устройстве `ROS_DOMAIN_ID` один, а на втором другой, узлы друг друга не увидят.

### Что где запускается

- `Raspberry Pi 5`: `bringup`, драйверы, `ros2_control`, работа с реальным железом
- `Huawei`: `MoveIt`, `RViz`, проверка топиков, планирование и GUI

На `Raspberry Pi 5` нет GUI, поэтому там не нужно запускать `RViz` и GUI-launch-файлы MoveIt.

### Терминал 1 на `Raspberry Pi 5`

В этом терминале подготавливаем workspace и запускаем bringup:

```bash
cd ~/cobot_ws
git pull
colcon build
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10
ros2 launch cobot_bringup bringup.launch.py
```

Этот терминал после запуска лучше не трогать, пусть в нём продолжает работать `bringup`.

### Терминал 2 на `Raspberry Pi 5`

Во втором терминале проверяем контроллеры:

```bash
cd ~/cobot_ws
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10
ros2 control list_controllers
```

Если `joint_state_broadcaster` и `arm_controller` уже в состоянии `active`, всё нормально.

Если контроллеры не активны, можно вручную выполнить:

```bash
ros2 control load_controller joint_state_broadcaster
ros2 control load_controller arm_controller
ros2 control set_controller_state joint_state_broadcaster active
ros2 control set_controller_state arm_controller active
```

После этого снова проверить:

```bash
ros2 control list_controllers
```

### Терминал 1 на `Huawei`

На десктопе подготавливаем окружение:

```bash
cd ~/cobot_ws
colcon build
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10
```

После этого можно проверить, что десктоп видит Pi:

```bash
ros2 node list
ros2 topic list
```

### Терминал 2 на `Huawei`

Если связь есть, запускаем MoveIt:

```bash
cd ~/cobot_ws
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10
ros2 launch cobot_moveit_config moveit.launch.py
```

### Терминал 3 на `Huawei`, если нужен GUI

Если нужен полный GUI-сценарий, можно запускать:

```bash
cd ~/cobot_ws
source /opt/ros/jazzy/setup.bash
source ~/cobot_ws/install/setup.bash
export ROS_DOMAIN_ID=10
ros2 launch cobot_moveit_config demo.launch.py
```

### Короткий сценарий целиком

1. Открываем `Терминал 1` на `Raspberry Pi 5` и запускаем `bringup`
2. Открываем `Терминал 2` на `Raspberry Pi 5` и проверяем `ros2 control list_controllers`
3. Если надо, вручную активируем `joint_state_broadcaster` и `arm_controller`
4. Открываем `Терминал 1` на `Huawei` и проверяем, что видны ROS 2-узлы и топики
5. Открываем `Терминал 2` на `Huawei` и запускаем `moveit.launch.py`
6. При необходимости открываем ещё один терминал на `Huawei` и запускаем `demo.launch.py`

### Короткое напоминание

- `ROS_DOMAIN_ID` должен совпадать на обоих устройствах
- `bringup` и работа с железом идут на `Raspberry Pi 5`
- `MoveIt` и `RViz` удобнее запускать на десктопе `Huawei`
- после проблем с контроллерами первым делом смотри `ros2 control list_controllers`

## Проверка связи между устройствами

Если `Huawei` и `Raspberry Pi 5` находятся в одном `ROS_DOMAIN_ID`, они должны видеть ROS 2-узлы и топики друг друга.

### На обоих устройствах сначала проверить домен

```bash
echo $ROS_DOMAIN_ID
```

Значение должно совпадать.

### Проверка списка узлов

```bash
ros2 node list
```

Если всё нормально, на десктопе должны быть видны узлы, запущенные на `Raspberry Pi 5`, например:

- `robot_state_publisher`
- `controller_manager`

### Проверка списка топиков

```bash
ros2 topic list
```

Обычно полезно проверить, видны ли:

- `/joint_states`
- `/robot_description`
- `/tf`
- `/tf_static`

### Проверка, что приходят данные по `joint_states`

```bash
ros2 topic echo /joint_states
```

Если связь есть и `bringup` запущен нормально, на десктопе должен идти поток сообщений от робота.

### Если устройства не видят друг друга

Проверь по порядку:

1. Совпадает ли `ROS_DOMAIN_ID`
2. Подключены ли оба устройства к одной сети
3. Запущен ли `bringup` на `Raspberry Pi 5`
4. Выполнен ли `source /opt/ros/jazzy/setup.bash`
5. Выполнен ли `source ~/cobot_ws/install/setup.bash`

## Быстрая проверка сети

### Узнать IP-адрес устройства

```bash
ip addr
```

или короче:

```bash
hostname -I
```

### Проверить доступность `Raspberry Pi 5` с десктопа

```bash
ping <IP_RASPBERRY_PI>
```

### Проверить доступность десктопа с `Raspberry Pi 5`

```bash
ping <IP_HUAWEI>
```

Если `ping` не проходит, сначала нужно решить сетевую проблему, и только потом проверять ROS 2.

## Если сеть режет discovery ROS 2

Иногда устройства находятся в одной сети, но ROS 2 всё равно плохо видит узлы. Частая причина в том, что сеть режет multicast-трафик.

Что проверить:

1. Оба устройства действительно в одной подсети
2. Нет ли изоляции клиентов на роутере или точке доступа
3. Не подключено ли одно устройство через другую сеть или hotspot
4. Совпадает ли `ROS_DOMAIN_ID`

Если `ping` проходит, но `ros2 node list` не показывает удалённые узлы, проблема обычно уже в discovery ROS 2 или сетевой политике.
