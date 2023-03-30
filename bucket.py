import utils
import logic.GrantLogic as GrantLogic

def bucketExists(client, bucket_name):
    try:
        client.head_bucket(Bucket=bucket_name)
        return True
    except:
        return False

def createBasicBucket(client, bucket_name, region):
    client.create_bucket(Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region})

def getBucketAclResponse(client, bucket_name):
    try:
        return utils.Optional().of(client.get_bucket_acl(Bucket=bucket_name))
    except:
        return utils.Optional()

def getAllGrantsExceptOwnerGrant(client, bucket_name):
    def _getAllGrantsExceptOwnerGrant(response):
        owner_id = response.get("Owner").get("ID")
        return GrantLogic.parseGrantsAsCondensed(owner_id, response.get("Grants"))
    return getBucketAclResponse(client, bucket_name).to(_getAllGrantsExceptOwnerGrant)

def getAccessControlPolicy(client, bucket_name, grants):
    owner_id = client.get_bucket_acl(Bucket=bucket_name).get("Owner").get("ID")
    return {'Owner': {'ID': owner_id}, 'Grants': GrantLogic.parseGrantsAsUncondensed(owner_id, grants)}

def getBucketOwnershipControlsResponse(client, bucket_name):
    try:
        return utils.Optional().of(client.get_bucket_ownership_controls(Bucket=bucket_name))
    except:
        return utils.Optional()

def getOwnershipControls(client, bucket_name):
    return getBucketOwnershipControlsResponse(client, bucket_name).to(lambda response: response.get("OwnershipControls"))

def getPublicAccessBlockResponse(client, bucket_name):
    try:
        return utils.Optional().of(client.get_public_access_block(Bucket=bucket_name))
    except:
        return utils.Optional()

def getPublicAccessBlockConfiguration(client, bucket_name):
    return getPublicAccessBlockResponse(client, bucket_name).to(lambda response: response.get("PublicAccessBlockConfiguration"))

def getBucketEncryptionResponse(client, bucket_name):
    try:
        return utils.Optional().of(client.get_bucket_encryption(Bucket=bucket_name))
    except:
        return utils.Optional()

def getServerSideEncryptionConfiguration(client, bucket_name):
    return getBucketEncryptionResponse(client, bucket_name).to(lambda response: response.get("ServerSideEncryptionConfiguration"))

def status(client, bucket_name):
    print(bucket_name)
    utils.print_status("ACL", lambda: client.get_bucket_acl(Bucket=bucket_name))
    utils.print_status("Ownership Control", lambda: client.get_bucket_ownership_controls(Bucket=bucket_name))
    utils.print_status("Policy", lambda: client.get_bucket_policy(Bucket=bucket_name))
    utils.print_status("Public Access Block", lambda: client.get_public_access_block(Bucket=bucket_name))
    utils.print_status("Encryption", lambda: client.get_bucket_encryption(Bucket=bucket_name))
    utils.print_status("Policy Status", lambda: client.get_bucket_policy_status(Bucket=bucket_name))
    print()

class BucketContext:

    def __init__(self, client, bucket_name, region):
        self.client = client
        self.bucket_name = bucket_name
        self.region = region
        self.model = {}
        if not bucketExists(client, bucket_name):
            createBasicBucket(client, bucket_name, region)

    def getBucketName(self):
        return self.bucket_name

    def getRegion(self):
        return self.region

    def getClient(self):
        return self.client

def updateGrants(bucket_context, access_control_policy):
    bucket_context.getClient().put_bucket_acl(Bucket=bucket_context.getBucketName(), AccessControlPolicy=access_control_policy)

def updateOwnershipControls(bucket_context, ownership_controls):
    bucket_context.getClient().put_bucket_ownership_controls(Bucket=bucket_context.getBucketName(), OwnershipControls=ownership_controls)

def updatePublicAccessBlockConfiguration(bucket_context, public_access_block_configuration):
    bucket_context.getClient().put_public_access_block(Bucket=bucket_context.getBucketName(), PublicAccessBlockConfiguration=public_access_block_configuration)

def updateServerSideEncryptionConfiguration(bucket_context, server_side_encryption_configuration):
    bucket_context.getClient().put_bucket_encryption(Bucket=bucket_context.getBucketName(), ServerSideEncryptionConfiguration=server_side_encryption_configuration)

def copyBucket(client_to, client_from, prefix, bucket_name, region):
    bucket_from = bucket_name
    bucket_to = (prefix + bucket_name)

    print("creating bucket")
    bucket_context = BucketContext(client_to, bucket_to, region)
    print("granting acl")
    getAllGrantsExceptOwnerGrant(client_from, bucket_from).ifExists(lambda grants: updateGrants(bucket_context, getAccessControlPolicy(bucket_context.getClient(), bucket_context.getBucketName(), grants)))
    print("setting ownership control")
    getOwnershipControls(client_from, bucket_from).ifExists(lambda ownership_controls: updateOwnershipControls(bucket_context, ownership_controls))
    print("setting public access block config")
    getPublicAccessBlockConfiguration(client_from, bucket_from).ifExists(lambda public_access_block_configuration: updatePublicAccessBlockConfiguration(bucket_context, public_access_block_configuration))
    print("setting encryption")
    getServerSideEncryptionConfiguration(client_from, bucket_from).ifExists(lambda server_side_encryption_configuration: updateServerSideEncryptionConfiguration(bucket_context, server_side_encryption_configuration))

def copyBucketsIfNotExist(client_to, client_from, prefix, region):
    def _copyBuckets(client_to, client_from, prefix, bucket_name, region):
        bucket_from = bucket_name
        bucket_to = (prefix + bucket_name)

        if bucketExists(client_to, bucket_to):
            print("already exists")
            return

        try:
            copyBucket(client_to, client_from, prefix, bucket_name, region)
        except Exception as e:
            print(e)
            deleteBucketIfExists(client_to, bucket_to)

    utils.applyForAllBuckets(client_from, lambda client, bucket_name: _copyBuckets(client_to, client, prefix, bucket_name, region))

def deleteBucketIfExists(client, bucket_name):
    if bucketExists(client, bucket_name):
        client.delete_bucket(Bucket=bucket_name)

def listBuckets(client):
    return client.list_buckets().get('Buckets')
