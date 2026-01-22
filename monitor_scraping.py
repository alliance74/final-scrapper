"""
Monitor scraping progress on Railway
"""
import requests
import time
import sys

def monitor_scraping(base_url, check_interval=30, max_checks=20):
    """Monitor scraping progress by checking stats"""
    
    base_url = base_url.rstrip('/')
    
    print("=" * 70)
    print("📊 MONITORING SCRAPING PROGRESS")
    print("=" * 70)
    print(f"URL: {base_url}")
    print(f"Checking every {check_interval} seconds")
    print(f"Max checks: {max_checks} ({max_checks * check_interval / 60:.1f} minutes)")
    print("=" * 70)
    
    previous_count = 0
    
    for i in range(max_checks):
        try:
            print(f"\n[Check {i+1}/{max_checks}] {time.strftime('%H:%M:%S')}")
            
            # Get stats
            r = requests.get(f"{base_url}/stats", timeout=10)
            if r.status_code == 200:
                data = r.json()
                total_events = data.get('total_events', 0)
                events_by_source = data.get('events_by_source', {})
                
                print(f"  📊 Total Events: {total_events}")
                
                if events_by_source:
                    print(f"  📍 Events by source:")
                    for source, count in events_by_source.items():
                        print(f"     - {source}: {count}")
                
                # Check if new events were added
                if total_events > previous_count:
                    new_events = total_events - previous_count
                    print(f"  ✅ +{new_events} new events!")
                    previous_count = total_events
                elif total_events > 0:
                    print(f"  ✅ Scraping complete! Total: {total_events}")
                    break
                else:
                    print(f"  ⏳ Waiting for scraper to collect data...")
            
            # Wait before next check
            if i < max_checks - 1:
                print(f"  ⏰ Next check in {check_interval} seconds...")
                time.sleep(check_interval)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Monitoring stopped by user")
            break
        except Exception as e:
            print(f"  ❌ Error: {e}")
            time.sleep(check_interval)
    
    # Final stats
    print("\n" + "=" * 70)
    print("📊 FINAL RESULTS")
    print("=" * 70)
    
    try:
        r = requests.get(f"{base_url}/stats", timeout=10)
        if r.status_code == 200:
            data = r.json()
            total_events = data.get('total_events', 0)
            events_by_source = data.get('events_by_source', {})
            
            print(f"✅ Total Events: {total_events}")
            if events_by_source:
                print(f"\n📍 Events by source:")
                for source, count in events_by_source.items():
                    print(f"   - {source}: {count}")
            
            if total_events > 0:
                print(f"\n🎉 SUCCESS! {total_events} events collected!")
                print(f"\n🔗 View events at:")
                print(f"   {base_url}/events")
                print(f"   {base_url}/combined-events")
            else:
                print(f"\n⚠️  No events yet. Scraping may still be in progress.")
                print(f"   Check Railway logs: railway logs")
    except Exception as e:
        print(f"❌ Error getting final stats: {e}")
    
    print("=" * 70)

if __name__ == "__main__":
    url = "https://final-scrapper-production.up.railway.app"
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    print("\n🔍 Starting scraping monitor...")
    print("Press Ctrl+C to stop monitoring\n")
    
    monitor_scraping(url, check_interval=30, max_checks=20)
