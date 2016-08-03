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
            if not auth: return False,None

            method,auth=auth.split(" ",1)
            if method.lower() is not 'basic': return False,None

            username,password=base64.b64encode(auth).split(":")
            user=self.authenticate(username,password)
            if user is None: return False,None

            return True,user.username
        except: return False,None

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
    if request.method is not "POST":
        print("404!")
        return HttpResponse(status=404)

    auth=HttpBasicAuthBackend()
    authd,username=auth.isAuthenticated(request)
    if not authd:
        response=HttpResponse(status=401)
        response['WWW-Authenticate']=auth.challengeHeaders()
        print("Challenge!")
        return response

    print("JSON!")
    return JsonResponse(dict(data="Hello!"))