import logging
from db_client import DBClient


logger = logging.getLogger("fastapi")



def add_user_stage_in_process():
    """ create user stage in proces """
    print("start process...")

    client      = DBClient()
    # get all data from visits table
    all_data    = client.get_visits_all_records()

    for visit in all_data:

        # if check is not none and not equal to none
        if visit.get('drchrono_res') is not None:
            if visit.get('drchrono_res') !="None":
                # add data to user_stage_in_process table
                client.add_user_stage_in_process(
                    visit.get('mrn'), 
                    stage       = "labs", 
                    completed   = True)

        # if check is not none and not equal to none      
        if visit.get('healthie_visit_zoom_link') is not None:
            if visit.get('healthie_visit_zoom_link') !="None":
                # add data to user_stage_in_process table
                client.add_user_stage_in_process(
                    visit.get('mrn'), 
                    stage       = "schedulued_visit", 
                    completed   = True)


    print("Successfully completed this process.")
    logger.info("Successfully completed.")


if __name__ == "__main__":
    add_user_stage_in_process()
