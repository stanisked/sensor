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
