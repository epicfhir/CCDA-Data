import jose.jwt
import jose
import requests
import uuid
import datetime
import base64
from flask import Flask, render_template, request, redirect, url_for
from main import token_generator

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_form', methods=['POST'])
def process_form():
    if request.method == 'POST':
        # Get form data from the request
        given    = request.form['given']
        family   = request.form['family']
        gender   = request.form['gender']
        birthday = request.form['birthday']
        address  = request.form['address']

        # You can perform any processing or validation here

        # Redirect to a different route with the form data
        return redirect(url_for('result', given=given, family=family, gender= gender, birthday= birthday, address= address))

@app.route('/result')
def result():
    given    = request.args.get('given')
    family   = request.args.get('family')
    gender   = request.args.get('gender')
    birthday = request.args.get('birthday')
    address  = request.args.get('address')
    # the generateCCDA function
    url = f'https://vendorservices.epic.com/interconnect-amcurprd-oauth/api/FHIR/R4/Patient?given={given}&family={family}&gender={gender}&birthdate={birthday}&address={address}'
    with open('access_token.txt', 'r') as file:
        access_token = file.read().strip()
        if access_token:
            new_headers = {'Content-type': 'application/json', "Authorization": "Bearer %s" % access_token,
                           "Accept": "application/fhir+json", 'Prefer': 'respond-async'}
            response = requests.get(url, headers=new_headers)
            if response.status_code == 200:
                patient_data = response.json().get('entry')[0].get('resource')
                patient_id = patient_data.get('id')

                new_url = "https://vendorservices.epic.com/interconnect-amcurprd-oauth/api/FHIR/R4/DocumentReference?subject=" + str(
                    patient_id) + "&category=summary-document"
                new_headers_reference = {'Content-type': 'application/json', "Authorization": "Bearer %s" % access_token,
                                         "Accept": "application/fhir+json", 'Prefer': 'respond-async'}
                document_response = requests.get(new_url, headers=new_headers_reference)

                for resources in document_response.json().get('entry'):
                    for item in resources.get("resource")["type"]["coding"]:
                        if item.get("code") == "34133-9":
                            urls = [data["attachment"]["url"] for data in resources.get("resource").get('content') if
                                    data["attachment"]["contentType"] == "application/xml"]
                            for url in urls:
                                new_url_binary = "https://vendorservices.epic.com/interconnect-amcurprd-oauth/api/FHIR/R4/" + str(
                                    url)
                                response = requests.get(new_url_binary, headers=new_headers)
                                convertbytes = response.json().get('data').encode("ascii")
                                convertedbytes = base64.b64decode(convertbytes)
                                decoded_sample = convertedbytes.decode("ascii")
                                print(f"The string after decoding is: {decoded_sample}")
                                return decoded_sample
            elif response.status_code == 401:
                token_generator()
                with open('access_token.txt', 'r') as file:
                    access_token = file.read().strip()
                    if access_token:
                        new_headers = {'Content-type': 'application/json', "Authorization": "Bearer %s" % access_token,
                                       "Accept": "application/fhir+json", 'Prefer': 'respond-async'}
                        response = requests.get(url, headers=new_headers)
                        if response.status_code == 200:
                            patient_data = response.json().get('entry')[0].get('resource')
                            patient_id = patient_data.get('id')

                            new_url = "https://vendorservices.epic.com/interconnect-amcurprd-oauth/api/FHIR/R4/DocumentReference?subject=" + str(
                                patient_id) + "&category=summary-document"
                            new_headers_reference = {'Content-type': 'application/json',
                                                     "Authorization": "Bearer %s" % access_token,
                                                     "Accept": "application/fhir+json", 'Prefer': 'respond-async'}
                            document_response = requests.get(new_url, headers=new_headers_reference)

                            for resources in document_response.json().get('entry'):
                                for item in resources.get("resource")["type"]["coding"]:
                                    if item.get("code") == "34133-9":
                                        urls = [data["attachment"]["url"] for data in
                                                resources.get("resource").get('content') if
                                                data["attachment"]["contentType"] == "application/xml"]
                                        for url in urls:
                                            new_url_binary = "https://vendorservices.epic.com/interconnect-amcurprd-oauth/api/FHIR/R4/" + str(
                                                url)
                                            response = requests.get(new_url_binary, headers=new_headers)
                                            convertbytes = response.json().get('data').encode("ascii")
                                            convertedbytes = base64.b64decode(convertbytes)
                                            decoded_sample = convertedbytes.decode("ascii")
                                            print(f"The string after decoding is: {decoded_sample}")
                                            return decoded_sample
                        else:
                            return f"Some problem with access token status code {response.status_code}"
        else:
            return "Access token not found"

if __name__ == "__main__":
    app.run()
