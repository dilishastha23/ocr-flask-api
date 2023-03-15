import os
import json

from flask import Flask,request, render_template
from PIL import Image
from utils.custom_response import custom_response
from utils.custom_decorator import error_handler
from utils.file_upload import upload_file
from utils.get_presigned_url import create_presigned_url

from dashboard.text_extraction import CitizenshipExtraction
import datetime
import ntr
import cv2

app = Flask(__name__)
ALTERNATIVE_DOMAIN = "https://bottle-ml-ocr-citizenship.s3.ap-south-1.amazonaws.com"

def get_s3_url(data, face):
    citizenship_filename = data["fileName"]
    user_id = data["user_id"]
    extension = citizenship_filename.split(".")[-1]
    object_name = f"raw/citizen/{face}/{user_id}/{citizenship_filename}"
    source_url = f"{ALTERNATIVE_DOMAIN}/{object_name}"

    return source_url, extension

app.config["UPLOAD_PATH"]="static/"
@app.route('/')
def home():
    return render_template('home.html')

@error_handler
@app.route('/extractfront', methods=['PUT'])
def extract_front(frontImage):
    print('extracting front...')
    # data = request.get_json()
    face = "front"
    # source_url, extension = get_s3_url(data, face)

    # if extension in ["png", "jpg", "jpeg"]:
        
    extract_citizen = CitizenshipExtraction()
    extract_citizen.read_image(frontImage)
    extract_citizen.get_image_preprocessing()
    data = extract_citizen.get_text_extraction(face)
    print(data)

    # response_body = {
    # "message": f"Data Extracted from {face} face of your Citizenship", 
    # "extracted_data": data,
    # "status": True
    # }
    return data
        
    # else:
    #     response_body = {
    #         "message": "The file extension is not supported you need to upload file in png jepg and jpg format"        }

    return custom_response(200, response_body)

@error_handler
@app.route('/extractback', methods=['POST'])
def extract_back():
    print("\n here\n")
    # data = request.get_json()
    face = "back"
    # source_url, extension = get_s3_url(data, face)
    
    # if extension in ["png", "jpg", "jpeg"]:
    f_back = request.files['back']
    f_front = request.files['front']
    # f_back.save(f_back.filename)
    f_back.save(os.path.join(
                app.config['UPLOAD_PATH'],
                f_back.filename
            ))
    # f_front.save(f_back.filename)
    f_front.save(os.path.join(
            app.config['UPLOAD_PATH'],
            f_front.filename
        ))
    # path = '/home/sudarshan/Desktop/'
    # print(path+f_back.filename)
    # path = os.getcwd()
    # path = os.path.join(dirname, 'OCR/path/to/file/you/want')
    # print("\npath is \n", path)
    # extract_citizen = request.form["fileName"]
    # print("file is", f)
    # jpgfile = Image.open(path+f.filename)
    jpgfile = cv2.imread(os.path.join(
            app.config['UPLOAD_PATH'])+f_back.filename)
    jpgfileFront = cv2.imread(os.path.join(
            app.config['UPLOAD_PATH'])+f_front.filename)
    
    # print(jpgfile.bits, jpgfile.size, jpgfile.format)    
    extract_citizen = CitizenshipExtraction()
    extract_citizen.read_image(jpgfile)
    extract_citizen.get_image_preprocessing()
    data = extract_citizen.get_text_extraction(face)
    
    front_res = extract_front(jpgfileFront)
    # print("\n the front res is \n", front_res)
    
    response_body = {
    "message": f"Data Extracted from {face} face of your Citizenship", 
    "extracted_data_back": data,
    "extracted_data_front": front_res,
    "image": {
        "back": os.path.join(
                app.config['UPLOAD_PATH'],
                f_back.filename),
        "front": os.path.join(
                app.config['UPLOAD_PATH'],
                f_front.filename)
    },
    "status": True
    }
    
    print("\nthe response body is\n", response_body)
    # else:
    #     response_body = {
    #         "message": "The file extension is not supported you need to upload file in png jepg and jpg format"        }

    return render_template("ctizenship_data.html", response = response_body)


UPLOAD_FOLDER = 'files'



@error_handler
@app.route('/extract-data', methods=['PUT'])
def extract_data():
    print('extract-data api hit')
    start_time = datetime.datetime.now()

    front_file = request.files['front']
    back_file = request.files['back']
    print('got files')

    front_extracted_data = extract_front_data(front_file)

    back_extracted_data = extract_back_data(back_file)


    
    
    #upload to s3 
    # print(os.getenv("S3_BUCKET"))
    # print(app.config['S3_BUCKET'])
    #get the url
    
    
    #call the above function




    #transliteration here
    response_body = {
        "message": f"Data Extracted from front face of your Citizenship", 
        "extracted_front_data": front_extracted_data,
        "extracted_back_data": back_extracted_data,
        "status": True
    }

    return custom_response(200, response_body)
    # return {
    #     "body": response_body,
    #     "isBase64Encoded": False,
    # }


def extract_front_data(front_file):
    front_file.save(front_file.filename)
    print('saved front: ', front_file.filename)
    front_url = upload_file(front_file.filename, "ml-ocr")  #make these two uploads async - taking 1 s to upload
    print(front_url)

    front_presigned_url = create_presigned_url('ml-ocr', front_file.filename)
    print(front_presigned_url)
    extract_citizen = CitizenshipExtraction(front_presigned_url)
    print("created CitizenshipExtraction object")

    extract_citizen.read_image()
    print("read image CitizenshipExtraction object")

    # extract_citizen.get_image_preprocessing()
    data = extract_citizen.get_text_extraction('front')
    print("extract data CitizenshipExtraction object", data)
    for k,v in data.items():
        data[k]=ntr.nep_to_rom(v)

    print(type(data))
    print(json.dumps(data))
    return data
    

def extract_back_data(back_file):
    back_file.save(back_file.filename)
    print('saved back : ', back_file.filename )
    back_url = upload_file(back_file.filename, "ml-ocr")    #make these two uploads async - taking 1 s to upload
    print(back_url)

    back_presigned_url = create_presigned_url('ml-ocr', back_file.filename)
    print(back_presigned_url)
    extract_citizen = CitizenshipExtraction(back_presigned_url)
    print("created CitizenshipExtraction object")

    extract_citizen.read_image()
    print("read image CitizenshipExtraction object")

    # extract_citizen.get_image_preprocessing()
    data = extract_citizen.get_text_extraction('back')
    print("extract data CitizenshipExtraction object", data)
    
    print(type(data))
    print(json.dumps(data))
    return data


if __name__ == '__main__':
    app.run(debug = True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['S3_BUCKET'] = "ml-ocr"
    app.config['S3_KEY'] = "AWS_ACCESS_KEY"
    app.config['S3_SECRET'] = "AWS_ACCESS_SECRET"
    app.config['S3_SECRET'] = "AWS_ACCESS_SECRET"
    app.config['S3_LOCATION'] = 'http://{}.s3.amazonaws.com/'.format(app.config['S3_BUCKET'])
