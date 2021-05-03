console.log("Landing Page.JS Called");

function refreshTable(selectedDistrict){
    $.get("/slots/district/" + selectedDistrict, function(response){
//        console.log(response)
        $("#slots-table").bootstrapTable({
            data: response
        });
    });
}

//autocomplete
$('.basicAutoComplete').autoComplete({
    resolverSettings: {
        url: '/districts'
    },
    minLength: 1
});

//on selection
$('.basicAutoComplete').on('autocomplete.select', function (evt, item) {
    console.log("item selected - " + item);
    selectedDistrict = item.split("|")[0].trim();
    $("#slots-table").bootstrapTable('destroy');
    refreshTable(selectedDistrict);
});


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
firebase.analytics();
const messaging = firebase.messaging();
firebaseApiToken = "BAEa3MCLg6weOFE9wYEZQ17NAAeOSMpevbXFy_Vttn2iAqds22Pwu9lS90MYbOxxueNbyj3Yn_FTe2e2xJoENKk";

navigator.serviceWorker.register('/static/js/firebase-messaging-sw.js')
.then(function(registration){
    console.log("1");
    return messaging.getToken({
        vapidKey: firebaseApiToken,
        serviceWorkerRegistration: registration
    });
})
.then((currentToken) => {
    console.log("2");

    if (currentToken) {
        console.log("Token Available \n");
        console.log(currentToken);
        //store in session, send to backend in case the user subscribes to updates
    } else {
        // Show permission request UI
        console.log('No registration token available. Request permission to generate one.');
    }
}).catch((err) => {
        console.log('An error occurred while retrieving token. ', err);
});

messaging.onMessage((payload) => {
  console.log('Message received. ', payload);
});


//https://stackoverflow.com/questions/58146752/firebase-cloud-messaging-web-not-receiving-test-messages
