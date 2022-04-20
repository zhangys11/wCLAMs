from pyCLAMs import clams
import os, sys, json, uuid
from flask import Flask, render_template, request
import uuid

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 # limit to 5MB

def generate(d, n):

    d = int(d)
    n = int(n)

    X,y = clams.mvg(nobs = n, md = d)

    # get the local file path
    fn = os.path.dirname(os.path.realpath(__file__)) + "/" + str(uuid.uuid4()) + ".csv"

    # save to csv file
    clams.save_file(X,y, fn)

    return fn

def analyze(csv, save_local = False):

    # store html result into a local html file
       
    if save_local:
        
        fn = os.path.dirname(os.path.realpath(__file__)) + "/" + str(uuid.uuid4()) + ".html"    
        
        with open(fn, 'w') as f:
            f.write(clams.analyze_file(csv))
        
        # fn is the local save path
        
    return clams.analyze_file(csv) # return the html content

# routes
@app.route("/", methods=['GET', 'POST'])
def index():
	return render_template("home.html")

@app.route("/about")
def about_page():
	return "Created by Dr. Zhang (oo@zju.edu.cn)"


@app.route("/submit", methods = ['GET', 'POST'])
def run_cla():
	if request.method == 'POST':
		
		r = ''
		use_sample = request.form["use_sample"]

		if (use_sample):
			d = request.form["d"] # distance between means, respect to std, i.e. (mu2 - mu1) / std, or how many stds is the difference.
			n = request.form["nobs"] # number of observations / samples			
			csv = generate(d, n)
		else:			
			f = request.files['dataFile']
			csv = os.path.dirname(os.path.realpath(__file__)) + "/" + str(uuid.uuid4()) + ".csv"
			f.save(csv)

		r = analyze(csv)
		
	return {'message': 'success', 'html': r} # render_template("home.html", use_sample = use_sample, d = d, nobs = n, cla_result = r)

'''
The Flask dev server is not designed to be particularly secure, stable, or efficient. 
By default it runs on localhost (127.0.0.1), change it to app.run(host="0.0.0.0") to run on all your machine's IP addresses.
0.0.0.0 is a special value that you can't use in the browser directly, you'll need to navigate to the actual IP address of the machine on the network. You may also need to adjust your firewall to allow external access to the port.
The Flask quickstart docs explain this in the "Externally Visible Server" section:
    If you run the server you will notice that the server is only accessible from your own computer, not from any other in the network. This is the default because in debugging mode a user of the application can execute arbitrary Python code on your computer.
    If you have the debugger disabled or trust the users on your network, you can make the server publicly available simply by adding --host=0.0.0.0 to the command line.
'''

import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open_new('http://localhost:5005/')
      
if __name__ =='__main__':
    # use netstat -ano|findstr 5005 to check port use
    Timer(3, open_browser).start()
    app.run(host="0.0.0.0", port=5005, debug = True)
    