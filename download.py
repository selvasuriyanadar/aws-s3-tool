import utils

def download(client, bucket, object, file_name):
    key = object.get('Key')
    progress_tracker_download = utils.ProgressTracker(key, object.get('Size'))
    with open(file_name, 'wb') as data:
        client.download_fileobj(bucket, key, data, Callback=lambda s: progress_tracker_download.progress(s))
