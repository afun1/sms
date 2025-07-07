# ClickSend Webhook Setup Guide

## Overview
This guide explains how to set up ClickSend webhooks to receive SMS delivery reports in your Sparky Messaging application.

## What's Already Implemented

### 1. Webhook Endpoint
- **URL**: `http://localhost:5000/api/webhook/clicksend`
- **Method**: POST
- **Purpose**: Receives delivery reports from ClickSend

### 2. Delivery Reports API
- **GET** `/api/delivery-reports` - View all delivery reports
- **GET** `/api/delivery-reports?message_id=XXX` - View specific report
- **DELETE** `/api/delivery-reports` - Clear all reports

### 3. Delivery Reports UI
- **URL**: `http://localhost:5000/delivery_reports.html`
- **Features**: 
  - View all delivery reports in a table
  - Search by message ID or phone number
  - Real-time refresh
  - Clear all reports

## Setup Steps

### 1. Configure Webhook in SMS Editor
1. Go to `http://localhost:5000/sms_editor.html`
2. Select ClickSend provider
3. Click "Setup Provider"
4. Fill in the webhook URL field:
   - **Local Development**: `http://localhost:5000/api/webhook/clicksend`
   - **Production**: `https://yourdomain.com/api/webhook/clicksend`

### 2. ClickSend Account Configuration
1. Log into your ClickSend account
2. Go to **Developers** → **Webhooks**
3. Add a new webhook:
   - **Name**: Sparky Messaging Delivery Reports
   - **URL**: `http://localhost:5000/api/webhook/clicksend`
   - **Events**: Select "SMS Delivery Reports"
   - **Method**: POST

### 3. Test the Setup
1. Send a test SMS through the SMS editor
2. Check the delivery reports page: `http://localhost:5000/delivery_reports.html`
3. Look for the delivery status updates

## Webhook Data Format

ClickSend sends POST requests with this data structure:
```json
{
  "message_id": "12345678",
  "status": "Delivered",
  "timestamp": "2025-01-15T10:30:00Z",
  "to": "+1234567890",
  "error_code": null,
  "error_text": null
}
```

## Status Values
- **Queued**: Message is queued for sending
- **Sent**: Message has been sent
- **Delivered**: Message was delivered successfully
- **Failed**: Message delivery failed
- **Undelivered**: Message could not be delivered

## Local Development vs Production

### Local Development
- Use `http://localhost:5000/api/webhook/clicksend`
- ClickSend cannot reach localhost directly
- Use ngrok or similar for testing: `ngrok http 5000`

### Production Deployment
- Deploy to Vercel, Netlify, or similar
- Use HTTPS URL: `https://yourdomain.com/api/webhook/clicksend`
- Update webhook URL in ClickSend account

## Troubleshooting

### 1. No Delivery Reports Appearing
- Check that webhook URL is configured in SMS editor
- Verify webhook is registered in ClickSend account
- Check server logs for incoming webhook requests

### 2. Webhook Not Receiving Data
- Ensure URL is publicly accessible (not localhost)
- Check ClickSend webhook logs in their dashboard
- Verify webhook URL format is correct

### 3. Reports Not Displaying
- Check browser console for JavaScript errors
- Verify API endpoint is responding: `http://localhost:5000/api/delivery-reports`
- Check that delivery_reports.html is loading correctly

## Security Considerations

### 1. Webhook Validation
Consider adding webhook signature validation:
```python
# In production, validate webhook signatures
def validate_clicksend_webhook(request):
    # Implement signature validation
    pass
```

### 2. Rate Limiting
Add rate limiting to prevent webhook abuse:
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/webhook/clicksend', methods=['POST'])
@limiter.limit("100 per minute")
def clicksend_webhook():
    # Webhook handler
    pass
```

## Database Integration

For production, consider storing reports in a database:
```python
# Example with SQLAlchemy
class DeliveryReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    error_code = db.Column(db.String(10), nullable=True)
    error_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

## Next Steps

1. **Test locally** with ngrok for webhook testing
2. **Deploy to production** with proper HTTPS endpoints
3. **Add database storage** for persistent delivery reports
4. **Implement notifications** for failed deliveries
5. **Add analytics** for delivery success rates

## Support

- Check server logs for webhook activity
- View delivery reports at: `http://localhost:5000/delivery_reports.html`
- API documentation available at server startup
- Contact support for ClickSend webhook configuration issues
