"""
Script diagnostico: testa l'accesso all'API LinkedIn e logga tutto.
Eseguito dal workflow test_linkedin.yml senza interazione Telegram.
"""
import os
import sys
import json
import requests

access_token = os.environ["LINKEDIN_ACCESS_TOKEN"]
headers_base = {"Authorization": f"Bearer {access_token}"}


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def call(method, url, **kwargs):
    resp = getattr(requests, method)(url, timeout=10, **kwargs)
    print(f"  {method.upper()} {url}")
    print(f"  Status: {resp.status_code}")
    try:
        print(f"  Body:   {json.dumps(resp.json(), indent=2)[:500]}")
    except Exception:
        print(f"  Body:   {resp.text[:300]}")
    return resp


section("1. /v2/userinfo (OpenID sub)")
call("get", "https://api.linkedin.com/v2/userinfo", headers=headers_base)

section("2. /v2/me (legacy numeric ID)")
call("get", "https://api.linkedin.com/v2/me",
     headers={**headers_base, "X-Restli-Protocol-Version": "2.0.0"})

section("3. /v2/me con projection")
call("get", "https://api.linkedin.com/v2/me?projection=(id,localizedFirstName,localizedLastName)",
     headers={**headers_base, "X-Restli-Protocol-Version": "2.0.0"})

section("4. registerUpload con urn:li:person:_S0LQqYM1H")
# Prende il sub da userinfo
r = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers_base, timeout=10)
sub = r.json().get("sub", "UNKNOWN")
person_urn = f"urn:li:person:{sub}"
print(f"  person_urn = {person_urn}")
call("post", "https://api.linkedin.com/v2/assets?action=registerUpload",
     headers={**headers_base, "Content-Type": "application/json", "X-Restli-Protocol-Version": "2.0.0"},
     json={
         "registerUploadRequest": {
             "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
             "owner": person_urn,
             "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}],
         }
     })

section("5. ugcPosts con urn:li:person:SUB (solo test, testo vuoto)")
call("post", "https://api.linkedin.com/v2/ugcPosts",
     headers={**headers_base, "Content-Type": "application/json", "X-Restli-Protocol-Version": "2.0.0"},
     json={
         "author": person_urn,
         "lifecycleState": "DRAFT",
         "specificContent": {
             "com.linkedin.ugc.ShareContent": {
                 "shareCommentary": {"text": "TEST - non pubblicare"},
                 "shareMediaCategory": "NONE",
             }
         },
         "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "CONNECTIONS"},
     })

section("6. Pagine LinkedIn amministrate (per trovare LINKEDIN_ORG_ID)")
# Richiede scope w_organization_social o rw_organization_admin
r = call("get",
         "https://api.linkedin.com/v2/organizationAcls?q=roleAssignee&role=ADMINISTRATOR&projection=(elements*(organization~(id,localizedName)))",
         headers={**headers_base, "X-Restli-Protocol-Version": "2.0.0"})
try:
    for el in r.json().get("elements", []):
        org = el.get("organization~", {})
        print(f"  >>> Pagina: {org.get('localizedName')}  ID={org.get('id')}")
except Exception:
    pass

section("FINE")
