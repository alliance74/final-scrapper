"""
Combined scraper for multiple Greek event websites
- Visit Greece: https://www.visitgreece.gr/events
- Ministry of Culture: https://allofgreeceone.culture.gov.gr/en/
"""

from visitgreece_improved_scraper import VisitGreeceImprovedScraper
from culture_gov_fixed_scraper import CultureGovFixedScraper
import json
import os
from datetime import datetime

def scrape_all_sources(max_events_per_source=200):
    """Scrape events from all sources"""
    
    all_events = {
        'metadata': {
            'scraped_at': datetime.now().isoformat(),
            'total_events': 0,
            'sources': []
        },
        'events': []
    }
    
    print("="*70)
    print("COMBINED GREEK EVENTS SCRAPER")
    print("="*70)
    
    # Source 1: Visit Greece
    print("\n" + "="*70)
    print("SOURCE 1: Visit Greece")
    print("="*70)
    
    try:
        vg_scraper = VisitGreeceImprovedScraper(headless=False)
        vg_events = vg_scraper.scrape_all_events(max_events=max_events_per_source)
        
        # Add source tag to each event
        for event in vg_events:
            event['source'] = 'Visit Greece'
            event['source_url'] = 'https://www.visitgreece.gr/events'
        
        all_events['events'].extend(vg_events)
        all_events['metadata']['sources'].append({
            'name': 'Visit Greece',
            'url': 'https://www.visitgreece.gr/events',
            'events_count': len(vg_events)
        })
        
        print(f"\n✓ Visit Greece: {len(vg_events)} events scraped")
        
    except Exception as e:
        print(f"\n✗ Visit Greece failed: {e}")
    
    # Source 2: Ministry of Culture
    print("\n" + "="*70)
    print("SOURCE 2: Greek Ministry of Culture")
    print("="*70)
    
    try:
        culture_scraper = CultureGovFixedScraper(headless=False)
        culture_events = culture_scraper.scrape_all_events(max_events=max_events_per_source)
        
        # Add source tag to each event
        for event in culture_events:
            event['source'] = 'Ministry of Culture'
            event['source_url'] = 'https://allofgreeceone.culture.gov.gr/en/'
        
        all_events['events'].extend(culture_events)
        all_events['metadata']['sources'].append({
            'name': 'Ministry of Culture',
            'url': 'https://allofgreeceone.culture.gov.gr/en/',
            'events_count': len(culture_events)
        })
        
        print(f"\n✓ Ministry of Culture: {len(culture_events)} events scraped")
        
    except Exception as e:
        print(f"\n✗ Ministry of Culture failed: {e}")
    
    # Update total count
    all_events['metadata']['total_events'] = len(all_events['events'])
    
    return all_events

def save_combined_events(data, filename='all_greek_events.json'):
    """Save combined events to JSON"""
    os.makedirs('scraped_data', exist_ok=True)
    filepath = os.path.join('scraped_data', filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*70}")
    print(f"✓ All events saved to: {filepath}")
    print(f"{'='*70}")
    return filepath

def print_summary(data):
    """Print summary of scraped data"""
    print("\n" + "="*70)
    print("SCRAPING SUMMARY")
    print("="*70)
    
    print(f"\nTotal events scraped: {data['metadata']['total_events']}")
    print(f"Scraped at: {data['metadata']['scraped_at']}")
    
    print("\nBy source:")
    for source in data['metadata']['sources']:
        print(f"  - {source['name']}: {source['events_count']} events")
    
    # Count by category
    print("\nBy category:")
    categories = {}
    for event in data['events']:
        cat = event.get('category') or event.get('event_type', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  - {cat}: {count}")
    
    # Count by location
    print("\nTop locations:")
    locations = {}
    for event in data['events']:
        loc = event.get('location', 'Unknown')
        if loc and loc != 'Unknown':
            locations[loc] = locations.get(loc, 0) + 1
    
    for loc, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  - {loc}: {count}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("COMBINED GREEK EVENTS SCRAPER")
    print("="*70)
    print("\nThis will scrape events from:")
    print("1. Visit Greece (visitgreece.gr)")
    print("2. Greek Ministry of Culture (allofgreeceone.culture.gov.gr)")
    print("="*70)
    
    max_per_source = input("\nMax events per source? (default: 200): ").strip()
    max_per_source = int(max_per_source) if max_per_source.isdigit() else 200
    
    # Scrape all sources
    combined_data = scrape_all_sources(max_events_per_source=max_per_source)
    
    # Save results
    if combined_data['events']:
        filepath = save_combined_events(combined_data)
        print_summary(combined_data)
        
        print(f"\n{'='*70}")
        print(f"✓ SUCCESS! Scraped {combined_data['metadata']['total_events']} total events")
        print(f"{'='*70}")
    else:
        print("\n✗ No events were scraped from any source")
