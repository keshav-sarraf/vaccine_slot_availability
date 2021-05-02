from firebase_admin import firestore

# Use the application default credentials
import firebase_admin
from firebase_admin import credentials

from api_service import get_all_dist_codes

cred = credentials.Certificate("vaccineslotavailability-firebase-adminsdk-6jiff-78515b332d.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


#dist_codes = get_all_dist_codes()

# doc_ref = db.collection(u'districts')
# for dist in dist_codes:
#     doc_ref.document(str(dist['dist_id'])).set(dist)

doc_ref = db.collection(u'districts')
