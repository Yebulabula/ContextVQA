import streamlit as st
import plotly.graph_objects as go
import os
import numpy as np
import json
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import random
import msgpack
import cv2

# Initialize Firebase credentials (dummy credentials for example)
firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')

firebase_credentials="ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAiY29udGV4dHZxYSIsCiAgInByaXZhdGVfa2V5X2lkIjogIjNiMWVhOGQ5ZjBjMDJiYjEwZDQwNTI4YWFlNWFmODI0MDAzMzZlZDEiLAogICJwcml2YXRlX2tleSI6ICItLS0tLUJFR0lOIFBSSVZBVEUgS0VZLS0tLS1cbk1JSUV2UUlCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktjd2dnU2pBZ0VBQW9JQkFRQ1kvdkV3QkpkN2RUcW1cblZkeHFVcExFMFFldTRFbS96dVA3YlV5YmxzUUZrVzhoNjBUUGdORlp0UXo2Z012L1VpZFBIcGxaSjRHWDVLZFhcbldVd2wrZkpHM2phZFhPcEJsaFlXaTBiNGhkWEhOY3NWSjR1dlFab0xrM05IcUJCbGhzSTU5eS96VU9QTTExc2xcbkRIVXVTL3ZhaGg4VHBwWEVubnRGV2lxNkYrTitmQmxhL3BtQlA1RDNuNG5qMnhObzgwbWsva3V3UjY0akpSZC9cbkVXeTZUaGExOXhPc3hWUFhCRUxFRXlLTGY2RzYwbU9jbnZpQWRwcU5MU2J0MUlwZUMwaWw0RlFuQUcwUUR3c3FcbmE5ay90b2t0OWs2NUFzc085dFcvVjcrTzVodmlySXUwL1pneXV3bGowbmNGRHNYb211UTRndXQ0Q3g3UUp2bndcbnA5Q3BMNTJaQWdNQkFBRUNnZ0VBRUNIdHo3amtPajNwd2NsUzlSa2c1Y1QrME9kUWozdWkyWXUwWk1HWWlOZkZcbmhxZVd1V1NsYnBhak9EVGxqZFlkVS8vdmZwR21YaHhic3QrMUlsb0JQSXpJNkgzNEs1TkdYL2t1c2h6MnBrdGJcblR5ODgwTzJUYno0TWpWVkE2VnUwMWtUazF2ekVFSUR5Mk95LzNISmhxN0N4elRJbkg3VHdYYWM4MHlPYXR1YjRcblRWMGNFYXRnVUdHQlJudjRzbVVmVG1LeU9MeFkvdWxEbllPTWtmRXlEL2lzaVlhaTBCbEY4RC9CbGlCVmJEVERcbk0veEthM21yYkh0YU0zTVVLVVdWZ1JFTFlOU0IwbWcxRGVDdldSM2RwQ1JxSUg4dWJzMGlGc0JvVG4vb0NNbUpcbkdpaHA1OGtTSlV2d2c3YWJSKzRpd2liaktrdFhEYjRrejFiNlN2MElTd0tCZ1FESlBObE8vMk12ZmtwZ1h6SDhcbmlnNW1CbGI2VWRkR29QT1pBTDdmeHpDVTd1TmtTTHJXUEVkY2gzcDNKV05tNDR6SWp0czJqd0VaZHBWdXdxTS9cbnY1Q2lwZExHMCtEMUhIL1BJK2lhUUJLWWExbHZWMHI0S2kxVWJiVFYzOVBPbkJ1S2RIZ3BRNkRhUS9tQ2RTK2hcbnkwQllXd0NJdUIzRUg1Wk5pTDY4azJHMnV3S0JnUURDb1ZnVkUvTTgrWnVpZUlUanZDSk5hNUYrakVMaXlQVlVcbitXRlBXQkpmN2tmRktuZHRleXdiZUR0U2NJRWV5OXJyVWo0anRyMCs2NDM0UTVoS2pPM2Q3c1VGRTlxcms2K09cbngrOUhtYlB6OGg3N3d2TXc3dXFncFEvZzlwUkJOZGFHS2FCMGszUWh6OFY2QXQra01sZkN6NXl0RGk5SUZ3c0RcblM3VmdqQ2E1dXdLQmdBemMyOU1GMWZRcU1WelptTnRZZzdVWHdLVjlaN0kzQlhzSkppb3RsRGhnMEo0UFhBbm5cbmpuUW1vTGhPNW55a0hOS1E5d2dVdWZCRHVTZDhQMjBLdEpjQTNHa2pEK1Q2N2x4eUlpTUI1MjVncGpYTXNaa05cbk1ScU5iSnFqRk9uRzVxZkI3QkJQSjAvc09sMlJXZnNRZjh0bC9iRy9lditYT1VjNWIxK2tXQUdUQW9HQURyTk5cbkNkcUY1cmNic0R2V0hiVmFDZXIwQkZEbnhHVlZVbU83bTlpVkdyWE9xZSs1TVlXNklTRUZxZ1poV2tnZmN1SzFcbld0RTBuZ29Bb1IzSjVPZWNGOFV2RUdFZGhSUVVrSDQ5Ym5VSGlJZGpHN1R2MVdSV1NHZnZPUmltdmY0cEE5MGxcbkIya1R2bklKQWx3eE5CK3hUVCtOSCswUVdTdVVZMTFXaDhKT01uMENnWUVBaHlYUGkxaC9MMWZybW1lWFlKTWRcblpROEhrT3dTVGdrelF6eER4WWttQ1dJN1lIeThzbU9SUGRSRlBOVEpUMVVRU0Y1d2Mwd1pENlUvTnFKMGlqTEtcblFqYzBOVUlkNmhlVFQ3cXpwdnp4VFZCcFNtbFJCVm1MTGJ3Q0plditQajczaU0rZEtSemIxYmpBQ1lEamM5OWhcbjhVazFDZW1GWXhzS2s5Z1Y0bktaQ2M4PVxuLS0tLS1FTkQgUFJJVkFURSBLRVktLS0tLVxuIiwKICAiY2xpZW50X2VtYWlsIjogImZpcmViYXNlLWFkbWluc2RrLXRxc2I3QGNvbnRleHR2cWEuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJjbGllbnRfaWQiOiAiMTA1OTg2MTIxMjI3NjY5MjQ1MDM1IiwKICAiYXV0aF91cmkiOiAiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tL28vb2F1dGgyL2F1dGgiLAogICJ0b2tlbl91cmkiOiAiaHR0cHM6Ly9vYXV0aDIuZ29vZ2xlYXBpcy5jb20vdG9rZW4iLAogICJhdXRoX3Byb3ZpZGVyX3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vb2F1dGgyL3YxL2NlcnRzIiwKICAiY2xpZW50X3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vcm9ib3QvdjEvbWV0YWRhdGEveDUwOS9maXJlYmFzZS1hZG1pbnNkay10cXNiNyU0MGNvbnRleHR2cWEuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJ1bml2ZXJzZV9kb21haW4iOiAiZ29vZ2xlYXBpcy5jb20iCn0K"

if firebase_credentials:
    if not firebase_admin._apps:
        cred = credentials.Certificate(json.loads(base64.b64decode(firebase_credentials).decode('utf-8')))
        firebase_admin.initialize_app(cred)

# Connect to Firestore
db = firestore.client()

@st.cache_data
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
    
    
@st.cache_data
def load_scene_annotations():
    with open('scene_annotations.msgpack', 'rb') as file:
        return msgpack.unpack(file, raw=False)
    
# Function to save context data to Firestore
def save_context_data(data):
    db.collection('Second_Round_Replacement_Changes').add(data)

# Function to generate and return a confirmation code
def generate_survey_code():
    return 'CQA_' + ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10))

# Streamlit app configuration
st.set_page_config(
    page_title="ContextQA Data Collection App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("ContextQA")

ROOT_1 = "3D_scans"
# Get sorted scene IDs that start with 'scene'
# SCENE_IDs = sorted([scene for scene in os.listdir(ROOT_1) if scene.startswith('scene')])

SCENE_IDs = ['09582225-e2c2-2de1-9564-f6681ef5e511', '0cac753c-8d6f-2d13-8e27-e0664fc33bb9', '0cac7558-8d6f-2d13-8fe1-c8af0362735d', '0cac7564-8d6f-2d13-8cb2-8b01c0a1b3d5', '0cac75ad-8d6f-2d13-8c74-5de4dfc4affc', '0cac75c4-8d6f-2d13-8c37-fcfaf141ae5a', '0cac75d0-8d6f-2d13-8c26-d771a31c3f50', '0cac760f-8d6f-2d13-8d9d-2d8df8f8cb6e', '0cac7642-8d6f-2d13-8f9f-eb19016049fa', '0cac7648-8d6f-2d13-8e30-76663c19baa4', '0cac7678-8d6f-2d13-8da3-dba8636cef51', '0cac768c-8d6f-2d13-8cc8-7ace156fc3e7', '10b17971-3938-2467-8a86-2b42613aa7ec', '13af338e-7397-2e54-84fc-fa003f91ac0c', '1776ad7e-4db7-2333-89e1-66854e82170c', '1d233ffe-e280-2b1a-8f1e-7ddb66c98d36', '1d234006-e280-2b1a-8e34-b2f670259e8d', '1d234010-e280-2b1a-8da8-205855a16b6b', '20c993b7-698f-29c5-847d-c8cb8a685f5a', '20c993c1-698f-29c5-86b8-50a2a0907e2b', '20c993c5-698f-29c5-8604-3248ede4091f', '210cdbab-9e8d-2832-85fa-87d12badb00e', '210cdbb2-9e8d-2832-87e5-7e474cf621ea', '283ccfeb-107c-24d5-8bbf-05519a3c7c47', '2e36952b-e133-204c-911e-7644cb34e8b2', '2e36953b-e133-204c-931b-a2cf0f93fed6', '2e36954b-e133-204c-92ad-1a66c6f63e1a', '2e36955d-e133-204c-90da-122ae14d42a3', '352e9c30-69fb-27a7-8b19-c703f0e190da', '352e9c36-69fb-27a7-889f-69b450a22b74', '352e9c40-69fb-27a7-8a6d-d2ca32644e09', '352e9c46-69fb-27a7-8b1d-bc83c253c676', '352e9c57-69fb-27a7-8bc7-4cf12e417e21', '355465d4-d29b-29f9-9550-e366a10d6924', '38770cb0-86d7-27b8-8466-1782505891fd', '3b7b33a9-1b11-283e-9b02-e8f35f6ba24c', '41385847-a238-2435-838b-61864922c518', '4138584b-a238-2435-8128-a939fb07c1c8', '422885af-192d-25fc-8651-420062adb475', '422885bd-192d-25fc-8571-abff2237f383', '422885e9-192d-25fc-87a9-7013fe4114f2', '4238490c-60a7-271e-9f38-3c651e3b3912', '43b8cae1-6678-2e38-9865-c19c07c25015', '43b8caed-6678-2e38-98f8-a76f51ef79af', '4731976a-f9f7-2a1a-9737-305b709ca37f', '4731977c-f9f7-2a1a-976c-34c48a84405c', '48005c65-7d67-29ec-85e0-6a925eb15a27', '4a9a43e0-7736-2874-87ac-c589da4d0f00', '4d3d829e-8cf4-2e04-8318-b76f02d91c93', '4d3d82a2-8cf4-2e04-810b-7634c83eed98', '4d3d82b0-8cf4-2e04-80a8-c955ea964c2f', '4e858c81-fd93-2cb4-8469-d9226116b5de', '4fbad31a-465b-2a5d-8566-f4e4845c1a78', '501ebf0b-a3bb-263f-86fd-7ef000a19588', '5104a9c7-adc4-2a85-9026-45557dcf9a87', '5341b7bf-8a66-2cdd-8794-026113b7c312', '5341b7db-8a66-2cdd-85c5-66dbe881bd5f', '5341b7e1-8a66-2cdd-87a3-02aad508ff86', '54b263a3-0199-2df4-87db-40539528902d', '55551077-36f1-29c0-89ec-2e7690991cb2', '5555107f-36f1-29c0-8903-9b66fb2301d0', '5555108d-36f1-29c0-8b37-5efa2bef59d4', '5630cfc9-12bf-2860-84ed-5bb189f0e94e', '5630cfcb-12bf-2860-87ee-b4e4a5bf0cb0', '5630cfcd-12bf-2860-87f0-65937859709c', '5630cfcf-12bf-2860-8784-83d28a611a83', '5630cfdc-12bf-2860-87b7-c7eab95718be', '569d8f0d-72aa-2f24-8ac6-c6ee8d927c4b', '569d8f13-72aa-2f24-8b64-3bde3b0603ab', '56d957ed-0184-2301-8f4f-616c3b537e45', '634b2181-f5d0-2fb7-8547-fd27b0795137', '634d11d3-6833-255d-8cb0-12c4fb3ea031', '63b87cf1-ef3f-28f2-871a-c1551f129ce6', '68bae76e-3567-2f7c-82bd-a09641695364', '68bae772-3567-2f7c-804c-d77a47cdc508', '6993478e-1286-2e5b-82d0-eb36d75214de', '6a36052d-fa53-2915-9764-30d81b2cc2b5', '6a36054b-fa53-2915-946e-4ec15f811f6e', '6bde6043-9162-246f-8e11-613aba0df55c', '6bde604b-9162-246f-8fb2-2dea80e7fb4c', '6bde6053-9162-246f-8d5d-54e5e3dd721d', '6bde6070-9162-246f-8ea9-c8bbe5d7133a', '6bde6081-9162-246f-8c4e-ffaf709d17b1', '6bde608b-9162-246f-8d16-901b429b2563', '6bde608d-9162-246f-8dde-3f158d134d50', '6bde6091-9162-246f-8ea8-fdfd6c0a7f77', '6bde609b-9162-246f-8f90-c3d2444a5ab8', '6bde609d-9162-246f-8e6e-a3f462f77042', '6bde60a3-9162-246f-8ca3-48f7e86e95b8', '6bde60a9-9162-246f-8f1a-2441db12c4d1', '6bde60c0-9162-246f-8d1f-32543babecfb', '6bde60cb-9162-246f-8cf5-d04f7426e56f', '6bde60d8-9162-246f-8f11-834bec23f91e', '6bde60e0-9162-246f-8df9-b07dc8fa8ddf', '6ed38500-7db9-2d45-810c-865e82827b54', '7272e161-a01b-20f6-8b5a-0b97efeb6545', '73315a2b-185c-2c8a-8772-fe23ddd2f531', '73315a2d-185c-2c8a-87e9-d8dfe07ae3cb', '751a5598-fe61-2c3b-8cf2-1c23632af9b4', '751a55a1-fe61-2c3b-8df5-925bfeac2496', '751a55a3-fe61-2c3b-8d1b-daad80d1af30', '75c25973-9ca2-2844-96f4-90cd531364ac', '75c25975-9ca2-2844-9769-84677f46d4cf', '75c259a1-9ca2-2844-973c-adc28f935d5d', '77361fbc-d054-2a22-8bd1-20da69ee28dc', '77361fca-d054-2a22-8974-547ca1fbb90f', '77361fd0-d054-2a22-8b5a-9d2acada2031', '7747a506-9431-24e8-87d9-37a5654d41f4', '7747a514-9431-24e8-8505-5979f3f20906', '77941460-cfdf-29cb-86c7-1f60e2ecd07a', '7ab2a9d1-ebc6-2056-8880-07b5c7404d58', '80b8588f-4a8d-222f-8712-eaa02a5450a9', '87e6cf7b-9d1a-289f-8692-57e5757dac99', '8eabc414-5af7-2f32-8797-72769173455b', '8eabc426-5af7-2f32-87bb-a16609b099e3', '8eabc42c-5af7-2f32-87c4-bf646779aa62', '8eabc435-5af7-2f32-85c3-163c1fa6e280', '8eabc44b-5af7-2f32-8553-18fd693ab49f', '8eabc451-5af7-2f32-87b5-026aa18e3190', '8eabc45f-5af7-2f32-8528-640861d2a135', '8eabc469-5af7-2f32-840f-c1be88e46c62', '8f0f1437-55de-28ce-828e-dbf210a7f472', '8f0f1467-55de-28ce-8331-b670a7274af9', 'a0905fd9-66f7-2272-9dfb-0483fdcc54c7', 'scene0014_00', 'scene0016_00', 'scene0019_00', 'scene0026_00', 'scene0028_00', 'scene0033_00', 'scene0037_00', 'scene0160_00', 'scene0163_00', 'scene0165_00', 'scene0170_00', 'scene0171_00', 'scene0173_00', 'scene0179_00', 'scene0180_00', 'scene0181_00', 'scene0184_00', 'scene0186_00', 'scene0187_00', 'scene0188_00', 'scene0189_00', 'scene0191_00', 'scene0196_00', 'scene0199_00', 'scene0203_00', 'scene0204_00', 'scene0208_00', 'scene0212_00', 'scene0213_00', 'scene0218_00', 'scene0220_00', 'scene0222_00', 'scene0223_00', 'scene0225_00', 'scene0234_00', 'scene0239_00', 'scene0243_00', 'scene0244_00', 'scene0245_00', 'scene0249_00', 'scene0251_00', 'scene0252_00', 'scene0253_00', 'scene0254_00', 'scene0259_00', 'scene0261_00', 'scene0262_00', 'scene0263_00', 'scene0265_00', 'scene0266_00', 'scene0267_00', 'scene0270_00', 'scene0272_00', 'scene0274_00', 'scene0275_00', 'scene0276_00', 'scene0281_00', 'scene0283_00', 'scene0287_00', 'scene0288_00', 'scene0292_00', 'scene0294_00', 'scene0296_00', 'scene0297_00', 'scene0300_00', 'scene0305_00', 'scene0306_00', 'scene0307_00', 'scene0311_00', 'scene0313_00', 'scene0314_00', 'scene0317_00', 'scene0319_00', 'scene0320_00', 'scene0321_00', 'scene0324_00', 'scene0326_00', 'scene0329_00', 'scene0330_00', 'scene0331_00', 'scene0336_00', 'scene0339_00', 'scene0340_00', 'scene0342_00', 'scene0344_00', 'scene0345_00', 'scene0347_00', 'scene0351_00', 'scene0356_00', 'scene0358_00', 'scene0359_00', 'scene0361_00', 'scene0362_00', 'scene0363_00', 'scene0366_00', 'scene0368_00', 'scene0371_00', 'scene0373_00', 'scene0374_00', 'scene0376_00', 'scene0380_00', 'scene0386_00', 'scene0387_00', 'scene0391_00', 'scene0392_00', 'scene0394_00', 'scene0399_00', 'scene0400_00', 'scene0401_00', 'scene0402_00', 'scene0403_00', 'scene0406_00', 'scene0407_00', 'scene0409_00', 'scene0411_00', 'scene0417_00', 'scene0418_00', 'scene0422_00', 'scene0424_00', 'scene0427_00', 'scene0430_00', 'scene0434_00', 'scene0435_00', 'scene0436_00', 'scene0437_00', 'scene0438_00', 'scene0440_00', 'scene0446_00', 'scene0447_00', 'scene0448_00', 'scene0449_00', 'scene0450_00', 'scene0451_00', 'scene0453_00', 'scene0455_00', 'scene0456_00', 'scene0457_00', 'scene0458_00', 'scene0459_00', 'scene0467_00', 'scene0472_00', 'scene0476_00', 'scene0479_00', 'scene0480_00', 'scene0481_00', 'scene0489_00', 'scene0490_00', 'scene0492_00', 'scene0493_00', 'scene0494_00', 'scene0495_00', 'scene0497_00', 'scene0498_00', 'scene0500_00', 'scene0502_00', 'scene0505_00', 'scene0506_00', 'scene0508_00', 'scene0511_00', 'scene0513_00', 'scene0517_00', 'scene0518_00', 'scene0521_00', 'scene0525_00', 'scene0528_00', 'scene0529_00', 'scene0536_00', 'scene0537_00', 'scene0538_00', 'scene0540_00', 'scene0544_00', 'scene0547_00', 'scene0548_00', 'scene0549_00', 'scene0550_00', 'scene0555_00', 'scene0557_00', 'scene0558_00', 'scene0560_00', 'scene0563_00', 'scene0566_00', 'scene0567_00', 'scene0568_00', 'scene0570_00', 'scene0572_00', 'scene0573_00', 'scene0575_00', 'scene0578_00', 'scene0579_00', 'scene0580_00', 'scene0582_00', 'scene0583_00', 'scene0586_00', 'scene0589_00', 'scene0591_00', 'scene0592_00', 'scene0594_00', 'scene0595_00', 'scene0596_00', 'scene0598_00', 'scene0599_00', 'scene0600_00', 'scene0604_00', 'scene0609_00', 'scene0610_00', 'scene0611_00', 'scene0612_00', 'scene0613_00', 'scene0614_00', 'scene0615_00', 'scene0616_00', 'scene0619_00', 'scene0620_00', 'scene0621_00', 'scene0623_00', 'scene0624_00', 'scene0627_00', 'scene0628_00', 'scene0630_00', 'scene0634_00', 'scene0640_00', 'scene0642_00', 'scene0645_00', 'scene0648_00', 'scene0652_00', 'scene0653_00', 'scene0654_00', 'scene0655_00', 'scene0656_00', 'scene0661_00', 'scene0662_00', 'scene0678_00']

SCENE_ID_TO_FILE = {
    scene_id: os.path.join(ROOT_1, scene_id, f'{scene_id}_filtered_vh_clean_2.npz') 
    if scene_id.startswith('scene') 
    else os.path.join(ROOT_1, scene_id, f'{scene_id}._vh_clean_2.npz') 
    for scene_id in SCENE_IDs
}


def read_instance_labels(scene_id):
    return load_json(f'{ROOT_1}/{scene_id}/{scene_id}_id2labels.json')

@st.cache_resource
def load_mesh(ply_file):
    return np.load(ply_file, allow_pickle=True, mmap_mode='r')

def initialize_plot(vertices, triangles, vertex_colors, annotations):
    trace1 = go.Mesh3d(x=vertices[:, 0], y=vertices[:, 1], z=vertices[:, 2], i=triangles[:, 0], j=triangles[:, 1], k=triangles[:, 2], vertexcolor=vertex_colors, opacity=1.0)
    fig = go.Figure(data=[trace1])

    for annotation in annotations:
        annotation['font'] = dict(color='white', size=12)  # Set font to white
        annotation['bgcolor'] = 'black'  # Add a black background for contrast
    
    fig.update_layout(
        scene=dict(
            aspectmode='data',
            annotations=annotations,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False)
        ),
        width=900,
        height=900,
        margin=dict(l=0, r=10, b=0, t=20),
        updatemenus=[
            dict(
                type="dropdown",
                direction="down",
                buttons=[
                    dict(args=["scene.annotations", annotations], label="Show Object Names", method="relayout"),
                    dict(args=["scene.annotations", []], label="Hide Object Names", method="relayout")
                ],
                showactive=True,
                xanchor="left",
                yanchor="top"
            ),
        ]
    )
    
    return fig

def initialize_state():
    if 'scene_id' not in st.session_state:
        st.session_state.scene_id = None

    if 'annotations' not in st.session_state:
        st.session_state.annotations = load_scene_annotations()
        
    if 'survey_code' not in st.session_state:
        st.session_state.survey_code = generate_survey_code()
        
        
def refresh_scene():
    if st.session_state.scene_id is None:
        st.session_state.scene_id = random.choice(list(SCENE_ID_TO_FILE.keys()))
        scene_id = st.session_state.scene_id
        ply_file = SCENE_ID_TO_FILE[scene_id]
        mesh_data = load_mesh(ply_file)
        vertices, triangles, vertex_colors = mesh_data.values()
        annotations = st.session_state.annotations[scene_id]
        st.session_state.fig = initialize_plot(vertices, triangles, vertex_colors, annotations)

initialize_state()

if 'fig' not in st.session_state:
    refresh_scene()

guideline_text = """
<span style="color:brown;">**Welcome!**</span>

Explore the provided 3D scene visualization and propose **five** hypothetical ways to **replace existing objects** with **new objects that are not currently present in the scene**.

**Consider the example scene below, possible object replacements can include:** (*This is just an example; please do not use it to write descriptions.*)

- The white cabinet near to the clock and table has been replaced with a yellow bookshelf.
- The coffee table in front of the couch has been replaced with two armchairs.

<img style='display: block; margin: auto; max-width: 30%; max-height: 30%;' src='data:image/png;base64,{}'/>


<span style="color:brown;">**Instructions:** </span>

<span style="color:brown;">- Object replacement has to be spatially feasible within the scene's layout </span>

<span style="color:brown;">- Each description must clearly and uniquely indicate the locations of the object(s) being replaced and what they are replaced with. Ambiguous or wrong descriptions will be </span> <span style="color:red;">**rejected**.</span> 

<span style="color:red;"> Good Description: </span> The red chair next to the desk has been replaced with a trash can.
<span style="color:green;"> Bad Description: </span> A chair has been replaced with something. (which chair?, what is it replaced with?)

<span style="color:brown;">- Each description should replace different objects from the scene. </span>

<span style="color:brown;">- Each description should be more than 10 words long. </span>

<span style="color:brown;">- All object replacements must occur within the same scene and be independent of one another. </span>

If you encounter any issues with the scene, please refresh the page to load a new one. Once you have finished the task, click the **Submit** button to receive your Completion Code.

*Please use your imagination and creativity to come up with unique and interesting replacements!*
"""

@st.cache_resource
def render_img_html(image_b64):
    st.markdown(f"<img style='max-width: 40%;max-height: 40%;' src='data:image/png;base64, {image_b64}'/>", unsafe_allow_html=True)

@st.cache_resource
def image_to_base64(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    target_size = (800, 800)
    resized_image = cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)
    
    _, encoded_image = cv2.imencode(".png", resized_image)
    base64_image = base64.b64encode(encoded_image.tobytes()).decode("utf-8")
    return base64_image

with st.expander("**Data Collection Guidelines --Please Read**", expanded=True, icon="📝"):
    image_path = "example.png"
    st.markdown(guideline_text.format(image_to_base64(image_path)), unsafe_allow_html=True)

left_col, right_col = st.columns([2, 1])

with right_col:
    
    
    with st.form(key="question_answer_form"):
        scene_id = st.session_state.scene_id
        changes = []
        
        for i in range(1,  6):
            # Plain text labels without HTML for text_area
            st.markdown(f"<div style='font-weight: bold; font-size: 20px;'>Replacement Change{i}</div>", unsafe_allow_html=True)
            context_change = st.text_area(f"Describe a possible object replacement within the scene in details.", key=f"change{i}", placeholder="Type here...", height=10)

        submitted = st.form_submit_button("Submit")
        if submitted:
            # Extract changes using list comprehension
            changes = [st.session_state.get(f'change{i}') for i in range(1, 6)]
            
            # Check if all changes are unique and non-empty
            if len(set(changes)) < len(changes):
                st.warning("Please ensure that all changes are unique.")
            elif not all(changes):
                st.warning("Please fill in all the changes.")
            elif not all(len(change.split()) >= 10 for change in changes):  # Check if each change has at least 10 words
                st.warning("Please ensure that all changes are at least 10 words long.")
            else:
                # Proceed with success case
                st.session_state.survey_code = generate_survey_code()
                st.success(f"Congratulations! Your Completion Code is: {st.session_state.survey_code}. Please submit this code to CloudResearch.")
                
                # Prepare entry for saving
                entry = {
                    'scene_id': scene_id,
                    'changes': changes,
                    'survey_code': st.session_state.survey_code
                }
                save_context_data(entry)

with left_col:
    if 'fig' not in st.session_state:
        st.session_state.fig = refresh_scene()
    
    id2labels = read_instance_labels(st.session_state.scene_id)
    excluded_categories = {'wall', 'object', 'floor', 'ceiling'}
    objects_by_category = {}
    for label in id2labels.values():
        category = label.split('_')[0]
        objects_by_category.setdefault(category, []).append(label)

    summary_text = "This scene contains " + ", ".join(
        f"{len(labels)} {category + ('s' if len(labels) > 1 else '')}"
        for category, labels in objects_by_category.items() if category not in excluded_categories
    ) + "."

    st.markdown(f"\n{summary_text}")
    
    st.plotly_chart(st.session_state.fig, use_container_width=True)
