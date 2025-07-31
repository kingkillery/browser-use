#!/usr/bin/env python3
"""
Test direct any-llm acompletion with OpenRouter ByteDance model.
"""
import os
import asyncio
from any_llm import acompletion

async def test_direct_bytedance():
    """Test direct acompletion with ByteDance model."""
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found")
        return False
    
    print("✅ OPENROUTER_API_KEY found")
    
    # Test different approaches to bypass provider validation
    approaches = [
        ("Use OpenAI provider to route to OpenRouter", "openai/bytedance/ui-tars-1.5-7b"),
        ("Use OpenAI provider generic", "openai/gpt-4o-mini"),  # Test known working model
    ]
    
    messages = [{"role": "user", "content": "Hello, what can you do for UI analysis?"}]
    
    for description, model in approaches:
        print(f"\n🧪 {description}")
        print(f"   Model: {model}")
        
        try:
            response = await acompletion(
                model=model,
                messages=messages,
                max_tokens=100,
                api_key=api_key,
                api_base='https://openrouter.ai/api/v1',
                temperature=0.1
            )
            
            if response and response.choices:
                content = response.choices[0].message.content
                print(f"✅ Success! Response: {content[:80]}...")
                
                # If this is the ByteDance model, we found the solution
                if "bytedance" in model:
                    print("🎉 ByteDance model accessible via this approach!")
                    return True
            else:
                print("❌ Empty response")
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}...")
    
    return False

if __name__ == "__main__":
    asyncio.run(test_direct_bytedance())
