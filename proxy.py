import requests
from flask import Flask, Response, request, render_template, redirect, url_for

app = Flask(__name__)
app.debug = True
default_port = None
server_index = 0
server_list = []
session = {}


@app.route('/', methods=['GET', 'POST'])
def index():
    if len(request.args) > 0:
        command = request.args.get('method')
        if command == 'import':
            return return_both('method=' + command, 'GET')
        if request.method == 'GET':
            return return_one('method=' + command, 'GET')
        else:
            print(request.data)
            return return_one('method=' + command, 'POST', request.data)
    else:
        if session.get('user') is None:
            return redirect(url_for('login'))
        return render_template('database.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    print(request.method)
    if request.method == 'POST':
        code = return_login(form=request.form)
        if code == 200:
            session['user'] = request.form.get('user')
            return redirect(url_for('index'))
        else:
            return render_template('error.html')
    return render_template('login.html')


def return_file(filename):
    global server_index
    server_index += 1
    if server_index == len(server_list):
        server_index = 0
    return Response(requests.get('http://' + server_list[server_index] + '/' + filename))


def return_one(command='', type='GET', data=None):
    global server_index
    server_index += 1
    if server_index == len(server_list):
        server_index = 0
    if type == 'GET':
        return Response(requests.get('http://' + server_list[server_index] + '/?' + command))
    else:
        return Response(requests.post('http://' + server_list[server_index] + '/?' + command, data=data))


def return_login(form):
    response = 400
    for server in server_list:
        response = requests.post('http://' + server + '/', data=form).status_code
    return response


def return_both(command: str, type: str):
    response = ''
    for server in server_list:
        if type == 'GET':
            response = Response(requests.get('http://' + server + '/?' + command))
        # else:  # login
        #     response = Response(requests.post('http://' + server + '/?' + command, data=form))
    return response


if __name__ == '__main__':
    server_list.append('127.0.0.1:8764')
    # server_list.append('')
    app.run(port=8765)
