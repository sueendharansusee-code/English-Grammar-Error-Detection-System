"""
Custom NLP Grammar and Writing Error Detection Rules.
Provides robust offline rule-based detection for 6 main categories:
1. Subject-Verb Agreement
2. Missing Punctuation
3. Repeated Words
4. Basic Spelling Mistakes
5. Incorrect Capitalization
6. Common Grammatical Patterns & Word Choice
"""

import re

# Common English spelling dictionary for educational grammar checker
SPELLING_DICTIONARY = {
    "teh": "the",
    "thier": "their",
    "recieve": "receive",
    "seperate": "separate",
    "definately": "definitely",
    "definatly": "definitely",
    "grammer": "grammar",
    "untill": "until",
    "occured": "occurred",
    "truely": "truly",
    "tommorow": "tomorrow",
    "tomorow": "tomorrow",
    "accomodate": "accommodate",
    "wierd": "weird",
    "beleive": "believe",
    "acheive": "achieve",
    "goverment": "government",
    "enviornment": "environment",
    "knowlege": "knowledge",
    "refering": "referring",
    "similiar": "similar",
    "embarass": "embarrass",
    "happenning": "happening",
    "begining": "beginning",
    "alot": "a lot",
    "succesful": "successful",
    "writting": "writing",
    "peaple": "people",
    "poeple": "people",
    "diffrent": "different",
    "intrested": "interested",
    "oppurtunity": "opportunity",
    "neccessary": "necessary",
    "necesary": "necessary",
    "exellent": "excellent",
    "recomended": "recommended",
    "recommened": "recommended",
    "privilege": "privilege",
    "privelege": "privilege",
    "pronounciation": "pronunciation",
    "independant": "independent",
    "calender": "calendar",
    "foreign": "foreign",
    "foriegn": "foreign",
    "maintainance": "maintenance"
}

DAYS_AND_MONTHS = {
    "monday": "Monday", "tuesday": "Tuesday", "wednesday": "Wednesday",
    "thursday": "Thursday", "friday": "Friday", "saturday": "Saturday", "sunday": "Sunday",
    "january": "January", "february": "February", "march": "March", "april": "April",
    "may": "May", "june": "June", "july": "July", "august": "August",
    "september": "September", "october": "October", "november": "November", "december": "December"
}

LANGUAGES = {
    "english": "English", "spanish": "Spanish", "french": "French", "german": "German",
    "chinese": "Chinese", "japanese": "Japanese", "italian": "Italian", "russian": "Russian",
    "arabic": "Arabic", "hindi": "Hindi", "portuguese": "Portuguese"
}

QUESTION_STARTERS = (
    "who", "what", "when", "where", "why", "how", "can", "could", "would", "should",
    "is", "are", "do", "does", "did", "have", "has", "will", "may", "might"
)


def detect_repeated_words(text):
    """Detect accidental repeated words (e.g. 'the the', 'is is')."""
    errors = []
    pattern = re.compile(r'\b([A-Za-z]+)\s+\1\b', re.IGNORECASE)
    for match in pattern.finditer(text):
        word = match.group(1)
        errors.append({
            "start": match.start(),
            "end": match.end(),
            "original": match.group(0),
            "replacement": word,
            "type": "Repeated Words",
            "explanation": f"The word '{word}' is repeated unnecessarily."
        })
    return errors


def detect_spelling_errors(text):
    """Detect common spelling mistakes."""
    errors = []
    word_pattern = re.compile(r'\b([A-Za-z]+)\b')
    for match in word_pattern.finditer(text):
        word = match.group(1)
        lower_word = word.lower()
        if lower_word in SPELLING_DICTIONARY:
            correct = SPELLING_DICTIONARY[lower_word]
            if word.istitle():
                correct = correct.capitalize()
            elif word.isupper():
                correct = correct.upper()
            
            errors.append({
                "start": match.start(),
                "end": match.end(),
                "original": word,
                "replacement": correct,
                "type": "Spelling",
                "explanation": f"'{word}' is a spelling mistake. Did you mean '{correct}'?"
            })
    return errors


def detect_capitalization_errors(text):
    """Detect capitalization issues: uncapitalized 'i', sentence starters, days/months, languages."""
    errors = []
    
    # 1. Uncapitalized pronoun 'i' or 'i'm', 'i've', 'i'd', 'i'll'
    i_pattern = re.compile(r'\b(i)(\'m|\'ve|\'d|\'ll)?\b')
    for match in i_pattern.finditer(text):
        if match.group(1) == 'i':
            suffix = match.group(2) if match.group(2) else ""
            original = match.group(0)
            replacement = "I" + suffix
            errors.append({
                "start": match.start(),
                "end": match.end(),
                "original": original,
                "replacement": replacement,
                "type": "Capitalization",
                "explanation": "The personal pronoun 'I' should always be capitalized."
            })
            
    # 2. Sentence starters capitalized
    sentences = re.split(r'(?<=[.!?])\s+', text)
    offset = 0
    for sent in sentences:
        if not sent:
            continue
        sent_start_match = re.search(r'[A-Za-z]', sent)
        if sent_start_match:
            char_idx = sent_start_match.start()
            char = sent[char_idx]
            if char.islower():
                abs_start = text.find(sent, offset) + char_idx if text.find(sent, offset) != -1 else offset + char_idx
                word_match = re.search(r'^[A-Za-z]+', sent[char_idx:])
                if word_match:
                    orig_word = word_match.group(0)
                    abs_end = abs_start + len(orig_word)
                    replacement = orig_word.capitalize()
                    errors.append({
                        "start": abs_start,
                        "end": abs_end,
                        "original": orig_word,
                        "replacement": replacement,
                        "type": "Capitalization",
                        "explanation": "Sentences should begin with a capital letter."
                    })
        offset += len(sent)
        
    # 3. Days, Months, Languages
    for match in re.finditer(r'\b([A-Za-z]+)\b', text):
        word = match.group(1)
        lower = word.lower()
        if word[0].islower():
            if lower in DAYS_AND_MONTHS:
                correct = DAYS_AND_MONTHS[lower]
                errors.append({
                    "start": match.start(),
                    "end": match.end(),
                    "original": word,
                    "replacement": correct,
                    "type": "Capitalization",
                    "explanation": f"Days of the week and months ('{correct}') must be capitalized."
                })
            elif lower in LANGUAGES:
                correct = LANGUAGES[lower]
                errors.append({
                    "start": match.start(),
                    "end": match.end(),
                    "original": word,
                    "replacement": correct,
                    "type": "Capitalization",
                    "explanation": f"Languages and nationalities ('{correct}') must be capitalized."
                })

    return errors


def detect_subject_verb_agreement(text):
    """Detect subject-verb agreement errors using rules & pattern matching."""
    errors = []
    
    specific_patterns = [
        (r'\b(he|she|it)\s+don\'t\b', "doesn't", "Use 'doesn't' with third-person singular subjects (he, she, it)."),
        (r'\b(they|we|you)\s+doesn\'t\b', "don't", "Use 'don't' with plural subjects and 'you'."),
        (r'\b(he|she|it)\s+go\b', "goes", "Use 'goes' for singular third-person subjects."),
        (r'\b(he|she|it)\s+work\b', "works", "Use 'works' for singular third-person subjects."),
        (r'\b(he|she|it)\s+have\b', "has", "Use 'has' for singular third-person subjects."),
        (r'\b(they|we|you)\s+is\b', "are", "Use 'are' with plural subjects."),
        (r'\b(they|we|you)\s+was\b', "were", "Use 'were' with plural subjects in past tense."),
        (r'\b(i)\s+is\b', "am", "Use 'am' with 'I'."),
        (r'\b(i)\s+has\b', "have", "Use 'have' with 'I'."),
        (r'\b(the\s+student|the\s+boy|the\s+girl|the\s+teacher|the\s+cat)\s+(go|work|are|have)\b', "goes/works/is/has", "Singular noun subjects require singular verbs.")
    ]
    
    for pattern, replacement, explanation in specific_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            matched_text = match.group(0)
            parts = matched_text.split()
            sub = parts[0]
            if "/" in replacement:
                verb_map = {"go": "goes", "work": "works", "are": "is", "have": "has"}
                v = parts[-1].lower()
                rep_verb = verb_map.get(v, replacement.split('/')[0])
                rep_text = f"{matched_text[:-len(parts[-1])].strip()} {rep_verb}"
            else:
                rep_text = f"{sub} {replacement}"
                
            errors.append({
                "start": match.start(),
                "end": match.end(),
                "original": matched_text,
                "replacement": rep_text,
                "type": "Subject-Verb Agreement",
                "explanation": explanation
            })
            
    return errors


def detect_punctuation_errors(text):
    """Detect missing or incorrect punctuation."""
    errors = []
    
    # 1. Missing space after comma or period
    space_pattern = re.compile(r'\b([A-Za-z]+)([,.:;])([A-Za-z]+)\b')
    for match in space_pattern.finditer(text):
        word1 = match.group(1)
        punc = match.group(2)
        word2 = match.group(3)
        original = match.group(0)
        replacement = f"{word1}{punc} {word2}"
        errors.append({
            "start": match.start(),
            "end": match.end(),
            "original": original,
            "replacement": replacement,
            "type": "Missing Punctuation",
            "explanation": f"Add a space after punctuation marks ('{punc}')."
        })
        
    # 2. Sentences missing end punctuation or question marks
    sentences = re.split(r'\n+', text)
    for sent in sentences:
        stripped = sent.strip()
        if not stripped:
            continue
        words = re.findall(r'\b[A-Za-z]+\b', stripped)
        if words:
            first_word = words[0].lower()
            idx = text.find(stripped)
            if idx != -1:
                if first_word in QUESTION_STARTERS:
                    if not stripped.endswith('?'):
                        errors.append({
                            "start": idx,
                            "end": idx + len(stripped),
                            "original": stripped,
                            "replacement": stripped.rstrip('.!') + '?',
                            "type": "Missing Punctuation",
                            "explanation": f"Sentences starting with '{words[0]}' are typically questions and should end with a question mark ('?')."
                        })
                elif not stripped.endswith(('.', '?', '!', '"', "'")):
                    errors.append({
                        "start": idx,
                        "end": idx + len(stripped),
                        "original": stripped,
                        "replacement": stripped + '.',
                        "type": "Missing Punctuation",
                        "explanation": "Complete sentences should end with a period, question mark, or exclamation mark."
                    })
                
    return errors


def detect_common_pattern_errors(text):
    """Detect article usage (a/an), homophone confusion, and word choice errors."""
    errors = []
    
    # 1. Article 'a' vs 'an'
    a_vowel_pattern = re.compile(r'\b(a)\s+([aeiou][a-z]+)\b', re.IGNORECASE)
    for match in a_vowel_pattern.finditer(text):
        art = match.group(1)
        following = match.group(2)
        if following.lower() not in {"university", "user", "unit", "unique", "useful", "european", "united", "universe"}:
            original = match.group(0)
            rep_art = "an" if art.islower() else "An"
            replacement = f"{rep_art} {following}"
            errors.append({
                "start": match.start(),
                "end": match.end(),
                "original": original,
                "replacement": replacement,
                "type": "Common Patterns",
                "explanation": f"Use 'an' instead of 'a' before words starting with a vowel sound ('{following}')."
            })
            
    an_consonant_pattern = re.compile(r'\b(an)\s+([bcdfghjklmnpqrstvwxyz][a-z]+)\b', re.IGNORECASE)
    for match in an_consonant_pattern.finditer(text):
        art = match.group(1)
        following = match.group(2)
        if following.lower() not in {"hour", "hours", "honest", "honor", "honour", "heir"}:
            original = match.group(0)
            rep_art = "a" if art.islower() else "A"
            replacement = f"{rep_art} {following}"
            errors.append({
                "start": match.start(),
                "end": match.end(),
                "original": original,
                "replacement": replacement,
                "type": "Common Patterns",
                "explanation": f"Use 'a' instead of 'an' before words starting with a consonant sound ('{following}')."
            })

    # 2. Homophones and common confused words
    confused_words = [
        (r'\b(your)\s+(welcome|right|wrong|going|doing|coming|the best|a good person)\b', "you're", "Use 'you're' (short for 'you are') instead of possessive 'your'."),
        (r'\b(their)\s+(is|are|was|were)\b', "there", "Use 'there' to indicate existence or location, not possessive 'their'."),
        (r'\b(they\'re)\s+(house|car|dog|cat|books|family|friend|school)\b', "their", "Use possessive 'their' for belonging, not contraction 'they're'."),
        (r'\b(its)\s+(raining|cold|hot|sunny|a good|nice|important|funny)\b', "it's", "Use 'it's' (short for 'it is') instead of possessive 'its'."),
        (r'\b(could|should|would)\s+of\b', "have", "Use 'have' instead of 'of' after modal verbs (e.g. 'could have')."),
        (r'\b(better|more|less|faster|slower|bigger|smaller)\s+then\b', "than", "Use 'than' for comparisons instead of 'then'."),
        (r'\b(less)\s+(people|students|books|cars|items|things|days)\b', "fewer", "Use 'fewer' for countable nouns (like people, books), and 'less' for uncountable quantities.")
    ]
    
    for pattern, rep, exp in confused_words:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            orig = match.group(0)
            word_parts = orig.split()
            if rep == "have":
                replacement = f"{word_parts[0]} have"
            elif rep == "than":
                replacement = f"{word_parts[0]} than"
            else:
                replacement = f"{rep} {word_parts[1]}"
                
            errors.append({
                "start": match.start(),
                "end": match.end(),
                "original": orig,
                "replacement": replacement,
                "type": "Common Patterns",
                "explanation": exp
            })

    return errors


def run_all_custom_rules(text):
    """Run all custom NLP rule detectors and merge results cleanly avoiding overlapping offsets."""
    raw_errors = []
    
    raw_errors.extend(detect_subject_verb_agreement(text))
    raw_errors.extend(detect_repeated_words(text))
    raw_errors.extend(detect_spelling_errors(text))
    raw_errors.extend(detect_capitalization_errors(text))
    raw_errors.extend(detect_punctuation_errors(text))
    raw_errors.extend(detect_common_pattern_errors(text))
    
    # Deduplicate and sort errors by character offset start position
    raw_errors.sort(key=lambda x: x["start"])
    
    filtered_errors = []
    last_end = -1
    for err in raw_errors:
        if err["start"] >= last_end:
            filtered_errors.append(err)
            last_end = err["end"]
            
    return filtered_errors
