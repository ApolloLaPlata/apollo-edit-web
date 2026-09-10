import urllib.request
req = urllib.request.Request('https://apollolaplata--apollo-render-router-apollo-api.modal.run/generate/image', data=b'{\"prompt\":\"test\",\"steps\":20,\"aspect_ratio\":\"vertical\"}', headers={'Content-Type':'application/json'})
try:
    res = urllib.request.urlopen(req)
    print(res.read())
except Exception as e:
    print(e)
