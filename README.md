# India_vaccine_slot_availability

https://vaccine-slot-availability.herokuapp.com/#!

## Simple app to send web notification when vaccine slots get available

Uses the following tools:
- Flask : Basic backend 
- HTML + JQuery + Bootstrap : Basic frontend
- Firebase : datastore and notification service provider

### Limitations:
- Not a realtime application, notifications may have some inherent delay
- Limited UI capabilities like search from pin code is not available at the moment
- Works on limited browsers ( which support web push notification ) and additionally browser needs to have permission to show notifications

Vaccine Slot info is periodically fetched from:
https://apisetu.gov.in
