import logging
from stripe_api import get_subscription, update_subscription, get_product, fetch_payment_intent
from mdintegrations import mdintegrations_api, mdintegrations_chat
from curexa import curexa
from db_client import DBClient
from api.klaviyo_api import klaviyo_track_profile, stripe_subscription_payment_failed
from bg_tasks import DrChronoNewLabOrder, drchrono_send_new_lab_order
from datetime import datetime
from fastapi import Depends
from sqlalchemy_db import get_db
from sqlalchemy.orm import Session
from models.failed_subscriptions import FailedSubscriptions

logger = logging.getLogger("fastapi")


class StripeInvoiceHandler:

    def __init__(self, invoice):
        self.invoice = invoice
        self.subscription_id = invoice['subscription']
        self.subscription = {}
        self.product = None
        self.item_type = None
        self.maximum_refills = 0
        self.visits = []
        self.visit = {}

    def _fetch_stripe_subscription_(self):
        """Fetch stripe subscription refill count"""
        try:
            if self.subscription_id is None:
                logger.warning(f"Not valid stripe subscription: {self.subscription_id}")
                return
            self.subscription = get_subscription(self.subscription_id)

        except Exception as e:
            logger.exception(e)

    def _get_stripe_subscription_refills_(self):
        """Fetch stripe subscription refill count"""

        refills_ordered = 0
        try:
            refills_ordered = self.subscription.get("metadata", {}).get("refills_ordered", 0)
        except Exception as e:
            logger.exception(e)
        return refills_ordered

    def _get_md_patient_id_(self):
        """Fetch md patient id"""
        patient_id_md = None
        try:
            patient_id_md = self.subscription.get("metadata", {}).get("patient_id_md")
        except Exception as e:
            logger.exception(e)
        return patient_id_md

    def _update_stripe_subscription_(self, case_id, refills_ordered):
        """Update stripe subscription for refill count & new case id"""
        try:
            if self.subscription_id is None:
                logger.warning(f"Not Updating stripe subscription: {self.subscription_id}")
                return

            logger.info(f"Updating stripe subscription: {self.subscription_id} with "
                        f"case_id: {case_id} & refills_ordered: {refills_ordered}")
            metadata = {
                "case_id": case_id,
                "refills_ordered": refills_ordered
            }
            update_subscription(self.subscription_id, metadata=metadata)

        except Exception as e:
            logger.exception(e)

    def _check_product_type_(self):
        product_dict = {
            # Herpes Medication
            'prod_LIX8hNl6g31vNM': 'curexa_Herpes',
            'prod_LIXB7Bnvzi2c8q': 'curexa_Herpes',
            'prod_KxooWZmNGbcC4p': 'curexa_Herpes',
            'prod_Ke0fQ1NomUhWNx': 'curexa_Herpes',
            'prod_Ke0fxliJCvn11N': 'curexa_Herpes',
            'prod_Ke0PKDnHAWLaCY': 'curexa_Herpes'
        }
        try:
            medication_type = self.subscription.get("metadata", {}).get("medication")
        except Exception as e:
            logger.exception(e)
        if medication_type == 'wegovy':
            self.product = 'Wegovy'
            self.maximum_refills = 5
            self.item_type = "weightloss"
        elif medication_type == 'ozempic':
            self.product = 'Ozempic'
            self.maximum_refills = 10
            self.item_type = "weightloss"
        elif medication_type == 'saxenda':
            self.product = 'Saxenda'
            self.maximum_refills = 10
            self.item_type = "weightloss"
        elif medication_type == 'rybelsus':
            self.product = 'Rybelsus'
            self.maximum_refills = 10
            self.item_type = "weightloss"
        else:
            self.product = product_dict.get(self.subscription['plan']['product'])
            self.item_type = "Curexa"
            # test subscription
            if self.product is None:
                try:
                    product = get_product(self.subscription['plan']['product'])
                    self.product = product.get("name")
                    self.item_type = "Test"
                except Exception as e:
                    logger.exception(e)

        logger.info(f"stripe subscription: {self.subscription_id} for {self.product}")

    def _get_md_clinician_id_(self):
        """Fetch md clinician id"""

        clinician_id = None
        try:
            case_id = self.subscription.get("metadata", {}).get("case_id")
            case = mdintegrations_api.get_case(case_id)
            clinician_id = case['case_assignment']['clinician']['clinician_id']

        except Exception as e:
            logger.exception(e)
        return clinician_id

    def _get_pharmacy_id_(self):
        patient_id_md = self._get_md_patient_id_()
        try:
            pharmacies = mdintegrations_api.get_patient_pharmacies(patient_id_md)
            for pharmacy in pharmacies:
                if pharmacy.get("is_preferred") is True:
                    return pharmacy.get("id")
            else:
                if len(pharmacies) > 0:
                    return pharmacies[0].get("id")
        except Exception as e:
            logger.exception(e)
        return None

    def create_mdi_case(self):
        medication = {
            'Saxenda': {
                2: {
                    "case_number": "3mg",
                    "partner_medication_id": "5aced861-ead6-49ed-9ecc-893c649919a3"
                }
            },
            'Rybelsus': {
                2: {
                    "case_number": "7mg",
                    "partner_medication_id": "2170e453-ae7d-4add-8f60-2a04049753b1"
                }
            },
            'Ozempic': {
                2: {
                    "case_number": "0.5mg",
                    "partner_medication_id": "5c3f174f-2d5b-49b8-830a-48dc6a69ad7"
                }
            },
            'Wegovy': {
                2: {
                    "case_number": "0.5mg",
                    "partner_medication_id": "739f3eb1-c97e-4b3c-b7ad-8cc15f468c1f"
                },
                3: {
                    "case_number": "1mg",
                    "partner_medication_id": "a68ad0e7-5756-4a16-ad7c-1e28a6d5833e"
                },
                4: {
                    "case_number": "1.7mg",
                    "partner_medication_id": "47c9e187-7e40-4231-b794-2299dfc5d4c3"
                },
                5: {
                    "case_number": "2.4mg",
                    "partner_medication_id": "9cadb333-8c6e-4720-a4e4-f7d28b05b5a6"
                }
            }
        }
        # same refills for 3 to 10
        for i in range(3, 11):
            medication['Ozempic'][i] = medication['Ozempic'][2]
            medication['Rybelsus'][i] = medication['Rybelsus'][2]
            medication['Saxenda'][i] = medication['Saxenda'][2]

        current_refill_count = self._get_stripe_subscription_refills_() + 1

        # case question array
        question = [{
            "question": f"{self.product.capitalize()} refill #{current_refill_count}",
            "type": "string",
            "important": True
        }]

        prescription = {
            'partner_medication_id': medication[self.product][current_refill_count]["partner_medication_id"]
        }
        
        pharmacy_id = self._get_pharmacy_id_()
        if pharmacy_id is not None:
            prescription['pharmacy_id'] = pharmacy_id
            
        if self.product == 'Saxenda':
            needles = {'partner_compound_id': 'c207db8b-12a1-4eb3-8a6b-adb71602fd9b'}
            case_prescriptions = [prescription, needles]
        else:
            case_prescriptions = [prescription]
    
        case_payload = {
            "patient_id": self._get_md_patient_id_(),
            "case_questions": question,
            "case_prescriptions": case_prescriptions
        }

        clinician_id = self._get_md_clinician_id_()
        if clinician_id is not None:
            case_payload['clinician_id'] = clinician_id
        logger.debug(f"creating case on mdintegrations: {case_payload}")
        response = mdintegrations_api.create_case(case_payload)
        logger.debug(response)
        return response.get('case_id')

    def fetch_visits_row(self):
        db = DBClient()
        self.visits = db.get_visits_by_subscription_id(self.subscription_id)
        for visit in self.visits:
            email = visit.get("email")
            if email is not None and email != '':
                self.visit = visit
                break

    def trigger_klaviyo(self, refills=None):
        try:
            self.fetch_visits_row()

            for visit in self.visits:
                email = visit.get("email")
                if email is not None and email != '':
                    phone = visit.get("phone")
                    self.visit = visit
                    if visit.get("insurance").lower() != "no":
                        is_insurance = 1
                    else:
                        is_insurance = 0

                    klaviyo_track_profile(
                        event=f"{self.item_type} subscription renewal",
                        email=email,
                        item_name=self.product,
                        item_type=self.item_type,
                        item_value=self.invoice.get("amount_paid")/100,
                        is_insurance=is_insurance,
                        patient_name=visit.get("patient_name"),
                        patient_address=visit.get("patient_address"),
                        phone_number=phone,
                        refills=refills
                    )
                    break
            else:
                logger.warning(f"visits not found for {self.subscription_id} can't trigger klaviyo")
                return None
        except Exception as e:
            logger.exception(e)

    def order_refill_weight_loss(self):
        refills_ordered = self._get_stripe_subscription_refills_()

        if refills_ordered == 0:
            # assuming 1st order was already created from frontend
            refills_ordered = 1

        if refills_ordered >= self.maximum_refills:
            logger.info(
                f"Maximum refills: {refills_ordered} already fulfilled for {self.subscription_id} "
                f"product: {self.product}")
            return
        logger.info(
            f"Trying to create MDI case for {self.subscription_id} product: {self.product}")

        try:
            # create mdi case for refills
            case_id = self.create_mdi_case()
            if case_id is not None:
                # update refills to metadata
                refills_ordered = self._get_stripe_subscription_refills_()
                self._update_stripe_subscription_(case_id, refills_ordered + 1)
        except Exception as e:
            logger.exception(e)

    def _increment_refills_ordered_(self):
        """Update stripe subscription for refill count by 1"""
        try:
            if self.subscription_id is None:
                logger.warning(f"Not Updating stripe subscription: {self.subscription_id}")
                return
            refills_ordered = self._get_stripe_subscription_refills_() + 1
            logger.info(f"Updating stripe subscription: {self.subscription_id} with "
                        f"refills_ordered: {refills_ordered}")
            metadata = {
                "refills_ordered": refills_ordered
            }
            update_subscription(self.subscription_id, metadata=metadata)

        except Exception as e:
            logger.exception(e)

    def handle_curexa_order_not_found(self):
        patient_id_md = None
        db = DBClient()
        self.visits = db.get_visits_by_subscription_id(self.subscription_id)
        for visit in self.visits:
            patient_id_md = visit.get("patient_id_md")
            if patient_id_md is not None and patient_id_md != '':
                break
        else:
            logger.warning(f"patient_id_md not found for {self.subscription_id}")
            return None
        cases = mdintegrations_api.get_patient_cases(patient_id_md)

        for case in cases.get("data", []):
            if len(case['case_questions']) > 0 and len(case['case_prescriptions']) > 0:
                for que in case['case_questions']:
                    if que.get('question') == 'MEDICATION' and que.get('answer') == 'MEDICINE REQUESTED':
                        return mdintegrations_chat.send_curexa_order(case['case_id'], self.subscription_id)
        return None

    def order_refill_curexa(self):
        logger.info(
            f"Trying to order curexa for {self.subscription_id} product: {self.product}")

        curexa_order = self.subscription.get("metadata", {}).get("order")
        if curexa_order is None:
            curexa_order = self.handle_curexa_order_not_found()
            if curexa_order is None:
                logger.warning(f"For {self.subscription_id}, Curexa Order not found!")
            return
        order_id = curexa_order.get("order_id")
        res = curexa.create_order(curexa_order)
        logger.debug(res)
        res = curexa.order_status(order_id=order_id)
        logger.debug(res)
        if 'order_id' in res and res['order_id'] == order_id:
            logger.warning(f"Sent order to curexa for {self.subscription_id} Successfully.")
            self._increment_refills_ordered_()

    def reorder_test(self):
        self.fetch_visits_row()
        db = DBClient()
        test_name = self.product.split(' Subscription')[0]
        logger.info(f"Reordering Test: {test_name} for {self.subscription_id}")
        db.insert_retest_visits(test_name, self.visit)
        if self.visit.get("sex") == 0:
            patient_gender = 'male'
        else:
            patient_gender = 'female'
        if self.visit.get("address").lower().startswith("quest"):
            order_type = "quest"
        elif self.visit.get("address").lower().startswith("labcorp"):
            order_type = "labcorp"
        else:
            order_type = 'bioreference'
        if self.visit.get("insurance").lower() != "no":
            bill_to = 'insurance'
        else:
            bill_to = 'patient'
        patient_id = self.visit.get("patient_id")
        if patient_id is None:
            logger.warning(f"Not Sending lab order for Test: {test_name} for {self.subscription_id}, "
                           f"patient_id: {patient_id}")
            return
        data = {
            'patient_id': patient_id,
            'patient_gender': patient_gender,
            'order_type': order_type,
            'bill_to': bill_to,
            'test_names': [test_name]
        }
        lab = DrChronoNewLabOrder(**data)
        logger.info(f"Sending lab order for Test: {test_name} for {self.subscription_id}: {data}")
        drchrono_send_new_lab_order(lab)

    def stripe_workflow(self):
        """Run the actual workflow"""
        self._fetch_stripe_subscription_()
        # check product type
        self._check_product_type_()
        if self.product is None:
            return
        # subscription creation: 1st refill from frontend
        if self.invoice['billing_reason'] == 'subscription_create':
            # update refills to metadata
            # self._update_stripe_subscription_(1)
            pass
        elif self.invoice['billing_reason'] == 'subscription_cycle':
            if self.product == 'Wegovy' or self.product == 'Ozempic' or \
                    self.product == 'Saxenda' or self.product == 'Rybelsus':
                refills_ordered = self._get_stripe_subscription_refills_()
                self.trigger_klaviyo(refills=refills_ordered + 1)
                self.order_refill_weight_loss()
            elif self.product.startswith("curexa_"):
                self.trigger_klaviyo()
                self.order_refill_curexa()
            elif self.product.lower().endswith("ubscription (insurance)") or \
                    self.product.lower().endswith("ubscription (out of pocket)"):
                self.trigger_klaviyo()
                self.reorder_test()

    def subscription_payment_failed_workflow(self):
        self._fetch_stripe_subscription_()
        # check product type
        self._check_product_type_()
        self.fetch_visits_row()
        self.insert_data_in_failed_subscriptions()
        if self.visit.get("email") is None:
            logger.warning(f"email not identified: {self.subscription_id}")
            return
        payment_intent = fetch_payment_intent(self.invoice.get("payment_intent"))
        created_time = datetime.fromtimestamp(payment_intent['created'])
        stripe_subscription_payment_failed(
            email=self.visit.get("email"),
            patient_name=self.visit.get("patient_name"),
            item_name=self.product,
            item_type=self.item_type,
            failure_reason=payment_intent['last_payment_error']['message'],
            payment_attempt_time=datetime.strftime(created_time, '%Y-%m-%dT%H:%M:%S'),
            subscription_renewal_time=datetime.strftime(created_time, '%Y-%m-%d'),
            payment_amount=self.invoice.get("amount_due")/100
        )

    def insert_data_in_failed_subscriptions(self):
        try:
            db = next(get_db())
            if self.visit.get("email") is None:
                logger.warning(f"email is not required: {self.subscription_id}")
                return
            failed_subscription = FailedSubscriptions(
                patient_name=self.visit.get('patient_name'),
                patient_email=self.visit.get('email'),
                patient_phone=self.visit.get('phone'),
                is_processed=0
            )
            db.add(failed_subscription)
            db.commit()
        except Exception as e:
            logger.exception(f"insert_data_in_failed_subscriptions ==> {str(e)}")


def stripe_webhook_handle(event):
    """Handle different stripe events"""
    logger.info(f"Event: {event['type']}")
    try:
        if event['type'] == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            if invoice['subscription'] is not None:
                handler = StripeInvoiceHandler(invoice)
                handler.stripe_workflow()

        elif event['type'] == 'invoice.payment_failed':
            invoice = event['data']['object']
            if invoice['subscription'] is not None:
                handler = StripeInvoiceHandler(invoice)
                handler.subscription_payment_failed_workflow()

        elif event['type'] == 'customer.subscription.created':
            subscription = event['data']['object']
            # logger.info(subscription)
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
        elif event['type'] == 'order.created':
            order = event['data']['object']
        elif event['type'] == 'order.payment_failed':
            order = event['data']['object']
        elif event['type'] == 'order.payment_succeeded':
            order = event['data']['object']
        elif event['type'] == 'order.updated':
            order = event['data']['object']
        elif event['type'] == 'payment_intent.amount_capturable_updated':
            payment_intent = event['data']['object']
        elif event['type'] == 'payment_intent.canceled':
            payment_intent = event['data']['object']
        elif event['type'] == 'payment_intent.created':
            payment_intent = event['data']['object']
        elif event['type'] == 'payment_intent.partially_funded':
            payment_intent = event['data']['object']
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
        elif event['type'] == 'payment_intent.processing':
            payment_intent = event['data']['object']
        elif event['type'] == 'payment_intent.requires_action':
            payment_intent = event['data']['object']
        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            #print(payment_intent)
        elif event['type'] == 'subscription_schedule.aborted':
            subscription_schedule = event['data']['object']
        elif event['type'] == 'subscription_schedule.canceled':
            subscription_schedule = event['data']['object']
        elif event['type'] == 'subscription_schedule.completed':
            subscription_schedule = event['data']['object']
        elif event['type'] == 'subscription_schedule.created':
            subscription_schedule = event['data']['object']
        elif event['type'] == 'subscription_schedule.expiring':
            subscription_schedule = event['data']['object']
        elif event['type'] == 'subscription_schedule.released':
            subscription_schedule = event['data']['object']
        elif event['type'] == 'subscription_schedule.updated':
            subscription_schedule = event['data']['object']
        else:
            logger.warning('Unhandled event type {}'.format(event['type']))

    except Exception as e:
        logger.exception(e)
