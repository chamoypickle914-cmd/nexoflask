import requests
from flask import Flask, jsonify, request
import time
app = Flask(__name__)
title = "1FF85D"
secret = "681HOGI5NYC8763THFWEZKRR5SK4RE87KIHNKCE4PCJHHYFJ1H"   
def GetUserId(ticket):return ticket[:16].replace("'", "").replace("-", "").replace(".", "")
def Headers():return {"content-type": "application/json", "X-SecretKey": secret}
def OculusValidationMadeByQwizx(ocid, nonce):
    keys = ["1185266791334586|4524d0320ec15915a12d105165731434| | stuff here, IF YOU HAVE MULTIPLE APPLABS ADD THEM LIKE THIS: "OC| |", "OC| |" "]
    for token in keys:
        try:
            url = f"https://graph.oculus.com/{ocid}?access_token={token}"
            response = requests.get(url, headers={"Content-Type": "application/json"})
            data = response.json()
            if 'id' in data:return True
            if 'error' in data:
                message = data['error'].get('message')
                if "Invalid OAuth access token - Cannot parse access token" in message:continue
            url = "https://graph.oculus.com/user_nonce_validate"
            response = requests.post(url, json={"nonce": nonce, "access_token": token})
            data = response.json()
            if data.get("is_valid") == "true":return True
            if 'error' in data:
                message = data['error'].get('message')
                if "Invalid OAuth access token - Cannot parse access token" in message:
                    continue
        except Exception as e:
            print(e)
    print("invalid")
    return False
@app.route("/photon", methods=["GET", "POST"])
def PhotonMadeByQwizx():
    data = request.get_json(silent=True) or request.args
    data = {k.lower(): v for k, v in data.items()}
    ticket = data.get("ticket") or data.get("username")
    nonce = data.get("nonce")
    titleid = data.get("appid")
    token = data.get("token")
    pid = GetUserId(ticket)
    if titleid != title: return jsonify({"error":"no"}), 403
    print(f"{data}")
    if not ticket:return jsonify({"error":"NO"}), 403
    if not nonce:return jsonify({"error":"NO"}), 403
    return jsonify({"ResultCode": 1,"StatusCode": 200, "UserId": pid, "AppId": titleid, "Ticket": ticket, "Token": token,"Nonce": nonce})
@app.route("/api/PlayFabAuthentication", methods=["POST"])
def PlayFabAuthentcationMadeByQwizx():
    data = request.get_json()
    oculus_id = data.get("OculusId")
    nonce = data.get("Nonce")
    if not data.get("Platform") == "Quest":return jsonify({"Message": "scary hacker!!"}), 403
    if not oculus_id or not OculusValidationMadeByQwizx(oculus_id, nonce):
        print("no nonce or ocid")
        return jsonify({"error": "no way brotein shake"}), 403
    lr = requests.post(url=f"https://{title}.playfabapi.com/Server/LoginWithServerCustomId",json={"ServerCustomId": f"OCULUS{oculus_id}","CreateAccount": True},headers=Headers())
    if lr.status_code == 200:
        d = lr.json().get("data")
        requests.post(url=f"https://{title}.playfabapi.com/Client/LinkCustomID",json={"CustomId": f"OCULUS{oculus_id}", "ForceLink": True},headers={"content-type": "application/json","x-authorization": d.get("SessionTicket")})
        print({"PlayFabId": d.get("PlayFabId"), "SessionTicket": d.get("SessionTicket"), "EntityToken": d.get("EntityToken", {}).get("EntityToken"), "EntityId": d.get("EntityToken", {}).get("Entity", {}).get("Id"), "EntityType": d.get("EntityToken", {}).get("Entity", {}).get("Type")}) 
        return jsonify({"PlayFabId": d.get("PlayFabId"),"SessionTicket": d.get("SessionTicket"),"EntityToken": d.get("EntityToken", {}).get("EntityToken"), "EntityId": d.get("EntityToken", {}).get("Entity", {}).get("Id"),"EntityType": d.get("EntityToken", {}).get("Entity", {}).get("Type")}), 200
    if lr.status_code == 403:
        data = lr.json()
    if data.get("errorCode") == 1002:
        reason, times = next(iter(data.get("errorDetails", {}).items()), ("no reason ?", []))
        print(reason)
        return jsonify({"BanMessage": reason,"BanExpirationTime": times[0] if times else "no expo ?"}), 403
@app.route("/cbfn", methods=["POST"])
def CheckForBadNameMadeByQwizx():return jsonify({"result": 0})
@app.route("/t", methods=["POST", "GET"])
def TitleDataMadeByQwizx():
    res = requests.post(f"https://{title}.playfabapi.com/Server/GetTitleData", headers=Headers())
    data = res.json().get("data", {}).get("Data", {})
    def n(obj):
        if isinstance(obj, dict):return {k: n(v) for k, v in obj.items()}
        elif isinstance(obj, list):return [n(i) for i in obj]
        elif isinstance(obj, str):return obj.replace("\\n", "\n")
        else:return obj
    f = n(data)
    return jsonify(f)
