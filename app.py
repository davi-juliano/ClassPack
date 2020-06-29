from flask import Flask, Response
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
	return "Index"

@app.route('/optimize')
def optimizer():
	import subprocess
	from flask import request, send_file
	data = list(request.args.values())[1:-1]
	try:
		process = subprocess.Popen(["script/teste.x"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		output, error = process.communicate(('\n'.join(data)).encode('utf-8'))
		#print("> ", output, error)
	except Exception as e:
		print(e, error)
		return '{0}({1})'.format(request.args.get('callback'), {'response': 100, 'error': e})
	else:
		import latex_converter
		import glob2 as gl
		import os
		import json
		filename = gl.glob("*"+str(process.pid)+".tex").pop()
		latex_converter.convert_tex_document(filename)
		loaded_json = json.loads(open(filename.replace(".tex", ".json"), 'r').read())
		print(loaded_json)
		os.remove(filename) #Removes .TEX file
		os.remove(filename.replace(".tex", ".json")) #Removes .JSON file
		process.terminate()
		return '{0}({1})'.format(request.args.get('callback'), {'response': 200, 'file': filename.replace(".tex", ".pdf"), 'found_solution': str(loaded_json['found_solution']), 'number_items': loaded_json['number_items'], 'min_distance': loaded_json['min_distance'], 'solutions': len(loaded_json['solutions'])})


@app.route('/reports/<filename>/pdf', methods=['POST'])
def download(filename):
	from flask import request, send_file
	import glob2 as gl
	if request.method == 'POST':
		print(filename)
		filename = gl.glob("*"+str(filename)+"*.pdf").pop()
		print(filename)
		return send_file(filename, mimetype='application/pdf')
	return '{0}({1})'.format(request.args.get('callback'), {'response': 404})

@app.route('/rows')
def optimize_rows():
	from otimizador_filas import otimizar_filas
	from flask import jsonify
	from flask import request
	from latex_converter import convert_coords_map
	import time
	data = list(request.args.values())[1:-1]
	result = otimizar_filas(
		float(data[0]),
        float(data[1]),
        float(data[2]),
        float(data[3]),
        float(data[4]),
        float(data[5]),
        float(data[6]))
	timestamp = time.time()
	print(result)
	convert_coords_map(result["resposta"], timestamp)
	return '{0}({1})'.format(request.args.get('callback'), {'response': 200, 'timestamp': timestamp})

if __name__ == '__main__':
	app.run()