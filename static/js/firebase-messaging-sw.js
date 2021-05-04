// Give the service worker access to Firebase Messaging.
// Note that you can only use Firebase Messaging here. Other Firebase libraries
// are not available in the service worker.
importScripts('https://www.gstatic.com/firebasejs/8.4.3/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/8.4.3/firebase-messaging.js');

// Initialize the Firebase app in the service worker by passing in
// your app's Firebase config object.
// https://firebase.google.com/docs/web/setup#config-object
var firebaseConfig = {
    apiKey: "AIzaSyCLaNNU4xvbXDG412usAzm_woTz3HzTcUA",
    authDomain: "vaccineslotavailability.firebaseapp.com",
    projectId: "vaccineslotavailability",
    storageBucket: "vaccineslotavailability.appspot.com",
    messagingSenderId: "837743212833",
    appId: "1:837743212833:web:12d2f5bdecbf7ad2742660",
    measurementId: "G-HPZFM219CL"
};

firebase.initializeApp(firebaseConfig);

// Retrieve an instance of Firebase Messaging so that it can handle background
// messages.
const messaging = firebase.messaging();

//messaging.onBackgroundMessage((payload) => {
//  self.registration.hideNotification();
//  console.log('[firebase-messaging-sw.js] Received background message ', payload);
//  // Customize notification here
//  const notificationTitle = 'Background Message Title';
//  const notificationOptions = {
//    body: 'Background Message body.',
//    icon: '/static/logo.png'
//  };
//
//  self.registration.showNotification(notificationTitle,notificationOptions);
//});
