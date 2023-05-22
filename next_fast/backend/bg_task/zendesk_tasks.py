import logging
import stripe
from sqlalchemy.orm import Session
from config import STRIPE_API_KEY
from utils import send_text_message, send_text_email
from database.crud import OpenloopCapacityRepo, ZendeskNotifyCrud, VisitsCrud, QuestionCrud
from database.schemas import ZendeskNotifyBase
from database.db import get_db
from healthie import healthie
from api.freshdesk_api import fr_api
from mdintegrations import mdi_weightloss
from bg_tasks import DrChronoNewLabOrder, drchrono_send_new_lab_order
import usaddress
import datetime

logger = logging.getLogger("fastapi")
db: Session = next(get_db())
stripe.api_key = STRIPE_API_KEY


class ZendeskWebhookHandler:
    """class to handle Zendesk webhook payload"""
    def __init__(self, payload):
        self.payload = payload
        self.event_type = None
        self.email = None
        self.user = {}
        self.today = datetime.date.today()
        self.visit = {}

    @staticmethod
    def send_notifications(email: str, to_phone: str, message: str):
        """
        send text & email notifications
        name: receiver's name
        email: receiver's email
        to_phone: receiver's phone
        message_type: 'intake' or 'checkin'
        """
        subject = 'Your Action Needed'
        try:
            logging.debug(f"Sending text to {to_phone}")
            send_text_message(to_phone, message)
        except Exception as e:
            logging.exception(e)

        SENDER = 'team@joinnextmed.com'
        logging.debug(f"Sending email to {email}")
        send_text_email(sender=SENDER, recipient=email, subject=subject, content=message)

    def zendesk_handle_yes_eligible(self):
        """Handle eligible == yes_eligible"""
        # "schedule_first_visit" to 1
        self.zendesk_update_db_schedule_first_visit()

        # notify user
        self.zendesk_get_healthie_patient()
        message = f"Hi {self.user.get('first_name')}, good news! It's time to schedule your first NextMed visit! " \
                  f"Please login to your NextMed portal here to book your visit and get started: " \
                  f"www.joinnextmed.com/login. We can't wait to meet you!"

        # notify user
        self.send_notifications(email=self.user.get('email'),
                                to_phone=self.user.get('phone_number'),
                                message=message)
        # Set cron tasks for reminder
        self.zendesk_set_cron_tasks('schedule_visit')

    def zendesk_handle_red_capacity(self):
        """Handle eligible == no_eligible OR capacity == red"""
        self.zendesk_visit_completed_status_3()
        # try:
        #     email = self.payload.get('email')
        #     # fetch patient details
        #     self.zendesk_get_healthie_patient()
        #     VisitsCrud.update_visits_is_async_by_email(db, email, '1')
        #     healthie_create_task_data = {
        #         "user_id": "1627246",
        #         "content": None,
        #         "client_id": self.payload.get('patientId'),
        #         "due_date": datetime.date.today().strftime('%Y-%m-%d'),
        #         "remainder": {
        #             "is_enabled": True,
        #             "interval_type": "daily",
        #             "interval_value": "friday",
        #             "remove_reminder": True
        #         }
        #     }
        #     if self.payload.get('visit_completed', 0) == 1:
        #         healthie_create_task_data["content"] = "async_followup"
        #     else:
        #         healthie_create_task_data["content"] = "async_new"
        #     healthie.create_task(healthie_create_task_data)
        # except Exception as e:
        #     logging.exception(e)

    def zendesk_get_healthie_patient(self):
        try:
            patient_id = self.payload.get('patientId')
            # call healthie api to get patient details
            response = healthie.get_patient(patient_id)
            self.user = response.get('data', {}).get('user', {})
            self.email = self.user.get('email')
        except Exception as e:
            logger.exception(e)

    def zendesk_update_db_state_capacity(self):
        """Update state capacity"""
        try:
            state = self.payload.get('state')
            capacity = self.payload.get('capacity')

            # update state capacity to db
            logger.info(f"Updating OpenloopCapacity: {capacity} to {state}")
            if 'green' == capacity:
                capacity_val = 1
            else:
                capacity_val = 0
            OpenloopCapacityRepo.update_state_capacity(db, state, capacity_val)
        except Exception as e:
            logger.exception(e)

    def zendesk_update_db_elig_info(self):
        """ Update copay_amount, coinsurance_amount, eligibility_check & insurance_elig_checked, ccmEligible, ccmCopay,
            ccmCoinsurance, rpmEligible, rpmCopay, rpmCoinsurance
        """
        try:
            copay_amount = self.payload.get('copay')
            coinsurance_amount = self.payload.get('coinsurance')
            eligibility_check = self.payload.get('eligible')
            insurance_elig_checked = 1
            self.email = self.payload.get('email')
            ccmEligible = self.payload.get("ccmEligible")
            ccmCopay = self.payload.get("ccmCopay")
            ccmCoinsurance = self.payload.get("ccmCoinsurance")
            rpmEligible = self.payload.get("rpmEligible")
            rpmCopay = self.payload.get("rpmCopay")
            rpmCoinsurance = self.payload.get("rpmCoinsurance")


            logger.info("zendesk_tasks: email=" + str(self.email) + " copay_amount=" + str(copay_amount))

            if not copay_amount:
                copay_amount = 0

            if not coinsurance_amount:
                coinsurance_amount = 0

            # update above info to db
            logger.info(f"Updating Visits: insurance_elig_checked to 1 for {self.email}")
            VisitsCrud.update_visits_eligibility_check_by_email(
                db_session=db,
                email=self.email,
                copay_amount=int(copay_amount),
                coinsurance_amount=int(coinsurance_amount),
                eligibility_check=eligibility_check,
                insurance_elig_checked=insurance_elig_checked,
                ccmEligible=ccmEligible,
                ccmCopay=ccmCopay,
                ccmCoinsurance=ccmCoinsurance,
                rpmEligible=rpmEligible,
                rpmCopay=rpmCopay,
                rpmCoinsurance=rpmCoinsurance
            )
        except Exception as e:
            logger.exception(e)

    def zendesk_handle_eligibility_check(self):
        """Handle TYPE == elig_check"""
        eligible = self.payload.get('eligible')
        logger.info("zendesk_tasks: email=" + str(self.payload.get('email')) + " eligible=" + str(eligible))

        # update visits row
        self.zendesk_update_db_elig_info()
        # update openloop capacity
        self.zendesk_update_db_state_capacity()

        capacity = self.payload.get('capacity')
        # over capacity
        if 'red' == capacity or eligible == 'no_ineligible':
            self.zendesk_handle_red_capacity()
        # under capacity
        else:
            state_abbr = self.parse_user_address_to_get_state_abbreviation(self.user.get("patient_address", ""))
            healthie_available_days_data = {
                "provider_id": "1367722",
                "date_from_month": self.today.isoformat(),
                "licensed_in_state": state_abbr,
                "org_level": True
            }
            logger.info(f"zendesk_tasks: email={str(self.payload.get('email'))}healthie_available_days_data={healthie_available_days_data}")
            if state_abbr in ['MO', 'SC', 'AL']:
                self.zendesk_handle_red_capacity()
            else:
                healthie_available_Days = healthie.get_available_days_self_scheduling(healthie_available_days_data)
                if len(healthie_available_Days.get("data", {"daysAvailableForRange": []}).get("daysAvailableForRange")) > 0:
                    daysAvailableForRange = healthie_available_Days.\
                        get("data", {"daysAvailableForRange": []}).\
                        get("daysAvailableForRange")
                    for date in daysAvailableForRange:
                        margin = datetime.timedelta(days=7)
                        date_to_test = datetime.datetime.strptime(date, "%Y-%m-%d").date()
                        result = date_to_test > self.today and self.today - margin <= date_to_test <= self.today + margin
                        if result:
                            eligible = 'yes_eligible'
                            break
                        else:
                            eligible = 'no_ineligible'
                if 'yes_eligible' == eligible:
                    self.zendesk_handle_yes_eligible()
                elif 'no_ineligible' == eligible:
                    self.zendesk_handle_red_capacity()
                else:
                    logger.warning(f"Unknown eligible: {eligible}")

    def zendesk_set_cron_task(self, event, ts_now, hour, last_notify=False):
        """Create new cron to db"""
        try:
            td = datetime.timedelta(hours=hour)
            ts_future = ts_now + td
            logger.info(f"zendesk_set_cron_task: setting cron for email={self.user.get('email')} patient_id={self.payload.get('patientId')} phone={self.user.get('phone_number')}")
            cron = ZendeskNotifyBase(
                scheduled_ts=ts_future.strftime("%Y/%m/%d %H:%M:%S"),
                email=self.user.get('email'),
                patient_id=self.payload.get('patientId'),
                patient_name=self.user.get('first_name'),
                phone=self.user.get('phone_number'),
                event=event,
                last_notify=last_notify)
            ZendeskNotifyCrud.create(db, cron)
        except Exception as e:
            logger.error("zendesk_set_cron_task: error="+str(e))

    def zendesk_set_cron_tasks(self, event):
        """Add cron task for 4, 12, 48, 72 & 96 hours"""
        ts_now = datetime.datetime.now()
        for hour in [4, 12, 24, 48, 72]:
            self.zendesk_set_cron_task(event, ts_now, hour)

        self.zendesk_set_cron_task(event, ts_now, 96, last_notify=True)

    def zendesk_update_db_schedule_first_visit(self, value=1):
        """update "schedule_first_visit" to 1"""
        try:
            VisitsCrud.update_visits_schedule_first_visit_by_email(db, self.email, value)
        except Exception as e:
            logger.exception(e)

    def zendesk_update_db_visit_no_showed(self, value="1"):
        """update "visit_no_showed " to 1"""
        try:
            VisitsCrud.update_visits_visit_no_showed_by_email(db, self.email, value)
        except Exception as e:
            logger.exception(e)

    def zendesk_update_db_first_visit(self, value="1"):
        """update "first_visit " to 1"""
        try:
            VisitsCrud.update_visits_first_visit_by_email(db, self.email, value)
        except Exception as e:
            logger.exception(e)

    def zendesk_update_db_followup_visit(self, value="1"):
        """update "first_visit " to 1"""
        try:
            VisitsCrud.update_schedule_followup_visit_col_endpoint(db, self.email)
        except Exception as e:
            logger.exception(e)

    def zendesk_update_db_start_pa_process(self, value="1"):
        """update "start_pa_process" to 1"""
        try:
            VisitsCrud.update_visits_start_pa_process_by_email(db, self.email, value)
        except Exception as e:
            logger.exception(e)

    def zendesk_visit_completed_status_1(self):
        # set "first_visit" to 1
        self.zendesk_update_db_first_visit()
        self.zendesk_update_db_followup_visit()
        if self.visit.get('is_async', 0) != 1 and \
                self.payload.get('modality', '') != 'asynchronous':
            product_price = int(self.visit.get('copay_amount', 30)) if \
                str(self.visit.get('copay_amount', 0)).isdigit() else 30
            customer_id = self.visit.get('customer_id')
            try:
                # check if the openloop customer id is already set, it is does not create token and customer and charge
                if self.visit.get('openloop_customer_id') is None or self.visit.get('openloop_customer_id') == '':
                    response = stripe.Token.create(
                        customer=customer_id,
                        stripe_account='acct_1LN074RXS9KcuSST',
                    )
                    logger.info("zendesk_visit_completed_status_1: token_id=" + str(response.get('id')) + " card_id=" + str(response.get('card').get('id')))
                    token_id = response.get('id')
                    response = stripe.Customer.create(
                        source=token_id,
                        stripe_account='acct_1LN074RXS9KcuSST',
                        email=self.visit.get('email'),
                    )
                    logger.info("zendesk_visit_completed_status_1: email=" + str(self.email) + " id=" + str(response.get('id')) + " default_source=" + str(response.get('default_source')))
                    if response.get('id'):
                        try:
                            openloop_customer_id = response.get('id')
                            # update the openloop_customer_id in the database
                            res = VisitsCrud.update_visits_openloop_customer_id_by_email(
                                db_session=db,
                                email=self.email,
                                openloop_customer_id=openloop_customer_id
                            )
                            if not res:
                                logger.error("zendesk_visit_completed_status_1: update_visits_openloop_customer_id_by_email" )

                            # if the copay is not 0, charge the customer
                            # if product_price != 0:
                            openloop_customer_id = response.get('id')
                            response = stripe.PaymentIntent.create(
                                amount=100 * 30, # product_price,
                                currency="usd",
                                confirm=True,
                                customer=openloop_customer_id,
                                stripe_account='acct_1LN074RXS9KcuSST',
                                statement_descriptor_suffix='NXTMD Health Partners'
                            )
                            logger.info(f"Stripe created first copay charge for connected account: payment_intent=" + str(response.get('id')))
                        except Exception as e:
                            logger.error("zendesk_visit_completed_status_1: " + str(e))
                    else:
                        logger.error("zendesk_visit_completed_status_1: missing id for copay")
                
                # if the openloop_customer_id is already set, we just need to charge the customer copay
                else:
                    logger.info("zendesk_visit_completed_status_1: email=" + str(self.email) + " id=" + str(self.visit.get('openloop_customer_id')))
                    try:
                        if product_price != 0:
                            openloop_customer_id = self.visit.get('openloop_customer_id')
                            response = stripe.PaymentIntent.create(
                                amount=100 * 30, # product_price,
                                currency="usd",
                                confirm=True,
                                customer=openloop_customer_id,
                                stripe_account='acct_1LN074RXS9KcuSST',
                                statement_descriptor_suffix='NXTMD Health Partners'
                            )
                            logger.info(f"Stripe created copay charge for connected account: payment_intent=" + str(response.get('id')))
                    except Exception as e:
                        logger.error("zendesk_visit_completed_status_1: error=" + str(e))

            except Exception as e:
                logger.error("zendesk_visit_completed_status_1: error=" + str(e))
        # set "is_async" to 1
        if self.payload.get('modality', '') == 'asynchronous':
            VisitsCrud.update_visits_is_async_by_email(db, self.email, '1')
        # set "start_pa_process" to 1
        if self.payload.get('user_type', "") in ["GLP", "GLP-Complete"]:
            self.zendesk_update_db_start_pa_process()

    def zendesk_visit_completed_status_3(self):
        """patient not eligible for program. We need to move the patient to MDI.
        Need to set is_healthie = 0, create an MDI patient and insert the mdi patient ID for weight loss,
        and then if the user purchased contrave, you need to create a case in MDI for contrave.
        If the user purchased GLP do nothing. """
        try:
            # fetch patient details
            self.zendesk_get_healthie_patient()
            # set is_healthie = 0
            email = self.user.get('email')
            logger.info("zendesk_visit_completed_status_3: updating is_healthie -> 0 for email=" + str(email))
            VisitsCrud.update_visits_is_healthie_by_email(db, email, '0')
            phone_number = self.user.get('phone_number')
            # create mdi_weightloss patient
            visits = VisitsCrud.get_visits_row_by_email(db, email)
            if not visits:
                logger.warning(f"zendesk_visit_completed_status_3: No visit found for {email}")
                return
            # parse address
            patient_address = visits[0].get('patient_address')
            patient_address_list = patient_address.split(',')
            data = {
                "first_name": self.user.get('first_name'),
                "last_name": self.user.get('last_name'),
                "email": self.user.get('email'),
                "metadata": "",
                "gender": 2 if self.user.get('gender') == 'female' else 1,
                "phone_number": phone_number,
                "phone_type": 2,
                "date_of_birth": self.user.get('dob'),
                "address": {
                    "address": patient_address_list[0].strip(),
                    "zip_code": visits[0].get('zip_code'),
                    "city_name": patient_address_list[1].strip(),
                    "state_name": patient_address_list[2].strip()
                }
            }
            logger.info(f"zendesk_visit_completed_status_3: creating mdi weightloss patient where data={data}")
            res = mdi_weightloss.create_patient(data)
            if 'patient_id' in res:
                patient_id = res.get('patient_id')
                try:
                    VisitsCrud.update_visits_patient_id_md_by_email(db, email, patient_id)
                except Exception as e:
                    logger.exception("ZendeskWebhookHandler.zendesk_visit_completed_status_3 => " + str(e))

                # Add pharmacy NXTMD-632
                pharmacy_id = visits[0].get('pharmacy_id')
                logger.info(f"zendesk_visit_completed_status_3: Adding pharmacy={pharmacy_id} to patient={patient_id}")
                res = mdi_weightloss.add_pharmacy_to_patient(patient_id, pharmacy_id, set_as_primary=True)
                logger.debug(res)

                # create case if contrave
                if 'contrave' in visits[0].get('chief_complaint').lower():
                    db_questions = QuestionCrud.get_question_by_mrn(db, visits[0].get('mrn'))
                    questions = []
                    if db_questions:
                        for que in db_questions:
                            q = {
                                'question': que.get('questions'),
                                'answer': que.get('answer'),
                                'type': "string",
                                'important': True
                            }
                            questions.append(q)

                    data = {
                        'patient_id': patient_id,
                        'case_prescriptions': [
                            {
                                'partner_medication_id': 'a48873c4-5dbe-4e70-8ec0-4bb8ee1e90c1'
                            },
                            {
                                'partner_medication_id': '2d1e80bb-a988-44fd-bfa5-ca099d0cee78'
                            }
                        ]
                    }

                    if questions:
                        data['case_questions'] = questions

                    logger.info(f"zendesk_visit_completed_status_3: creating case with data={data}")
                    res = mdi_weightloss.create_case(data)
            else:
                logger.error(f"zendesk_visit_completed_status_3: No patient id found for email={email} after patient was created in MDI")
        except Exception as e:
            logger.exception("ZendeskWebhookHandler.zendesk_visit_completed_status_3 => " + str(e))

    def zendesk_visit_completed_status_4(self):
        """patient missing labs. Need to call create lab order ep for this patient for GLP Weight Loss standard labs.
        Test name: 'GLP-1 Weight Loss Program'. Need to send patient email and sms that they are missing labs and
        an order will be placed shortly, they can be tested as soon as a couple hours from now or tomorrow."""
        self.zendesk_get_healthie_patient()
        message = f"Hi {self.user.get('first_name')}, your provider is missing up to date lab testing. " \
                  f"We are placing an order for you now with Labcorp, and it will be ready within a couple of hours. " \
                  f"Feel free to go and get tested either later today or schedule an appointment with LabCorp. " \
                  f"Your lab form and scheduling instructions can be downloaded from your portal at " \
                  f"joinnextmed.com/login and is valid at any LabCorp location in the US."

        # notify user
        email = self.user.get('email')
        self.send_notifications(email=email,
                                to_phone=self.user.get('phone_number'),
                                message=message)
        visits = VisitsCrud.get_visits_row_by_email(db, email)
        if not visits:
            logger.error(f"zendesk_visit_completed_status_4: No visit found for {email}")
            return
        data = {
            'patient_id': visits[0].get('patient_id'),
            'patient_gender': self.user.get('gender'),
            'order_type': 'labcorp',
            'bill_to': 'insurance',
            'test_names': ['GLP-1 Weight Loss Program']
        }
        lab = DrChronoNewLabOrder(**data)
        drchrono_send_new_lab_order(lab)
        VisitsCrud.update_visits_is_second_lab_order_by_email(
            db_session=db,
            email=self.user.get('email'),
            is_second_lab_order=True
        )

    def zendesk_visit_completed_status_5(self):
        """patient chart missing other info. Need to create a fresh desk ticket """
        try:
            self.zendesk_get_healthie_patient()
            email = self.user.get('email')
            patient_name = self.user.get('first_name')
            healthie_id = self.payload.get('patientId')
            data = {
                'name': patient_name,
                'email': email,
                'status': 2,
                'priority': 1,
                'subject': 'PATIENT MISSING DATA FOR HEALTHIE',
                'description': f'Patient: {patient_name}, email: {email}, healthie_id: {healthie_id} needs missing data filled in! '
                               f'Please check their healthie profile and correct it ASAP.',
            }
            logger.info(f"creating freshdesk ticket: {data}")
            res = fr_api.create_ticket(data)
            logger.debug(res)
        except Exception as e:
            logger.exception("ZendeskWebhookHandler.zendesk_visit_completed_status_5 => " + str(e))

    def zendesk_handle_visit_status(self):
        """Handle TYPE == visit_status"""
        visit_status = self.payload.get('visitStatus')
        visits = VisitsCrud.get_visits_row_by_email(db, self.email)
        if len(visits) > 0:
            self.visit = visits[0]
        if 'visit_completed' == visit_status or 'visit_completed_status_1' == visit_status:
            self.zendesk_visit_completed_status_1()
        elif 'visit_completed_status_2' == visit_status:
            """patient on contrave or metformin. Keep logic same, but please change chief_complaint to 
            contrave program instead of glp because we are moving the patient to this program category. 
            Do not start the pa process. """
            self.zendesk_visit_completed_status_1()

            healthie_id = self.payload.get('patientId')

            VisitsCrud.update_visits_chief_complaint_by_healthie_id(
                db,
                healthie_id=healthie_id,
                chief_complaint='Contrave Weight Loss Program'
            )

        elif 'visit_completed_status_3' == visit_status:
            logger.info("zendesk_visit_completed_status_3: email=" + str(self.email))
            self.zendesk_visit_completed_status_3()

        elif 'visit_completed_status_4' == visit_status:
            self.zendesk_visit_completed_status_1()
            self.zendesk_visit_completed_status_4()

        elif 'visit_completed_status_5' == visit_status:
            self.zendesk_visit_completed_status_1()
            self.zendesk_visit_completed_status_5()

        elif 'visit_cancelled' == visit_status:
            # set "schedule_first_visit" to 1
            self.zendesk_update_db_schedule_first_visit()

            self.zendesk_get_healthie_patient()
            message = f"Hi {self.user.get('first_name')}, Your NextMed visit was cancelled. " \
                      f"You need to reschedule the visit as soon as possible from your NextMed portal. " \
                      f"Get started here: www.joinnextmed.com/login. Thanks!"

            # notify user
            self.send_notifications(email=self.user.get('email'),
                                    to_phone=self.user.get('phone_number'),
                                    message=message)
            # Set cron tasks for reminder
            self.zendesk_set_cron_tasks(visit_status)

        elif 'visit_noshow' == visit_status:
            # set visit_no_showed to 1
            self.zendesk_update_db_visit_no_showed()
            # set "schedule_first_visit" to 1
            self.zendesk_update_db_schedule_first_visit()
            # notify user
            self.zendesk_get_healthie_patient()
            message = f"Hi {self.user.get('first_name')}, Your NextMed visit was cancelled. " \
                      f"You need to reschedule the visit as soon as possible from your NextMed portal. " \
                      f"Get started here: www.joinnextmed.com/login. If you do not reschedule your visit, " \
                      f"you will be charged a $99 visit no-show fee. We are trying to help you reschedule. " \
                      f"If you have any questions please contact team@joinnextmed.com. Thanks!"
            self.send_notifications(email=self.user.get('email'),
                                    to_phone=self.user.get('phone_number'),
                                    message=message)
            # Set cron tasks for reminder
            self.zendesk_set_cron_tasks(visit_status)
        else:
            logger.warning(f"Unknown visitStatus: {visit_status}")

    def zendesk_get_healthie_all_prescriptions(self):
        try:
            patient_id = self.payload.get('patientId')
            # call healthie api to get patient details
            response = healthie.get_all_prescriptions(patient_id)
            data = response.get('data', {}).get('prescriptions', [])
            logger.info(f'zendesk_handle_prescription_written: getting prescription data={data}')
            return data
        except Exception as e:
            logger.exception("zendesk_handle_prescription_written: error=" + str(e))
            return []

    @staticmethod
    def match_weight_medicine_type(product_name: str):
        """return weight_medicine_type type or None"""
        weight_medicine_type_list = ['ozempic', 'wegovy', 'mounjaro', 'rybelsus', 'saxenda', 'trulicity', 'victoza',
                                     'metformin']
        semaglutide_in_product_name = {
            '0.25': 'ozempic',
            '0.5': 'wegovy',
            '0.6': 'saxenda',
            '1.2': 'victoza',
            '3': 'rybelsus',
        }
        product_name = product_name.lower()

        if 'bupropion' in product_name or 'natrexone' in product_name:
            return 'contrave'

        for med in weight_medicine_type_list:
            if med in product_name:
                return med

        if 'semaglutide' in product_name:
            for key, val in semaglutide_in_product_name.items():
                if key in product_name:
                    return val
        return None

    def zendesk_handle_prescription_written(self):
        """Handle TYPE == erx"""
        self.zendesk_get_healthie_patient()
        logger.info('zendesk_handle_prescription_written: handling type erx...')
        prescriptions = self.zendesk_get_healthie_all_prescriptions()

        message = f"Hi {self.user.get('first_name')}, a new prescription has been ordered to your pharmacy. " \
                  f"Please call your chosen pharmacy to see when it will be ready before going to pick it up. " \
                  f"This process could take a few hours. Thanks!"

        # notify user
        self.send_notifications(email=self.user.get('email'),
                                to_phone=self.user.get('phone_number'),
                                message=message)
        if not prescriptions:
            logger.warning(f"No prescriptions found for {self.user.get('email')}, {self.payload.get('patientId')}")
            return

        for erx in prescriptions.reverse():
            product_name = erx.get('product_name', '')
            weight_medicine_type = self.match_weight_medicine_type(product_name)
            if weight_medicine_type:
                VisitsCrud.update_visits_weight_medicine_type_by_healthie_id(
                    db,
                    self.payload.get('patientId'),
                    weight_medicine_type
                )
                break

    def zendesk_workflow(self):
        try:
            self.event_type = self.payload.get('type')
            logger.info("zendesk_tasks: email=" + str(self.payload.get('email')) + " type=" + str(self.event_type))

            if 'elig_check' == self.event_type:
                self.zendesk_handle_eligibility_check()
            elif 'visit_status' == self.event_type:
                self.zendesk_get_healthie_patient()
                self.zendesk_handle_visit_status()
            elif 'erx' == self.event_type:
                self.zendesk_handle_prescription_written()
            else:
                logger.warning(f"Unknown Type: {self.event_type}")

        except Exception as e:
            logger.exception("ZendeskWebhookHandler.workflow => " + str(e))

    def parse_user_address_to_get_state_abbreviation(self, patient_address):
        states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
                  'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
                  'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
                  'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
                  'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']

        location = usaddress.parse(patient_address)
        converted_data = dict(location)
        for key, value in converted_data.items():
            if value == "StateName" and key.upper() in states:
                return key
        return 'NY'

def zendesk_webhook_handle(data):
    """Handle different zendesk webhook events"""
    try:
        logger.debug(data)
        handler = ZendeskWebhookHandler(data)
        handler.zendesk_workflow()
    except Exception as e:
        logger.exception("zendesk_webhook_handle => " + str(e))
