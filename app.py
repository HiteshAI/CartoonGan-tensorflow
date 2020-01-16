# from flask import Flask
# import your_module # this will be your file name; minus the `.py`

# app = Flask(__name__)

# @app.route('/test')
# def dynamic_page():
#     return "hello"

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port='8000', debug=True)

    
    

from flask import Flask, request
import my_utils as my_utils
import os
import services
import requests
import io
import pytesseract
import json
from PIL import Image

app=Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():

    my_output={
        'username': "hitesh",
        'password': 'hitesh'
    }

#     print(my_output)

#     return json.dumps(my_output)
    return "Congrats, you reached nulllpointer's root!!!!"





@app.route('/api/tesseract/image/translate', methods=['POST'])
def image_translate():
    if request.method == 'POST':  # this block is only entered when the form is submitted

        img = request.files['file']


        img=Image.open(img,'r').convert('L')

        width, height = img.size
        new_size = width * 6, height * 6
        img = img.resize(new_size, Image.LANCZOS)
        img = img.convert('L')
        img = img.point(lambda x: 0 if x < 155 else 255, '1')
        imagetext = pytesseract.image_to_string(img)
        imagetext.encode(encoding='utf-8')

        print(imagetext)
        # return json_response_text_output(imagetext,"","")
        return imagetext

def json_response_text_output(output, form_values, s):
    my_output = {
        "success": True,
        # "session_id": str(s['sid']),
        # "user": s['username'],
        'message': output,
        # 'data': form_values,

    }
    return json.dumps(my_output, ensure_ascii=False, sort_keys=True)


if __name__ == '__main__':
    # create_app()
    # app.run(host='0.0.0.0', port=5001)

    app.run(host='0.0.0.0', debug=True)
    
