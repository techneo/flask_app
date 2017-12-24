from app import app


from flask import render_template , jsonify , abort , make_response , request , url_for

from flask_httpauth import HTTPBasicAuth

from passlib.hash import sha256_crypt


users = {
    # "suren": "ddd",
    # "john": ""
}

auth = HTTPBasicAuth()

'''
	asset_id int4 NOT NULL,
	asset_name varchar NULL,
	asset_cost int4 NULL,
	asset_desc varchar NULL,
	asset_purchase_date date NULL,
	asset_status varchar NULL,
	asset_category varchar NULL,
	asset_request_date date NULL,
	asset_approval_date date NULL,
	emp_id int4 NULL,
	asset_approval_status varchar NULL,
	PRIMARY KEY (asset_id),
	FOREIGN KEY (emp_id) REFERENCES emp_details(emp_id)



'''

assets = [
    {
        'asset_id': 1,
        'asset_name': u'Lauterbach',
        'asset_desc': u'Debugger for 8051', 
        'asset_cost':12000,
        'asset_purchase_date':'1.12.17',
        'asset_category':'tools',
        'asset_status': False,
        'emp_id':'000',
        'checkout_date':'12.12.17',
        'asset_request_date':'1.1.17',
        'asset_approval_date':'2.1.17',
        'asset_approval_status':True

    },
    {
        'asset_id': 2,
        'asset_name': u'E10A',
        'asset_desc': u'Debugger for RL78', 
        'asset_cost':12000,
        'asset_purchase_date':'1.12.17',
        'asset_category':'tools',
        'asset_status': False,
        'emp_id':'000',
        'checkout_date':'12.12.17',
        'asset_request_date':'1.1.17',
        'asset_approval_date':'2.1.17',
        'asset_approval_status':True
    }
]

#decorators that apply to the function that comes after it
# when a web browser requests either of these two URLs, Flask is 
# going to invoke this function and will pass the return value of 
# it back to the browser as a response
@app.route('/')
@app.route('/index')

def index():
    # docstring for a function definition
    """Return the index page."""
    return render_template("index.html")


@app.route('/hello/<user>/<int:age>')
def hello(user,age):
    """ Function to greet the user """
    return render_template('hello.html',name=user ,age=age)


@app.route('/result')
def result():
   dict = {'phy':50,'che':60,'maths':70}
   return render_template('result.html', result = dict)


#  returning all the assets
@app.route('/api/v1/assets',methods=['GET'])
@auth.login_required
def get_assets(): 
    return jsonify({'assets':[make_public_asset(asset) for asset in assets]})

# returning a specific Asset
@app.route('/api/v1/assets/<int:id>',methods=['GET']) 
@auth.login_required
def get_asset(id): 
    asset = [ asset for asset in assets if asset['asset_id'] == id]
    if len(asset) == 0 :
        abort(404)
    return ( jsonify({'asset':asset[0]}))

    return jsonify({'assets':assets})

# to crate a new asset 
@app.route('/api/v1/assets', methods=['POST'])
@auth.login_required
def create_asset():
    if not request.json or not 'asset_name' in request.json:
        abort(400)
    asset = {
        'asset_id': assets[-1]['asset_id'] + 1,
        'asset_name': request.json['asset_name'],
        'asset_desc': request.json.get('asset_desc', ""),
        'asset_status': request.json['asset_status']
    }
    assets.append(asset)
    return jsonify({'asset': asset}), 201


#update a asset
@app.route('/api/v1/assets/<int:asset_id>', methods=['PUT'])
@auth.login_required
def update_asset(asset_id):
    asset = [asset for asset in assets if asset['asset_id'] == asset_id]
    print asset
    if len(asset) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'asset_name' in request.json and type(request.json['asset_name']) != unicode:
        abort(400)
    if 'asset_desc' in request.json and type(request.json['asset_desc']) is not unicode:
        abort(400)
    if 'asset_status' in request.json and type(request.json['asset_status']) is not bool:
        print type(request.json['asset_status'])
        abort(400)
    asset[0]['asset_name'] = request.json.get('asset_name', asset[0]['asset_name'])
    asset[0]['asset_desc'] = request.json.get('asset_desc', asset[0]['asset_desc'])
    asset[0]['asset_status'] = request.json.get('asset_status', asset[0]['asset_status'])
    return jsonify({'asset': asset[0]})


#delete a asset
@app.route('/api/v1/assets/<int:asset_id>', methods=['DELETE'])
@auth.login_required
def del_asset(asset_id):
    asset = [asset for asset in assets if asset['asset_id'] == asset_id]
    if len(asset) == 0:
        abort(404)
    assets.remove(asset[0])
    return jsonify({'result': True})


@app.route('/api/v1/users',methods=['POST'])
def new_user():
    if not request.json or not 'user_name' in request.json or not 'passkey' in request.json:
        abort(400)
    if request.json['passkey'] == 'freedom':
        users[request.json['user_name'] ]= sha256_crypt.encrypt(request.json['new_password'])
        return jsonify({'result': "password set"}), 201
    else:
        return jsonify({'result': "not set"}), 400


# custom handler for the 400 error
@app.errorhandler(400)
def not_found1(error):
    return make_response(jsonify({'error': 'format wrong'}), 404)

# custom handler for the 404 error
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# this function will add a new field to our asset dict item
# called uri that will hold the api for fecting a individual asset
# this allows the server to change the uri later without affecting the 
# client

def make_public_asset(asset):
    new_asset = {}
    for field in asset:
        if field == 'asset_id':
            new_asset['uri'] = url_for('get_asset', id=asset['asset_id'], _external=True)
        else:
            new_asset[field] = asset[field]
    return new_asset

@auth.verify_password
def verify_pw(username, password):
    if username not in users:
        return False
    else:
        return sha256_crypt.verify(password, users[username])

# @auth.get_password
# def get_pw(username):
#     if username in users and users.get(username)!="":
#         return users.get(username)
#     else:
#         print "no user or pass not set"
#     return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)