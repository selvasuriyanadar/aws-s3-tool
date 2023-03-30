class ProgressTracker:
    def __init__(self, key, total):
        def callBack(t, c, i, p):
            print(f"{key} :- total: {t} | completed: {c} | increment: {i} | percentage: {p}\r", end="")
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
