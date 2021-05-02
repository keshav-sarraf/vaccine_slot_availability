from flask import Flask, jsonify, render_template, request
from api_service import get_all_dist_codes, get_filtered_dists

app = Flask(__name__)


@app.route('/districts', methods=['GET'])
def get_districts():
    query = request.args.get('q')
    filtered_dists = get_filtered_dists(query)

    return jsonify(filtered_dists)


@app.route('/')
def hello_world():
    return render_template("landing.html")

'''
for notification:
    email,
    device info ?
'''

if __name__ == '__main__':
    app.run(debug=True)
