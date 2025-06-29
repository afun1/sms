# SimpleTalk.ai Integration Guide

## Overview

Sparky Messaging now includes powerful AI-driven message generation and optimization capabilities through integration with SimpleTalk.ai. This integration allows you to:

- 🤖 Generate optimized SMS messages
- 🎙️ Create compelling RVM (Ringless Voicemail) scripts  
- ✨ Optimize existing messages for better engagement
- 🔄 Build multi-step conversation flows
- 📊 Monitor AI usage and account limits

## Setup Instructions

### 1. Get SimpleTalk.ai API Access

1. Sign up for a SimpleTalk.ai account at https://simpletalk.ai
2. Navigate to your API settings
3. Generate an API key
4. Note your preferred model (e.g., `gpt-4`, `gpt-3.5-turbo`)

### 2. Configure Environment Variables

Add the following to your `.env` file:

```bash
# SimpleTalk.ai Configuration
SIMPLETALK_API_KEY=your_api_key_here
SIMPLETALK_BASE_URL=https://api.simpletalk.ai/v1
SIMPLETALK_MODEL=gpt-4
```

### 3. Restart the Server

```bash
python sms_api_server.py
```

## API Endpoints

### Check AI Status
```http
GET /api/ai/status
```

**Response:**
```json
{
  "configured": true,
  "message": "SimpleTalk.ai ready"
}
```

### Generate SMS Message
```http
POST /api/ai/generate/sms
```

**Request Body:**
```json
{
  "context": "Follow up on meeting about marketing automation",
  "contact_info": {
    "name": "John Smith",
    "company": "ABC Corp"
  },
  "tone": "professional",
  "max_length": 160
}
```

**Response:**
```json
{
  "success": true,
  "message": "Hi John, thanks for meeting with us about marketing automation for ABC Corp. Our solution can increase your lead conversion by 40%. When can we schedule a demo? - Sarah",
  "length": 159,
  "tone": "professional",
  "context": "Follow up on meeting about marketing automation"
}
```

### Generate RVM Script
```http
POST /api/ai/generate/rvm
```

**Request Body:**
```json
{
  "context": "Introduction to new service offering",
  "contact_info": {
    "name": "Jane Doe",
    "company": "XYZ Inc"
  },
  "tone": "conversational",
  "duration": "30 seconds"
}
```

**Response:**
```json
{
  "success": true,
  "script": "Hi Jane, this is Sarah from TechSolutions. I hope you're having a great day. I wanted to reach out because we've just launched a new service that I think could really benefit XYZ Inc. We're helping companies like yours streamline their operations and save up to 30% on overhead costs. I'd love to share more details with you. Please give me a call back at 555-123-4567, or visit our website. Thanks Jane, and have a wonderful day!",
  "length": 456,
  "tone": "conversational",
  "duration": "30 seconds",
  "context": "Introduction to new service offering"
}
```

### Optimize Existing Message
```http
POST /api/ai/optimize
```

**Request Body:**
```json
{
  "original_message": "Hey there! We have a new product that might interest you. Give us a call!",
  "optimization_goal": "engagement"
}
```

**Response:**
```json
{
  "success": true,
  "original_message": "Hey there! We have a new product that might interest you. Give us a call!",
  "optimized_message": "Hi! We've just launched something that could save you 20% on monthly costs. Interested in a 5-minute demo? Reply YES for details!",
  "improvements": "Made the message more specific with a clear value proposition, added a quantifiable benefit, included a simple call-to-action, and made it more personal",
  "optimization_goal": "engagement"
}
```

### Create Conversation Flow
```http
POST /api/ai/conversation-flow
```

**Request Body:**
```json
{
  "campaign_goal": "Generate leads for consulting services",
  "audience_info": "Small business owners in tech industry",
  "num_steps": 3
}
```

**Response:**
```json
{
  "success": true,
  "flow": {
    "flow_name": "Tech Consulting Lead Generation",
    "total_steps": 3,
    "steps": [
      {
        "step": 1,
        "type": "sms",
        "timing": "immediate",
        "message": "Hi [Name], struggling with tech challenges? We help tech startups scale efficiently. Free 15-min consultation available. Interested?",
        "purpose": "introduction/awareness"
      },
      {
        "step": 2,
        "type": "rvm",
        "timing": "24 hours later",
        "message": "Hi [Name], this is Sarah from TechAdvantage Consulting. I sent you a message yesterday about our free consultation...",
        "purpose": "value delivery"
      },
      {
        "step": 3,
        "type": "sms",
        "timing": "72 hours later",
        "message": "Final reminder: Our free tech audit helped businesses save avg $10k/year. Still available this week. Book at [link]",
        "purpose": "final conversion push"
      }
    ]
  },
  "campaign_goal": "Generate leads for consulting services",
  "audience_info": "Small business owners in tech industry"
}
```

### Get AI Usage Stats
```http
GET /api/ai/usage
```

**Response:**
```json
{
  "success": true,
  "usage": {
    "requests_made": 45,
    "tokens_used": 15420,
    "monthly_limit": 100000,
    "remaining_tokens": 84580
  }
}
```

## Dashboard Usage

### AI Message Generation Interface

1. **Navigate to Dashboard**: Open http://localhost:5000/ in your browser
2. **Scroll to AI Section**: Find the "🤖 AI-Powered Message Generation" section
3. **Choose Your Tool**:
   - **Generate SMS**: Create optimized SMS messages
   - **Generate RVM**: Generate voicemail scripts
   - **Optimize Message**: Improve existing messages
   - **Conversation Flow**: Build multi-step campaigns

### Using the SMS Generator

1. Enter the context/purpose of your message
2. Optionally add contact information for personalization
3. Select the desired tone (friendly, professional, casual, urgent)
4. Set maximum message length
5. Click "🚀 Generate SMS"

### Using the RVM Generator

1. Enter the context/purpose of your voicemail
2. Optionally add contact information
3. Select the tone and target duration
4. Click "🎙️ Generate RVM Script"

### Message Optimization

1. Paste your existing message
2. Choose optimization goal (engagement, conversion, clarity, brevity)
3. Click "✨ Optimize Message"
4. Review the improvements and suggestions

### Conversation Flow Builder

1. Define your campaign goal
2. Describe your target audience
3. Choose number of steps (2-5)
4. Click "🔄 Create Flow"
5. Review the complete multi-channel sequence

## Features & Benefits

### ✨ AI-Powered Content Creation
- **Smart Personalization**: Uses contact information for targeted messaging
- **Tone Adaptation**: Adjusts language style based on your needs
- **Length Optimization**: Ensures messages fit SMS character limits
- **Context Awareness**: Understands campaign goals and audience

### 🎯 Message Optimization
- **Engagement Focus**: Increases open and response rates
- **Conversion Optimization**: Drives more actions and sales
- **Clarity Enhancement**: Makes messages easier to understand
- **Brevity Improvement**: Removes unnecessary words

### 🔄 Multi-Channel Flows
- **SMS + RVM Combination**: Leverages both channels effectively
- **Timed Sequences**: Optimizes message timing
- **Progressive Value**: Builds relationship over multiple touchpoints
- **Compliance Ready**: Follows messaging best practices

### 📊 Usage Monitoring
- **Token Tracking**: Monitor API usage and costs
- **Request Limits**: Stay within account boundaries
- **Performance Metrics**: Track generation success rates

## Best Practices

### Message Generation
1. **Be Specific**: Provide clear context about your goal
2. **Include Contact Info**: Use names and companies for personalization  
3. **Choose Right Tone**: Match tone to your audience and brand
4. **Test Variations**: Generate multiple versions and A/B test

### RVM Scripts
1. **Natural Language**: Write for speaking, not reading
2. **Clear Call-to-Action**: Always include next steps
3. **Time Awareness**: Keep within 30-60 seconds for best results
4. **Professional Quality**: Use proper pacing and pauses

### Conversation Flows
1. **Value-First**: Lead with benefits, not features
2. **Progressive Disclosure**: Share more value in each step
3. **Multi-Channel**: Combine SMS and RVM for maximum impact
4. **Compliance**: Follow opt-out and frequency guidelines

## Troubleshooting

### "SimpleTalk.ai not configured"
- Check that `SIMPLETALK_API_KEY` is set in `.env`
- Verify API key is valid and active
- Restart the server after adding credentials

### API Rate Limiting
- Monitor usage via `/api/ai/usage` endpoint
- Upgrade SimpleTalk.ai plan if needed
- Implement request queuing for high-volume use

### Poor Message Quality
- Provide more specific context
- Include detailed audience information
- Try different tones and optimization goals
- Use conversation flow for complex campaigns

## Integration with Existing Features

The SimpleTalk.ai integration works seamlessly with:
- **Multi-Provider SMS**: Generated messages sent via best provider
- **Slybroadcast RVM**: AI scripts converted to voicemail
- **GoHighLevel Workflows**: Trigger AI generation from GHL
- **Bulk Operations**: Generate personalized messages for CSV lists
- **API Integration**: Embed AI generation in external systems

## Pricing Considerations

SimpleTalk.ai charges based on:
- **API Requests**: Per generation call
- **Token Usage**: Based on input/output length
- **Model Selection**: GPT-4 costs more than GPT-3.5

Monitor usage via the dashboard and API to optimize costs.

## Support

For issues with:
- **Sparky Messaging**: Check project documentation
- **SimpleTalk.ai API**: Contact SimpleTalk.ai support
- **Integration Problems**: Review configuration and logs

The integration is designed to fail gracefully - if AI is unavailable, standard messaging features continue to work normally.
