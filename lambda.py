#function1
import json
import boto3
import base64
import io

s3 = boto3.client('s3')

def lambda_handler(event,context):
    """A function to serialize target data from S3"""
    print(event)
    # Get the s3 address from the Step Function event input
    key = event["s3_key"]
    bucket = event["s3_bucket"]

    # Download the data from s3 to /tmp/image.png
    s3.download_file(bucket, key, "/tmp/image.png")

    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }




#function2
import json
import sagemaker
import base64
from sagemaker.serializers import IdentitySerializer
import boto3
import io


# Fill this in with the name of your deployed model
ENDPOINT = 'image-classification-2023-08-26-15-44-01-262'## TODO: fill in
runtime = boto3.client('runtime.sagemaker')

def lambda_handler(event, context):

    # Decode the image data
    print(event.keys())
    image = base64.b64decode(event['body']['image_data'])
    # Instantiate a Predictor
    inference = runtime.invoke_endpoint(EndpointName=ENDPOINT,
                                       ContentType='application/x-image',
                                       Body=image)
    
    # We return the data back to the Step Function 
    result = inference["Body"].read().decode()
    result_json = json.loads(result)
    event["body"]["inferences"] = result_json
    return {
        'statusCode': 200,
        'body': {
            'image_data': event["body"]['image_data'],
            's3_bucket': event["body"]['s3_bucket'],
            's3_key': event["body"]['s3_key'],
            'inferences': event["body"]['inferences']
        }
        
    }




#function3

import json


THRESHOLD = .91


def lambda_handler(event, context):

    # Grab the inferences from the event
    inferences = event['body']['inferences']

    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = any(i > THRESHOLD for i in inferences)

    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': {
            'image_data': event['body']['image_data'],
            's3_bucket': event['body']['s3_bucket'],
            's3_key': event['body']['s3_key'],
            'inferences': event['body']['inferences']
        }
    }