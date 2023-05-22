import base64
import logging
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import requests
from pathlib import Path
from config import HEALTHIE_API_KEY, HEALTHIE_API_URL

API_KEY = HEALTHIE_API_KEY
API_URL = HEALTHIE_API_URL
logger = logging.getLogger("fastapi")

ListAllPatient_query = """
query users(
  $offset: Int,
  $keywords: String,
  $sort_by: String,
  $active_status: String,
  $group_id: String,
  $show_all_by_default: Boolean,
  $should_paginate: Boolean,
  $provider_id: String,
  $conversation_id: ID,
  $limited_to_provider: Boolean,
) {
  users(
    offset: $offset,
    keywords: $keywords,
    sort_by: $sort_by,
    active_status: $active_status,
    group_id: $group_id,
    conversation_id: $conversation_id,
    show_all_by_default: $show_all_by_default,
    should_paginate: $should_paginate,
    provider_id: $provider_id,
    limited_to_provider: $limited_to_provider
  ) {
      id
      first_name
      last_name
      legal_name
      email
      phone_number
      dob
      gender
      height
  }
}
"""

List_All_Patients_Query = """
query users(
  $offset: Int,
  $keywords: String,
  $sort_by: String,
  $active_status: String,
  $group_id: String,
  $show_all_by_default: Boolean,
  $should_paginate: Boolean,
  $provider_id: String,
  $conversation_id: ID,
  $limited_to_provider: Boolean,
) {
  usersCount(
    keywords: $keywords,
    active_status:$active_status,
    group_id: $group_id,
    conversation_id: $conversation_id,
    provider_id: $provider_id,
    limited_to_provider: $limited_to_provider
  )
  users(
    offset: $offset,
    keywords: $keywords,
    sort_by: $sort_by,
    active_status: $active_status,
    group_id: $group_id,
    conversation_id: $conversation_id,
    show_all_by_default: $show_all_by_default,
    should_paginate: false,
    provider_id: $provider_id,
    limited_to_provider: $limited_to_provider
  ) {
      id
      first_name
      last_name
      legal_name
      email
      phone_number
  }
}
"""

CreatePatient_mutation = """
mutation createClient($first_name: String, 
                      $last_name: String, 
                      $email: String, 
                      $skipped_email: Boolean, 
                      $phone_number: String,
                      $legal_name: String
                      $dietitian_id: String, 
                      $user_group_id: String, 
                      $dont_send_welcome: Boolean,
                      $other_provider_ids: [String]) {
  createClient(input: { first_name: $first_name, 
                        last_name: $last_name, email: $email,
                        skipped_email: $skipped_email, 
                        phone_number: $phone_number,
                        legal_name: $legal_name,
                        dietitian_id: $dietitian_id, 
                        user_group_id: $user_group_id, 
                        dont_send_welcome: $dont_send_welcome,
                        other_provider_ids: $other_provider_ids, }) {
    user {
      id
      first_name
      last_name
      email
      phone_number
      legal_name
      user_group_id
      other_provider_ids
    }
    messages {
      field
      message
    }
  }
}
"""

CreatePatient_All_in_one_mutation = """
mutation createClient($first_name: String, 
                      $last_name: String, 
                      $email: String, 
                      $phone_number: String,
                      $dietitian_id: String, 
                      $dont_send_welcome: Boolean,
                      $user_group_id: String
                      ){
  createClient(input: { first_name: $first_name, 
                        last_name: $last_name, email: $email,
                        phone_number: $phone_number,
                        dietitian_id: $dietitian_id, 
                        dont_send_welcome: $dont_send_welcome,
                        user_group_id: $user_group_id
                        }) {
    user {
      id
      first_name
      last_name
      email
      phone_number
      dietitian_id
    }
    messages {
      field
      message
    }
  }
}
"""

GetPatient_query = """
query getUser($id: ID) {
  user(id: $id) {
    id
    first_name
    last_name
    dob
    gender
    email
    phone_number
    user_group_id
    next_appt_date
    height
    referring_provider_id
    state_licenses{
      state
    }
    appointment_types {
      id
    }
  }
}
"""

GetPatientConversation_query = """
query getUser($user_id: ID) {
  user(id: $user_id) {
  last_conversation_id
  }
}
"""

GetPatientConversationMembership_query = """
query ConversationMemberships(
	$client_id: String
) {
	conversationMemberships(
		client_id: $client_id
	) {
		conversation_id
    display_name
		convo {
			notes {
        creator {
          name
        }
        created_at
        user_id
        recipient_id
        content
				id
				content
			}
		}
		archived
		creator {
			id
		}
	}
}
"""

UpdatePatient_mutation = """
mutation updateClient (
    $id: ID,
    $first_name: String,
    $last_name: String,
    $phone_number: String,
    $legal_name: String,
    $email: String,
    $dob: String,
    $gender: String,
    $height: String,
    $user_group_id: String,
    $pronouns: String,
    $dietitian_id: String,
    $other_provider_ids: [String],
    $location: ClientLocationInput,
  	$policies: [ClientPolicyInput],
  ) {
  updateClient(input:
    {
      id: $id,
      first_name: $first_name,
      last_name: $last_name,
      phone_number: $phone_number,
      legal_name: $legal_name,
      email: $email,
      dob: $dob,
      gender: $gender,
      height: $height,
      user_group_id: $user_group_id,
      pronouns: $pronouns,
      dietitian_id: $dietitian_id,
      other_provider_ids: $other_provider_ids,
      location: $location,
      policies: $policies,
    }) {
    user {
      id
      first_name
      last_name
      phone_number
      legal_name
      email
      dob
      gender
      height
      user_group_id
      pronouns
      other_provider_ids
      dietitian_id
      location{
        id
      }
      policies{
        id
        type_string
        insurance_card_front_id
        insurance_card_back_id
        insurance_plan{
          payer_id
          payer_name
          
        }
      }
      }
    messages {
      field
      message
    }
  }
}
"""

UpdatePatient_mutation_All_in_one = """
mutation updateClient (
    $id: ID,
    $first_name: String,
    $last_name: String,
    $phone_number: String,
    $email: String,
    $dob: String,
    $gender: String,
    $dietitian_id: String,
    $height: String,
    $location: ClientLocationInput,
    $policies: [ClientPolicyInput]
  ) {
  updateClient(input:
    {
      id: $id,
      first_name: $first_name,
      last_name: $last_name,
      phone_number: $phone_number,
      email: $email,
      dietitian_id: $dietitian_id,
      dob: $dob,
      gender: $gender,
      height: $height,
      location: $location,
      policies: $policies,
    }) {
    user {
      id
      first_name
      last_name
      phone_number
      email
      dob
      gender
      dietitian_id
      height
      }
    messages {
      field
      message
    }
  }
}
"""

Get_Potential_Appointment_and_contactTypes_query = """
 query appointmentTypes(
                          $clients_can_book: Boolean, 
                          $provider_id: String 
  ) {
      appointmentTypes(provider_id: $provider_id,
                       clients_can_book: $clients_can_book ) {
        id
        name
        length
        available_contact_types
        is_group
      }
  }
"""

Get_Available_Days_querry = """
query daysAvailableForRange(
      $provider_id: String
      $date_from_month: String
      $org_level: Boolean
      $licensed_in_state: String
      $timezone: String
      $appt_type_id: String
    ) {
      daysAvailableForRange(
        provider_id: $provider_id
        date_from_month: $date_from_month
        org_level: $org_level
        licensed_in_state: $licensed_in_state
        timezone: $timezone
        appt_type_id: $appt_type_id
      )
    }
"""

Get_Available_Slots_querry = """
 query availableSlotsForRange(
  $provider_id: String
  $start_date: String
  $end_date: String
  $org_level: Boolean
  $licensed_in_state: String
  $timezone: String
  $appt_type_id: String
) {
  availableSlotsForRange(
    provider_id: $provider_id
    start_date: $start_date
    end_date: $end_date
    org_level: $org_level
    licensed_in_state : $licensed_in_state
    timezone: $timezone
    appt_type_id: $appt_type_id
  ) {
    user_id
    date
  }
}
"""

Book_The_Appointment_mutation = """
mutation completeCheckout(
    $appointment_type_id: String,
    $contact_type: String,
    $date: String,
    $first_name: String,
    $last_name: String,
    $email: String,
    $phone_number: String,
    $provider_id: String,
    $timezone: String,
  ) {
    completeCheckout(
      input: {
        appointment_type_id: $appointment_type_id,
        contact_type: $contact_type,
        date: $date,
        timezone: $timezone,
        first_name: $first_name,
        last_name: $last_name,
        email: $email,
        phone_number: $phone_number,
        provider_id: $provider_id,
      }
    ) {
      appointment {
        provider {
          id
          full_name
        }
        id
        date
        contact_type
        appointment_type {
          id
          name
          length
        }
      }
      messages {
        field
        message
      }
    }
  }
"""

Creating_Appointment_mutation = """
mutation createAppointment(
  $user_id: String, # ID of patient in Healthie
  $appointment_type_id: String, # ID of appointment type in Healthie
  $contact_type: String, # e.g "Phone Call"
  $datetime: String, # Timestamp in YYYY-MM-DD HH:MM:SS or ISO8601 format, supercedes date, time params.
  $recurring_appointment: RecurringAppointmentInput
  $providers: String
  $timezone: String
) {
  createAppointment(
    input: {
      user_id: $user_id, 
      appointment_type_id: $appointment_type_id,
      contact_type: $contact_type,
      datetime: $datetime,
      recurring_appointment: $recurring_appointment,
      providers: $providers
      timezone: $timezone
    }
  ) {
    appointment {
      id
      contact_type
    }
    messages {
      field
      message
    }
  }
}
"""

Deleting_Appointment_mutation = """
mutation deleteAppointment($appointment_id: ID, $delete_recurring: Boolean) {
  deleteAppointment(input: { id: $appointment_id, deleteRecurring: $delete_recurring }) {
    appointment {
      id
    }
    messages {
      field
      message
    }
  }
}
"""

Get_The_Appointment_ID_rescheduling_query = """
query appointments(
  $user_id: ID,
  $filter: String,
  $sort_by: String,
  $should_paginate: Boolean,
  $offset: Int,
  $is_active: Boolean,
  $with_all_statuses: Boolean
) {
  appointmentsCount(user_id: $user_id, filter: $filter, is_org: true, is_active: $is_active)
  appointments(
    is_active: $is_active,
    user_id: $user_id,
    filter: $filter,
    is_org: true,
    sort_by: $sort_by,
    should_paginate: $should_paginate,
    offset: $offset,
    with_all_statuses: $with_all_statuses
  ) {
    id
    date
    contact_type
    length
    location
    provider {
      id
      full_name
    }

    appointment_type {
      name
      id
    }

    attendees {
      id
      full_name
      first_name
      avatar_url
      phone_number
    }
  }
}
"""

Get_Available_Days_rescheduling_query = """
query daysAvailableForRange(
      $provider_id: String # Should be the other_party_id from Step 1
      $date_from_month: String 
      $timezone: String
      $appt_type_id: String # should be the appointment_type_id from Step 1
      $appointment_to_reschedule_id: ID # should be the ID of the appointment from Step 1
      $licensed_in_state: String
    ) {
      daysAvailableForRange(
        provider_id: $provider_id
        date_from_month: $date_from_month
        timezone: $timezone
        appt_type_id: $appt_type_id
        appointment_to_reschedule_id: $appointment_to_reschedule_id
        licensed_in_state: $licensed_in_state
      )
    }
"""

Get_Available_Slots_rescheduling_query = """
query availableSlotsForRange(
  $provider_id: String
  $start_date: String
  $end_date: String
  $timezone: String
  $appt_type_id: String
  $licensed_in_state: String
  $appointment_to_reschedule_id: ID
) {
  availableSlotsForRange(
    provider_id: $provider_id
    start_date: $start_date
    end_date: $end_date
    timezone: $timezone
    appt_type_id: $appt_type_id
    licensed_in_state : $licensed_in_state
    appointment_to_reschedule_id: $appointment_to_reschedule_id
  ) {
    user_id
    date
  }
}
"""

Update_The_rescheduling_Appointment_mutation = """
mutation updateAppointment(
    $pm_status: String,
    $datetime: String,
    $id: ID,
    $timezone: String
  ) {
    updateAppointment(
      input: {
        pm_status: $pm_status,
        datetime: $datetime,
        id: $id,
        timezone: $timezone
      }
    ) {
      appointment {
        id
        date
      }
      messages {
        field
        message
      }
    }
  }
"""

Storing_Metric_data_mutation = """
mutation createEntry (
  $metric_stat: String, # e.g "182"
  $category: String, # e.g "Weight"
  $type: String, # "MetricEntry"
  $user_id: String # e.g "61"
  $created_at: String, # e.g "2021-09-23 15:27:01 -0400",

 ) {
  createEntry (input:{
    metric_stat: $metric_stat,
    category: $category,
    type: $type,
    user_id: $user_id,
    created_at: $created_at,
  })
  {
    entry {
      id
    }
    messages
    {
      field
      message
    }
  }
}
"""

Querying_Filled_Out_Forms_query = """
query formAnswerGroups(
  $date: String, # e.g "2021-10-29"
  $custom_module_form_id: ID, # e.g "11"
  ) {
  formAnswerGroups(
    date: $date,
    custom_module_form_id: $custom_module_form_id,
    ) {
    id
    name
    created_at
    form_answers {
      label
      displayed_answer
      id
      custom_module {
        required
        id
        mod_type
        label
      }
    }
  }
}
"""

Querying_After_Visit_Summary_Query = """
query formAnswerGroups(
  $user_id: String
  ) {
  formAnswerGroups(
    custom_module_form_id: "1188468",
    user_id: $user_id
    ) {
    id
    name
    created_at
    form_answers {
      label
      displayed_answer
      id
      custom_module {
        required
        id
        mod_type
        label
      }
    }
  }
}
"""

Creating_Filled_Out_Form_mutation = """
mutation createFormAnswerGroup(
  $finished: Boolean, # Should almost always true
  $custom_module_form_id: String, # ID of the custom_module_form (e.g "100")
  $user_id: String, # ID of the patient (e.g "61")
  $form_answers: [FormAnswerInput!]!, # e.g [{custom_module_id: "1", answer: "foo", user_id: "61"}, 
                      #     {custom_module_id: "2", answer: "bar", user_id: "61"}]
  # $label: String
) {
  createFormAnswerGroup(
    input: {
      finished: $finished,
      custom_module_form_id: $custom_module_form_id,
      user_id: $user_id,
      form_answers: $form_answers,
      # label: $label
    }
  ) {
    form_answer_group {
      id
    }
    messages {
      field
      message
    }
  }
}
"""

Creating_Filled_Out_PA_Mutation = """
mutation createFormAnswerGroup(
  $finished: Boolean, # Should almost always true
  $user_id: String, # ID of the patient (e.g "61")
  $form_answers: [FormAnswerInput!]!, # e.g [{custom_module_id: "1", answer: "foo", user_id: "61"}, 
                      #     {custom_module_id: "2", answer: "bar", user_id: "61"}]
) {
  createFormAnswerGroup(
    input: {
      finished: $finished,
      custom_module_form_id: "1188700",
      user_id: $user_id,
      form_answers: $form_answers,
    }
  ) {
    form_answer_group {
      id
    }
    messages {
      field
      message
    }
  }
}
"""

CreateAllergySensitivity_mutation = """
mutation createAllergySensitivity(
    $user_id: String,
    $category: String,
    $category_type: String,
    $is_current: Boolean,
    $name: String,
    $custom_name: String,
    $reaction: String,
    $custom_reaction: String,
    $severity: String
  ) {
  createAllergySensitivity(
    input: {
      user_id: $user_id,
      severity: $severity,
      category: $category,
      category_type: $category_type,
      is_current: $is_current,
      reaction: $reaction,
      custom_reaction: $custom_reaction,
      name: $name,
      custom_name: $custom_name,
    }
  ) {
    allergy_sensitivity {
      id
    }
    duplicatedAllergy: duplicate_allergy {
      id
      name
      category
      category_type
    }
    messages {
      field
      message
    }
  }
}
"""

CreateMedication_mutation = """
mutation createMedication(
  $user_id: String,
  $active: Boolean,
  $comment: String,
  $directions: String,
  $dosage: String,
  $custom_name: String,
  $name: String,
  $start_date: String,
  $end_date: String
) {
  createMedication(
    input: {
      user_id: $user_id,
      active: $active,
      comment: $comment,
      directions: $directions,
      dosage: $dosage,
      custom_name: $custom_name,
      name: $name,
      start_date: $start_date,
      end_date: $end_date
    }
  ) {
    medication {
      id
      name
    }
    messages {
      field
      message
    }
  }
}
"""

Create_Document_mutation = """
mutation createDocument(
  $rel_user_id: String,
  $file_string: String,
  $description: String,
  $from_date: String,
  $to_date: String,
  $include_in_charting : Boolean,
  $display_name: String,
) {
  createDocument(
    input: {
      rel_user_id: $rel_user_id,
      file_string: $file_string,
      description: $description,
      from_date: $from_date,
      to_date: $to_date,
      include_in_charting: $include_in_charting,
      display_name: $display_name,
    }
  ) {
    currentUser {
      id
    }
    document{
      id
      description
      display_name
      expiring_url
      # file_string
      description
      # from_date
      # to_date
    }
    messages {
      field
      message
    }
  }
}
"""

Create_Document_All_in_one_mutation = """
mutation createDocument(
  $rel_user_id: String,
  $file_string: String,
  $include_in_charting : Boolean,
  $display_name: String,
  $photo_id: Boolean,
  $share_with_rel: Boolean,
) {
  createDocument(
    input: {
      rel_user_id: $rel_user_id,
      file_string: $file_string,
      include_in_charting: $include_in_charting,
      display_name: $display_name,
      is_photo_id: $photo_id,
      share_with_rel: $share_with_rel
    }
  ) {
    currentUser {
      id
    }
    document{
      id
      display_name
      rel_user_id
      rel_user{
        id
        name
        email
      }
      display_name
      extension
      owner{
        id
        name
      }
      users{
        id
        name
      }
    }
    messages {
      field
      message
    }
  }
}
"""

Get_Insurance_plans_query = """
query {
  insurancePlans{
    payer_id,
    payer_name,
  }
}
"""

Create_Requested_Form_Completion_mutation = """
mutation createRequestedFormCompletion(
  $recipient_id: ID, 
  $custom_module_form_id: ID, 
  $item_type: String, 
  $form: String, 
  $is_recurring: Boolean,) {
  createRequestedFormCompletion(
    input: {recipient_id: $recipient_id, 
      custom_module_form_id: $custom_module_form_id, 
      item_type: $item_type, 
      form: $form, 
      is_recurring: $is_recurring,}
  ) {
    requestedFormCompletion {
      id
    }
    requestedFormCompletionStatus{
      status
    }
    messages {
      field
      message
    }
  }
}
"""

Get_Custom_Module_Form_Completion_query = """
query CustomModuleForm{
  customModuleForms {
  id
  name
  }
}
"""

Update_Policy_mutation = """
mutation updatePolicy(
  $id: ID,
  $type_string: String,
  $holder_first: String,
  $holder_mi: String,
  $holder_last: String,
  $holder_dob: String,
  $holder_gender: String,
  $holder_phone: String,
  $notes: String,
  $insurance_card_front_id: String,
  $insurance_card_back_id: String,
) {
  updatePolicy(input: {
    id: $id,
    type_string: $type_string, 
    holder_first: $holder_first, 
    holder_mi: $holder_mi, 
    holder_last: $holder_last, 
    holder_dob: $holder_dob,
    holder_gender: $holder_gender,
    holder_phone: $holder_phone,
    notes: $notes,
    insurance_card_front_id: $insurance_card_front_id,
    insurance_card_back_id: $insurance_card_back_id,
  }) {
    policy {
      id
      insurance_card_front_id
      insurance_card_back_id

    }
    messages {
      field
      message
    }
  }
}
"""

Prescriptions_query = """
query prescriptions(
  $patient_id: ID,
  $status: String
  ) {
  prescriptions(
    patient_id: $patient_id,
    status: $status,
    ) {
    	date_written
    directions
    status
    id
    ndc
    product_name
    quantity
    refills
    status
    pharmacy{
      id
      city
      name
      state
      zip
    }  
  }
}
"""

All_Prescriptions_query = """
query prescriptions(
  $patient_id: ID
  ) {
  prescriptions(
    patient_id: $patient_id
    ) {
    date_written
    directions
    status
    id
    ndc
    product_name
    quantity
    refills
    status
    pharmacy{
      id
      city
      name
      state
      zip
    }  
  }
}
"""

Creating_Conversation_mutation = """
mutation createConversation(
  $simple_added_users: String # e.g "user-1,group-2,user-3"
  $owner_id: ID # e.g "4"
  $name: String # e.g "Questions for Next Appointment"
) {
  createConversation(
    input: {
      simple_added_users: $simple_added_users
      owner_id: $owner_id
      name: $name
    }
  ) {
    conversation {
      id
    }
    messages {
      field
      message
    }
  }
}
"""

Retrieving_Conversation_query = """
query getConversation($id: ID, $provider_id: ID) {
  conversation(id: $id, provider_id: $provider_id) {
    id
    conversation_memberships_count
    includes_multiple_clients
    name
    notes{
    id
    content
  }
  }
}
"""

Retrieve_Conversation_By_ID_Query = """
query getConversation($id: ID) {
  conversation(id: $id){
    id
    conversation_memberships_count
    includes_multiple_clients
    name
    patient_id
    notes{
      attached_audio_url
      attached_image_url
      content
      created_at
      creator{
        id
        name
      }
      recipient_id
      viewed
    }
  }
}
"""

Updating_Conversation_mutation = """
mutation updateConversation(
  $id: ID,
  $simple_added_users: String,
  $name: String,
  $closed_by_id: ID,
) {
  updateConversation(
    input: {
      id: $id,
      simple_added_users: $simple_added_users,
      name: $name,
      closed_by_id: $closed_by_id,
    }
  ) {
    conversation {
      id
    }
    messages {
      field
      message
    }
  }
}
"""

Retrieve_Note_Query = """
query getNote($id: ID) {
  note(id: $id) {
    content
    conversation_id
  }
}
"""

Create_Task_mutation = """
mutation createTask(
  $content: String,
  $user_id: String,
  $priority: Int,
  $client_id: String,
  $due_date: String,
  $reminder: TaskReminderInput
) {
  createTask(input: {
    content: $content,
    user_id: $user_id,
    priority: $priority,
    client_id: $client_id,
    due_date: $due_date,
    reminder: $reminder
  }) {
    task {
      id
      content
    }
    messages {
      field
      message
    }
  }
}
"""


Retrieve_Conversations_Query = """
query conversationMemberships(
  $active_status: String
  $read_status: String
  $conversation_type: String
  $client_id: String
) {
  conversationMembershipsCount(
    active_status: $active_status
    read_status: $read_status
    conversation_type: $conversation_type
    client_id: $client_id
  )
  conversationMemberships(
    active_status: $active_status
    read_status: $read_status
    conversation_type: $conversation_type
    client_id: $client_id
  ) {
    conversation_id
    display_avatar
    id
    display_name
    archived
    viewed
    convo {
      id
      conversation_memberships_count
      notes {
      creator {
          name
        }
      content
      created_at
      user_id
      }
    }
  }
}
"""

Create_Webhooks = """
{

"resource_id": resource_id, # The ID of the resource that was affected 

"resource_id_type": resource_id_type, # The type of resource (can be 'Appointment', 'FormAnswerGroup', 'Entry', or 'Note')  

"event_type": event_type # The event that occurred

}

# mutation createWebhook(
#   $resource_id: ID
#   $resource_id_type: String
#   # $event_type: String
  
# ) {
#   createWebhook(
#     input: {
#       resource_id: $resource_id
#       resource_id_type: $resource_id
#       # event_type: $event_type
      
#     }
#   ) {
#     from_answer_group {
#       event_type
#     }
#     messages {
#       field
#       message
#     }
#   }
# }
"""


Retrieve_Prescriptions_Query = """
 query prescriptions($patient_id: ID) {
        prescriptions(patient_id: $patient_id) {
            id
            date_written
            directions
            ndc
            product_name
            quantity
            refills
            status
            unit
            pharmacy {
                city
                id
                line1
                line2
                phone_number
                name
                state
                zip
            }
        }
      }
"""

Conversation_Membership_Query = """
 query ConversationMemberships($client_id: String) {
        conversationMemberships(client_id: $client_id) {
            conversation_id
            convo {
              notes {
                id
                content
              }
            }
            archived
            creator {
              id
            }
        }
      }
"""



List_Appointments_Query = """
query appointments(
  $is_active: Boolean,
  $with_all_statuses: Boolean,
  $user_id: ID,
  $sort_by: String,
) {
  appointmentsCount(user_id: $user_id, is_org: true, is_active: $is_active)
  appointments(
    is_active: $is_active,
    is_org: true,
    sort_by: $sort_by,
    user_id: $user_id,
    with_all_statuses: $with_all_statuses
  ) {
    id
    date
    contact_type
    length
    location
    provider {
      id
      full_name
    }
    appointment_type {
      name
      id
    }
    attendees {
      id
      full_name
      first_name
      avatar_url
      phone_number
    }
  }
}
"""

Send_Message_Query = """
mutation createNote(
  $user_id: String,
  $conversation_id: String,
  $content: String,
  $attached_image_string: String
) {
  createNote(
    input: {
      user_id: $user_id,
      conversation_id: $conversation_id,
      content: $content,
      attached_image_string: $attached_image_string
    }
  ) {
    note {
      id
      content
    }
    messages {
      field
      message
    }
  }
}
"""

class HealthieAPI:
    def __init__(self):
        self.base_url = API_URL

    def _get_request_(self, json=None, authenticate=True):
        """
        Send a requests.get request
        :param uri: Endpoint URI273579
        :param params: URL Parameters
        :param json: body to be sent with request
        :return: json of response
        """
        url = self.base_url

        headers = {
            'Authorization': "Basic " + API_KEY,
            'AuthorizationSource': "API"
        }
        try:
            if not authenticate:
                res = requests.get(url)
            else:
                if json is None:
                    try:
                      res = requests.get(url, headers=headers)
                    except:
                      logger.error(f"healthie _get_request_ => empty json, still error")
                else:
                    logger.info(f"healthie _get_request_ => json: {json}")
                    res = requests.get(url, headers=headers, json=json)
            logger.info(res.status_code)
            logger.info(res.text)
            return res.json()
        except Exception as e:
            logger.exception("healthie _post_request_ => error: " + str(e))
            return {}

    def _post_request_(self, json=None, authenticate=True):
        """
        Send a requests.post request
        :param uri: Endpoint URI273579
        :param params: URL Parameters
        :param json: body to be sent with request
        :return: json of response
        """
        url = self.base_url

        headers = {
            'Authorization': "Basic " + API_KEY,
            'AuthorizationSource': "API"
        }
        try:
            if not authenticate:
                res = requests.post(url, json=json)
            else:
                if json is None:
                    res = requests.post(url, headers=headers)
                else:
                    logger.info(f"healthie _post_request_ => json: {json}")
                    res = requests.post(url, headers=headers, json=json)
            logger.info(res.status_code)
            logger.info(res.text)
            return res.json()
        except Exception as e:
            logger.exception("healthie _post_request_ => error: " + str(e))
            return {}

    def list_patient(self):
        r = self._post_request_(json={'query': ListAllPatient_query})
        return r

    def list_all_patients(self):
        r = self._post_request_(json={'query': ListAllPatient_query})
        return r

    def create_patient(self, data):
        r = self._post_request_(json={'query': CreatePatient_mutation, 'variables': data})
        return r

    def create_patient_all_in_one(self, data):
        r = self._post_request_(json={'query': CreatePatient_All_in_one_mutation, 'variables': data})
        if r.get("data").get('createClient').get("messages"):
            logger.error(str(r.get("data").get('createClient').get("messages")[0].get('message')))
        return r

    def get_patient(self, user_id):
        r = self._post_request_(json={'query': GetPatient_query, 'variables': {'id': user_id}})
        print(r)
        return r

    def get_patient_recent_conversation(self, user_id):
        r = self._post_request_(json={'query': GetPatientConversation_query, 'variables': {'user_id': user_id}})
        if r.get("error"):
            logger.error(str(r.get("error")))
        return r

    def get_patient_conversation_memberships(self, user_id):
        r = self._post_request_(json={'query': GetPatientConversationMembership_query, 'variables': {'user_id': user_id}})
        if r.get("error"):
            logger.error(str(r.get("error")))
        return r

    def update_patient(self, data):
        r = self._post_request_(json={'query': UpdatePatient_mutation, 'variables': data})
        return r

    def update_patient_all_in_one(self, data):
        r = self._post_request_(json={'query': UpdatePatient_mutation_All_in_one, 'variables': data})
        return r

    def get_potential_appointment_and_contactTypes_self_scheduling(self):
        r = self._post_request_(json={'query': Get_Potential_Appointment_and_contactTypes_query})
        return r

    def get_available_days_self_scheduling(self, data):
        r = self._post_request_(json={'query': Get_Available_Days_querry, 'variables': data})
        return r

    def get_available_slots_self_scheduling(self, data):
        r = self._post_request_(json={'query': Get_Available_Slots_querry, 'variables': data})
        return r

    def book_the_appointment_self_scheduling(self, data):
        r = self._post_request_(json={'query': Book_The_Appointment_mutation, 'variables': data}, authenticate=False)
        return r

    def creating_appointment(self, data):
        r = self._post_request_(json={'query': Creating_Appointment_mutation, 'variables': data})
        if r.get('errors'):
            logger.error(str(r.get("errors")[0].get('message')))
        return r

    def deleting_appointment(self, data):
        r = self._post_request_(json={'query': Deleting_Appointment_mutation, 'variables': data})
        if not r:
            logger.error('healthie-deleting-appointment - {}')
        return r

    def get_the_rescheduling_appointment_id(self, data):
        r = self._post_request_(json={'query': Get_The_Appointment_ID_rescheduling_query, 'variables': data})
        return r

    def get_rescheduling_available_days(self, data):
        r = self._post_request_(json={'query': Get_Available_Days_rescheduling_query, 'variables': data})
        return r

    def get_rescheduling_available_slots(self, data):
        r = self._post_request_(json={'query': Get_Available_Slots_rescheduling_query, 'variables': data})
        return r

    def update_rescheduling_appointment(self, data):
        r = self._post_request_(json={'query': Update_The_rescheduling_Appointment_mutation, 'variables': data})
        return r

    def storing_Metric_data(self, data):
        r = self._post_request_(json={'query': Storing_Metric_data_mutation, 'variables': data})
        return r

    def querying_filled_out_forms(self):
        r = self._post_request_(json={'query': Querying_Filled_Out_Forms_query})
        return r
    
    def querying_after_visit_summaries(self, data):
        r = self._post_request_(json={'query': Querying_After_Visit_Summary_Query, 'variables': data})
        return r

    def creating_filled_out_forms(self, data):
        try:
            r = self._post_request_(json={'query': Creating_Filled_Out_Form_mutation, 'variables': data})
            if r.get("data", {}) and r.get("data", {}).get('createFormAnswerGroup', {}) and r.get("data", {}).get('createFormAnswerGroup', {}).get('messages'):
                logger.error(str(r.get("data").get('createFormAnswerGroup').get('messages')[0].get('message')))
            return r
        except:
            return None
      
    def creating_filled_out_pa_forms(self, data):
        try:
          r = self._post_request_(json={'query': Creating_Filled_Out_PA_Mutation, 'variables': data})
          if r.get("data", {}) and r.get("data", {}).get('createFormAnswerGroup', {}) and r.get("data", {}).get('createFormAnswerGroup', {}).get('messages'):
                  logger.error(str(r.get("data").get('createFormAnswerGroup').get('messages')[0].get('message')))
          return r
        except:
          return None

    def create_allergy_sensitivity(self, data):
        r = self._post_request_(json={'query': CreateAllergySensitivity_mutation, 'variables': data})
        if not r:
            logger.error('healthie-create-allergy-sensitivity - {}')
        return r

    def create_medication(self, data):
        r = self._post_request_(json={'query': CreateMedication_mutation, 'variables': data})
        if r.get("data").get('createMedication').get('messages'):
            logger.error(str(r.get("data").get('createMedication').get('messages')[0].get('message')))
        return r

    def upload_document(self, data):
        r = self._post_request_(json={'query': Create_Document_mutation, 'variables': data})
        return r

    def upload_document_all_in_one(self, data):
        r = self._post_request_(json={'query': Create_Document_All_in_one_mutation, 'variables': data})
        if not r:
            logger.error('healthie-create-new-docs - {}')
        return r

    def get_insurance_plans(self):
        r = self._post_request_(json={'query': Get_Insurance_plans_query})
        return r

    def create_requested_form_completion(self, data):
        r = self._post_request_(json={'query': Create_Requested_Form_Completion_mutation, 'variables': data})
        return r

    def get_custom_module_form_completion(self):
        r = self._post_request_(json={'query': Get_Custom_Module_Form_Completion_query})
        return r

    def update_policy(self, data):
        r = self._post_request_(json={'query': Update_Policy_mutation, 'variables': data})
        return r

    def prescriptions(self, data):
        r = self._post_request_(json={'query': Prescriptions_query, 'variables': data})
        return r

    def get_all_prescriptions(self, patient_id: str):
        r = self._post_request_(json={'query': All_Prescriptions_query, 'variables': {'patient_id': patient_id}})
        return r

    def create_conversation(self, data):
        r = self._post_request_(json={'query': Creating_Conversation_mutation, 'variables': data})
        if r.get("data").get('createConversation').get('messages'):
            logger.error(str(r.get("data").get('createConversation').get('messages')[0].get('message')))
        return r

    def create_note(self, data):
        r = self._post_request_(json={'query': Create_Note_mutation, 'variables': data})
        return r

    def retrieve_note(self, data):
        r = self._post_request_(json={'query': Retrieve_Note_Query, 'variables': data})
        return r

    def retrieve_conversation(self, id, provider_id):
        r = self._post_request_(
            json={'query': Retrieving_Conversation_query, 'variables': {'id': id, 'provider_id': provider_id}}
        )
        return r

    def retrieve_conversation_by_id(self, id_):
        r = self._post_request_(
            json={'query': Retrieve_Conversation_By_ID_Query, 'variables': {'id': id_}}
        )
        return r

    def update_conversation(self, data):
        r = self._post_request_(json={'query': Updating_Conversation_mutation, 'variables': data})
        if r.get("data").get('updateConversation').get('messages'):
            logger.error(str(r.get("data").get('updateConversation').get('messages')[0].get('message')))
        return r

    def create_webhooks(self, data):
        r = self._post_request_(json={'variables': data})
        return r

    def create_task(self, data):
        r = self._post_request_(json={'query': Create_Task_mutation, 'variables': data})
        return r

    def list_appointments(self, data):
        r = self._post_request_(json={'query': List_Appointments_Query, 'variables': data})
        return r

    def retrieve_list_conversations(self, data):
        r = self._post_request_(json={'query': Retrieve_Conversations_Query, 'variables': data})
        return r

    def retrieve_presecriptions(self, data):
        r = self._post_request_(json={'query': Retrieve_Prescriptions_Query, 'variables': data})
        return r

    def send_message(self, data):
        r = self._post_request_(json={'query': Send_Message_Query, 'variables': data})
        if r.get("data").get('createNote').get('messages'):
            logger.error(str(r.get("data").get('createNote').get('messages')[0].get('message')))
        return r

    def conversation_membership(self, data):
        r = self._post_request_(json={'query': Conversation_Membership_Query, 'variables': data})
        return r


class HealthieGraphAPI:

    def __init__(self):
        headers = {
            'Authorization': "Basic " + HEALTHIE_API_KEY,
            'AuthorizationSource': "API"
        }
        # Select your transport with a defined url endpoint
        transport = AIOHTTPTransport(url=HEALTHIE_API_URL, headers=headers)

        # Create a GraphQL client using the defined transport
        self.client = Client(transport=transport, fetch_schema_from_transport=True)

    def list_all_patients(self):
        query = gql(ListAllPatient_query)
        result = self.client.execute(query)
        return result

    async def create_document(
            self,
            patient_id: str,
            filepath: str,
            desc: str=None,
            include_in_charting=False,
            display_name: str=None
    ):
        """
        creates/uploads a doc to healthie
        patient_id: healthie patient_id
        filepath: path of file
        desc: any description
        """
        query = gql(
            """mutation createDocument(
              $rel_user_id: String,
              $file_string: String,
              $description: String,
              $include_in_charting : Boolean,
              $display_name: String,
            ) {
              createDocument(input: {
                rel_user_id: $rel_user_id,
                file_string: $file_string,
                description: $description,
                include_in_charting: $include_in_charting,
                display_name: $display_name
              }) {
                document {
                  id
                }
                messages {
                  field
                  message
                }
              }
            }"""
        )
        try:
          upload_file = Path(filepath)
          if not upload_file.is_file():
              return {"error": "file doesn't exist"}
          with open(filepath, "rb") as f:
              encoded = base64.b64encode(f.read())
              decoded = encoded.decode()
              file_string = f"""data:application/pdf;base64,{decoded}"""
              params = {
                  "rel_user_id": patient_id,
                  "file_string": file_string,
                  "description": desc,
                  "include_in_charting": include_in_charting,
                  "display_name": display_name
              }
              result = await self.client.execute_async(query, variable_values=params, upload_files=True)
          return result
        except Exception as e:
          logger.error(f"""create_document: error with creating user {str(patient_id)} and error = {str(e)}""")
          return {"error": str(e)}

    def get_document(self, document_id: str):
        query = gql(
            """query document(
                  $id: ID
                ) {
                  document(
                    id: $id
                  ) {
                    id
                    display_name
                    rel_user_id
                    file_content_type
                    description
                    opens {
                      id
                    }
                    owner {
                      id
                      email
                    }
                    users {
                      id
                      email
                    }
                  }
                }"""
        )
        params = {
            "id": document_id
        }
        result = self.client.execute(query, variable_values=params)
        return result


healthie = HealthieAPI()
healthie_api = HealthieGraphAPI()


if __name__ == '__main__':
    r = healthie_api.get_document('61191')
    #r = healthie_api.create_document('124680', 'C:\\python_work\\Next-Medical\\backend\\pdfs\\labcorp_gc.pdf', 'Trial')
    print(r)
    pass
