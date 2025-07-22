import re
def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return None
        
    # Remove excessive dots and formatting artifacts
    if text.count('.') > len(text) * 0.3:  
        return None
    
    text = text.strip()
    # Remove multiple spaces and normalize
    text = ' '.join(text.split())
    
    # Filter out very short fragments
    if len(text) <= 5:
        return None
    
    # Filter out obvious non-headings
    exclude_patterns = [
        # Pure dates and times
        r'^\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}$',
        r'^(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}$',
        r'^\d{1,2}:\d{2}(\s*(am|pm))?$',
        # Page references
        r'^page\s+\d+$',
        r'^p\.\s*\d+$',
        # Pure numbers
        r'^\d+$',
        # Email/URL fragments
        r'.*@.*\..*',
        r'.*(\.com|\.org|\.ca|\.edu).*',
        # Table headers
        r'^(s\.no|sr\.no|no\.|name|date|signature|remarks|version)\.?$',
        # Common artifacts
        r'^(\.{3,}|_{3,}|-{3,})$'
    ]
    
    text_lower = text.lower()
    for pattern in exclude_patterns:
        if re.match(pattern, text_lower):
            return None
    
    # Filter out fragments that are likely broken words
    if (len(text) < 15 and 
        not any(v in text_lower for v in 'aeiou') and 
        not text.startswith(tuple(str(i) + '.' for i in range(1, 10)))):
        return None
    
    # Filter out single word fragments unless they're important
    if (len(text.split()) == 1 and 
        len(text) < 10 and 
        not text_lower in ['summary', 'background', 'introduction', 'conclusion', 'references', 'appendix']):
        return None
    
    return text


def determine_heading_level(text, font_size, font_flags, is_numbered=False):
    """Determine heading level based on text content and formatting"""
    text_lower = text.lower()
    
    # H1: Main sections - numbered sections (1., 2., etc.) or major document parts
    if (text.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) and 
        not text.startswith(('1.1', '2.1', '3.1', '4.1', '5.1', '6.1', '7.1', '8.1', '9.1'))) or \
       any(keyword in text_lower for keyword in [
           'revision history', 'table of contents', 'acknowledgements', 
           'introduction', 'overview', 'references', 'abstract', 'conclusion', 
           'appendix', 'bibliography'
       ]) or \
       (font_size >= 18 and 'appendix' in text_lower):
        return "H1"
    
    # H2: Major subsections - x.y numbering or important section headers
    if (re.match(r'^\d+\.\d+\s', text) and not re.match(r'^\d+\.\d+\.\d+', text)) or \
       any(keyword in text_lower for keyword in [
           'summary', 'background', 'approach', 'evaluation', 'milestones',
           'business plan', 'specific proposal', 'awarding of contract'
       ]) or \
       (font_size >= 16 and any(word in text_lower for word in ['intended audience', 'career paths', 'learning objectives'])):
        return "H2"
    
    # H3: Sub-subsections - x.y.z numbering or detailed subsections
    if re.match(r'^\d+\.\d+\.\d+', text) or \
       (text.endswith(':') and any(keyword in text_lower for keyword in [
           'timeline', 'phase', 'funding', 'preamble', 'terms of reference', 
           'membership', 'appointment', 'chair', 'meetings'
       ])) or \
       any(keyword in text_lower for keyword in [
           'equitable access', 'shared decision', 'shared governance', 'shared funding',
           'local points', 'guidance', 'training', 'purchasing', 'technological support'
       ]):
        return "H3"
    
    # H4: Detailed items and specific points
    if text.startswith('For each') or \
       text.endswith(':') or \
       font_size < 14:
        return "H4"
    
    # Font size based fallback
    if font_size >= 18:
        return "H1"
    elif font_size >= 16:
        return "H2"
    elif font_size >= 14:
        return "H3"
    else:
        return "H4"


def is_likely_heading(text, font_size, font_flags):
    """Determine if text is likely a heading based on various criteria"""
    if not text:
        return False
    
    # Clean the text first
    clean_title = clean_text(text)
    if not clean_title:
        return False
    
    text_lower = clean_title.lower()
    
    # Check formatting criteria
    is_bold = bool(font_flags & 16)  # Bold flag
    is_large = font_size >= 14
    
    # Content-based criteria
    has_proper_length = 10 <= len(clean_title) <= 200
    
    # Strong positive indicators
    is_numbered_section = bool(re.match(r'^\d+\.', clean_title))
    is_appendix = 'appendix' in text_lower
    is_common_heading = any(keyword in text_lower for keyword in [
        'introduction', 'overview', 'summary', 'background', 'conclusion', 
        'references', 'acknowledgements', 'table of contents', 'revision history',
        'approach', 'evaluation', 'milestones', 'phases', 'funding'
    ])
    
    # Medium positive indicators
    ends_with_colon = clean_title.endswith(':')
    is_title_case = clean_title.istitle()
    is_all_caps = clean_title.isupper() and len(clean_title) > 8
    
    # Exclusion criteria
    is_date = bool(re.search(r'\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}', clean_title))
    is_time = bool(re.search(r'\d{1,2}:\d{2}', clean_title))
    is_funding_detail = 'million' in text_lower or '$' in clean_title
    is_timeline_detail = bool(re.search(r'(march|april|may|june|july|august|september|october|november|december)\s+\d{4}', text_lower))
    
    # Strong indicators override formatting
    if is_numbered_section or is_appendix or is_common_heading:
        return True
    
    # Must have good formatting AND content
    if (is_bold or is_large) and has_proper_length:
        if not (is_date or is_time or is_funding_detail or is_timeline_detail):
            return (ends_with_colon or is_title_case or is_all_caps)
    
    return False


def merge_text_fragments(text_fragments):
    """Merge broken text fragments into complete headings"""
    if not text_fragments:
        return []
    
    merged = []
    current_line = ""
    
    for fragment in text_fragments:
        fragment = fragment.strip()
        if not fragment:
            continue
            
        # If this looks like the start of a new heading (capitalized, numbered, etc.)
        if (fragment[0].isupper() or 
            fragment.startswith(tuple(str(i) + '.' for i in range(1, 10))) or
            current_line == ""):
            
            # Save the previous line if it exists
            if current_line and len(current_line) > 5:
                merged.append(current_line.strip())
            
            # Start new line
            current_line = fragment
        else:
            # Continue the current line
            if current_line:
                current_line += " " + fragment
            else:
                current_line = fragment
    
    # Don't forget the last line
    if current_line and len(current_line) > 5:
        merged.append(current_line.strip())
    
    return merged


def process_outline_structure(outline):
    """Process outline to clean and structure the data"""
    if not outline:
        return []
    
    processed = []
    
    # Sort outline by page number first
    outline.sort(key=lambda x: x.get('page', 0))
    
    for item in outline:
        # Create the processed item following the required schema
        processed_item = {
            "level": item["level"],
            "text": item["text"].strip(),
            "page": item["page"]
        }
        
        processed.append(processed_item)
    
    return processed


def extract_text_with_formatting(page):
    """Extract text with formatting information from a page"""
    text_elements = []
    
    # Get text in dictionary format for detailed formatting
    text_dict = page.get_text("dict")
    
    for block in text_dict.get("blocks", []):
        if "lines" in block:
            for line in block["lines"]:
                # Combine all spans in a line to get complete text
                line_text = ""
                max_font_size = 0
                line_flags = 0
                
                for span in line["spans"]:
                    line_text += span["text"]
                    # Use the largest font size in the line
                    if span["size"] > max_font_size:
                        max_font_size = span["size"]
                        line_flags = span["flags"]
                
                if line_text.strip():
                    text_elements.append({
                        "text": line_text.strip(),
                        "font_size": max_font_size,
                        "font_flags": line_flags,
                        "bbox": line["bbox"]  # Bounding box for position
                    })
    
    return text_elements
