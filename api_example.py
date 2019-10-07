def get_response_from_bitly_api():
    import requests

    class BearerAuth(requests.auth.AuthBase):
        token = None

        def __init__(self, token):
            self.token = token

        def __call__(self, r):
            r.headers["authorization"] = "Bearer " + self.token
            return r

    url = 'https://api-ssl.bitly.com/oauth/access_token'
    data = {
        'client_id': '0e3285aaa788064ed81ca25a4c87add98e42fb91',
        'client_secret': 'cf87938864aa0b7a75c486ad7aa4544e2e48c77f',
        'code': 'd81764b63270a1a6f880b20d41a3ee7f1ad6cfe6',
        'redirect_uri': 'http://example.com/',
    }
    headers = {
        # "Authorization": "Bearer MYREALLYLONGTOKENIGOT",
        'Content-type': 'application/x-www-form-urlencoded', }
    response = requests.post(url, data=data, headers=headers)
    response.text
    'access_token=e7470ba94a7532eeb9244300b4ea63762c35ccaf&login=o_2sqmpodunm&apiKey=R_3fd6e447743f408db4a4282b455f0ebf'

    access_token = 'e7470ba94a7532eeb9244300b4ea63762c35ccaf'
    url = 'https://api-ssl.bitly.com/v4/organizations'
    response = requests.get(url, auth=BearerAuth(access_token))

    bitlink = 'OpjqIE'
    bitlink = 'nlpkg_proposal'
    url = 'https://api-ssl.bitly.com/v4/bitlinks/bit.ly/{bitlink}/countries'.format(
        bitlink=bitlink)
    response = requests.get(url, auth=BearerAuth(access_token))
    response.json()
    # response = requests.post(url, data=data, auth=(user, password))
    import pdb;
    pdb.set_trace()

    response = requests.get('https://www.example.com/',
                            auth=BearerAuth('3pVzwec1Gs1m'))
