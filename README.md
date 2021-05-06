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

### How it works:
- Assume you are new to town and have been invited to a party.
- You go to the party and meet a bunch of people, but they all have complicated names, so instead of learning their names, you give them all different nickname in your head. Lets say you decide to name one of them Ram.
- After interacting with Jack, you come to know you both have a shared interested in movies and both of you are eagerly waiting for new releases
- One day, out of blue a colleague of yous named Shyam tells you that a new movie is about to release next week.
- When you learn about this new movie, the next thing that comes to your mind is thought of your buddy Ram.
- You immediately send him a message with this exciting news and book tickets to the show

Now in this story, 
- Ram is analogous to a user of this website. You don't actually know the real name of Ram, it's just a nickname that you gave him
- The Party is analogus to this website where you meet Ram (user) and learn about his interests in movies (vaccination slots in his area)
- Caterer of the party is Python-Flask ( Backend ) while the decorations are done using HTML, JQuery and Bootstrap ( Frontend )
- You are analogous to a service offered by Google called Firebase Cloud Messaging. You memorize Ram's ( users ) interests and send him a message ( notification ) when you come to know about a new movie ( vaccination slot ) that you think might be of his interest
- Your colleague Shyam is a python script that periodically checks if there are any new movies ( vaccination slots ) about to release. ( In this case, the data is found in API Setu )
- You (FCM) sending a message (push notification) to Ram (user) informing him about the movie (vaccination slot) is how this all sums up :)

