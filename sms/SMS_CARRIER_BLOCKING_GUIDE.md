# SMS Carrier Blocking & Filtering Guide
*Updated: June 26, 2025*

## Overview
Cell phone carriers implement various blocking and filtering mechanisms to protect users from spam, phishing, and unwanted messages. Understanding these mechanisms is crucial for successful SMS campaigns.

## Major US Carriers That Block Messages

### 🔴 **Heavily Filtering Carriers**

#### **1. Verizon Wireless**
- **Blocking Level**: High
- **Key Filters**:
  - A2P 10DLC compliance required for business messaging
  - Content filtering for spam keywords
  - Rate limiting (velocity controls)
  - Sender reputation scoring
  - URL filtering and link shortener restrictions
- **Common Block Reasons**:
  - Non-registered 10DLC campaigns
  - High opt-out rates
  - Spam content patterns
  - Gray route traffic

#### **2. AT&T**
- **Blocking Level**: High
- **Key Filters**:
  - Strict A2P 10DLC enforcement
  - Machine learning content analysis
  - Sender reputation algorithms
  - Message volume thresholds
  - Link verification systems
- **Common Block Reasons**:
  - Unregistered business numbers
  - Suspicious content patterns
  - High delivery failure rates
  - Non-compliant opt-in practices

#### **3. T-Mobile**
- **Blocking Level**: Very High
- **Key Filters**:
  - Advanced AI-powered spam detection
  - Real-time content analysis
  - Behavioral pattern recognition
  - Aggressive keyword filtering
  - Link reputation checking
- **Common Block Reasons**:
  - Marketing messages without proper registration
  - Financial/crypto content
  - Shortened URLs from suspicious domains
  - High user complaint rates

### 🟡 **Moderate Filtering Carriers**

#### **4. US Cellular**
- **Blocking Level**: Moderate
- **Key Filters**:
  - Basic 10DLC compliance
  - Standard spam filtering
  - Volume-based throttling
- **Common Block Reasons**:
  - Bulk messaging without registration
  - Generic spam patterns

#### **5. Cricket Wireless (AT&T)**
- **Blocking Level**: Moderate to High
- **Key Filters**:
  - Inherits AT&T filtering systems
  - Additional prepaid-focused filters
- **Common Block Reasons**:
  - Same as AT&T parent network
  - Enhanced filtering for prepaid users

### 🟢 **Lower Filtering Carriers**

#### **6. Metro by T-Mobile**
- **Blocking Level**: Moderate
- **Key Filters**:
  - Basic T-Mobile filtering
  - Reduced enterprise-level filtering
- **Common Block Reasons**:
  - Major spam violations
  - High volume unregistered traffic

#### **7. Boost Mobile**
- **Blocking Level**: Low to Moderate
- **Key Filters**:
  - Basic spam protection
  - Limited content analysis
- **Common Block Reasons**:
  - Obvious spam patterns
  - Excessive messaging rates

## International Carriers with Heavy Blocking

### **Canada**
- **Rogers**: Heavy filtering, similar to US carriers
- **Bell Canada**: Moderate to high filtering
- **Telus**: Advanced spam protection

### **United Kingdom**
- **EE**: Strict content filtering
- **O2**: Advanced AI spam detection
- **Three**: Moderate filtering
- **Vodafone**: High-level enterprise filtering

### **Australia**
- **Telstra**: Aggressive spam filtering
- **Optus**: Advanced content analysis
- **Vodafone Australia**: Moderate filtering

### **European Union**
- **Orange (France)**: GDPR-compliant filtering
- **Deutsche Telekom (Germany)**: Privacy-focused blocking
- **Vodafone (Multi-country)**: Unified EU filtering

## Types of SMS Blocking

### **1. Content-Based Filtering**
- **Keyword Detection**: Spam words, financial terms, adult content
- **Pattern Recognition**: Repetitive messages, template patterns
- **Link Analysis**: Suspicious URLs, shortened links, domain reputation
- **Language Processing**: AI-powered content understanding

### **2. Sender-Based Filtering**
- **Number Reputation**: Historical spam reports, user complaints
- **Registration Status**: A2P 10DLC compliance, brand verification
- **Volume Patterns**: Sudden spikes, unusual sending behavior
- **Geographic Filtering**: International vs domestic senders

### **3. Recipient-Based Filtering**
- **Opt-in Verification**: Confirmed consent requirements
- **User Preferences**: Individual blocking settings
- **Engagement Metrics**: Open rates, response rates, deletions
- **Complaint History**: Previous spam reports from recipients

### **4. Network-Level Filtering**
- **Gray Route Detection**: Unauthorized message routing
- **Carrier Interconnect**: Direct carrier relationships required
- **Traffic Shaping**: Rate limiting and throttling
- **Protocol Compliance**: Proper SMS protocol adherence

## Common Blocking Triggers

### **High-Risk Content**
```
❌ "URGENT: Claim your prize NOW!"
❌ "Make $5000 working from home"
❌ "Limited time offer expires today"
❌ "Click here to win: bit.ly/xxx"
❌ "Free trial - no credit card required"
❌ Financial advice or investment opportunities
❌ Cryptocurrency promotions
❌ Dating/adult content
❌ Pharmacy/medical claims
❌ Get-rich-quick schemes
```

### **Sending Behavior Triggers**
- Sending to unverified numbers
- High message volume without warming up
- Identical messages to multiple recipients
- Messages sent outside business hours
- Rapid-fire message sequences
- No opt-out mechanism provided

### **Technical Triggers**
- Using non-registered phone numbers
- Sending through gray routes
- Missing sender identification
- Invalid message encoding
- Oversized message content
- Improper concatenated SMS handling

## Bypass Strategies (Compliant)

### **1. Proper Registration**
- Register for A2P 10DLC campaigns
- Verify brand and campaign information
- Use registered toll-free numbers
- Implement proper opt-in processes

### **2. Content Optimization**
- Use natural, conversational language
- Avoid spam trigger words
- Include clear opt-out instructions
- Use branded short domains
- Personalize messages when possible

### **3. Sender Reputation Management**
- Gradually increase message volume
- Monitor delivery rates and user feedback
- Maintain low opt-out rates
- Respond to user inquiries promptly
- Use consistent sender identification

### **4. Technical Best Practices**
- Use direct carrier connections
- Implement proper message encoding
- Follow SMS protocol standards
- Monitor delivery receipts
- Set appropriate sending rates

## Monitoring & Compliance

### **Key Metrics to Track**
- **Delivery Rate**: Percentage of messages delivered
- **Bounce Rate**: Failed delivery attempts
- **Opt-out Rate**: Unsubscribe requests
- **Spam Reports**: User complaints
- **Response Rate**: User engagement

### **Compliance Requirements**
- **TCPA Compliance**: Consent and opt-out requirements
- **CAN-SPAM Act**: Commercial message regulations
- **GDPR**: EU privacy and consent rules
- **CASL**: Canadian anti-spam legislation
- **Industry Standards**: CTIA messaging principles

### **Regular Audits**
- Review message content for compliance
- Verify opt-in processes
- Test delivery rates across carriers
- Monitor sender reputation scores
- Update registration information

## Recommendations for SMS Campaigns

### **Best Practices**
1. **Always** register for A2P 10DLC before sending business messages
2. **Use** direct carrier-grade SMS providers
3. **Implement** double opt-in for marketing messages
4. **Monitor** delivery rates and adjust strategy accordingly
5. **Avoid** using URL shorteners from suspicious domains
6. **Include** clear branding and opt-out instructions
7. **Respect** user preferences and time zones
8. **Test** messages with small groups before large campaigns

### **Provider Selection**
- Choose providers with direct carrier relationships
- Verify 10DLC registration capabilities
- Ensure delivery rate transparency
- Look for advanced filtering bypass features
- Confirm international coverage if needed

### **Legal Considerations**
- Obtain proper consent before messaging
- Maintain opt-in records for compliance
- Respect opt-out requests immediately
- Include required disclosure information
- Follow industry-specific regulations

---

## Conclusion

SMS carrier blocking is a complex landscape that requires careful navigation. Success depends on:
- **Compliance** with carrier requirements
- **Quality** content that provides value
- **Proper** technical implementation
- **Ongoing** monitoring and optimization

The carriers listed above represent the most common blocking scenarios, but filtering rules change frequently. Regular testing and monitoring are essential for maintaining good deliverability rates.

*This guide is for educational purposes. Always consult with legal counsel and SMS compliance experts for specific campaign requirements.*
