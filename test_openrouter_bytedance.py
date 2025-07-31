#!/usr/bin/env python3
"""
Test OpenRouter ByteDance model integration using ChatOpenRouter.
"""
import os
import asyncio
from browser_use.llm import ChatOpenRouter
from browser_use.llm.messages import UserMessage, SystemMessage

async def test_openrouter_bytedance():
    """Test ByteDance model integration via OpenRouter using ChatOpenRouter."""
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found")
        return False
    
    print("✅ OPENROUTER_API_KEY found")
    
    try:
        # Correctly configure ChatOpenRouter for ByteDance UI-TARS
        llm = ChatOpenRouter(
            model='bytedance/ui-tars-1.5-7b',
            api_key=api_key,
            temperature=0.1
        )
        
        print(f"✅ ChatOpenRouter configured with model: {llm.model}")
        
        # Test message to send
        messages = [
            SystemMessage(content="You are a UI analysis expert."),
            UserMessage(content="Explain what you do.")
        ]
        
        print("🧪 Testing OpenRouter with ByteDance model...")
        
        response = await llm.ainvoke(messages)
        
        if response and response.completion:
            print("✅ Success! OpenRouter ByteDance model accessible.")
            print(f"📝 Response: {response.completion[:100]}...")
            return True
        else:
            print("❌ Empty response")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_openrouter_bytedance())
