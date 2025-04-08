import pyspark
from pyspark import SparkConf
from pyspark.sql import SparkSession
import clickhouse_connect
from pyspark.sql.functions import when, col, lit ,substring



#**********************************************Extract**************************************************************************
# spark configuration**********
conf = SparkConf() \
    .setMaster("local") \
    .setAppName("My App") \
    .set("spark.driver.memory", "40g") \
    .set("spark.executor.memory", "50g") \
    .set("spark.jars.packages",
         "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1,"
         "mysql:mysql-connector-java:8.0.33,"
        "com.clickhouse:clickhouse-jdbc:0.3.2-patch9")
# Create sparksession**********
spark = SparkSession.builder.config(conf=conf).getOrCreate()



# MongoDb connection***********
pipeline = '[{"$match": {"source": "lpr", "orientation": "EXIT"}}]'

mongo_df = spark.read \
    .format("com.mongodb.spark.sql.DefaultSource") \
    .option("uri", "mongodb://localhost:27017/lpr.enforcementlprs") \
    .option("pipeline", pipeline) \
    .load() \
    .select(
        "plate", "make", "model", "state", "entryLprDateTime", "lprDateTime", "zid"
    ).alias("mongo")



# Mysql connection*************
mysql_url = "jdbc:mysql://localhost:3306/booking_service"
mysql_props = {
    "user": "root",
    "password": "root12345",
    "driver": "com.mysql.cj.jdbc.Driver"
}

# reading data from booking  and zone table**************
table1_df = spark.read.jdbc(url=mysql_url, table="booking", properties=mysql_props).select(
    "zid", "plateOriginal", "entryTime", "exitTime", "totalAmount", "validatedAmount"
).alias("booking")
table2_df = spark.read.jdbc(url=mysql_url, table="zone", properties=mysql_props).select("zid", "zcode","name").alias("zone")

#verify data*****************
# display(mongo_df.limit(50).toPandas())
# display(table1_df.limit(50).toPandas())




#**********************************************Transform**************************************************************************

booking_zone_df = table1_df.join(
    table2_df,
    on="zid",
    how="inner"
).alias("booking_zone")

joined_df = booking_zone_df.join(
    mongo_df.alias("mongo"),
    (col("zcode") == col("mongo.zid")) &
    (col("plate") == col("mongo.plate")) &
    (substring(col("entryTime"), 1, 16) == substring(col("mongo.entryLprDateTime"), 1, 16)) &
    (substring(col("exitTime"), 1, 16) == substring(col("mongo.lprDateTime"), 1, 16)),
    how="inner"
).select(
    col("zcode").alias("Location Code"),
    col("name").alias("Location Name"),
    col("plate").alias("Plate"),
    col("mongo.make").alias("Make"),
    col("mongo.model").alias("Model"),
    col("mongo.state").alias("State"),
    col("mongo.entryLprDateTime").alias("Entry Time"),
    col("mongo.lprDateTime").alias("Exit Time"),
    when(col("totalAmount").isNull(), lit(0)).otherwise(col("totalAmount")).alias("Total Amount"),
    when(col("validatedAmount").isNull(), lit(0)).otherwise(col("validatedAmount")).alias("Validated Amount"),
)

joined_df.show(20, truncate=False)


#**********************************************Load**************************************************************************
#clickhouse connection*****************
client = clickhouse_connect.get_client(
    host='localhost',
    port=8123,
    username='default',
    password='',
    database='parker_demographics'
)

# Convert to Pandas
pandas_df = joined_df.toPandas()

# Insert into ClickHouse table
client.insert_df('merged_data', pandas_df)


# **********CSV genaration*****************

joined_df.coalesce(1).write.option("header", True).csv("output/final_data.csv")

