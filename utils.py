class ProgressTracker:
    def __init__(self, key, total):
        def callBack(t, c, i, p):
            print(f"{key} :\n\t total: {t} | completed: {c} | increment: {i} | percentage: {p}\r", end="")
            if (p == 100):
                print()

        self.total = total
        self.callBack = callBack
        self.completed = 0

    def progress(self, inc):
        self.completed += inc
        self._view(inc)

    def _view(self, inc):
        self.callBack(self.total, self.completed, inc, (self.completed/self.total)*100)

def navigateThroughObjects(client, bucket, callBack):
    for page in client.get_paginator('list_objects_v2').paginate(Bucket=bucket):
        for object in page.get('Contents'):
            callBack(object);

def applyForAllBucketsExcept(client, exceptions, callBack):
    def _callBack(client, bucket, callBack):
        if bucket in exceptions:
            return
        callBack(client, bucket)
    utils.applyForAllBuckets(client, lambda client, bucket: _callBack(client, bucket, callBack))

def applyForAllBuckets(client, callBack):
    for bucket in client.list_buckets().get('Buckets'):
        print(bucket)
        callBack(client, bucket.get('Name'))

def print_status(label, callBack):
    try:
        print(f"{label}: {json.dumps(callBack(), indent=1)}")
    except:
        print(f"{label}: not available..")

class Optional:

    def __init__(self):
        self.value = None

    def of(self, value):
        self.value = value
        return self

    def to(self, callBack):
        if self.value:
            return Optional().of(callBack(self.value))
        return Optional()

    def produce(self, default):
        if self.value:
            return self.value
        return default

    def map(self, default, callBack):
        if self.value:
            return callBack(self.value)
        return default

    def ifExists(self, callBack):
        if self.value:
            callBack(self.value)
        return self

    def ifNotExists(self, callBack):
        if not self.value:
            callBack()
        return self

class Region:
    def __init__(self, region_name):
        self.region = {'region': region_name, 'directions': {}}

    def _direction(self, direction, count):
        self.region.get('directions')[direction] = count
        return self

    def central(self, count):
        return self._direction('central', count)

    def east(self, count):
        return self._direction('east', count)

    def west(self, count):
        return self._direction('west', count)

    def north(self, count):
        return self._direction('north', count)

    def south(self, count):
        return self._direction('south', count)

    def southeast(self, count):
        return self._direction('southeast', count)

    def southwest(self, count):
        return self._direction('southwest', count)

    def northwest(self, count):
        return self._direction('northwest', count)

    def northeast(self, count):
        return self._direction('northeast', count)

    def getRegionLabels(self):
        return [f"{self.region.get('region')}-{direction}-{str(number)}" for direction, count in self.region.get('directions').items() for number in range(1, count+1)]

class Regions:
    def __init__(self):
        self.regions = []

    def add(self, region):
        self.regions.append(region)
        return self

    def getRegionLabels(self):
        return [regionLabel for region in self.regions for regionLabel in region.getRegionLabels()]

regions = Regions().add(Region('us').east(2).west(2)).add(Region('ap').south(2).northeast(3).southeast(2)).add(Region('ca').central(1)).add(Region('eu').central(1).west(3).north(1)).add(Region('sa').east(1))
def getRegionLabels():
    return regions.getRegionLabels()
