from pyspark.sql import functions as F

NUM_COLS = 3
NUM_ROWS = 10**3

# create dataframe
df = spark.range(1, NUM_ROWS + 1)
new_columns = ["col" + ("000" + str(l))[-3:] for l in range(NUM_COLS)]
seed = 0
for col_name in new_columns:
    df = df.withColumn(col_name, F.rand(seed=seed))
    seed += 1

# write dataframe
df.write.mode("overwrite").parquet(
    root_path + "/bronze/table/"
)

# read dataframe twice
df1 = spark.read.parquet(
    root_path + "/bronze/table/"
)
df2 = spark.read.parquet(
    root_path + "/bronze/table/"
)

# make join
df_result = df1.join(df2, df1.id + df2.id == (NUM_ROWS + 1)).select(df1["*"])

# write results in delta format
df_result.write.format("delta").mode("overwrite").save(
    root_path + "/silver/table/"
)

df_result.limit(10).show()
