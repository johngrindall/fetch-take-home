#Script To Access AQS SQS Queue
       
#Imports (And Dependency Install)
try:
	import boto3
	import json
	import hashlib
	import datetime
	import psycopg2
	import sys
except:
	import subprocess
	print("MISSING DEPENDENCIES, INSTALLING NOW")
	subprocess.run(["pip", "install", "-r", "requirements.txt"])
	print("DEPENDENCIES INSTALLED")

#Helper functions
def hash_value(value):
	"""
	Helper function to encode given value into hash
	
	"""
	sha256_value = hashlib.sha256()
	sha256_value.update(value.encode("utf-8"))
	return sha256_value.hexdigest()

def version_to_int(version):
	"""
	Helper function to convert a version num to an int for storage in DB

	"""
	return int(version.replace(".", ""))

#Read command line arg for deletion of SQS queue data
try:
	argv1 = sys.argv[1]
except:
	argv1 = "No Arg"

#Display help message if argv1 is "help"
if(argv1 == "help"):
	print("Usage: python3 AccessScript.py [options]")
	print("Options:")
	print("  help            Show This Help Message and Exit")
	print("  deleteSQS       Deletes SQS Messages Following Read")
	print("  SQSCount        Displays # of Messages in SQS Queue and Exit")
	print("	 clearDB         Clears PostgreSQL Table of All Rows")
	print("Example:")
	print("  python AccessScript.py deleteSQS")
	exit()

#Initialize postgreSQL database connection
database_name = "postgres"
user = "postgres"
password = "postgres"
host = "localhost"
port = "5432"
try:
	postgres_conn = psycopg2.connect(
		dbname=database_name,
		user=user,
		password=password,
		host=host,
		port=port,
	)
except:
	print("CANNOT CONNECT TO POSTGRESQL DATABASE")
	exit()

postgres_cursor = postgres_conn.cursor()

#Clear postgreSQL database if argv1 is "clearDB"
if(argv1 == "clearDB"):
	delete_query = "DELETE FROM user_logins;"
	postgres_cursor.execute(delete_query)
	postgres_conn.commit()
	postgres_cursor.close()
	postgres_conn.close()
	exit()

#Set credentials for SQS queue
sqs_queue_name = "fetch-localstack-1"
sqs_region_name = "us-east-1" #May need to change based on AWS region
sqs_endpoint_url = "http://localhost:4566/000000000000/login-queue"

#Initialize boto3 client to connect to SQS queue
try:
	sqs_boto3_client = boto3.client(
		'sqs', 
		region_name=sqs_region_name, 
		endpoint_url=sqs_endpoint_url,
		aws_access_key_id='dummy',
	    aws_secret_access_key='dummy',
	    aws_session_token='dummy'
	)
except:
	print("CANNOT CONNECT TO SQS CLIENT")
	exit()

if(argv1 == "SQSCount"):
	# Get the queue attributes
	queue_attributes = sqs_boto3_client.get_queue_attributes(
	    QueueUrl=sqs_endpoint_url,
	    AttributeNames=['ApproximateNumberOfMessages']
	)
	approx_num_messages = int(queue_attributes['Attributes']['ApproximateNumberOfMessages'])
	print("NUMBER OF MSGS IN SQS QUEUE: " + str(approx_num_messages))
	exit()

#Recieve responses from the boto3 client and append hashed values to new array
try:
	sqs_response = sqs_boto3_client.receive_message(QueueUrl=sqs_endpoint_url, MaxNumberOfMessages=1000000)
	sqs_messages = sqs_response.get('Messages', [])
	current_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
	masked_sqs_messages = []
except:
	print("CANNOT CONNECT TO SQS CLIENT")
	exit()

for msg in sqs_messages:
	try:
		#Hash device id and ip
		ip_hash = hash_value(json.loads(msg["Body"])["ip"])
		id_hash = hash_value(json.loads(msg["Body"])["device_id"])

		#Generate new dict object and append to masked msg array
		new_dict_obj = {
			"user_id": json.loads(msg["Body"])["user_id"],
			"device_type": json.loads(msg["Body"])["device_type"],
			"masked_ip": ip_hash,
			"masked_device_id": id_hash,
			"locale": json.loads(msg["Body"])["locale"],
			"app_version": version_to_int(json.loads(msg["Body"])["app_version"]),
			"create_date": current_date
		}
		masked_sqs_messages.append(new_dict_obj)
		print("APPENDED USR LOGIN MSG: " + json.loads(msg["Body"])["user_id"])


		#Delete the current db message if the 1st command ln arg specifies
		if(argv1 == "deleteSQS"):
			sqs_boto3_client.delete_message(QueueUrl=sqs_endpoint_url, ReceiptHandle=msg["ReceiptHandle"])
			print("DELETED USR LOGIN MSG: " + json.loads(msg["Body"])["user_id"])
	except:
		print("DB ACCESS ERROR, TRY RUNNING AGAIN!")

#Loop through all processed SQS rows and insert into DB
insert_query = """
    INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
"""
for json_data in masked_sqs_messages:
	values_to_insert = (
	    json_data["user_id"],
	    json_data["device_type"],
	    json_data["masked_ip"],
	    json_data["masked_device_id"],
	    json_data["locale"],
	    json_data["app_version"],
	    json_data["create_date"]
	)

	#Execute and commit 
	postgres_cursor.execute(insert_query, values_to_insert)
	postgres_conn.commit()

# Close the cursor and connection for PostgreSQL/SQS Client
print("CLOSING CONNECTIONS")
postgres_cursor.close()
postgres_conn.close()
sqs_boto3_client.close()




