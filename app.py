from flask import Flask, jsonify
from flask_cors import CORS
import psutil
import json
import time
import threading
import os
import GPUtil
import string

app = Flask(__name__)
CORS(app)

if not os.path.exists('performance.json'):
  with open('performance.json', 'w') as f:
    json.dump({
      'cpu': 0,
      'memory': 0,
      'c_disk': '0 GB/0 GB',
      'd_disk': '0 GB/0 GB',
      'gpu_usage': 0,
      'vram_usage': 0
    }, f)

def get_performance_data():
  gpu_usage, vram_usage = 0, 0
  try:
    gpus = GPUtil.getGPUs()
    if gpus:
      gpu = gpus[0]
      gpu_usage = gpu.load * 100
      vram_usage = gpu.memoryUsed / gpu.memoryTotal * 100
  except Exception as e:
    print(f"Error getting GPU data: {e}")

  return {
    'cpu': psutil.cpu_percent(),
    'memory': psutil.virtual_memory().percent,
    'gpu_usage': gpu_usage,
    'vram_usage': vram_usage
  }

def update_performance_data():
  while True:
    try:
      data = get_performance_data()
      drives = [f"{drive}:\\" for drive in string.ascii_uppercase if os.path.exists(f"{drive}:\\")]
      for drive in drives:
        usage = psutil.disk_usage(drive)
        data[f"{drive[0].lower()}_disk"] = f"{usage.used / (1024 ** 3):.1f} GB/{usage.total / (1024 ** 3):.1f} GB"

      with open('performance.json', 'w') as f:
        json.dump(data, f)
    except Exception as e:
      print(f"Error updating performance data: {e}")
    time.sleep(1)

threading.Thread(target=update_performance_data, daemon=True).start()

@app.route('/performance', methods=['GET'])
def get_performance():
  try:
    with open('performance.json') as f:
      return jsonify(json.load(f))
  except Exception as e:
    return jsonify({'error': f"Error reading performance data: {e}"}), 500

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)