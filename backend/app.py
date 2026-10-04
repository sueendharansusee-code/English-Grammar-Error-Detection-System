"""
Flask Application for English Grammar Error Detection System.
Provides RESTful APIs for real-time text analysis, SQLite history storage, and sample texts.
"""

from flask import Flask, request, jsonify, render_template
import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, save_analysis, get_all_history, get_history_by_id, clear_all_history
from backend.grammar_engine import analyze_grammar

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates"),
    static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
)

# Initialize Database on launch
with app.app_context():
    init_db()


# Preset sample sentences for user testing
SAMPLE_SENTENCES = [
    {
        "id": "sva",
        "title": "Subject-Verb Agreement",
        "category": "Grammar",
        "text": "He go to school every day. They is very happy with the results, but she don't know what happened."
    },
    {
        "id": "capitalization_spelling",
        "title": "Spelling & Capitalization",
        "category": "Orthography",
        "text": "i visited london on monday. teh weather was definately cold, and i had an wonderfull time with peaple."
    },
    {
        "id": "punctuation_repetition",
        "title": "Punctuation & Repeated Words",
        "category": "Punctuation",
        "text": "The student written the essay. the the professor asked why why did you submit it late"
    },
    {
        "id": "common_patterns",
        "title": "Homophones & Article Patterns",
        "category": "Word Choice",
        "text": "Your welcome to visit a apple farm with us. Their is more then ten books on the desk."
    },
    {
        "id": "full_essay",
        "title": "Mixed Essay Paragraph",
        "category": "Full Paragraph",
        "text": "i am writting this essay to show how grammer checking helps students. He work hard untill he reach his goal. your going to see big improvements soon. the the results is clear."
    }
]


@app.route('/')
def index():
    """Render the main educational dashboard."""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """API endpoint to analyze input text."""
    data = request.get_json() or {}
    text = data.get('text', '')
    
    if not text or not text.strip():
        return jsonify({
            "status": "error",
            "message": "Input text cannot be empty."
        }), 400
        
    try:
        report = analyze_grammar(text)
        
        # Save to database
        record_id = save_analysis(
            original_text=report["original_text"],
            corrected_text=report["corrected_text"],
            score=report["score"],
            error_count=report["error_count"],
            sentence_count=report["sentence_count"],
            word_count=report["word_count"],
            details=report["errors"]
        )
        report["id"] = record_id
        
        return jsonify({
            "status": "success",
            "data": report
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"An error occurred during text analysis: {str(e)}"
        }), 500


@app.route('/api/history', methods=['GET'])
def history():
    """Retrieve history records."""
    try:
        records = get_all_history()
        return jsonify({
            "status": "success",
            "data": records
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve history: {str(e)}"
        }), 500


@app.route('/api/history/<int:record_id>', methods=['GET'])
def history_detail(record_id):
    """Retrieve detailed history item."""
    try:
        record = get_history_by_id(record_id)
        if not record:
            return jsonify({
                "status": "error",
                "message": "History item not found."
            }), 404
            
        return jsonify({
            "status": "success",
            "data": record
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to fetch record detail: {str(e)}"
        }), 500


@app.route('/api/history', methods=['DELETE'])
def clear_history():
    """Clear all history items."""
    try:
        clear_all_history()
        return jsonify({
            "status": "success",
            "message": "History cleared successfully."
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to clear history: {str(e)}"
        }), 500


@app.route('/api/samples', methods=['GET'])
def samples():
    """Return pre-configured sample sentences."""
    return jsonify({
        "status": "success",
        "data": SAMPLE_SENTENCES
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
