import logging
import boto3
import string
import random
#from utils import send_text_email

logger = logging.getLogger("fastapi")

COGNITO_POOL = 'us-east-2_vpCRfIvXD'
cognito_client = boto3.client(
    'cognito-idp',
    region_name='us-east-2',
    aws_access_key_id="AKIAJSZRUVGIPVVOPUGA",
    aws_secret_access_key="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",
)


def get_password():
    """Returns a random password"""
    length = 4
    # get random password pf length 8 with letters, digits, and symbols
    characters = string.ascii_letters + string.digits
    password = random.choice(string.ascii_uppercase) + random.choice(string.ascii_lowercase)
    password += ''.join(random.choice(characters) for i in range(length))
    password += random.choice(['#', '@', '$', '!', '%', '&'])
    password += random.choice(string.digits)
    return password


def send_password_email(email, password):
    try:
        # send password email to user
        logger.debug(f"Sending password email to {email}")
        recipient = email
        SENDER = 'team@joinnextmed.com'
        subject = 'NextMed Login Password'
        content = f"""
            Here is your login password: {password}"""

        send_text_email(sender=SENDER, recipient=recipient, subject=subject, content=content)
    except Exception as e:
        logger.exception(e)


def cognito_set_password(email, password):
    """Set password for account"""
    try:
        logger.debug(f"Setting password for {email}")
        response = cognito_client.admin_set_user_password(
            UserPoolId=COGNITO_POOL,
            Username=email,
            Password=password,
            Permanent=True
        )
        logger.debug(response)
    except Exception as e:
        logger.exception(e)


def cognito_mark_email_verified(email):
    try:
        logger.debug(f"Marking email: {email} as verified.")
        response = cognito_client.admin_update_user_attributes(
            UserPoolId=COGNITO_POOL,
            Username=email,
            UserAttributes=[
                {
                    'Name': 'email_verified',
                    'Value': 'true'
                },
            ]
        )
    except Exception as e:
        logger.exception(e)


def cognito_mark_email_phone_verified(email, phone):
    try:
        logger.debug(f"Marking email: {email} & phone: {phone} as verified.")
        response = cognito_client.admin_update_user_attributes(
            UserPoolId=COGNITO_POOL,
            Username=email,
            UserAttributes=[
                {
                    'Name': 'email_verified',
                    'Value': 'true'
                },
                {
                    'Name': 'phone_number_verified',
                    'Value': 'true'
                },
            ]
        )
    except Exception as e:
        logger.exception(e)


def cognito_signup_apple_pay_user(email, name, phone=None):
    k = get_password()
    user_attribs = [
        {
            'Name': 'email',
            'Value': email
        },
        {
            'Name': 'name',
            'Value': name
        },
    ]
    if phone != '' and phone is not None:
        user_attribs.append({
            'Name': 'phone_number',
            'Value': phone
        })
    try:
        logger.debug(f"Creating cognito apple pay user: {email}")
        response = cognito_client.admin_create_user(
            UserPoolId=COGNITO_POOL,
            Username=email,
            UserAttributes=user_attribs,
            TemporaryPassword=k,
            DesiredDeliveryMediums=[
                'EMAIL'
            ],
            MessageAction="SUPPRESS"
        )
        logger.debug(response)
    except Exception as e:
        logger.exception(e)
    try:
        response = cognito_client.admin_get_user(
            UserPoolId=COGNITO_POOL,
            Username=email
        )
        logger.debug(response)
        for UserAttribute in response.get('UserAttributes'):
            if UserAttribute['Name'] == 'phone_number':
                cognito_mark_email_phone_verified(email, phone)
                break
        else:
            cognito_mark_email_verified(email)
    except Exception as e:
        logger.exception(e)
    random_pass = get_password()
    try:
        logger.debug(f"Setting password for {email}")
        response = cognito_client.admin_set_user_password(
            UserPoolId=COGNITO_POOL,
            Username=email,
            Password=random_pass,
            Permanent=True
        )
        logger.debug(response)
        # send_password_email(email, random_pass)
    except Exception as e:
        logger.exception(e)
    return random_pass


def cognito_signup_patient(email, password=None, phone=None):
    k = get_password()
    user_attribs = [
        {
            'Name': 'email',
            'Value': email
        },
        {
            'Name': 'name',
            'Value': ''
        },
    ]
    if phone != '' and phone is not None:
        user_attribs.append({
            'Name': 'phone_number',
            'Value': phone
        })
    try:
        logger.debug(f"Creating cognito card pay user: {email}")
        response = cognito_client.admin_create_user(
            UserPoolId='us-east-2_vpCRfIvXD',
            Username=email,
            UserAttributes=user_attribs,
            TemporaryPassword=k,
            DesiredDeliveryMediums=[
                'EMAIL'
            ],
            MessageAction="SUPPRESS"
        )
        logger.debug(response)
    except Exception as e:
        logger.exception(e)

    try:
        response = cognito_client.admin_get_user(
            UserPoolId=COGNITO_POOL,
            Username=email
        )
        logger.debug(response)
        for UserAttribute in response.get('UserAttributes'):
            if UserAttribute['Name'] == 'phone_number':
                cognito_mark_email_phone_verified(email, phone)
                break
        else:
            cognito_mark_email_verified(email)
    except Exception as e:
        logger.exception(e)
    if password is None or password == '':
        password = get_password()
    cognito_set_password(email, password)

    return password


def signup_user(email, name):
    response = cognito_client.admin_create_user(
        UserPoolId='us-east-2_WMP1mBeSc',
        Username=email,
        UserAttributes=[
            {
                'Name': 'email',
                'Value': email
            },
            {
                'Name': 'name',
                'Value': name
            },

        ],

        TemporaryPassword="Password1!",
        DesiredDeliveryMediums=[
            'EMAIL'
        ],
    )


def confirm_signup(email):
    try:
        logger.debug(f"Confirming signup: {email}")
        response = cognito_client.admin_confirm_sign_up(
            UserPoolId='us-east-2_vpCRfIvXD',
            Username=email,
        )
        return {"status": "success"}
    except Exception as e:
        logger.exception(e)


def resend_temp_password(email, name):
    try:
        response1 = cognito_client.admin_delete_user(
            UserPoolId='us-east-2_vpCRfIvXD',
            Username=email,
        )
    except:
        print("")
    k = get_password()
    response = cognito_client.admin_create_user(
        UserPoolId='us-east-2_vpCRfIvXD',
        Username=email,
        UserAttributes=[
            {
                'Name': 'email',
                'Value': email
            },
            {
                'Name': 'name',
                'Value': name
            },

        ],

        TemporaryPassword=k,
        DesiredDeliveryMediums=[
            'EMAIL'
        ],
    )
    return k


def cognito_get_user_email(cognito_id: str):
    """Fetch email id from cognito pool using username"""
    try:
        response = cognito_client.admin_get_user(
            UserPoolId=COGNITO_POOL,
            Username=cognito_id
        )
        for attr in response.get('UserAttributes', []):
            if attr.get('Name') == 'email':
                return attr.get('Value')
    except Exception as e:
        logger.exception(e)
    return None


def cognito_upload_image(email, url):
    try:
        response = cognito_client.admin_update_user_attributes(
            UserPoolId='us-east-2_vpCRfIvXD',
            Username=email,
            UserAttributes=[
                {
                    'Name': 'picture',
                    'Value': url
                },
            ],
        )
        logger.debug(response)
    except Exception as e:
        logger.exception(e)
        return False
    return True


def cognito_change_email(email, new_email):
    """change user email in cognito"""
    try:
        response = cognito_client.admin_get_user(
            UserPoolId=COGNITO_POOL,
            Username=email
        )
        logger.debug(response)
        username = response.get('Username')

        logger.info(f"changing {email} to {new_email} in cognito...")

        response = cognito_client.admin_update_user_attributes(
            UserPoolId=COGNITO_POOL,
            Username=username,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': new_email
                },
            ]
        )

        cognito_mark_email_verified(new_email)

    except Exception as e:
        logger.exception(e)


if __name__ == '__main__':
    cognito_change_email('xenum4u@gmail.com', 'urstealth@gmail.com')
