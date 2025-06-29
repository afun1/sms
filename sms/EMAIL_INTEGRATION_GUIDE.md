# Email Integration Guide - Sparky Messaging

## 📧 Multi-Provider Email Support

Sparky Messaging now supports professional email campaigns with automatic provider selection, cost optimization, and enterprise-grade deliverability.

## 🚀 Supported Email Providers

### 1. **Gmail SMTP** (Free Tier)
- **Cost**: Free
- **Daily Limit**: 500 emails
- **Best For**: Small businesses, testing
- **Setup**: App password required (2FA must be enabled)

### 2. **SendGrid API** (Professional)
- **Cost**: $0.000295 per email ($2.95 per 10k emails)
- **Daily Limit**: 100,000+ emails
- **Best For**: High-volume marketing campaigns
- **Features**: Advanced analytics, deliverability optimization

### 3. **Mailgun API** (Developer-Friendly)
- **Cost**: $0.0008 per email ($0.80 per 1k emails)
- **Daily Limit**: 10,000+ emails
- **Best For**: Transactional emails, API integration
- **Features**: Email validation, detailed logs

### 4. **Amazon SES** (Enterprise)
- **Cost**: $0.0001 per email ($0.10 per 1k emails)
- **Daily Limit**: 200 (sandbox), unlimited (verified)
- **Best For**: Large enterprises, AWS ecosystem
- **Features**: High deliverability, scalable infrastructure

### 5. **ClickSend** (Multi-Service Platform)
- **Cost**: $0.0009 per email ($0.90 per 1k emails)
- **Daily Limit**: 50,000+ emails
- **Best For**: International campaigns, unified SMS+Email platform
- **Features**: Global delivery, SMS integration, competitive international rates

## ⚙️ Configuration

### Environment Variables (.env file)

```bash
# Gmail SMTP Configuration
GMAIL_EMAIL=your_gmail_address@gmail.com
GMAIL_APP_PASSWORD=your_16_character_app_password

# SendGrid API Configuration
SENDGRID_API_KEY=SG.your_sendgrid_api_key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# Mailgun API Configuration
MAILGUN_API_KEY=your_mailgun_api_key
MAILGUN_DOMAIN=yourdomain.com

# Amazon SES SMTP Configuration
AWS_SES_SMTP_USERNAME=your_ses_smtp_username
AWS_SES_SMTP_PASSWORD=your_ses_smtp_password
AWS_REGION=us-east-1

# ClickSend Multi-Service API (SMS + Email + Voice)
CLICKSEND_USERNAME=your_clicksend_username
CLICKSEND_API_KEY=your_clicksend_api_key
CLICKSEND_FROM_EMAIL=noreply@yourdomain.com
```

## 📱 Email Editor Features

### ✍️ Rich Text Editor
- **HTML Email Composer**: Create beautiful HTML emails
- **Plain Text Option**: Simple text-based emails
- **Formatting Toolbar**: Bold, italic, underline, links, images
- **Variable Insertion**: Dynamic content with {{variables}}

### 📋 Professional Templates
- **Welcome Email**: Onboarding new customers
- **Follow-up**: Sales and lead nurturing
- **Newsletter**: Regular updates and content
- **Promotion**: Special offers and announcements

### 🔍 Live Preview
- **Real-time Preview**: See email as recipients will
- **Multiple Formats**: HTML and plain text preview
- **Header Simulation**: From, To, Subject preview
- **Mobile Responsive**: Automatic mobile optimization

### 💰 Cost Intelligence
- **Provider Comparison**: Real-time cost comparison
- **Auto-selection**: Cheapest available provider
- **Bulk Estimates**: Calculate costs for large campaigns
- **Usage Tracking**: Monitor daily limits and spending

## 🛠️ API Endpoints

### Send Single Email
```bash
POST /api/email/send
Content-Type: application/json

{
  "to_email": "recipient@example.com",
  "subject": "Your Subject Here",
  "content": "<h1>HTML Content</h1><p>Your email content...</p>",
  "from_name": "Your Company",
  "content_type": "html"
}
```

### Send Bulk Emails
```bash
POST /api/email/bulk
Content-Type: application/json

{
  "recipients": ["user1@example.com", "user2@example.com"],
  "subject": "Bulk Email Subject",
  "content": "Your bulk email content...",
  "from_name": "Your Company",
  "content_type": "html"
}
```

### Multi-Channel (Email + SMS)
```bash
POST /api/multi/email-sms
Content-Type: application/json

{
  "contact": {
    "email": "user@example.com",
    "phone": "+1234567890"
  },
  "email_subject": "Email Subject",
  "email_content": "Email content...",
  "sms_message": "SMS follow-up message",
  "from_name": "Your Company",
  "delay_minutes": 30
}
```

### Get Email Capacity
```bash
GET /api/email/capacity
```

### Get Usage Statistics
```bash
GET /api/email/usage
```

### Cost Estimate
```bash
POST /api/email/cost-estimate
Content-Type: application/json

{
  "email_count": 1000
}
```

## 🎯 Best Practices

### 1. **Provider Selection Strategy**
- **Gmail**: Testing and small campaigns (< 500/day)
- **Amazon SES**: Cost-effective for medium volume (1k-10k/day)
- **SendGrid**: High-volume marketing (10k+ emails/day)
- **Mailgun**: Developer-focused, API-heavy usage
- **ClickSend**: International campaigns, unified SMS+Email platform

### 2. **Email Content Optimization**
- Use clear, compelling subject lines
- Include personalization with {{variables}}
- Maintain proper HTML structure for deliverability
- Test both HTML and plain text versions
- Include unsubscribe links for compliance

### 3. **Deliverability Tips**
- Authenticate your domain (SPF, DKIM, DMARC)
- Start with engaged subscribers
- Monitor bounce and complaint rates
- Use double opt-in for list building
- Avoid spam trigger words

### 4. **Cost Optimization**
- Use Gmail for testing and small volumes
- Switch to SES for cost-effective bulk sending
- Monitor daily limits to avoid service interruption
- Implement list hygiene to reduce bounces

## 🔧 Setup Instructions

### 1. Gmail Configuration
1. Enable 2-Factor Authentication on your Google account
2. Go to Google Account Settings > Security
3. Generate an App Password for "Mail"
4. Add to .env file: `GMAIL_EMAIL` and `GMAIL_APP_PASSWORD`

### 2. SendGrid Setup
1. Create account at sendgrid.com
2. Generate API key with "Mail Send" permissions
3. Verify sender identity or domain
4. Add to .env: `SENDGRID_API_KEY` and `SENDGRID_FROM_EMAIL`

### 3. Mailgun Setup
1. Sign up at mailgun.com
2. Add and verify your domain
3. Get API credentials from ClickSend dashboard
4. Add to .env: `CLICKSEND_USERNAME`, `CLICKSEND_API_KEY`, `CLICKSEND_FROM_EMAIL`

### 5. ClickSend Setup
1. Sign up at clicksend.com
2. Verify your account and add funds
3. Get username and API key from dashboard
4. Add to .env: `CLICKSEND_USERNAME`, `CLICKSEND_API_KEY`, `CLICKSEND_FROM_EMAIL`

### 4. Amazon SES Setup
1. Create AWS account and enable SES
2. Verify email address or domain
3. Create SMTP credentials
4. Add to .env: `AWS_SES_SMTP_USERNAME`, `AWS_SES_SMTP_PASSWORD`, `AWS_REGION`

## 📊 Integration with Existing Features

### Campaign Builder Integration
- Email is now available as a channel option
- Combine with SMS and RVM for multi-channel campaigns
- AI-powered email content generation
- Automated follow-up sequences

### AI-Powered Content
- Generate email content with SimpleTalk.ai
- Optimize subject lines for better open rates
- Personalize content based on recipient data
- A/B test different versions automatically

### GoHighLevel Integration
- Email campaigns trigger from GHL workflows
- Contact data automatically populates email variables
- Campaign results sync back to GHL
- Unified reporting across all channels

## 🚨 Troubleshooting

### Common Issues
1. **"No email providers configured"**
   - Check .env file has correct provider credentials
   - Verify API keys are valid and have proper permissions

2. **Gmail authentication errors**
   - Ensure 2FA is enabled
   - Use App Password, not regular password
   - Check for typos in email address

3. **SendGrid/Mailgun delivery issues**
   - Verify sender identity is confirmed
   - Check domain authentication status
   - Review content for spam triggers

4. **Daily limit exceeded**
   - Switch to higher-capacity provider
   - Implement email scheduling to spread volume
   - Upgrade provider plan if needed

### Support Resources
- Check provider status dashboards
- Review email logs for detailed error messages
- Test with single emails before bulk sending
- Monitor delivery rates and adjust strategy

## 🔮 Future Enhancements

### Planned Features
- **Advanced Templates**: Drag-and-drop email builder
- **A/B Testing**: Automated subject line and content testing
- **Email Automation**: Drip campaigns and autoresponders
- **Enhanced Analytics**: Open rates, click tracking, conversions
- **List Management**: Segmentation and targeting tools
- **Compliance Tools**: GDPR, CAN-SPAM compliance features

---

**📧 Ready to revolutionize your email marketing with Sparky Messaging!**

For technical support or feature requests, contact our development team.
