from firebase_admin import firestore

# Use the application default credentials
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

from api_service import get_all_dist_codes

cred = credentials.Certificate("vaccineslotavailability-firebase-adminsdk-6jiff-78515b332d.json")
firebase_admin.initialize_app(cred)
#db = firestore.client()


#dist_codes = get_all_dist_codes()

# doc_ref = db.collection(u'districts')
# for dist in dist_codes:
#     doc_ref.document(str(dist['dist_id'])).set(dist)

#doc_ref = db.collection(u'districts')


# [START send_to_token]
# This registration token comes from the client FCM SDKs.
registration_token = 'd7fftIONwFgXSlVLpabKPF:APA91bEpAxx2o8zL_xIR6kSwsOgZ_liQPgqayARRxHObPJesezLklh4uD32bOvozBzp_JQtu-EOfxT-fPe18JShPN-a5MCJQ2_cgnofDsvWl1oytsofVzaqn8-XsExIIL_6BnLsTmgPn'
# See documentation on defining a message payload.
message = messaging.Message(
    data={
        'score': '850',
        'time': '2:45',
    },
    token=registration_token,
)

# Send a message to the device corresponding to the provided
# registration token.
response = messaging.send(message)
# Response is a message ID string.
print('Successfully sent message:', response)
# [END send_to_token]

