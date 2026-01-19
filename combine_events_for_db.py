"""
Combine all scraped events into a single file formatted for database seeding
"""

import json
import os
from datetime import datetime, timedelta
import re

def load_json_file(filepath):
    """Load a JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def extract_region_from_location(location):
    """Extract region from location string"""
    if not location:
        return 'Αττική'  # Default
    
    # Map of keywords to regions
    region_map = {
        'athens': 'Αττική',
        'αθήνα': 'Αττική',
        'attica': 'Αττική',
        'thessaloniki': 'Κεντρική Μακεδονία',
        'θεσσαλονίκη': 'Κεντρική Μακεδονία',
        'macedonia': 'Κεντρική Μακεδονία',
        'patras': 'Δυτική Ελλάδα',
        'πάτρα': 'Δυτική Ελλάδα',
        'heraklion': 'Κρήτη',
        'ηράκλειο': 'Κρήτη',
        'crete': 'Κρήτη',
        'κρήτη': 'Κρήτη',
        'rhodes': 'Νότιο Αιγαίο',
        'ρόδος': 'Νότιο Αιγαίο',
        'santorini': 'Νότιο Αιγαίο',
        'σαντορίνη': 'Νότιο Αιγαίο',
        'mykonos': 'Νότιο Αιγαίο',
        'μύκονος': 'Νότιο Αιγαίο',
        'corfu': 'Ιόνια Νησιά',
        'κέρκυρα': 'Ιόνια Νησιά',
        'ioannina': 'Ήπειρος',
        'ιωάννινα': 'Ήπειρος',
        'larissa': 'Θεσσαλία',
        'λάρισα': 'Θεσσαλία',
        'volos': 'Θεσσαλία',
        'βόλος': 'Θεσσαλία'
    }
    
    location_lower = location.lower()
    for keyword, region in region_map.items():
        if keyword in location_lower:
            return region
    
    return 'Αττική'  # Default

def extract_category(event):
    """Extract category from event data"""
    # Check category field
    if event.get('category'):
        cat = event['category'].lower()
        if 'music' in cat or 'μουσική' in cat or 'concert' in cat:
            return 'Music'
        elif 'theater' in cat or 'θέατρο' in cat:
            return 'Theater'
        elif 'sport' in cat or 'αθλητισμός' in cat:
            return 'Sports'
        elif 'exhibition' in cat or 'έκθεση' in cat:
            return 'Exhibition'
        elif 'festival' in cat or 'φεστιβάλ' in cat:
            return 'Festival'
        elif 'dance' in cat or 'χορός' in cat:
            return 'Dance'
    
    # Check URL
    url = event.get('url', '').lower()
    if 'music' in url or 'concert' in url:
        return 'Music'
    elif 'theater' in url or 'theatre' in url:
        return 'Theater'
    elif 'sport' in url:
        return 'Sports'
    elif 'exhibition' in url:
        return 'Exhibition'
    
    return 'Cultural'  # Default

def extract_price(event):
    """Extract price from event data"""
    price_str = event.get('price', '')
    
    if not price_str:
        return 0
    
    # Try to extract number from price string
    try:
        # Remove currency symbols and text
        price_str = str(price_str).lower()
        
        # Check for free
        if 'free' in price_str or 'δωρεάν' in price_str or 'ελεύθερη' in price_str:
            return 0
        
        # Extract numbers
        numbers = re.findall(r'\d+(?:\.\d+)?', price_str)
        if numbers:
            return float(numbers[0])
    except:
        pass
    
    return 0

def parse_date(date_str):
    """Parse date string to JavaScript Date format"""
    if not date_str:
        # Return a future date if no date found
        future_date = datetime.now() + timedelta(days=30)
        return f"new Date('{future_date.strftime('%Y-%m-%d')}')"
    
    try:
        # Try to extract year
        year_match = re.search(r'20\d{2}', str(date_str))
        if year_match:
            year = year_match.group()
            
            # Try to extract month
            month_map = {
                'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12',
                'ιαν': '01', 'φεβ': '02', 'μαρ': '03', 'απρ': '04',
                'μαΐ': '05', 'ιουν': '06', 'ιουλ': '07', 'αυγ': '08',
                'σεπ': '09', 'οκτ': '10', 'νοε': '11', 'δεκ': '12'
            }
            
            month = '01'
            for month_name, month_num in month_map.items():
                if month_name in str(date_str).lower():
                    month = month_num
                    break
            
            # Try to extract day
            day_match = re.search(r'\b(\d{1,2})\b', str(date_str))
            day = day_match.group(1).zfill(2) if day_match else '01'
            
            return f"new Date('{year}-{month}-{day}')"
    except:
        pass
    
    # Default to 30 days from now
    future_date = datetime.now() + timedelta(days=30)
    return f"new Date('{future_date.strftime('%Y-%m-%d')}')"

def clean_text(text):
    """Clean text for JavaScript string"""
    if not text:
        return ''
    
    text = str(text)
    # Remove newlines and extra spaces
    text = ' '.join(text.split())
    # Escape single quotes
    text = text.replace("'", "\\'")
    # Limit length
    if len(text) > 500:
        text = text[:497] + '...'
    
    return text

def convert_event_to_db_format(event, source):
    """Convert scraped event to database format"""
    
    title = clean_text(event.get('title', 'Untitled Event'))
    
    # Get description
    description = ''
    if event.get('description'):
        description = clean_text(event['description'])
    elif event.get('content') and isinstance(event['content'], list):
        # Take first few content items
        description = clean_text(' '.join(event['content'][:3]))
    elif event.get('full_text'):
        description = clean_text(event['full_text'][:500])
    
    if not description:
        description = title
    
    # Get location
    location = event.get('location', '')
    if isinstance(location, str):
        location = clean_text(location)
    
    # Get image
    image = None
    if event.get('images') and len(event['images']) > 0:
        if isinstance(event['images'][0], str):
            image = event['images'][0]
        elif isinstance(event['images'][0], dict):
            image = event['images'][0].get('src')
    
    db_event = {
        'title': title,
        'description': description,
        'date': parse_date(event.get('date')),
        'region': extract_region_from_location(location),
        'category': extract_category(event),
        'price': extract_price(event),
        'maxCapacity': 100,  # Default capacity
        'location': location[:200] if location else '',
        'url': event.get('url', ''),
        'image': image,
        'source': source
    }
    
    return db_event

def main():
    print("Combining all scraped events for database seeding...")
    print("=" * 60)
    
    # Load all JSON files
    files = {
        'Visit Greece': 'scraped_data/visitgreece_all_events.json',
        'Culture Gov': 'scraped_data/culture_gov_final_events.json',
        'Pigolampides': 'scraped_data/pigolampides_events.json',
        'More.com': 'scraped_data/more_events_optimized.json'
    }
    
    all_events = []
    
    for source, filepath in files.items():
        if os.path.exists(filepath):
            events = load_json_file(filepath)
            print(f"✓ Loaded {len(events)} events from {source}")
            
            for event in events:
                db_event = convert_event_to_db_format(event, source)
                all_events.append(db_event)
        else:
            print(f"⚠ File not found: {filepath}")
    
    print(f"\n{'='*60}")
    print(f"Total events: {len(all_events)}")
    print(f"{'='*60}")
    
    # Generate JavaScript/TypeScript seed file
    output_file = 'scraped_data/events_seed.js'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("// Auto-generated events seed file\n")
        f.write("// Generated on: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
        f.write("const events = [\n")
        
        for i, event in enumerate(all_events):
            f.write("  {\n")
            f.write(f"    title: '{event['title']}',\n")
            f.write(f"    description: '{event['description']}',\n")
            f.write(f"    date: {event['date']},\n")
            f.write(f"    region: '{event['region']}',\n")
            f.write(f"    category: '{event['category']}',\n")
            f.write(f"    price: {event['price']},\n")
            f.write(f"    maxCapacity: {event['maxCapacity']},\n")
            if event['location']:
                f.write(f"    location: '{event['location']}',\n")
            if event['url']:
                f.write(f"    url: '{event['url']}',\n")
            if event['image']:
                f.write(f"    image: '{event['image']}',\n")
            f.write(f"    source: '{event['source']}'\n")
            
            if i < len(all_events) - 1:
                f.write("  },\n")
            else:
                f.write("  }\n")
        
        f.write("];\n\n")
        f.write("// Prisma seed code\n")
        f.write("// for (const event of events) {\n")
        f.write("//   await prisma.event.create({ data: event });\n")
        f.write("// }\n\n")
        f.write("module.exports = events;\n")
    
    print(f"\n✓ Seed file created: {output_file}")
    
    # Also create a JSON version
    json_output = 'scraped_data/all_events_combined.json'
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(all_events, f, indent=2, ensure_ascii=False)
    
    print(f"✓ JSON file created: {json_output}")
    
    # Print statistics
    print(f"\n{'='*60}")
    print("Statistics:")
    print(f"{'='*60}")
    
    # By source
    by_source = {}
    for event in all_events:
        source = event['source']
        by_source[source] = by_source.get(source, 0) + 1
    
    print("\nBy source:")
    for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True):
        print(f"  {source}: {count}")
    
    # By category
    by_category = {}
    for event in all_events:
        cat = event['category']
        by_category[cat] = by_category.get(cat, 0) + 1
    
    print("\nBy category:")
    for cat, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")
    
    # By region
    by_region = {}
    for event in all_events:
        region = event['region']
        by_region[region] = by_region.get(region, 0) + 1
    
    print("\nBy region:")
    for region, count in sorted(by_region.items(), key=lambda x: x[1], reverse=True):
        print(f"  {region}: {count}")
    
    # With images
    with_images = sum(1 for e in all_events if e.get('image'))
    print(f"\nEvents with images: {with_images} ({with_images*100//len(all_events)}%)")

if __name__ == "__main__":
    main()
