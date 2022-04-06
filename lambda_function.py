#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: t.kogure
"""
import botocore
import boto3
import re
# import os
from logging import getLogger, StreamHandler, DEBUG

# ---------------------------------------------
# Set Logger
# ---------------------------------------------
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False
# ---------------------------------------------

sns = boto3.client('sns')


def lambda_handler(event, context):
    logger.debug(event)
    
    try:
        from_number = event['Details']['ContactData']['CustomerEndpoint']['Address']
    except KeyError as e:
        logger.error({
            'LogLevel': 'ERROR',
            'Message': 'The calling phone number is unknown'
        })
        raise KeyError(e)
    except Exception as e:
        logger.error(
            {
                'LogLevel': 'ERROR',
                'Message': "An exception error occurred while getting the caller's phone number",
                'Detail':str(e)
            }
            )
    else:
        if whether_mobile_phone_num(phone_number=from_number):
            publish_sns(
                phone_number=from_number,
                message="テストメッセージ"
            )
            return {
                'statusCode':200,
                'body':"All processing was completed normally"
            }
        else:
            return {
                'statusCode':400,
                'body':"Couldn't send SMS because it's not in the mobile phone number."
            }
    
    
def publish_sns(phone_number,sender_id='SMS',message=""):
    message_attributes = {
        'AWS.SNS.SMS.SenderID': {
            'DataType': 'String',
            'StringValue': sender_id
            }}

    try:
        res = sns.publish(
            PhoneNumber=phone_number,
            Message=message,
            MessageAttributes=message_attributes
        )
        logger.debug(res)
    except botocore.exceptions.ClientError as e:
        logger.error(
            {
                'LogLevel': 'ERROR',
                'Code':e.response['Error']['Code'],
                'Message': e.response['Error']['Message']
            }
            )
        raise e
    else:
        if res['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise PublishSNSError("Failed to send SNS. Check the log")
        else:
            logger.debug(
                {
                    'LogLevel': 'INFO',
                    'Message': "Succeeded in sending SNS (SMS). The process is complete.",
                }
                )
                
def whether_mobile_phone_num(phone_number):
    pattern = '\+81[7-9]0\d{8}'
    return re.match(pattern,phone_number)
    
class PublishSNSError(Exception):
    """Failed to send to SNS"""
    pass

# class WrongPhoneNumberError(Exception):
#     """Phone number is not a mobile phone number"""
#     pass