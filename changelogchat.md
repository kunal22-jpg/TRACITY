# TRACITY AI Chat Integration Changelog & Solutions

## Current Issue
The Botpress chatbot cannot answer questions about MongoDB data (crime rates, literacy rates, etc.) because it's isolated from the TRACITY backend API and database.

## Root Cause
- **Before**: Custom AI chat → `/api/chat` endpoint → MongoDB queries → OpenAI insights
- **After**: Botpress iframe (isolated) → No database access → Cannot answer data questions

## Solution Options

### Option 1: Hybrid Chat System (Recommended)
Create a smart routing system that decides whether to use Botpress or the backend API.

#### Implementation Steps:
1. **Detect Data Questions**: Use keywords to identify database queries
   - Keywords: "crime rate", "literacy rate", "AQI", "power consumption", "Delhi", "Kerala", state names, years
   
2. **Create Chat Router Component**:
```javascript
// /app/frontend/src/components/ChatRouter.js
const ChatRouter = ({ message, onResponse }) => {
  const dataKeywords = ['crime rate', 'literacy', 'aqi', 'power', 'delhi', 'mumbai', 'kerala', ...allStates];
  const isDataQuery = dataKeywords.some(keyword => 
    message.toLowerCase().includes(keyword.toLowerCase())
  );
  
  if (isDataQuery) {
    // Route to backend API
    return callBackendAPI(message);
  } else {
    // Route to Botpress
    return useBotpress(message);
  }
};
```

3. **Modify ChatPopup.js**:
   - Add input field overlay on top of Botpress iframe
   - Intercept user messages before they reach Botpress
   - Route based on content
   - Display responses in custom message area

### Option 2: Botpress Webhook Integration
Configure Botpress to call your backend API for data questions.

#### Implementation Steps:
1. **Create Webhook Endpoint**:
```javascript
// Add to /app/backend/server.py
@api_router.post("/webhook/botpress")
async def botpress_webhook(request: dict):
    query = request.get('query', '')
    # Process using existing chat logic
    result = await process_data_query(query)
    return {"response": result}
```

2. **Configure Botpress**:
   - Add webhook action in Botpress studio
   - Set webhook URL: `https://your-domain.com/api/webhook/botpress`
   - Create intent detection for data queries
   - Route data questions to webhook

### Option 3: Enhanced Custom Chat (Full Replacement)
Replace Botpress with enhanced custom chat that has all your requirements.

#### Implementation Steps:
1. **Restore Custom Chat with Enhancements**:
   - Keep TRACITY loading animation
   - Add better conversation memory
   - Enhance UI/UX to match Botpress quality
   - Add typing indicators, better formatting

2. **Add Advanced Features**:
   - Session management
   - Conversation history
   - Rich message formatting
   - File upload capabilities
   - Voice input (if needed)

## Detailed Implementation Guide

### Step 1: Backup Current State
```bash
# Backup current ChatPopup.js
cp /app/frontend/src/components/ChatPopup.js /app/frontend/src/components/ChatPopup_botpress.js
```

### Step 2: Create Hybrid System Files

#### A. Create Message Router
```javascript
// /app/frontend/src/utils/messageRouter.js
export class MessageRouter {
  static dataKeywords = [
    'crime', 'literacy', 'aqi', 'air quality', 'power consumption',
    'delhi', 'mumbai', 'bangalore', 'kerala', 'tamil nadu', 'punjab',
    'maharashtra', 'gujarat', 'rajasthan', 'uttar pradesh', 'bihar',
    'west bengal', 'andhra pradesh', 'telangana', 'karnataka',
    'year', '2019', '2020', '2021', '2022', '2023', '2024',
    'rate', 'statistics', 'data', 'trend', 'compare'
  ];

  static isDataQuery(message) {
    const lowerMessage = message.toLowerCase();
    return this.dataKeywords.some(keyword => lowerMessage.includes(keyword));
  }

  static async routeMessage(message) {
    if (this.isDataQuery(message)) {
      return await this.callBackendAPI(message);
    } else {
      return await this.callBotpress(message);
    }
  }

  static async callBackendAPI(message) {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: message, dataset: null })
      });
      
      const data = await response.json();
      return {
        type: 'data',
        content: data.results?.[0]?.insight || "I couldn't find data for that query.",
        source: 'TRACITY Database'
      };
    } catch (error) {
      return {
        type: 'error',
        content: "Sorry, I couldn't access the database right now.",
        source: 'Error'
      };
    }
  }

  static async callBotpress(message) {
    // This would require Botpress API integration
    return {
      type: 'general',
      content: "This would be handled by your Botpress bot.",
      source: 'Botpress'
    };
  }
}
```

#### B. Create Enhanced Chat Component
```javascript
// /app/frontend/src/components/HybridChatPopup.js
import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageRouter } from '../utils/messageRouter';

const HybridChatPopup = ({ onClose }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      content: "Hello! I'm your TRACITY AI assistant. I can help you analyze data from our MongoDB database or answer general questions. Try asking about crime rates, literacy statistics, or any other data insights!",
      timestamp: new Date(),
      source: 'TRACITY'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    // TRACITY loading animation
    setTimeout(() => setIsInitializing(false), 2000);
  }, []);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const query = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await MessageRouter.routeMessage(query);
      
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: response.content,
        timestamp: new Date(),
        source: response.source,
        dataType: response.type
      };
      
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: "I apologize, but I'm having trouble processing your request right now. Please try again.",
        timestamp: new Date(),
        source: 'Error'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Rest of the component similar to original with TRACITY loading...
};
```

### Step 3: Backend Enhancements

#### A. Improve Chat Endpoint
```python
# Add to /app/backend/server.py
@api_router.post("/chat/enhanced")
async def enhanced_chat(query: ChatQuery):
    """Enhanced chat with better data processing"""
    try:
        # Detect query type
        query_lower = query.query.lower()
        
        # State detection
        indian_states = ['delhi', 'mumbai', 'bangalore', 'kerala', 'tamil nadu', ...]
        detected_states = [state for state in indian_states if state in query_lower]
        
        # Year detection
        years = re.findall(r'\b(20\d{2})\b', query.query)
        
        # Data type detection
        if 'crime' in query_lower:
            collection = 'crimes'
        elif 'literacy' in query_lower:
            collection = 'literacy'
        elif 'aqi' in query_lower or 'air quality' in query_lower:
            collection = 'aqi'
        elif 'power' in query_lower:
            collection = 'power_consumption'
        else:
            collection = None
        
        if collection and (detected_states or years):
            # Build specific query
            filter_query = {}
            if detected_states:
                filter_query['state'] = {'$in': detected_states}
            if years:
                filter_query['year'] = {'$in': [int(year) for year in years]}
            
            # Get specific data
            data = await db[collection].find(filter_query).limit(10).to_list(10)
            
            if data:
                # Generate enhanced insight
                insight = await generate_specific_insight(data, query.query, collection)
                return {
                    "query": query.query,
                    "results": [{
                        "insight": insight,
                        "data": data[:3],  # Sample data
                        "collection": collection,
                        "filters_applied": filter_query
                    }]
                }
        
        # Fallback to general search
        return await chat_with_ai(query)
        
    except Exception as e:
        logging.error(f"Enhanced chat error: {e}")
        return {"error": "Could not process your request"}

async def generate_specific_insight(data, query, collection):
    """Generate specific insights for exact queries"""
    try:
        # Calculate statistics
        if collection == 'crimes':
            total_crimes = sum(item.get('count', 0) for item in data)
            avg_crimes = total_crimes / len(data) if data else 0
            states = list(set(item.get('state', '') for item in data))
            
            insight = f"Based on our database, "
            if len(states) == 1:
                insight += f"in {states[0]}, "
            else:
                insight += f"across {', '.join(states)}, "
                
            insight += f"there were {total_crimes:,} total crime incidents recorded "
            insight += f"with an average of {avg_crimes:.1f} incidents per record. "
            
            # Add trend analysis if multiple years
            years = sorted(set(item.get('year', 0) for item in data))
            if len(years) > 1:
                insight += f"Data spans from {min(years)} to {max(years)}. "
                
        elif collection == 'literacy':
            rates = [item.get('literacy_rate', 0) for item in data if item.get('literacy_rate')]
            if rates:
                avg_rate = sum(rates) / len(rates)
                max_rate = max(rates)
                min_rate = min(rates)
                insight = f"Literacy rates show an average of {avg_rate:.1f}%, "
                insight += f"ranging from {min_rate:.1f}% to {max_rate:.1f}%. "
        
        return insight
        
    except Exception as e:
        return f"Found {len(data)} relevant records in our database for your query."
```

## Files to Modify

### Frontend Changes:
1. `/app/frontend/src/components/ChatPopup.js` - Implement hybrid system
2. `/app/frontend/src/utils/messageRouter.js` - Create (new file)
3. `/app/frontend/src/components/HybridChatPopup.js` - Create (new file)

### Backend Changes:
1. `/app/backend/server.py` - Add enhanced chat endpoint
2. Add better query processing and state/year detection

## Implementation Priority

### High Priority (Essential):
1. **Message Routing System**: Detect data vs general queries
2. **Backend API Integration**: Restore database query functionality
3. **UI Integration**: Seamless experience for users

### Medium Priority (Enhancements):
1. **Better Query Processing**: Natural language understanding
2. **Rich Responses**: Charts, tables, formatted data
3. **Session Management**: Remember conversation context

### Low Priority (Future):
1. **Voice Integration**: Speech-to-text
2. **File Upload**: CSV analysis
3. **Advanced Analytics**: Predictive insights

## Testing Checklist

### Data Query Tests:
- [ ] "What is the crime rate in Delhi in 2020?"
- [ ] "Show me literacy rates in Kerala"
- [ ] "Compare AQI between Mumbai and Bangalore"
- [ ] "Power consumption trends in 2023"

### General Query Tests:
- [ ] "Hello, how are you?"
- [ ] "What can you help me with?"
- [ ] "Tell me a joke"
- [ ] "How does TRACITY work?"

## Estimated Implementation Time
- **Option 1 (Hybrid)**: 4-6 hours
- **Option 2 (Webhook)**: 6-8 hours  
- **Option 3 (Custom)**: 3-4 hours

## Recommended Approach
**Start with Option 3 (Enhanced Custom Chat)** because:
1. Faster implementation
2. Full control over functionality
3. Better integration with existing backend
4. No external dependencies
5. Keep TRACITY branding and loading animation

## Current Status
- ✅ Botpress integrated with TRACITY branding
- ✅ Custom loading animation implemented
- ❌ Database query functionality missing
- ❌ Cannot answer data-specific questions

## Next Steps
1. Choose implementation option
2. Backup current Botpress integration
3. Implement chosen solution
4. Test with sample queries
5. Deploy and verify functionality

---
*Created: Current Date*
*Status: Implementation Required*
*Priority: High - Core functionality missing*