# ClickSend Webhook Integration Guide

## Overview

This guide explains how to set up and use ClickSend webhooks to receive SMS delivery reports in your Sparky Messaging application.

## 🔧 Setup Instructions

### 1. Configure Your Webhook URL

In the SMS Editor, when setting up your ClickSend provider:

**Local Development:**
```
http://localhost:5000/api/webhook/clicksend
```

**Production (after deployment):**
```
https://yourdomain.com/api/webhook/clicksend
```

### 2. ClickSend Account Configuration

1. Log in to your ClickSend dashboard
2. Go to **Account Settings** → **Webhooks**
3. Add a new webhook with the following settings:
   - **URL**: Your webhook endpoint (see above)
   - **Events**: Select "SMS" delivery reports
   - **Format**: JSON
   - **Method**: POST

### 3. Test Your Webhook

1. Send a test SMS using the SMS Editor
2. Check the delivery reports page: `http://localhost:5000/delivery_reports.html`
3. You should see delivery status updates within a few minutes

## 📊 Webhook Data Format

ClickSend sends webhook data in the following format:

```json
{
  "message_id": "12345678-1234-1234-1234-123456789012",
  "status": "Delivered",
  "timestamp": "2025-01-15T10:30:00Z",
  "to": "+1234567890",
  "error_code": null,
  "error_text": null,
  "custom_string": "optional"
}
```

## 🎯 Status Types

Common delivery statuses you'll receive:

- **Queued**: Message is queued for sending
- **Sent**: Message has been sent to the carrier
- **Delivered**: Message successfully delivered to recipient
- **Failed**: Message delivery failed
- **Expired**: Message expired before delivery

## 🔍 Viewing Delivery Reports

### Via Web Interface
1. Navigate to **Reports** in the main navigation
2. Or visit: `http://localhost:5000/delivery_reports.html`
3. Use the search box to filter by message ID or phone number

### Via API
```javascript
// Get all delivery reports
fetch('/api/delivery-reports')
  .then(response => response.json())
  .then(data => console.log(data.reports));

// Get specific report
fetch('/api/delivery-reports?message_id=12345678-1234-1234-1234-123456789012')
  .then(response => response.json())
  .then(data => console.log(data.report));
```

## 🚀 Production Deployment

### For Vercel/Netlify
1. Create an API route in your deployment platform
2. Configure your webhook URL to point to the public endpoint
3. Ensure your Flask server is running and accessible

### Example Vercel API Route
Create `/api/webhook/clicksend.js`:
```javascript
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const webhookData = req.body;
  
  // Process webhook data
  // Store in database, send notifications, etc.
  
  res.status(200).json({ 
    success: true, 
    message: 'Webhook received' 
  });
}
```

## 🔒 Security Considerations

### IP Whitelisting
ClickSend sends webhooks from specific IP addresses. Consider whitelisting:
- 103.16.79.102
- 103.16.79.103
- 103.16.79.104

### Webhook Validation
For production, implement webhook signature validation:
```javascript
const crypto = require('crypto');

function validateWebhook(payload, signature, secret) {
  const hmac = crypto.createHmac('sha256', secret);
  hmac.update(payload);
  const computedSignature = hmac.digest('hex');
  return computedSignature === signature;
}
```

## 📝 API Endpoints

### Webhook Endpoint
- **POST** `/api/webhook/clicksend`
- Receives delivery reports from ClickSend

### Delivery Reports API
- **GET** `/api/delivery-reports` - Get all reports
- **GET** `/api/delivery-reports?message_id=ID` - Get specific report
- **DELETE** `/api/delivery-reports` - Clear all reports

## 🐛 Troubleshooting

### Common Issues

1. **Webhook not receiving data**
   - Check your webhook URL is publicly accessible
   - Verify ClickSend webhook configuration
   - Check server logs for errors

2. **Reports not showing**
   - Ensure webhook URL is correctly configured in SMS editor
   - Check if Flask server is running
   - Verify webhook endpoint is responding with 200 status

3. **Local development issues**
   - Use ngrok to make localhost publicly accessible
   - Configure ClickSend webhook to point to ngrok URL

### Debug Mode
Enable debug logging in your Flask application:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Support

For additional support:
- Check ClickSend documentation: https://developers.clicksend.com/
- Review Flask application logs
- Test webhook endpoint with tools like Postman

## 📋 Next Steps

1. Deploy your application to a production environment
2. Configure production webhook URLs
3. Set up database storage for delivery reports
4. Implement real-time notifications for delivery status
5. Add retry logic for failed webhook deliveries

---

*Last updated: July 2025*
