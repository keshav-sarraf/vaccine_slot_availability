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

$("#subscribeBtn").click(function(){
    initFCM()
    .then(function(){
        sendSubscriptionRequest();
    });
});

$("#unsubscribeBtn").click(function(){
    initFCM()
    .then(function(){
        sendUnsubscriptionRequest();
    });
});


$("#testBtn").click(function(){
    console.log("Test Called");
    initFCM()
    .then(function(){
        sendTestNotificationRequest();
    });
});

function sendSubscriptionRequest(){
    console.log("sending subscription request");
    //get the token
    notificationToken = getToken();

    if(notificationToken == null){
        alert("Unable to subscribe, are you using chrome browser ?");
        return;
    }

    requestBody = {
        "notification_token" : notificationToken,
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
            alert("You'll get a notification when a slot comes up");
        }
    });
}

function sendUnsubscriptionRequest(){
    console.log("sending un-subscription request");
    //get the token
    notificationToken = getToken();

    requestBody = {
        "notification_token" : notificationToken,
        'state_name' : selectedState,
        'dist_name' : selectedDistrict,
        'pincode' : selectedPincode,
    };

    $.ajax( "/notification-subscription", {
    data : JSON.stringify(requestBody),
    contentType : 'application/json',
    type : 'DELETE',
    success : function( response ) {
        console.log(response);
        alert("Hope you got vaccinated :)");
    }
    });
}

function sendTestNotificationRequest(){
    console.log("sending test notification request");
    //get the token
    notificationToken = getToken();

    console.log("token");
    console.log(notificationToken);

    if(notificationToken == null) {
        alert('Permission not granted to show notifications');
        return
    }

    requestBody = {
        "notification_token" : notificationToken,
        'state_name' : selectedState,
        'dist_name' : selectedDistrict,
        'pincode' : selectedPincode,
    };

    $.ajax( "/notification-test", {
    data : JSON.stringify(requestBody),
    contentType : 'application/json',
    type : 'POST',
    success : function( response ) {
        console.log(response);
    }
    });

    alert("Now close the tab, you'll get a notification in few seconds :)");
}

function initFCM(){

    if(!firebase.messaging.isSupported()) {
        alert("Browser doesn't supports web notifications, use Chrome / Firefox instead");
        throw "Permission Denied";
    }

    var initPromise = navigator.serviceWorker.register('/static/js/firebase-messaging-sw.js')
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
                                    //alert('Permission not granted to show notifications');
                                    throw "Permission Denied";
                                }
                      })
                       .catch((err) => {
                                console.log('An error occurred while retrieving token. ', err);
                                alert('Permission not granted to show notifications');
                                throw "Permission Denied";
                      });

    return initPromise;
}

//Hide the div with subscription options initially
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
    appId: "1:837743212833:web:b8f723e653b52229742660",
    measurementId: "G-0L3592Q6HT"
};

firebase.initializeApp(firebaseConfig);
firebase.analytics();
const messaging = firebase.messaging();

firebaseApiToken = "BE9QCQjrA14YVfoK_-BT3FHHoBO-eyHi5vEzZ-lu5tW-0uuFmTVZ1OVSf0SKPti1iqMf789fe0rizFkZKLA6qr8";

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