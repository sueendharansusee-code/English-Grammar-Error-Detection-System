"""
Hybrid Grammar Engine supporting NLTK tokenization, rule-based error detection,
and optional LanguageTool integration with automatic fallback.
"""

import re
import nltk
from backend.rules import run_all_custom_rules

# Ensure required NLTK resources are available safely
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt', quiet=True)
    except Exception:
        pass

# Optional LanguageTool integration with graceful fallback
LANGUAGE_TOOL_AVAILABLE = False
lt_tool = None

try:
    import language_tool_python
    # Attempt to initialize LanguageTool (may run local or download server binary)
    # If Java / local server fails, catch exception and fallback to rule-based engine
    lt_tool = language_tool_python.LanguageTool('en-US')
    LANGUAGE_TOOL_AVAILABLE = True
except Exception as e:
    LANGUAGE_TOOL_AVAILABLE = False


def tokenize_sentences(text):
    """Tokenize text into sentences using NLTK or regex fallback."""
    try:
        sentences = nltk.sent_tokenize(text)
        if sentences:
            return sentences
    except Exception:
        pass
    
    # Fallback sentence tokenizer regex
    raw_sents = re.split(r'(?<=[.!?])\s+', text)
    return [s for s in raw_sents if s.strip()]


def calculate_grammar_score(word_count, sentence_count, error_count):
    """
    Compute a Grammar Score out of 100 based on error density per 100 words.
    Score = max(0, 100 - (errors / max(1, words)) * 200)
    """
    if word_count == 0:
        return 100
        
    error_density = (error_count / word_count) * 100
    penalty = error_density * 2.5
    score = max(0, min(100, round(100 - penalty)))
    
    # Adjust score if no errors found
    if error_count == 0:
        return 100
        
    return int(score)


def generate_corrected_text(text, errors):
    """Generate corrected text by applying replacements to character offsets."""
    if not errors:
        return text
        
    # Sort errors by start offset
    sorted_errors = sorted(errors, key=lambda x: x["start"])
    
    result = []
    last_idx = 0
    
    for err in sorted_errors:
        start = err["start"]
        end = err["end"]
        replacement = err["replacement"]
        
        if start >= last_idx:
            result.append(text[last_idx:start])
            result.append(replacement)
            last_idx = end
            
    result.append(text[last_idx:])
    return "".join(result)


def analyze_text_with_languagetool(text):
    """Analyze text using LanguageTool if active."""
    matches = lt_tool.check(text)
    errors = []
    
    for match in matches:
        category_name = match.category
        rule_id = match.ruleId
        
        # Categorize
        if "SPELL" in rule_id.upper() or "TYPO" in rule_id.upper():
            err_type = "Spelling"
        elif "PUNCT" in rule_id.upper() or "COMMA" in rule_id.upper():
            err_type = "Missing Punctuation"
        elif "CAPITAL" in rule_id.upper() or "UPPER" in rule_id.upper():
            err_type = "Capitalization"
        elif "AGREEMENT" in rule_id.upper() or "SVA" in rule_id.upper() or "VERB" in rule_id.upper():
            err_type = "Subject-Verb Agreement"
        elif "REPETITION" in rule_id.upper() or "DUP" in rule_id.upper():
            err_type = "Repeated Words"
        else:
            err_type = "Common Patterns"
            
        replacement = match.replacements[0] if match.replacements else match.context
        
        errors.append({
            "start": match.offset,
            "end": match.offset + match.errorLength,
            "original": text[match.offset:match.offset + match.errorLength],
            "replacement": replacement,
            "type": err_type,
            "explanation": match.message
        })
        
    return errors


def analyze_grammar(text):
    """
    Main analysis pipeline.
    Runs LanguageTool if available, or custom rule engine as fallback.
    Returns complete report dict.
    """
    text = text.strip()
    if not text:
        return {
            "original_text": "",
            "corrected_text": "",
            "score": 100,
            "error_count": 0,
            "correct_sentences": 0,
            "suggestions_count": 0,
            "word_count": 0,
            "sentence_count": 0,
            "engine_used": "NLTK + Rules Engine",
            "errors": []
        }

    # 1. Count sentences and words
    sentences = tokenize_sentences(text)
    sentence_count = len(sentences)
    words = re.findall(r'\b[A-Za-z0-9\'-]+\b', text)
    word_count = len(words)
    
    # 2. Run NLP detection
    engine_used = "LanguageTool Engine"
    errors = []
    
    if LANGUAGE_TOOL_AVAILABLE and lt_tool is not None:
        try:
            errors = analyze_text_with_languagetool(text)
        except Exception:
            errors = run_all_custom_rules(text)
            engine_used = "NLTK + Custom Rules (LT Fallback)"
    else:
        errors = run_all_custom_rules(text)
        engine_used = "NLTK + Custom Rules Engine"

    # 3. Calculate statistics
    error_count = len(errors)
    
    # Determine correct sentences count
    # Sentence is correct if no error overlaps its offsets
    correct_sentences = 0
    for sent in sentences:
        sent_start = text.find(sent)
        sent_end = sent_start + len(sent) if sent_start != -1 else 0
        
        sent_has_error = any(
            err["start"] >= sent_start and err["end"] <= sent_end
            for err in errors
        )
        if not sent_has_error:
            correct_sentences += 1
            
    score = calculate_grammar_score(word_count, sentence_count, error_count)
    corrected_text = generate_corrected_text(text, errors)
    suggestions_count = error_count  # Each error yields a correction suggestion
    
    return {
        "original_text": text,
        "corrected_text": corrected_text,
        "score": score,
        "error_count": error_count,
        "correct_sentences": correct_sentences,
        "suggestions_count": suggestions_count,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "engine_used": engine_used,
        "errors": errors
    }
