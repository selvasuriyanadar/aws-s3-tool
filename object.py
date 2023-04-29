import utils
import logic.GrantLogic as GrantLogic

def objectExists(client, bucket_name, object_key):
    try:
        client.head_object(Bucket=bucket_name, Key=object_key)
        return True
    except:
        return False

def getObjectAclResponse(client, bucket_name, key):
    try:
        return utils.Optional().of(client.get_object_acl(Bucket=bucket_name, Key=key))
    except:
        return utils.Optional()

def getAllGrantsExceptOwnerGrant(client, bucket_name, key):
    def _getAllGrantsExceptOwnerGrant(response):
        owner_id = response.get("Owner").get("ID")
        return GrantLogic.parseGrantsAsCondensed(owner_id, response.get("Grants"))
    return getObjectAclResponse(client, bucket_name, key).to(_getAllGrantsExceptOwnerGrant)

def getAccessControlPolicy(client, bucket_name, grants, key):
    owner_id = client.get_object_acl(Bucket=bucket_name, Key=key).get("Owner").get("ID")
    return {'Owner': {'ID': owner_id}, 'Grants': GrantLogic.parseGrantsAsUncondensed(owner_id, grants)}

def copyObject(client_to, client_from, bucket_from, bucket_to, object):
    key = object.get('Key')
    progress_tracker_upload = utils.ProgressTracker(key, object.get('Size'))
    object_details = client_from.get_object(Bucket=bucket_from, Key=key)
    with open('temp/temp_data', 'wb') as data:
        for line in object_details.get('Body'):
            data.write(line)
            progress_tracker_upload.progress(len(line))

    with open('temp/temp_data', 'rb') as data:
        client_to.put_object(Body=data, Bucket=bucket_to, Key=key, ContentLength=object_details.get('ContentLength'), ContentType=object_details.get('ContentType'), Metadata=object_details.get('Metadata'))
        getAllGrantsExceptOwnerGrant(client_from, bucket_from, key).ifExists(lambda grants: client_to.put_object_acl(Bucket=bucket_to, Key=key, AccessControlPolicy=getAccessControlPolicy(client_to, bucket_to, grants, key)))

def copyObjectIfNotExist(client_to, client_from, bucket_from, bucket_to, object):
    if not objectExists(client_to, bucket_to, object.get('Key')):
        copyObject(client_to, client_from, bucket_from, bucket_to, object)

def copyObjectsIfNotExist(client_to, client_from, bucket_from, bucket_to):
    utils.navigateThroughObjects(client_from, bucket_from, lambda o: copyObjectIfNotExist(client_to, client_from, bucket_from, bucket_to, o))

def copy(client_to, client_from, bucket_from, bucket_to, object):
    key = object.get('Key')
    progress_tracker = utils.ProgressTracker(key, object.get('Size'))
    client_to.copy(CopySource={'Bucket': bucket_from, 'Key': key}, Bucket=bucket_to, Key=key, Callback=lambda s: progress_tracker.progress(s), SourceClient=client_from)

def edit(s3, bucket, object, contentType):
    print(object.get('Key'))
    s3.Object(bucket, object.get('Key')).copy_from(
            CopySource={'Bucket': bucket, 'Key': object.get('Key')},
            Metadata={} if (object.get('Metadata') == None) else object.get('Metadata'),
            MetadataDirective="REPLACE",
            ContentType=contentType)
