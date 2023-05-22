import pymysql
import boto3

COGNITO_POOL = 'us-east-2_vpCRfIvXD'
cognito_client = boto3.client(
    'cognito-idp',
    region_name='us-east-2',
    aws_access_key_id="AKIAJSZRUVGIPVVOPUGA",
    aws_secret_access_key="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",
)

connection = pymysql.connect("nextmed-database.crkwdx8kqlsw.us-east-2.rds.amazonaws.com", user='admin',
                             passwd='password6969', db="nextmed")

cursor = connection.cursor(pymysql.cursors.DictCursor)

cursor.execute("select DISTINCT email, phone from nextmed.visits where server_date_time like '%/03/2022%'")

data = list(cursor.fetchall())


def update_number(email, phone):
    response = cognito_client.admin_update_user_attributes(
        UserPoolId=COGNITO_POOL,
        Username=email,
        UserAttributes=[
            {
                'Name': 'phone_number',
                'Value': phone
            },
        ]
    )
    response = cognito_client.admin_update_user_attributes(
        UserPoolId=COGNITO_POOL,
        Username=email,
        UserAttributes=[
            {
                'Name': 'phone_number_verified',
                'Value': 'true'
            },
        ]
    )


def get_user_phone(email):
    if email is None:
        return 1
    response = cognito_client.admin_get_user(
        UserPoolId=COGNITO_POOL,
        Username=email
    )
    for UserAttribute in response.get('UserAttributes'):
        if UserAttribute['Name'] == 'phone_number':
            return UserAttribute['Value']
    return None


#print(get_user_phone('xenum4u@gmail.com'))
for d in data:
    try:
        email = d['email'].strip()
        cognito_phone = get_user_phone(email)
        if cognito_phone is not None:
            continue
        print("updating", d)
        if d['phone'] != '' and d['phone'] is not None:
            if d['phone'].startswith('1'):
                phone = f"+{d['phone']}"
            elif not d['phone'].startswith('+1'):
                phone = f"+1{d['phone']}"
            else:
                phone = d['phone']
            update_number(email, phone)
        else:
            print('not updating for', d['email'])
    except Exception as e:
        print(d)
        print(e)
