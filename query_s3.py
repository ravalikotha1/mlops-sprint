import duckdb
import boto3

session = boto3.Session()
creds = session.get_credentials().get_frozen_credentials()

# In-memory DuckDB connection - no local database file needed
conn = duckdb.connect()
conn.execute(f"""
    SET s3_region='us-east-1';
    SET s3_access_key_id='{creds.access_key}';
    SET s3_secret_access_key='{creds.secret_key}';
""")

result = conn.execute("""
    SELECT
        json_extract_string(content, '$.timestamp') as timestamp,
        json_extract_string(content, '$.input.sepal_length') as sepal_length,
        json_extract_string(content, '$.output.prediction') as prediction,
        json_extract_string(content, '$.output.confidence') as confidence
    FROM read_text('s3://mlops-sprint-ravali/predictions/**/*.json')
""").fetchall()

for row in result:
    print(row)
