
from app_faceId import app

if __name__ == "__main__":

    app.run(debug=False, ssl_context='adhoc', host=app.config['IP_Server'], port=app.config['PORT_server'])
    # app.run(debug=True, ssl_context='adhoc', port=256, host='192.168.1.183')

