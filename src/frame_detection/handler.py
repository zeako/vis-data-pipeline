import json
import os

import boto3

# lambda fails if any isn't provided
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']
SQS_SOURCE_URL = os.environ['SQS_SOURCE_URL']

rekognition = boto3.client('rekognition')
sns = boto3.client('sns')
sqs = boto3.client('sqs')


def publish(bucket, key):
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=json.dumps({
            'default': f'plant detected @ s3 object: {bucket}/{key}',
            'plantDetected': True,
            'bucket': bucket,
            'key': key
        }),
        MessageStructure='json'
    )



def lambda_handler(event, context):
    """process s3 ObjectCreated:Put events via SQS.
    runs them via Rekognition to identify if Plants exists in any of these s3 objects.
    for any s3 object where a plant was detected a message is published to sns

    Args:
        event: sqs event
        context: lambda context - unused
    """    
    entries = [{'Id': r['messageId'], 'ReceiptHandle': r['receiptHandle']}
               for r in event['Records']]

    s3_events = (json.loads(r['body']) for r in event['Records'])

    bucket_key_pairs = [(rs['s3']['bucket']['name'], rs['s3']['object']['key'])
                        for e in s3_events for rs in e['Records']]
    rekognition_images = (
        {
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        }
        for (bucket, key) in bucket_key_pairs
    )

    results = (
        rekognition.detect_labels(
            Image=image,
            MaxLabels=2
        )
        for image in rekognition_images
    )

    labels_list = ([labels['Name'] for labels in result['Labels']]
                   for result in results)

    for (bucket, key), labels in zip(bucket_key_pairs, labels_list):
        if 'Plant' in labels:
            publish(bucket, key)

    sqs.delete_message_batch(
        QueueUrl=SQS_SOURCE_URL,
        Entries=entries
    )
