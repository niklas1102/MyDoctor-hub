from celery import shared_task
from .cloud_utils import create_condition, create_document_reference, create_immunization, create_medical_request, create_observation, create_patient, delete_condition, delete_document_reference, delete_immunization, delete_medical_request, delete_observation, update_condition, update_document_reference, update_immunization, update_medical_request, update_observation, update_patient, delete_patient, create_encounter, update_encounter, delete_encounter

@shared_task
def push_patient_to_cloud(resource_data):
    response = create_patient(resource_data)
    return response

@shared_task
def update_patient_in_cloud(patient_id, updated_data):
    response = update_patient(patient_id, updated_data)
    return response

@shared_task
def delete_patient_from_cloud(patient_id):
    response = delete_patient(patient_id)
    return response

@shared_task
def push_encounter_to_cloud(resource_data):
    response = create_encounter(resource_data)
    return response

@shared_task
def update_encounter_in_cloud(encounter_id, updated_data):
    response = update_encounter(encounter_id, updated_data)
    return response

@shared_task
def delete_encounter_from_cloud(encounter_id):
    response = delete_encounter(encounter_id)
    return response

@shared_task
def push_lab_result_to_cloud(resource_data):
    response = create_condition(resource_data)
    return response

@shared_task
def update_lab_result_in_cloud(lab_result_id, updated_data):
    response = update_condition(lab_result_id, updated_data)
    return response

@shared_task
def delete_lab_result_from_cloud(lab_result_id):
    response = delete_condition(lab_result_id)
    return response

@shared_task
def push_prescription_to_cloud(resource_data):
    response = create_medical_request(resource_data)
    return response

@shared_task
def update_prescription_in_cloud(prescription_id, updated_data):
    response = update_medical_request(prescription_id, updated_data)
    return response

@shared_task
def delete_prescription_from_cloud(prescription_id):
    response = delete_medical_request(prescription_id)
    return response

@shared_task
def push_diagnosis_to_cloud(resource_data):
    response = create_condition(resource_data)
    return response

@shared_task
def update_diagnosis_in_cloud(diagnosis_id, updated_data):
    response = update_condition(diagnosis_id, updated_data)
    return response

@shared_task
def delete_diagnosis_from_cloud(diagnosis_id):
    response = delete_condition(diagnosis_id)
    return response

@shared_task
def push_immunization_to_cloud(resource_data):
    response = create_immunization(resource_data)
    return response

@shared_task
def update_immunization_in_cloud(immunization_id, updated_data):
    response = update_immunization(immunization_id, updated_data)
    return response

@shared_task
def delete_immunization_from_cloud(immunization_id):
    response = delete_immunization(immunization_id)
    return response

@shared_task
def push_document_to_cloud(resource_data):
    response = create_document_reference(resource_data)
    return response

@shared_task
def update_document_in_cloud(document_id, updated_data):
    response = update_document_reference(document_id, updated_data)
    return response

@shared_task
def delete_document_from_cloud(document_id):
    response = delete_document_reference(document_id)
    return response