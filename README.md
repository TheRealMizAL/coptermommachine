# Coptermommachine Server - сервер средства защиты программного обеспечения от статического анализа
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-yellow.svg)](CHANGELOG.md)

## Установка и настройка

### Вариант 1: Настройка на базе готовой виртуальной машины
### Вариант 2: Настройка на базе исходников

1. **Скачайте** образ Alpine Linux с [официального сайта](https://alpinelinux.org/downloads/)
2. **Импортируйте** образ в гипервизор (VirtualBox/VMware)
3. **Запустите** и проведите базовую настройку образа с помощю встроенной утилиты ```setup-alpine```
4. **Перезагрузите** виртуальную машину. Убедитесь, что у вас есть подключение к Интернету
5. **Обновите** apk командой ```apk update && apk upgrade```
6. **Установите** git командой ```apk add git```
7. **Скачайте** код из репозиторий командой ```git clone https://github.com/TheRealMizAL/coptermommachine```
8. **Предоставьте** право использования скрипта командой ```chmod +x ./coptermommachine/scripts/setup_env.sh```
9. **Запустите** скрипт
10. В результате выполнения скрипта в систему **установятся** PostgreSQL и Docker в rootless режиме, будет произведена базовая настройка безопасности и включен файрволл
11. 

## Стандартные УЗ Linux

|Имя пользователя|Пароль|
|----------------|------|
|postgres|postgres|
|dockeruser|dockseruser|

## Станадртные УЗ PostgreSQL
|Имя пользователя|Пароль|
|----------------|------|
|oidc_admin|oidc_admin|
|oidc_service|oidc_service|
