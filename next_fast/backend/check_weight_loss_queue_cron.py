from db_client import DBClient
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from mdintegrations import mdintegrations_api

def check_weight_loss_queue_entry():
    try:
        client = DBClient()
        # Get all the weight loss entries that are pending
        data = client.get_weight_loss_queues()

        # wagovy refill details from csv
        wagovy_case_detail =[
            {
                "case_number": "0.25mg",
                "partner_medication_id": "8eb34cbb-8ae6-48db-83ff-2bc94e5c398f"
            },
            {
                "case_number": "0.5mg",
                "partner_medication_id": "739f3eb1-c97e-4b3c-b7ad-8cc15f468c1f"
            },
            {
                "case_number": "1mg",
                "partner_medication_id": "a68ad0e7-5756-4a16-ad7c-1e28a6d5833e"
            },
            {
                "case_number": "1.7mg",
                "partner_medication_id": "47c9e187-7e40-4231-b794-2299dfc5d4c3"
            },
            {
                "case_number": "2.4mg",
                "partner_medication_id": "9cadb333-8c6e-4720-a4e4-f7d28b05b5a6"
            }
        ]

        # ozempic refill details from csv
        ozempic_case_detail =[
            {
                "case_number": "0.5mg",
                "partner_medication_id": "5c3f174f-2d5b-49b8-830a-48dc6a69ad7"
            }
        ]

        # today date time
        now = datetime.datetime.now()
        for i in data:
            
            day_count = (now - i["last_refill_date"]).days

            # if day count is greater than equal to 28 days
            if day_count >= 28:
                i["order_count"] += 1

                # updating the last refill date and order count
                client.update_weight_loss_queues(now , i["order_count"], i["id"])
                
                # md integration create case request
                # case question array
                question = [{
                    "question":  i["brand_name"].capitalize()+" refill #" + str(i["order_count"]), 
                    "type": "string", 
                    "important": True
                }]

                # get partner medication id from csv with refill number
                if i["brand_name"] == "wagovy":
                    partner_medication_id = wagovy_case_detail[(i["order_count"] - 1)].get("partner_medication_id")
                else:
                    partner_medication_id = ozempic_case_detail[(i["order_count"] - 1)].get("partner_medication_id")
                
                # payload for case request
                case_payload = {
                    "patient_id": i["patient_id_md"], 
                    "case_questions": question, 
                    "case_prescriptions": [{"partner_medication_id": partner_medication_id}]
                }

                mdintegrations_api.create_case(case_payload)

            # if frequency and order_count match, then delete the entry from the queue
            if i["frequency"] == i["order_count"]:
                client.delete_weight_loss_queue_entry(i["id"])
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

print("STARTING JOB")
sched = BlockingScheduler({'apscheduler.timezone': 'EST'})
sched.add_job(check_weight_loss_queue_entry, 'cron',hour=0, minute=0)
sched.start()

