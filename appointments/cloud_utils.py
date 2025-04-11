import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()


SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE', '/path/to/default/service-account.json')
print(SERVICE_ACCOUNT_FILE)
def get_healthcare_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('healthcare', 'v1', credentials=credentials)
    return service

PROJECT_ID = 'mydoctor-ehr'
LOCATION = 'europe-west3'
DATASET_ID = 'patient-records'
FHIR_STORE_ID = 'ehr_store'
FHIR_BASE_URL = f"projects/{PROJECT_ID}/locations/{LOCATION}/datasets/{DATASET_ID}/fhirStores/{FHIR_STORE_ID}"
# patient crud
def create_patient(resource_data):
    service = get_healthcare_service()
    request = service.projects().locations().datasets().fhirStores().fhir().create(
        parent=FHIR_BASE_URL,
        type='Patient',
        body=resource_data
    )
    return request.execute()

def get_patient(patient_id):
    service = get_healthcare_service()
    name = f"{FHIR_BASE_URL}/Patient/{patient_id}"
    request = service.projects().locations().datasets().fhirStores().fhir().read(name=name)
    return request.execute()

def update_patient(patient_id, updated_data):
    service = get_healthcare_service()
    name = f"{FHIR_BASE_URL}/Patient/{patient_id}"
    request = service.projects().locations().datasets().fhirStores().fhir().update(
        name=name,
        body=updated_data
    )
    return request.execute()

def delete_patient(patient_id):
    service = get_healthcare_service()
    name = f"{FHIR_BASE_URL}/Patient/{patient_id}"
    request = service.projects().locations().datasets().fhirStores().fhir().delete(name=name)
    return request.execute()

# encounter crud
def create_encounter(resource_data):
    service = get_healthcare_service()
    request = service.projects().locations().datasets().fhirStores().fhir().create(
        parent=FHIR_BASE_URL,
        type='Encounter',
        body=resource_data
    )
    return request.execute()

def get_encounter(encounter_id):
    service = get_healthcare_service()
    name = f"{FHIR_BASE_URL}/Encounter/{encounter_id}"
    request = service.projects().locations().datasets().fhirStores().fhir().read(name=name)
    return request.execute()

def update_encounter(encounter_id, updated_data):
    service = get_healthcare_service()
    name = f"{FHIR_BASE_URL}/Encounter/{encounter_id}"
    request = service.projects().locations().datasets().fhirStores().fhir().update(
        name=name,
        body=updated_data
    )
    return request.execute()

def delete_encounter(encounter_id):
    service = get_healthcare_service()
    name = f"{FHIR_BASE_URL}/Encounter/{encounter_id}"
    request = service.projects().locations().datasets().fhirStores().fhir().delete(name=name)
    return request.execute()

# condition crud
def create_condition(resource_data):
    service = get_healthcare_service()
    request = service.projects().locations().datasets().fhirStores().fhir().create(
        parent=FHIR_BASE_URL,
        type='Condition',
        body=resource_data
    )
    return request.execute()

def get_condition(condition_id):
    service = get_healthcare_service()
    name = f"{FHIR_BASE_URL}/Condition/{condition_id}"
    request = service.projects().locations().datasets().fhirStores().fhir().read(name=name)
    return request.execute()

def update_condition(condition_id,updated_data):
    service = get_healthcare_service()
    name = f"{FHIR_BASE_URL}/Condition/{condition_id}"
    request = service.projects().locations().datasets().fhirStores().fhir().update(
        name=name,
        body=updated_data
    )
    return request.execute()

def delete_condition(condition_id):
    service = get_healthcare_service()
    name = f"{FHIR_BASE_URL}/Condition/{condition_id}"
    request = service.projects().locations().datasets().fhirStores().fhir().delete(name=name)
    return request.execute()

# medication request crud
def create_medical_request(resource_data):
    service = get_healthcare_service()
    request = service.projects().locations().datasets().fhirStores().fhir().create(
        parent=FHIR_BASE_URL,
        type='MedicationRequest',
        body=resource_data
    )
    return request.execute()

def get_medical_request(request_id):
    service = get_healthcare_service()
    name = f"{FHIR_BASE_URL}/MedicationRequest/{request_id}"
    request = service.projects().locations().datasets().fhirStores().fhir().read(name=name)
    return request.execute()

def update_medical_request(request_id, updated_data):
    service = get_healthcare_service()
    name = f"{FHIR_BASE_URL}/MedicationRequest/{request_id}"
    request = service.projects().locations().datasets().fhirStores().fhir().update(
        name=name,
        body=updated_data
    )
    return request.execute()

def delete_medical_request(request_id):
    service = get_healthcare_service()
    name = f"{FHIR_BASE_URL}/MedicationRequest/{request_id}"
    request = service.projects().locations().datasets().fhirStores().fhir().delete(name=name)
    return request.execute()

# observation crud
def create_observation(resource_data):
    service = get_healthcare_service()
    request = service.projects().locations().datasets().fhirStores().fhir().create(
        parent=FHIR_BASE_URL,
        type='Observation',
        body=resource_data
    )
    return request.execute()

def get_observation(observation_id):
    service = get_healthcare_service()
    name = f"{FHIR_BASE_URL}/Observation/{observation_id}"
    request = service.projects().locations().datasets().fhirStores().fhir().read(name=name)
    return request.execute()

def update_observation(observation_id, updated_data):
    service = get_healthcare_service()
    name = f"{FHIR_BASE_URL}/Observation/{observation_id}"
    request = service.projects().locations().datasets().fhirStores().fhir().update(
        name=name,
        body=updated_data
    )
    return request.execute()

def delete_observation(observation_id):
    service = get_healthcare_service()
    name = f"{FHIR_BASE_URL}/Observation/{observation_id}"
    request = service.projects().locations().datasets().fhirStores().fhir().delete(name=name)
    return request.execute()

# immunization crud
def create_immunization(resource_data):
    service = get_healthcare_service()
    request = service.projects().locations().datasets().fhirStores().fhir().create(
        parent=FHIR_BASE_URL,
        type='Immunization',
        body=resource_data
    )
    return request.execute()

def get_immunization(immunization_id):
    service = get_healthcare_service()
    name = f"{FHIR_BASE_URL}/Immunization/{immunization_id}"
    request = service.projects().locations().datasets().fhirStores().fhir().read(name=name)
    return request.execute()

def update_immunization(immunization_id, updated_data):
    service = get_healthcare_service()
    name = f"{FHIR_BASE_URL}/Immunization/{immunization_id}"
    request = service.projects().locations().datasets().fhirStores().fhir().update(
        name=name,
        body=updated_data
    )
    return request.execute()

def delete_immunization(immunization_id):
    service = get_healthcare_service()
    name = f"{FHIR_BASE_URL}/Immunization/{immunization_id}"
    request = service.projects().locations().datasets().fhirStores().fhir().delete(name=name)
    return request.execute()

# document reference crud
def create_document_reference(resource_data):
    service = get_healthcare_service()
    request = service.projects().locations().datasets().fhirStores().fhir().create(
        parent=FHIR_BASE_URL,
        type='DocumentReference',
        body=resource_data
    )
    return request.execute()

def get_document_reference(document_id):
    service = get_healthcare_service()
    name = f"{FHIR_BASE_URL}/DocumentReference/{document_id}"
    request = service.projects().locations().datasets().fhirStores().fhir().read(name=name)
    return request.execute()

def update_document_reference(document_id, updated_data):
    service = get_healthcare_service()
    name = f"{FHIR_BASE_URL}/DocumentReference/{document_id}"
    request = service.projects().locations().datasets().fhirStores().fhir().update(
        name=name,
        body=updated_data
    )
    return request.execute()

def delete_document_reference(document_id):
    service = get_healthcare_service()
    name = f"{FHIR_BASE_URL}/DocumentReference/{document_id}"
    request = service.projects().locations().datasets().fhirStores().fhir().delete(name=name)
    return request.execute()




