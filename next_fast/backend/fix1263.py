import pymysql
from drchrono import drchrono


def fetch_drchrono_id(email):
    p = {"email": email}
    res = drchrono.patients_list(params=p)
    if 'results' in res:
        results = res['results']
        if len(results) > 0:
            return results[0].get("id")
        else:
            return None
    else:
        return None


connection = pymysql.connect("nextmed-database.crkwdx8kqlsw.us-east-2.rds.amazonaws.com", user='admin',
                             passwd='password6969', db="nextmed")

cursor = connection.cursor(pymysql.cursors.DictCursor)

cursor.execute("select * from visits where  server_date_time like '%2022%'")

data = list(cursor.fetchall())


def update(email, pid):
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute(f'update visits set patient_id="{pid}" where email="{email}";')
    connection.commit()


for d in data:
    try:
        pid = fetch_drchrono_id(d['email'])
        print(d['email'], d['patient_id'], pid)

        if pid is not None:
            update(d['email'], pid)
            pass
    except Exception as e:
        print(e)
