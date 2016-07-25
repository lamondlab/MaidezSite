from django.shortcuts import render
from django.http import JsonResponse
import redis

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
