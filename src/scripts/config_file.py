# опции безопасности Кафки
kafka_security_options = {
    'kafka.security.protocol': 'SASL_SSL',
    'kafka.sasl.mechanism': 'SCRAM-SHA-512',
    'kafka.sasl.jaas.config': f'org.apache.kafka.common.security.scram.ScramLoginModule required username=\"de-student\" password=\"ltcneltyn\";',
    'kafka.bootstrap.servers': 'rc1b-2erh7b35n4j4v869.mdb.yandexcloud.net:9091',
}

# библиотеки для интеграции Spark с Kafka и PostgreSQL
spark_jars_packages = ",".join(
    [
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0",
        "org.postgresql:postgresql:42.4.0",
    ]
)

# параметры подключения к БД PostgreSQl в докере (на локальном сервере)
docker_postgresql_settings = {
    'user': 'jovyan',
    'password': 'jovyan',
    'url': f'jdbc:postgresql://localhost:5432/postgres',
    'driver': 'org.postgresql.Driver',
    'dbtable': 'public.create_subscribers_feedback',
}

# параметры подключения к БД PostgreSQL в облачном сервисе
postgresql_settings = {
    'user': 'student',
    'password': 'de-student',
    'url': f'jdbc:postgresql://rc1a-fswjkpli01zafgjm.mdb.yandexcloud.net:6432/de',
    'driver': 'org.postgresql.Driver',
    'dbtable': 'subscribers_restaurants',
}

TOPIC_IN = 'student.topic.cohort17.StaceyKuzmenko_in'
TOPIC_OUT = 'student.topic.cohort17.StaceyKuzmenko_out'
