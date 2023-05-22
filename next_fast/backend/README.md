# Next-Medical Backend API

## Run FastAPI as an ubuntu gunicorn service on aws instance

Install the service:

```commandline
sudo cp gunicorn.service /lib/systemd/system/

sudo ls /lib/systemd/system/gunicorn.service

sudo chmod 644 /lib/systemd/system/gunicorn.service

sudo systemctl daemon-reload

sudo systemctl enable gunicorn.service
```

To start the service:
```commandline
sudo systemctl start gunicorn.service
```

To stop the service:
```commandline
sudo systemctl stop gunicorn.service
```

To restart the service:
```commandline
sudo systemctl restart gunicorn.service
```

To check the status of service:
```commandline
sudo systemctl status gunicorn.service
```

Install redis on ubuntu:
```commandline
sudo apt update
sudo apt install redis-server
```
> https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-20-04

To start redis service:
```commandline
sudo systemctl start redis
```

To check the status of redis service:
```commandline
sudo systemctl status redis
```

### FastAPI logs

Logs would be appended to file: `/var/log/next-med.log`

### Run using docker container

Build the docker image first
```shell
docker build -t next-medical-backend .
```

Run the docker container
```shell
docker run -it -p 5039:5039 -v ${PWD}:/backend -e AWS_ACCESS_KEY_ID={your_aws_access_key_id} -e AWS_SECRET_ACCESS_KEY={your_aws_secret_access_key} -e ENV=DEV next-medical-backend
```
#### Note: `ENV` can be `DEV` or `PROD`

Run the server locally
```shell
export ENV=
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
uvicorn main:app --reload
```

## Celery Service

Start Celery Process in a new terminal using the command below: 
```shell
export ENV=PROD
export IS_PROD=True
export PYTHONPATH=/home/ubuntu/Next-Medical
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export CELERY_WORKER_SERVICE_NAME='next-med-celery-service-live'
export CELERY_PRODUCER_SERVICE_NAME='next-med-celery-producer-live'
cd /home/ubuntu/Next-Medical/backend
pm2 --name=celery-service start 'celery -A celery_service.celery_service.CELERY_APP worker -P gevent --loglevel=DEBUG --autoscale=100,10 -E' --cron-restart="0 */2 * * *"
```

- Start Celery flower UI in a new terminal using the command below:
- Check celery process using celery flower on http://localhost:5566
```shell
pm2 --name=celery-flower start 'celery -A celery_service.celery_service.CELERY_APP flower --address=0.0.0.0 --port=5566 --basic_auth=nextmed:hWY2Vq7djKG7' --cron-restart="0 */2 * * *" 
```

To update a patient data using Celery, use the following example
```shell
curl --location --request POST \
'http://localhost:5039/update-patient-data' \
--header 'Content-Type: application/json' \
--data-raw '{
    "profile_data": {
        "patient_name": "Kaitlyn",
        "test_type": "weightloss",
        "pharmacy_ins_patient": ", , ",
        ....
    },
    "case_data": {
        "case_questions": [
            {
                "question": "Do you have any of the following?",
                "answer": "No",
                "type": "string",
                "important": false
            }
        ],
        "pharmacy_notes": "some random text",
        "case_prescriptions": [
            {
                "partner_medication_id": "a783r2387c2627868",
                "pharmacy_id": 4751
            }
        ],
        "subscription_id": "3894723896864786"
    },
    "md_data": {
        "first_name": "Kaitlyn",
        "last_name": "Hoffman",
        "email": "kaitlyn22@gmail.com",
        .....
    },
    "dr_chrono_data": {
        "doctor": 297491,
        "first_name": "Kaitlyn",
        "last_name": "Hoffman",
        .....
    },
    "dr_chrono_task_data": {
        "title": "Contrave Weight Loss Program-Patient Bill-f-lab_test_location",
        "status": 2,
        "assignee_user": 438633
    },
    "dr_chrono_appointment_data": {
        "date": "",
        "date_range": "",
        "doctor": 297491,
        ......
    },
    "ins_data": {
        "primary_insurance": {
            "insurance_company": " ",
            "insurance_id_number": "",
            "insurance_group_name": " ",
             ......
        },
        "secondary_insurance": {
            "insurance_company": " ",
            "insurance_id_number": "",
            "insurance_group_name": " ",
            .....
        },
        "tertiary_insurance": {
            "insurance_company": " ",
            "insurance_id_number": "",
            "insurance_group_name": " ",
            ......
        }
    },
    "email": "kaitlynhoffman5@gmail.com",
    "healthie_data": {
        "first_name": "Kaitlyn",
        "last_name": "Hoffman",
        "email": "kaitlyn5@gmail.com",
        "phone_number": "+177737193",
        "dont_send_welcome": true,
        "dietitian_id": "1513247"
    }
}'
```

The response will be something like
```json
{
  "task_id": "a29fbd9e-0fc5-4bc8-9a20-ae2708ccbe14"
}
```

Check the status of the celery task using:
```shell
curl --location --request POST \
'http://localhost:5039/celery-task-info' \
--header 'Content-Type: application/json' \
--data-raw '{
	"task_id": "a29fbd9e-0fc5-4bc8-9a20-ae2708ccbe14"
}'
```

The response will be something like this when the task is still in pending status:
```json
{
    "status": "PENDING",
    "result": null,
    "task_id": "a29fbd9e-0fc5-4bc8-9a20-ae2708ccbe15"
}
```

The response will be something like this when the task is completed:
```json
{
    "status": "SUCCESS",
    "result": {
        "status": "success",
        "md_id": "635988722", 
        "drchorno_id": "Y635H722", 
        "case_id": "775322",
        "mdintegration_patient_created": true, 
        "questions_created": true, 
        "mdintegration_case_created": true, 
        "drchrono_patient_created": true, 
        "drchrono_appointment_created": true, 
        "drchrono_task_created": true 
    },
    "task_id": "a29fbd9e-0fc5-4bc8-9a20-ae2708ccbe15"
}
```