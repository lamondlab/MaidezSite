from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.backends import ModelBackend
import redis, base64

CONTENT_TYPE="application/json-rpc"

class HttpBasicAuthBackend(ModelBackend):
    REALM='PepTrackerRestricted'
     
    def challengeHeaders(self):
        return 'Basic realm="{0}"'.format(HttpBasicAuthBackend.REALM)    

    def isAuthenticated(self, request):
        try:
            auth=request.META.get('HTTP_AUTHORIZATION', None)
            print("AUTH",auth)
            if not auth: return False,None

            method,auth=auth.split(" ",1)
            print("Method:",method,auth)
            if method.lower()!='basic': return False,None

            username,password=base64.b64decode(auth).decode('utf-8').split(":")
            print("U/P:",username,password)
            user=self.authenticate(username,password)
            if user is None: return False,None

            return True,user.username
        except Exception as e: 
            print(e)
            return False,None

REDIS_KEYS=(
    "upsModel",
    "upsStatus",
    "batteryStatus",
    "batteryTime",
    "batteryCapacity",
    "batteryTemperature",
    "batteryTimeRemaining",
    "batteryVoltage",
    "inputVoltage",
    "inputVoltageMax",
    "inputVoltageMin",
    "inputFrequency",
    "inputFailCause",
    "outputStatus",
    "outputVoltage",
    "outputFrequency",
    "outputLoad",
    "outputCurrent",
    "outputEfficiency",
    "outputEnergyUsage",
    "heartbeat",
)
_redis=redis.Redis()

def index(request):
    return render(request, "maidez/index.html")

def heartbeat(request):
    if request.method!='GET': return
    if not request.is_ajax(): return

    data={k:_redis.get(k) for k in REDIS_KEYS}
    for k,v in data.items():
        try: data[k]=v.decode('utf8')
        except AttributeError: data[k]=str(v)

    return JsonResponse(data)

@csrf_exempt
def rpc(request):
    if request.method!="POST": return HttpResponse(status=404)

    auth=HttpBasicAuthBackend()
    authd,username=auth.isAuthenticated(request)
    if not authd:
        response=HttpResponse(status=401)
        response['WWW-Authenticate']=auth.challengeHeaders()
        return response

    data=dict(
        phoneNumber=request.POST['phoneNumber'],
        message=request.POST['message']
    )

    return JsonResponse(data)
