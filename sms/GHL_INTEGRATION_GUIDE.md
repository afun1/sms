# GoHighLevel SMS Integration Guide

## 🚀 Quick Setup

1. **Start the API Server:**
   ```
   python sms_api_server.py
   ```
   Server runs on: `http://localhost:5000`

2. **Make it accessible to GHL:**
   - Use ngrok: `ngrok http 5000`
   - Or deploy to cloud (Heroku, Render, etc.)

## 📡 API Endpoints

### 1. Send Single SMS
**POST** `/api/sms/send`
```json
{
  "phone": "+1234567890",
  "message": "Hello {name}, your appointment is confirmed!",
  "name": "John Doe"
}
```

### 2. Send Bulk SMS
**POST** `/api/sms/bulk`
```json
{
  "contacts": [
    {"phone": "+1234567890", "name": "John", "message": "Custom message"},
    {"phone": "+1987654321", "name": "Jane"}
  ],
  "default_message": "Hello {name}, this is a message for you!",
  "delay": 2
}
```

### 3. GHL Webhook (Main Integration)
**POST** `/api/webhook/ghl`

GoHighLevel will send contact data like this:
```json
{
  "contact": {
    "phone": "+1234567890",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com"
  },
  "message": "Hi {firstName}, your appointment is confirmed!",
  "trigger": "appointment_confirmed"
}
```

## 🔧 GoHighLevel Workflow Setup

### Step 1: Create Webhook in GHL
1. Go to **Automation** → **Workflows**
2. Create new workflow or edit existing
3. Add **Webhook** action
4. Set webhook URL: `https://your-domain.com/api/webhook/ghl`
5. Method: **POST**
6. Content-Type: **application/json**

### Step 2: Configure Webhook Payload
```json
{
  "contact": {
    "phone": "{{contact.phone}}",
    "firstName": "{{contact.first_name}}",
    "lastName": "{{contact.last_name}}",
    "email": "{{contact.email}}"
  },
  "message": "Hi {{contact.first_name}}, your appointment with Dr. Smith is confirmed for tomorrow at 2 PM. Reply STOP to opt out.",
  "trigger": "appointment_confirmed"
}
```

### Step 3: Test the Integration
Use the test endpoint first:
**POST** `/api/webhook/test`

## 🛠️ Available Placeholders

In your messages, you can use:
- `{firstName}` - Contact's first name
- `{lastName}` - Contact's last name  
- `{fullName}` - Full name
- `{name}` - Alias for full name

## 📱 Common GHL Use Cases

### 1. Appointment Confirmations
```json
{
  "message": "Hi {firstName}, your appointment is confirmed for {appointment_date} at {appointment_time}. Location: {business_address}. Reply STOP to opt out."
}
```

### 2. Payment Reminders
```json
{
  "message": "Hi {firstName}, this is a friendly reminder that your payment of ${amount} is due on {due_date}. Pay now: {payment_link}"
}
```

### 3. Welcome Messages
```json
{
  "message": "Welcome {firstName}! Thanks for joining {business_name}. We're excited to work with you. Questions? Reply to this message."
}
```

### 4. Follow-up Messages
```json
{
  "message": "Hi {firstName}, how was your experience with us? We'd love your feedback: {review_link}"
}
```

## 🌐 Making Your API Public

### Option 1: ngrok (Quick Testing)
```bash
# Install ngrok: https://ngrok.com/download
ngrok http 5000
# Use the https URL in GHL webhook
```

### Option 2: Deploy to Cloud

**Heroku:**
1. Create `Procfile`: `web: python sms_api_server.py`
2. Deploy: `git push heroku main`

**Render.com:**
1. Connect GitHub repo
2. Set start command: `python sms_api_server.py`

## 🔐 Security & Authentication

Add API key authentication:
```python
# In your .env file
API_KEY=your_secret_api_key_here
```

Then validate in webhook:
```python
def validate_api_key():
    api_key = request.headers.get('X-API-Key')
    if api_key != os.getenv('API_KEY'):
        return False
    return True
```

## 📊 Monitoring & Logs

The API logs all SMS activities:
- Successful sends
- Failed attempts
- Webhook calls
- Error details

Check logs in console or add logging to file:
```python
logging.basicConfig(
    filename='sms_api.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

## 🚨 Important Notes

1. **Rate Limiting**: Add delays between bulk messages
2. **Error Handling**: Always check response status
3. **Phone Format**: Use international format (+1234567890)
4. **Compliance**: Include opt-out instructions
5. **Testing**: Test thoroughly before going live

## 📞 Support

If you need help:
1. Check API status: `GET /api/health`
2. Test webhook: `POST /api/webhook/test`
3. Review logs for errors
4. Validate phone number formats
