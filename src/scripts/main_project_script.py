import os
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, LongType
from config_file import kafka_security_options, docker_postgresql_settings, postgresql_settings, spark_jars_packages, TOPIC_IN, TOPIC_OUT
from kafka.errors import KafkaError

# текущее время в миллисекундах
current_timestamp_utc = int(round(datetime.utcnow().timestamp()))

# запись в PostgreSQL (Docker) и в Kafka
def foreach_batch_function(df):
    df.persist()

    # Добавляем пустое поле 'feedback'
    feedback_df = df.withColumn('feedback', F.lit(None).cast(StringType()))

    # отправка в PostgreSQL
    feedback_df.write \
              .format('jdbc') \
              .mode('append') \
              .options(**docker_postgresql_settings) \
              .save()

    # сериализация для Kafka
    df_to_stream = (feedback_df
                    .select(F.to_json(F.struct(F.col('*'))).alias('value'))
                    .select('value')
                    )

    # отправка в Kafka
    df_to_stream.write \
                .format('kafka') \
                .options(**kafka_security_options) \
                .option('topic', TOPIC_OUT) \
                .option('truncate', False) \
                .save()

    # очищаем память от df
    df.unpersist()

def spark_init(Spark_Session_Name) -> SparkSession:
    return (SparkSession
            .builder
            .appName({Spark_Session_Name})
            .config("spark.jars.packages", spark_jars_packages)
            .config("spark.sql.session.timeZone", "UTC") 
            .getOrCreate()
    )
    
def restaurant_read_stream(spark):
    df = spark.readStream \
            .format('kafka') \
            .options(**kafka_security_options) \
            .option('subscribe', TOPIC_IN) \
            .load()

    df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
        .writeStream \
        .format("console") \
        .outputMode("append") \
        .start() \
        .awaitTermination()

    df_json = df.withColumn('key_str', F.col('key').cast(StringType())) \
            .withColumn('value_json', F.col('value').cast(StringType())) \
            .drop('key', 'value')

    # определяем схему входного сообщения для json
    incoming_message_schema = StructType([
        StructField('restaurant_id', StringType(), nullable=True),
        StructField('adv_campaign_id', StringType(), nullable=True),
        StructField('adv_campaign_content', StringType(), nullable=True),
        StructField('adv_campaign_owner', StringType(), nullable=True),
        StructField('adv_campaign_owner_contact', StringType(), nullable=True),
        StructField('adv_campaign_datetime_start', LongType(), nullable=True),
        StructField('adv_campaign_datetime_end', LongType(), nullable=True),
        StructField('datetime_created', LongType(), nullable=True)
        ])

    # десериализуем из value и фильтруем по времени
    df_string = df_json \
        .withColumn('key', F.col('key_str')) \
        .withColumn('value', F.from_json(F.col('value_json'), incoming_message_schema))

    df_filtered = df_string.select(
        F.col('value.restaurant_id').cast(StringType()).alias('restaurant_id'),
        F.col('value.adv_campaign_id').cast(StringType()).alias('adv_campaign_id'),
        F.col('value.adv_campaign_content').cast(StringType()).alias('adv_campaign_content'),
        F.col('value.adv_campaign_owner').cast(StringType()).alias('adv_campaign_owner'),
        F.col('value.adv_campaign_owner_contact').cast(StringType()).alias('adv_campaign_owner_contact'),
        F.col('value.adv_campaign_datetime_start').cast(LongType()).alias('adv_campaign_datetime_start'),
        F.col('value.adv_campaign_datetime_end').cast(LongType()).alias('adv_campaign_datetime_end'),
        F.col('value.datetime_created').cast(LongType()).alias('datetime_created'),
    ) \
        .filter((F.col('adv_campaign_datetime_start') <= current_timestamp_utc) & (
                F.col('adv_campaign_datetime_end') > current_timestamp_utc))
    return df_filtered

# вычитываем всех пользователей с подпиской на рестораны
def subscribers_restaurants(spark):
    df = spark.read \
        .format('jdbc') \
        .options(**postgresql_settings) \
        .load()
    df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
        .writeStream \
        .format("console") \
        .outputMode("append") \
        .start() \
        .awaitTermination()
    df = df.dropDuplicates(['client_id', 'restaurant_id'])
    return df

# объединяем датасеты
def join(restaurant_read_stream_df, subscribers_restaurant_df):
    df = restaurant_read_stream_df \
        .join(subscribers_restaurant_df, 'restaurant_id') \
        .withColumn('trigger_datetime_created', F.lit(current_timestamp_utc)) \
        .select(
        'restaurant_id',
        'adv_campaign_id',
        'adv_campaign_content',
        'adv_campaign_owner',
        'adv_campaign_owner_contact',
        'adv_campaign_datetime_start',
        'adv_campaign_datetime_end',
        'datetime_created',
        'client_id',
        'trigger_datetime_created')
    return df

if __name__ == '__main__':
    spark = spark_init("RestaurantSubscribeStreamingService")
    print("\n Создаем сессию \n")
    spark.conf.set('spark.sql.streaming.checkpointLocation', 'test_query')
    print("\n Создаем чекпоинт локации\n")
    restaurant_read_stream_df = restaurant_read_stream(spark)
    print("\n Определяем акции ресторанов \n")
    subscribers_restaurant_df = subscribers_restaurants(spark)
    print("\n Определяем пользователей, у которых рестораны находятся в списке Избранное \n")
    result = join(restaurant_read_stream_df, subscribers_restaurant_df)
    print("\n Формируем списки пользователей для рассылки уведомлений \n")

    query = (result.writeStream \
        .foreachBatch(foreach_batch_function) \
        .start())
    try:
        query.awaitTermination()
    finally:
        query.stop()
