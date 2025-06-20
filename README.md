# Sparky Messaging

**Professional SMS + RVM automation platform with AI-powered message generation**

This application allows you to send SMS messages and ringless voicemails in bulk with GoHighLevel integration and SimpleTalk.ai-powered message optimization.

## 🚀 Key Features
- **Multi-provider SMS** (Twilio, TextBelt, ClickSend) with automatic failover
- **Ringless Voicemail** via Slybroadcast integration
- **🤖 AI-powered message generation** and optimization via SimpleTalk.ai
- **GoHighLevel workflow integration** for seamless automation
- **Multi-channel campaigns** (SMS + RVM combo)
- **No A2P registration required** for immediate deployment
- **Bulk operations** with CSV support
- **Real-time cost tracking** and provider management
- **Professional dashboard** with live stats and API testing

## Setup

1. Install required packages:
   ```
   pip install -r requirements.txt
   ```

2. Get Twilio credentials:
   - Sign up for a free Twilio account at https://www.twilio.com/try-twilio
   - Get your Account SID and Auth Token from the console
   - Get a Twilio phone number

3. Create a `.env` file with your credentials:
   ```
   TWILIO_ACCOUNT_SID=your_account_sid_here
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_PHONE_NUMBER=your_twilio_phone_number_here
   ```

## CSV Format

Your CSV file should have the following columns:
- `phone_number`: Recipient's phone number (with country code, e.g., +1234567890)
- `name`: Recipient's name (optional, for personalization)
- `message`: Custom message for this recipient (optional)

Example CSV:
```csv
phone_number,name,message
+1234567890,John Doe,
+1987654321,Jane Smith,Special offer just for you!
```

## Usage

Run the application:
```
python sms_sender.py
```

## 🤖 AI Integration

Sparky Messaging includes powerful AI capabilities via SimpleTalk.ai:

### Quick Start
1. Get SimpleTalk.ai API key from https://simpletalk.ai
2. Add to `.env`: `SIMPLETALK_API_KEY=your_key_here`
3. Access AI features in dashboard at http://localhost:5000/

### AI Features
- **Smart SMS Generation**: Context-aware message creation
- **RVM Script Writing**: Natural voicemail scripts optimized for TTS
- **Message Optimization**: Improve engagement and conversion rates
- **Conversation Flows**: Multi-step campaign sequences
- **Usage Monitoring**: Track AI costs and limits

See `SIMPLETALK_AI_INTEGRATION_GUIDE.md` for complete documentation.

## 📊 Dashboard

Access the professional dashboard at http://localhost:5000/:
- Live system statistics and provider status
- Interactive API endpoint testing
- AI-powered message generation interface
- Settings management with custom branding
- Real-time cost tracking and capacity monitoring

## 🔗 API Integration

RESTful API endpoints for external integration:
- `POST /api/sms/send` - Send single SMS
- `POST /api/rvm/send` - Send ringless voicemail  
- `POST /api/multi/send` - Send SMS + RVM combo
- `POST /api/webhook/ghl` - GoHighLevel webhook
- `POST /api/ai/generate/sms` - AI SMS generation
- `POST /api/ai/generate/rvm` - AI RVM script generation

Full API documentation available in the dashboard.

## 📁 Documentation

- `GHL_INTEGRATION_GUIDE.md` - GoHighLevel setup and workflows
- `SLYBROADCAST_SETUP_GUIDE.md` - Ringless voicemail configuration  
- `SIMPLETALK_AI_INTEGRATION_GUIDE.md` - AI features and usage
- `DAILY_LIMITS_GUIDE.md` - Provider limits and compliance
- `CLICKSEND_PRICING_2025.md` - ClickSend pricing and setup

## Notes

- For non-A2P usage, stick to:
  - Personal communications
  - Low volume sending (under 200 messages per day)
  - Non-commercial messages
  - Messages to people who have opted in

- Higher volume or commercial messaging will require A2P registration
