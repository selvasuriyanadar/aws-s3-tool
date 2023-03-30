def isCanonicalUserGrant(grant):
    return grant.get("Grantee").get("Type") == "CanonicalUser"

def isOwnerGrant(owner_id, grant):
    return isCanonicalUserGrant(grant) and grant.get("Grantee").get("ID") == owner_id

def isCondensedOwnerGrant(grant):
    return grant.get("Grantee").get("Type") == "Owner"

def condenseOwnerGrant(grant):
    return {"Grantee": {"Type": "Owner"}, "Permission": grant.get("Permission")}

def uncondenseOwnerGrant(owner_id, grant):
    return {"Grantee": {"Type": "CanonicalUser", "ID": owner_id}, "Permission": grant.get("Permission")}

def parseGrantsAsCondensed(owner_id, grants):
    return [grant if not isOwnerGrant(owner_id, grant) else condenseOwnerGrant(grant) for grant in grants]

def parseGrantsAsUncondensed(owner_id, grants):
    return [grant if not isCondensedOwnerGrant(grant) else uncondenseOwnerGrant(owner_id, grant) for grant in grants]
