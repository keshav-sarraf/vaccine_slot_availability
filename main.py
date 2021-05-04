from flask import Flask, jsonify, render_template, request
from api_service import get_all_dist_codes, get_filtered_dists, get_dist_vaccination_calendar, get_dist_id_from_name
from db_service import add_subscriber_to_topic

app = Flask(__name__, static_url_path='/static')


@app.route('/districts', methods=['GET'])
def get_districts():
    query = request.args.get('q')
    filtered_dists = get_filtered_dists(query)
    filtered_dists_list = list(map(lambda x: "{} | {}".format(x["dist_name"], x["state_name"]), filtered_dists))
    filtered_dists_list = filtered_dists_list[0:10]
    return jsonify(filtered_dists_list)


@app.route('/slots/district/<dist_name>')
def get_vaccination_slots(dist_name):

    dist_id = get_dist_id_from_name(dist_name)
    vaccination_calendar = get_dist_vaccination_calendar(str(dist_id))
    return jsonify(vaccination_calendar)


@app.route('/')
def landing_page():
    return render_template("landing.html")


@app.route('/notification-subscription', methods=['POST'])
def accept_notification_subscription():
    payload = request.json

    dist_name = payload["dist_name"]
    notification_token = payload["notification_token"]
    # age_group = payload["age_group"]

    dist_id = get_dist_id_from_name(dist_name)
    result = add_subscriber_to_topic(notification_token, dist_id)

    return jsonify(result)


'''
for notification:
    email,
    device info ?
    
    dist_id:
        dist_name
        notifiers:[
            p1:
                is_notified?
                push_id:
                timestamp_of_subscription
        ]
        
    
'''

#TODO: change api to pick from firestore
#TODO: create apis to refresh firestore periodically
#TODO: create api to accept pin code
#TODO: create api to accept coordinates
#TODO: create api to accept subscription
#TODO: create job to send notification if slots available
#TODO: remove from list after sending notification
#TODO: if sharing url with location, then populate the list automatically
#TODO: create a page to show how to enable notifications
#TODO: validate token before sending notification

if __name__ == '__main__':
    app.run(debug=True)
