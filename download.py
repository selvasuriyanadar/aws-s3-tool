import utils

def download(client_to, client_from, bucket_from, bucket_to, object, file_name):
    key = object.get('Key')
    progress_tracker_download = utils.ProgressTracker(key, object.get('Size'))
    with open(file_name, 'wb') as data:
        client_from.download_fileobj(bucket_from, key, data, Callback=lambda s: progress_tracker_download.progress(s))
