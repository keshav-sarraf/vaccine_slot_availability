from flask import Flask, jsonify, render_template, request
from api_service import get_all_dist_codes, get_filtered_dists, get_dist_vaccination_calendar, get_dist_id_from_name

app = Flask(__name__, static_url_path='/static')


@app.route('/districts', methods=['GET'])
def get_districts():
    query = request.args.get('q')
    filtered_dists = get_filtered_dists(query)
    filtered_dists_list = list(map(lambda x: "{} | {}".format(x["dist_name"], x["state_name"]), filtered_dists))
    return jsonify(filtered_dists_list)


@app.route('/slots/district/<dist_name>')
def get_vaccination_slots(dist_name):

    dist_id = get_dist_id_from_name(dist_name)
    vaccination_calendar = get_dist_vaccination_calendar(str(dist_id))
    return jsonify(vaccination_calendar)


@app.route('/')
def hello_world():
    return render_template("landing.html")


'''
for notification:
    email,
    device info ?
    
    dist_id:
        dist_name
        notifiers:[
            p1:
                is_notified?
                email:
                push_id:
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

if __name__ == '__main__':
    app.run(debug=True)
