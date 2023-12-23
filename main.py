import jose.jwt
import jose
import requests
import uuid
import datetime
import base64


def token_generator():
    time = datetime.datetime.now() + datetime.timedelta(minutes=4)
    jwt_claims = {
        "iss": "ad0acdf9-0244-4f15-9db4-424171fd18f5",
        "sub": "ad0acdf9-0244-4f15-9db4-424171fd18f5",
        "aud": "https://vendorservices.epic.com/interconnect-amcurprd-oauth/oauth2/token",
        "exp": time.strftime('%s'),
        "jti": uuid.uuid1().__str__()
    }
    newHeaders = {
        "alg": "RS384",
        "typ": "JWT",
        "kid": "kid"
    }
    with open('privatekeylonghealth.pem', 'rb') as fh:
        rsa_signing_jwk = fh.read()
        x = jose.jwt.encode(jwt_claims, rsa_signing_jwk, algorithm='RS384', headers=newHeaders)
        headers = newHeaders
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        data = {
            'grant_type': 'client_credentials',
            'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
            'client_assertion': x
        }
        x = requests.post('https://vendorservices.epic.com/interconnect-amcurprd-oauth/oauth2/token', headers=headers,
                          data=data)
        Access_Token = x.json().get('access_token')
        with open('access_token.txt', 'w') as file:
            file.write(Access_Token)
            print("Token is updated successfully")
            return True
    return False

def generateCCDA():
    with open('access_token.txt', 'r') as file:
        access_token = file.read()
        url = 'https://vendorservices.epic.com/interconnect-amcurprd-oauth/api/FHIR/R4/Patient?given=Pone&family=Dialysis&gender=male&birthdate=1958-05-26&address=123 Anywhere'
        new_headers = {'Content-type': 'application/json', "Authorization": "Bearer %s" % access_token,
                       "Accept": "application/fhir+json", 'Prefer': 'respond-async'}
        response = requests.get(url, headers=new_headers)
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
                        new_url_binary = "https://vendorservices.epic.com/interconnect-amcurprd-oauth/api/FHIR/R4/" + str(url)
                        response = requests.get(new_url_binary, headers=new_headers)
                        convertbytes = response.json().get('data').encode("ascii")
                        convertedbytes = base64.b64decode(convertbytes)
                        decoded_sample = convertedbytes.decode("ascii")
                        print(f"The string after decoding is: {decoded_sample}")

if __name__ == "__main__":
    generateCCDA()