import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from core.router_chain import route_and_respond
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/twilio', methods=['POST'])
def twilio_webhook():
    from_number = request.values.get('From', '')
    body = request.values.get('Body', '')

    print(f"👾 Received from Twilio: {from_number} -> {body}")
    reply = route_and_respond(body)
    print(f"✅ Replying via Twilio: {reply}")

    resp = MessagingResponse()
    resp.message(reply)
    return Response(str(resp), mimetype='application/xml')

if __name__ == '__main__':
    app.run(port=5000)
