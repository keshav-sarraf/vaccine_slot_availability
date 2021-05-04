console.log("Landing Page.JS Called");

var selectedDistrict = null;
var selectedState = null;

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
    selectedState = item.split("|")[1].trim();
    selectedPincode = "";

    $("#slots-table").show();
    $("#slots-table").bootstrapTable('destroy');
    refreshTable(selectedDistrict);
    $("#subscription-div").show();
});

$("#notificationBtn").click(function(){
    //get the token
    notificationToken = getToken();

    if(notificationToken == null){
        alert("Unable to subscribe, please check the details section for probable reasons");
        return;
    }

//    var ageGroup = $('#ageGroupSelector').find(":selected").text();
//    console.log(ageGroup);

    requestBody = {
        "notification_token" : notificationToken,
//        'age_group' : ageGroup,
        'state_name' : selectedState,
        'dist_name' : selectedDistrict,
        'pincode' : selectedPincode,
    };

    $.ajax( "/notification-subscription", {
    data : JSON.stringify(requestBody),
    contentType : 'application/json',
    type : 'POST',
    success : function( response ) {
        console.log(response);
    }
    });

    //send ajax request
});

$(".toast").toast({ autohide: false });
$("#slots-table").hide();
$("#subscription-div").hide();

//Firebase related stuff
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
        saveToken(currentToken);
        //store in session, send to backend in case the user subscribes to updates
    } else {
        // Show permission request UI
        console.log('No registration token available. Request permission to generate one.');
    }
}).catch((err) => {
        console.log('An error occurred while retrieving token. ', err);
});

messaging.onMessage((payload) => {
  console.log('Message payload', payload);
  console.log('Message received. ', payload.notification);
  $("#toast-title").text(payload.notification.title);
  $("#toast-body").text(payload.notification.body);
  $('.toast').toast('show');
});

//https://stackoverflow.com/questions/58146752/firebase-cloud-messaging-web-not-receiving-test-messages

function saveToken(token){
   window.localStorage.setItem('myToken', token);
}

function getToken(){
    return window.localStorage.getItem('myToken');
}