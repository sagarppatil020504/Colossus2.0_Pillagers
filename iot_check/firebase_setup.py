import firebase_admin
from firebase_admin import credentials, db
class firebase:
    def fire_main(self):
        try:
            app = firebase_admin.get_app()
        except ValueError:
            # Initialize Firebase Admin
            cred = credentials.Certificate("firebase_json.json")
            app = firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://vishwas-patra-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
if __name__ == "__main__":
    firebase().fire_main()
# -----------------------------------------#####----------------------------------------------------------------#
# import firebase_admin                 thsi is js code for frontend
# import { initializeApp } from "firebase/app";
# import { getStorage } from "firebase/storage";

# // Your Firebase configuration (from firebase.initializeApp())
# const firebaseConfig = {
#     apiKey: "YOUR_API_KEY",
#     authDomain: "YOUR_AUTH_DOMAIN",
#     projectId: "vishwas-patra", //Your Project ID
#     storageBucket: "vishwas-patra.appspot.com", //This line is generally unnecessary.
#     messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
#     appId: "YOUR_APP_ID",
#     measurementId: "YOUR_MEASUREMENT_ID"
# };

# // Initialize Firebase
# const app = initializeApp(firebaseConfig);
# // Get a reference to the storage service, which will automatically use the correct bucket.
# const storage = getStorage(app);

# //Now you can use the storage object to upload, download, etc.
# // ... your Firebase Storage code here ...
