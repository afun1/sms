"""
SimpleTalk.ai Integration for Sparky Messaging
Provides AI-powered conversation generation and message optimization
"""

import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class SimpleTalkAI:
    def __init__(self):
        self.api_key = os.getenv('SIMPLETALK_API_KEY')
        self.base_url = os.getenv('SIMPLETALK_BASE_URL', 'https://api.simpletalk.ai/v1')
        self.model = os.getenv('SIMPLETALK_MODEL', 'gpt-4')
        
        if not self.api_key:
            logger.warning("SimpleTalk.ai API key not configured")
    
    def is_configured(self):
        """Check if SimpleTalk.ai is properly configured"""
        return bool(self.api_key)
    
    def generate_sms_message(self, context, contact_info=None, tone="friendly", max_length=160):
        """
        Generate optimized SMS message using SimpleTalk.ai
        
        Args:
            context (str): Context or purpose of the message
            contact_info (dict): Contact information (name, company, etc.)
            tone (str): Message tone (friendly, professional, urgent, casual)
            max_length (int): Maximum message length for SMS
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.is_configured():
            return False, "SimpleTalk.ai not configured"
        
        try:
            # Prepare contact context
            contact_context = ""
            if contact_info:
                name = contact_info.get('name', 'there')
                company = contact_info.get('company', '')
                if company:
                    contact_context = f"The recipient is {name} from {company}. "
                else:
                    contact_context = f"The recipient is {name}. "
            
            # Create prompt for SMS generation
            prompt = f"""Generate a {tone} SMS message that is concise and effective.

Context: {context}
{contact_context}

Requirements:
- Maximum {max_length} characters (SMS limit)
- {tone.capitalize()} tone
- Clear call-to-action if applicable
- Personalized if contact info provided
- Compliant with SMS best practices

Generate only the SMS message text, no quotes or extra formatting:"""

            # Call SimpleTalk.ai API
            response = self._make_api_call('chat/completions', {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': 'You are an expert SMS marketing specialist who creates compelling, concise messages that drive engagement while staying within character limits.'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 100,
                'temperature': 0.7
            })
            
            if response and 'choices' in response:
                message = response['choices'][0]['message']['content'].strip()
                
                # Ensure message length
                if len(message) > max_length:
                    message = message[:max_length-3] + "..."
                
                logger.info(f"Generated SMS message: {len(message)} characters")
                return True, message
            else:
                return False, "Failed to generate message"
                
        except Exception as e:
            logger.error(f"Error generating SMS message: {e}")
            return False, f"Error: {str(e)}"
    
    def generate_rvm_script(self, context, contact_info=None, tone="conversational", duration="30 seconds"):
        """
        Generate voicemail script using SimpleTalk.ai
        
        Args:
            context (str): Context or purpose of the voicemail
            contact_info (dict): Contact information
            tone (str): Script tone (conversational, professional, urgent, friendly)
            duration (str): Target duration
        
        Returns:
            tuple: (success: bool, script: str)
        """
        if not self.is_configured():
            return False, "SimpleTalk.ai not configured"
        
        try:
            # Prepare contact context
            contact_context = ""
            if contact_info:
                name = contact_info.get('name', 'there')
                company = contact_info.get('company', '')
                if company:
                    contact_context = f"The recipient is {name} from {company}. "
                else:
                    contact_context = f"The recipient is {name}. "
            
            prompt = f"""Generate a {tone} voicemail script for text-to-speech conversion.

Context: {context}
{contact_context}

Requirements:
- Target duration: {duration}
- {tone.capitalize()} and natural speaking tone
- Clear and compelling message
- Proper pacing for TTS (avoid rushed content)
- Professional but human-sounding
- Include natural pauses with commas and periods

Generate only the voicemail script text:"""

            response = self._make_api_call('chat/completions', {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': 'You are an expert voicemail copywriter who creates engaging, natural-sounding scripts optimized for text-to-speech conversion and maximum callback rates.'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 200,
                'temperature': 0.7
            })
            
            if response and 'choices' in response:
                script = response['choices'][0]['message']['content'].strip()
                logger.info(f"Generated RVM script: {len(script)} characters")
                return True, script
            else:
                return False, "Failed to generate script"
                
        except Exception as e:
            logger.error(f"Error generating RVM script: {e}")
            return False, f"Error: {str(e)}"
    
    def create_conversation_flow(self, campaign_goal, audience_info, num_steps=3):
        """
        Create a multi-step conversation flow using SimpleTalk.ai
        
        Args:
            campaign_goal (str): Goal of the campaign
            audience_info (str): Information about target audience
            num_steps (int): Number of steps in the flow
        
        Returns:
            tuple: (success: bool, flow: list)
        """
        if not self.is_configured():
            return False, "SimpleTalk.ai not configured"
        
        try:
            prompt = f"""Create a {num_steps}-step conversation flow for a multi-channel campaign.

Campaign Goal: {campaign_goal}
Target Audience: {audience_info}

Create a strategic sequence that combines SMS and voicemail messages:

Requirements:
- {num_steps} sequential touchpoints
- Mix of SMS and RVM (ringless voicemail) 
- Progressive value delivery
- Clear calls-to-action
- Proper timing between steps
- Compliance with messaging best practices

Format as JSON with this structure:
{{
  "flow_name": "Campaign Name",
  "total_steps": {num_steps},
  "steps": [
    {{
      "step": 1,
      "type": "sms",
      "timing": "immediate",
      "message": "SMS content here",
      "purpose": "introduction/awareness"
    }},
    {{
      "step": 2,
      "type": "rvm", 
      "timing": "24 hours later",
      "message": "Voicemail script here",
      "purpose": "value delivery"
    }}
  ]
}}

Generate only the JSON response:"""

            response = self._make_api_call('chat/completions', {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': 'You are a marketing automation expert who creates high-converting multi-channel conversation flows. Always respond with valid JSON only.'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 500,
                'temperature': 0.7
            })
            
            if response and 'choices' in response:
                flow_json = response['choices'][0]['message']['content'].strip()
                
                # Parse JSON response
                try:
                    flow_data = json.loads(flow_json)
                    logger.info(f"Generated conversation flow: {flow_data.get('flow_name', 'Unnamed')}")
                    return True, flow_data
                except json.JSONDecodeError:
                    logger.error("Failed to parse JSON response from SimpleTalk.ai")
                    return False, "Invalid JSON response"
            else:
                return False, "Failed to generate conversation flow"
                
        except Exception as e:
            logger.error(f"Error creating conversation flow: {e}")
            return False, f"Error: {str(e)}"
    
    def optimize_message(self, original_message, optimization_goal="engagement"):
        """
        Optimize an existing message using SimpleTalk.ai
        
        Args:
            original_message (str): The original message to optimize
            optimization_goal (str): Goal (engagement, conversion, clarity, brevity)
        
        Returns:
            tuple: (success: bool, optimized_message: str, improvements: str)
        """
        if not self.is_configured():
            return False, "SimpleTalk.ai not configured", ""
        
        try:
            prompt = f"""Optimize this message for {optimization_goal}:

Original Message: "{original_message}"

Optimization Goal: {optimization_goal}

Please provide:
1. An optimized version of the message
2. A brief explanation of improvements made

Format your response as:
OPTIMIZED: [optimized message]
IMPROVEMENTS: [explanation of changes]"""

            response = self._make_api_call('chat/completions', {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': f'You are a messaging optimization expert. Improve messages for maximum {optimization_goal} while maintaining clarity and compliance.'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 150,
                'temperature': 0.7
            })
            
            if response and 'choices' in response:
                result = response['choices'][0]['message']['content'].strip()
                
                # Parse the response
                lines = result.split('\n')
                optimized_message = ""
                improvements = ""
                
                for line in lines:
                    if line.startswith('OPTIMIZED:'):
                        optimized_message = line.replace('OPTIMIZED:', '').strip()
                    elif line.startswith('IMPROVEMENTS:'):
                        improvements = line.replace('IMPROVEMENTS:', '').strip()
                
                logger.info(f"Optimized message for {optimization_goal}")
                return True, optimized_message, improvements
            else:
                return False, "Failed to optimize message", ""
                
        except Exception as e:
            logger.error(f"Error optimizing message: {e}")
            return False, f"Error: {str(e)}", ""
    
    def _make_api_call(self, endpoint, data):
        """Make API call to SimpleTalk.ai"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}/{endpoint}"
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"SimpleTalk.ai API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"SimpleTalk.ai API call failed: {e}")
            return None
    
    def get_account_usage(self):
        """Get SimpleTalk.ai account usage information"""
        if not self.is_configured():
            return False, "SimpleTalk.ai not configured"
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f"{self.base_url}/usage", headers=headers, timeout=10)
            
            if response.status_code == 200:
                usage_data = response.json()
                return True, usage_data
            else:
                return False, f"API error: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Error getting usage: {e}")
            return False, f"Error: {str(e)}"

# Example usage and testing
def test_simpletalk_integration():
    """Test SimpleTalk.ai integration"""
    
    print("🤖 Testing SimpleTalk.ai Integration")
    print("=" * 50)
    
    ai = SimpleTalkAI()
    
    # Check configuration
    if not ai.is_configured():
        print("❌ SimpleTalk.ai not configured")
        print("💡 Please set SIMPLETALK_API_KEY in .env")
        return
    
    print("✅ SimpleTalk.ai configured")
    
    # Test SMS generation
    print("\n📱 Testing SMS Generation...")
    contact = {"name": "John Smith", "company": "ABC Corp"}
    success, message = ai.generate_sms_message(
        "Follow up on meeting about marketing automation",
        contact,
        tone="professional"
    )
    
    if success:
        print(f"✅ Generated SMS: {message}")
        print(f"📏 Length: {len(message)} characters")
    else:
        print(f"❌ SMS generation failed: {message}")
    
    # Test RVM script generation
    print("\n🎙️ Testing RVM Script Generation...")
    success, script = ai.generate_rvm_script(
        "Introduction to new service offering",
        contact,
        tone="conversational"
    )
    
    if success:
        print(f"✅ Generated RVM Script:")
        print(f"📝 {script}")
    else:
        print(f"❌ RVM generation failed: {script}")
    
    # Test conversation flow
    print("\n🔄 Testing Conversation Flow...")
    success, flow = ai.create_conversation_flow(
        "Generate leads for consulting services",
        "Small business owners in tech industry",
        num_steps=3
    )
    
    if success:
        print(f"✅ Generated Flow: {flow.get('flow_name', 'Unknown')}")
        print(f"📊 Steps: {len(flow.get('steps', []))}")
    else:
        print(f"❌ Flow generation failed: {flow}")

if __name__ == "__main__":
    test_simpletalk_integration()
