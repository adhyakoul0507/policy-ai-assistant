from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from firebase_config import db
from firebase_admin import auth
import os
from datetime import datetime
import logging
from dotenv import load_dotenv
import json
import time
from functools import wraps

load_dotenv()

app = Flask(__name__)
CORS(app)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')


def retry_on_quota_error(max_retries=3, delay=35):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if "quota" in str(e).lower() and attempt < max_retries - 1:
                        logger.warning(f"Quota exceeded, waiting {delay} seconds before retry {attempt + 1}")
                        time.sleep(delay)
                        continue
                    raise e
            return func(*args, **kwargs)
        return wrapper
    return decorator


@retry_on_quota_error()
def generate_with_gemini(prompt):
    response = model.generate_content(prompt)
    return response.text


def verify_token(token):
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except:
        return None

def get_user_id(request):
    """Extract user ID from request headers"""
    auth_header = request.headers.get('Authorization')
    if auth_header:
        token = auth_header.split(' ')[1]
        user_data = verify_token(token)
        return user_data['uid'] if user_data else 'anonymous'
    return 'anonymous'


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Policy Chatbot Backend is running!",
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "/api/compare-policies",
            "/api/sentiment-analysis",
            "/api/check-eligibility",
            "/api/regional-policies",
            "/api/general-query",
            "/api/chat",
            "/api/test"
        ]
    })

@app.route('/api/test', methods=['GET', 'POST'])
def test():
    return jsonify({
        "success": True,
        "message": "API endpoint working!",
        "method": request.method,
        "timestamp": datetime.now().isoformat(),
        "headers": dict(request.headers),
        "data": request.json if request.method == 'POST' else None
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })


@app.route('/api/compare-policies', methods=['POST'])
def compare_policies():
    try:
        user_id = get_user_id(request)
        data = request.json
        policy1 = data.get('policy1', '')
        policy2 = data.get('policy2', '')
        
        
        prompt = f"""
        Please provide a comprehensive comparison between {policy1} and {policy2} government policies.
        
        Include:
        1. Overview of each policy
        2. Key differences in implementation
        3. Target beneficiaries
        4. Budget allocation and funding sources
        5. Success metrics and outcomes
        6. Challenges and criticisms
        7. Future prospects
        
        Format the response in a clear, structured manner.
        """
        
        comparison_text = generate_with_gemini(prompt)
        
     
        comparison_data = {
            'user_id': user_id,
            'policy1': policy1,
            'policy2': policy2,
            'comparison': comparison_text,
            'timestamp': datetime.now(),
            'type': 'policy_comparison'
        }
        
        db.collection('policy_analyses').add(comparison_data)
        
        return jsonify({
            'success': True,
            'comparison': comparison_text,
            'timestamp': datetime.now().isoformat(),
            'language': 'English'
        })
        
    except Exception as e:
        logger.error(f"Error in compare_policies: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sentiment-analysis', methods=['POST'])
def sentiment_analysis():
    try:
        user_id = get_user_id(request)
        data = request.json
        policy_name = data.get('policy_name', '')
        
        
        prompt = f"""
        Analyze the sentiment and stakeholder perspectives on the {policy_name} government policy.
        
        Please provide:
        1. Overall public sentiment (positive/negative/neutral)
        2. Different stakeholder group perspectives:
           - Citizens/Beneficiaries
           - Media coverage
           - Opposition parties
           - NGOs and civil society
           - Industry/Business groups
        3. Key areas of support and criticism
        4. Regional variations in sentiment
        5. Changes in sentiment over time
        6. Recommendations for improving public perception
        
        Format the response with clear sections and bullet points.
        """
        
        analysis_text = generate_with_gemini(prompt)
        

        sentiment_data = {
            'user_id': user_id,
            'policy_name': policy_name,
            'analysis': analysis_text,
            'timestamp': datetime.now(),
            'type': 'sentiment_analysis'
        }
        
        db.collection('policy_analyses').add(sentiment_data)
        
        return jsonify({
            'success': True,
            'analysis': analysis_text,
            'timestamp': datetime.now().isoformat(),
            'language': 'English'
        })
        
    except Exception as e:
        logger.error(f"Error in sentiment_analysis: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/check-eligibility', methods=['POST'])
def check_eligibility():
    try:
        user_id = get_user_id(request)
        data = request.json
        
        
        age = data.get('age', 0)
        gender = data.get('gender', '')
        income = data.get('income', 0)
        caste = data.get('caste', '')
        occupation = data.get('occupation', '')
        state = data.get('state', '')
        location = data.get('location', '')
        
     
        prompt = f"""
        Based on the following personal information, check eligibility for Indian government schemes:
        
        Age: {age} years
        Gender: {gender}
        Annual Income: ₹{income}
        Category: {caste}
        Occupation: {occupation}
        State: {state}
        Location: {location}
        
        Please provide:
        1. A list of eligible government schemes with:
           - Scheme name
           - Key benefits
           - Application process
           - Eligibility criteria
        2. Detailed analysis of why each scheme is suitable
        3. Application deadlines and important dates
        4. Required documents
        5. Contact information for applications
        
        Format the response as a comprehensive guide.
        """
        
        eligibility_text = generate_with_gemini(prompt)
        
        
        eligible_schemes = [
            {
                'name': 'PM-KISAN',
                'benefits': 'Direct income support of ₹6,000 per year',
                'application': 'Online through PM-KISAN portal',
                'criteria': {'income': 'Below ₹2 lakh', 'occupation': 'Farmer'}
            },
            {
                'name': 'Ayushman Bharat',
                'benefits': 'Health insurance up to ₹5 lakh',
                'application': 'Through Common Service Centers',
                'criteria': {'income': 'Below poverty line', 'category': 'All'}
            }
        ]
        
    
        eligibility_data = {
            'user_id': user_id,
            'user_profile': data,
            'eligible_schemes': eligible_schemes,
            'detailed_analysis': eligibility_text,
            'timestamp': datetime.now(),
            'type': 'eligibility_check'
        }
        
        db.collection('policy_analyses').add(eligibility_data)
        
        return jsonify({
            'success': True,
            'eligible_schemes': eligible_schemes,
            'detailed_analysis': eligibility_text,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in check_eligibility: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/regional-policies', methods=['POST'])
def regional_policies():
    try:
        user_id = get_user_id(request)
        data = request.json
        state = data.get('state', '')
        
        
        prompt = f"""
        Provide comprehensive information about government policies specific to {state}, India.
        Be careful to use only factual and up-to-date information. Do not assume or exaggerate statistics such as population or budget. If exact values are not known, say "data not available".
        Include:
        1. State-specific government schemes and policies
        2. Budget allocation and spending priorities
        3. Key development initiatives
        4. Agricultural and rural development programs
        5. Industrial and economic policies
        6. Social welfare schemes
        7. Infrastructure development projects
        8. Comparison with national policies
        9. Recent policy changes and updates
        10. Contact information for state departments
        
        Format the response with clear sections and practical information.
        """

        
        
        regional_info = generate_with_gemini(prompt)
        
  
        regional_data = {
            'user_id': user_id,
            'state': state,
            'regional_info': regional_info,
            'timestamp': datetime.now(),
            'type': 'regional_policies'
        }
        
        db.collection('policy_analyses').add(regional_data)
        
        return jsonify({
            'success': True,
            'regional_info': regional_info,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in regional_policies: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/general-query', methods=['POST'])
def general_query():
    try:
        user_id = get_user_id(request)
        data = request.json
        query = data.get('query', '')
        language = data.get('language', 'English')
        
        
        prompt = f"""
        Answer the following policy-related question in {language}:
        
        Question: {query}
        
        Please provide:
        1. A comprehensive answer
        2. Relevant policy details
        3. Implementation information
        4. Benefits and eligibility
        5. Application process if applicable
        6. Recent updates or changes
        7. Official sources and contacts
        
        Format the response in a clear, informative manner.
        """
        
        answer_text = generate_with_gemini(prompt)
        
    
        query_data = {
            'user_id': user_id,
            'query': query,
            'answer': answer_text,
            'language': language,
            'timestamp': datetime.now(),
            'type': 'general_query'
        }
        
        db.collection('policy_analyses').add(query_data)
        
        return jsonify({
            'success': True,
            'answer': answer_text,
            'language': language,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in general_query: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        user_id = get_user_id(request)
        data = request.json
        message = data.get('message', '')
        
        bot_response = generate_with_gemini(message)
        
        
        conversation_data = {
            'user_id': user_id,
            'user_message': message,
            'bot_response': bot_response,
            'timestamp': datetime.now(),
            'session_id': data.get('session_id', 'default'),
            'type': 'chat'
        }
        
        db.collection('conversations').add(conversation_data)
        
        return jsonify({
            'success': True,
            'response': bot_response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/history/<user_id>', methods=['GET'])
def get_history(user_id):
    try:
        from google.cloud import firestore
        

        conversations = db.collection('conversations')\
            .where('user_id', '==', user_id)\
            .order_by('timestamp', direction=firestore.Query.DESCENDING)\
            .limit(50)\
            .stream()
        
        history = []
        for conv in conversations:
            data = conv.to_dict()
            history.append({
                'id': conv.id,
                'user_message': data.get('user_message'),
                'bot_response': data.get('bot_response'),
                'timestamp': data.get('timestamp').isoformat()
            })
        
        return jsonify({'success': True, 'history': history})
        
    except Exception as e:
        logger.error(f"Error in get_history: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/<user_id>', methods=['GET'])
def get_analytics(user_id):
    try:
        from google.cloud import firestore
        
      
        analyses = db.collection('policy_analyses')\
            .where('user_id', '==', user_id)\
            .order_by('timestamp', direction=firestore.Query.DESCENDING)\
            .limit(100)\
            .stream()
        
        analytics_data = []
        for analysis in analyses:
            data = analysis.to_dict()
            analytics_data.append({
                'id': analysis.id,
                'type': data.get('type'),
                'timestamp': data.get('timestamp').isoformat(),
                'details': data
            })
        
        return jsonify({'success': True, 'analytics': analytics_data})
        
    except Exception as e:
        logger.error(f"Error in get_analytics: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=5000)
