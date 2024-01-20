# Проект 8-го спринта

### Структура репозитория
Вложенные файлы в репозиторий будут использоваться для проверки и предоставления обратной связи по проекту. Поэтому постарайтесь публиковать ваше решение согласно установленной структуре — так будет проще соотнести задания с решениями.

Внутри `src` расположена папка:
- `/src/scripts`.

### Описание задачи

Агрегатор для доставки еды набирает популярность и вводит новую опцию — подписку. Она открывает для пользователей ряд возможностей, одна из которых — добавлять рестораны в избранное. Только тогда пользователю будут поступать уведомления о специальных акциях с ограниченным сроком действия. Систему, которая поможет реализовать это обновление, вам и нужно будет создать.
Благодаря обновлению рестораны смогут привлечь новую аудиторию, получить фидбэк на новые блюда и акции, продать профицит товара и увеличить продажи в непиковые часы. Акции длятся недолго, всего несколько часов, и часто бывают ситуативными, а значит, важно быстро доставить их кругу пользователей, у которых ресторан добавлен в избранное.  
Система работает так:
Ресторан отправляет через мобильное приложение акцию с ограниченным предложением. Например, такое: «Вот и новое блюдо — его нет в обычном меню. Дарим на него скидку 70% до 14:00! Нам важен каждый комментарий о новинке».
Сервис проверяет, у кого из пользователей ресторан находится в избранном списке.
Сервис формирует заготовки для push-уведомлений этим пользователям о временных акциях. Уведомления будут отправляться только пока действует акция.

### План проекта
Итак, задача — реализовать сервис. Схематично его работа будет выглядеть так:

![Project_plan](https://github.com/StaceyKuzmenko/de-project-sprint-8/blob/main/Project_plan.png)

### Схемы

1. Входная таблица данных (уже существует в базе данных 'de' в PostgreSQL)

```
-- DROP TABLE public.subscribers_restaurants;

CREATE TABLE public.subscribers_restaurants (
    id serial4 NOT NULL,
    client_id varchar NOT NULL,
    restaurant_id varchar NOT NULL,
    CONSTRAINT pk_id PRIMARY KEY (id)
);

-- Пример заполненных данных
id|client_id                           |restaurant_id                       |
--+------------------------------------+------------------------------------+
 1|223e4567-e89b-12d3-a456-426614174000|123e4567-e89b-12d3-a456-426614174000|
 2|323e4567-e89b-12d3-a456-426614174000|123e4567-e89b-12d3-a456-426614174000|
 3|423e4567-e89b-12d3-a456-426614174000|123e4567-e89b-12d3-a456-426614174000|
 4|523e4567-e89b-12d3-a456-426614174000|123e4567-e89b-12d3-a456-426614174000|
 5|623e4567-e89b-12d3-a456-426614174000|123e4567-e89b-12d3-a456-426614174000|
 6|723e4567-e89b-12d3-a456-426614174000|123e4567-e89b-12d3-a456-426614174000|
 7|823e4567-e89b-12d3-a456-426614174000|123e4567-e89b-12d3-a456-426614174000|
 8|923e4567-e89b-12d3-a456-426614174000|123e4567-e89b-12d3-a456-426614174001|
 9|023e4567-e89b-12d3-a456-426614174000|123e4567-e89b-12d3-a456-426614174000|
10|123e4567-e89b-12d3-a456-426614174000|123e4567-e89b-12d3-a456-426614174000|

```
2. Финальная таблица данных

```
-- Выходная таблица
-- DROP TABLE public.subscribers_feedback;

CREATE TABLE public.subscribers_feedback (
  id serial4 NOT NULL,
    restaurant_id text NOT NULL,
    adv_campaign_id text NOT NULL,
    adv_campaign_content text NOT NULL,
    adv_campaign_owner text NOT NULL,
    adv_campaign_owner_contact text NOT NULL,
    adv_campaign_datetime_start int8 NOT NULL,
    adv_campaign_datetime_end int8 NOT NULL,
    datetime_created int8 NOT NULL,
    client_id text NOT NULL,
    trigger_datetime_created int4 NOT NULL,
    feedback varchar NULL,
    CONSTRAINT id_pk PRIMARY KEY (id)
);

-- Пример заполненных данных
id|restaurant_id                       |adv_campaign_id                     |adv_campaign_content|adv_campaign_owner   |adv_campaign_owner_contact|adv_campaign_datetime_start|adv_campaign_datetime_end|datetime_created|client_id                           |trigger_datetime_created|feedback|
--+------------------------------------+------------------------------------+--------------------+---------------------+--------------------------+---------------------------+-------------------------+----------------+------------------------------------+------------------------+--------+
 1|123e4567-e89b-12d3-a456-426614174000|123e4567-e89b-12d3-a456-426614174003|first campaign      |Ivanov Ivan Ivanovich|iiivanov@restaurant.ru    |                 1659203516|               2659207116|      1659131516|223e4567-e89b-12d3-a456-426614174000|              1659304828|        |
 2|123e4567-e89b-12d3-a456-426614174000|123e4567-e89b-12d3-a456-426614174003|first campaign      |Ivanov Ivan Ivanovich|iiivanov@restaurant.ru    |                 1659203516|               2659207116|      1659131516|323e4567-e89b-12d3-a456-426614174000|              1659304828|        |
 3|123e4567-e89b-12d3-a456-426614174000|123e4567-e89b-12d3-a456-426614174003|first campaign      |Ivanov Ivan Ivanovich|iiivanov@restaurant.ru    |                 1659203516|               2659207116|      1659131516|423e4567-e89b-12d3-a456-426614174000|              1659304828|        |
 4|123e4567-e89b-12d3-a456-426614174000|123e4567-e89b-12d3-a456-426614174003|first campaign      |Ivanov Ivan Ivanovich|iiivanov@restaurant.ru    |                 1659203516|               2659207116|      1659131516|523e4567-e89b-12d3-a456-426614174000|              1659304828|        |
 5|123e4567-e89b-12d3-a456-426614174000|123e4567-e89b-12d3-a456-426614174003|first campaign      |Ivanov Ivan Ivanovich|iiivanov@restaurant.ru    |                 1659203516|               2659207116|      1659131516|623e4567-e89b-12d3-a456-426614174000|              1659304828|        |
 6|123e4567-e89b-12d3-a456-426614174000|123e4567-e89b-12d3-a456-426614174003|first campaign      |Ivanov Ivan Ivanovich|iiivanov@restaurant.ru    |                 1659203516|               2659207116|      1659131516|723e4567-e89b-12d3-a456-426614174000|              1659304828|        |
 7|123e4567-e89b-12d3-a456-426614174000|123e4567-e89b-12d3-a456-426614174003|first campaign      |Ivanov Ivan Ivanovich|iiivanov@restaurant.ru    |                 1659203516|               2659207116|      1659131516|823e4567-e89b-12d3-a456-426614174000|              1659304828|        |
 8|123e4567-e89b-12d3-a456-426614174000|123e4567-e89b-12d3-a456-426614174003|first campaign      |Ivanov Ivan Ivanovich|iiivanov@restaurant.ru    |                 1659203516|               2659207116|      1659131516|023e4567-e89b-12d3-a456-426614174000|              1659304828|        |
```

### Команды

```
# write topic
kafkacat -b rc1b-2erh7b35n4j4v869.mdb.yandexcloud.net:9091 \
-X security.protocol=SASL_SSL \
-X sasl.mechanisms=SCRAM-SHA-512 \
-X sasl.username="de-student" \
-X sasl.password="ltcneltyn" \
-X ssl.ca.location=/.ssh/CA.pem \
-t student.topic.cohort17.StaceyKuzmenko_in \
-K: \
-P
first_message:{"restaurant_id": "123e4567-e89b-12d3-a456-426614174000","adv_campaign_id": "123e4567-e89b-12d3-a456-426614174003","adv_campaign_content": "first campaign","adv_campaign_owner": "Ivanov Ivan Ivanovich","adv_campaign_owner_contact": "iiivanov@restaurant_id","adv_campaign_datetime_start": 1659203516,"adv_campaign_datetime_end": 2659207116,"datetime_created": 1659131516}
#ввести ctrl+D, чтобы отправить сообщение

# read topic
kafkacat -b rc1b-2erh7b35n4j4v869.mdb.yandexcloud.net:9091 \
-X security.protocol=SASL_SSL \
-X sasl.mechanisms=SCRAM-SHA-512 \
-X sasl.username="de-student" \
-X sasl.password="ltcneltyn" \
-X ssl.ca.location=/.ssh/CA.pem \
-t student.topic.cohort17.StaceyKuzmenko_out \
-C \
-o beginning
```


