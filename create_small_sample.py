#!/usr/bin/env python3
"""
Create a smaller sample ABF file containing just a few events for testing.
"""
import pandas as pd
import numpy as np
import pyabf
from scipy.io import savemat
import struct

def create_small_sample():
    # Read the results to see what events we found
    results = pd.read_csv('nanopore_analysis_results_test.csv')
    
    print("Available events:")
    print(results[['event_display_idx', 'analysis_method', 'event_start_time_s', 'event_end_time_s', 'dwell_time_ms']].head(10))
    
    # Load the original ABF file
    print("\nLoading original ABF file...")
    abf = pyabf.ABF("tests/data/sample_data.abf")
    original_data = abf.sweepY
    original_time = abf.sweepX
    sample_rate = abf.dataRate
    
    print(f"Original data: {len(original_data)} points, {original_time[-1]:.2f} seconds")
    
    # Select a few interesting events
    # Let's get: 1 ADEPT event, 2-3 CUSUM events with different characteristics
    selected_events = [
        # Event 1: Short CUSUM event (0.192 ms)
        1,
        # Event 2: Long CUSUM event (25.1 ms) 
        2,
        # Event 3: Another long CUSUM (24.8 ms)
        3,
        # The ADEPT event (0.08 ms) - this is event_display_idx 35, but let's find it
    ]
    
    # Find the ADEPT event
    adept_event = results[results['analysis_method'] == 'ADEPT'].iloc[0]
    print(f"\nADEPT event: {adept_event['event_display_idx']} at {adept_event['event_start_time_s']:.3f}s")
    
    # Get time ranges for selected events with padding
    time_ranges = []
    for event_idx in selected_events:
        event = results.iloc[event_idx - 1]  # Convert to 0-based index
        start_time = event['event_start_time_s']
        end_time = event['event_end_time_s']
        duration = end_time - start_time
        
        # Add 10x the event duration as padding on each side (minimum 1ms)
        padding = max(duration * 10, 0.001)  
        padded_start = max(0, start_time - padding)
        padded_end = min(original_time[-1], end_time + padding)
        
        time_ranges.append((padded_start, padded_end))
        print(f"Event {event_idx}: {start_time:.3f}-{end_time:.3f}s (duration: {duration*1000:.2f}ms) -> padded: {padded_start:.3f}-{padded_end:.3f}s")
    
    # Add ADEPT event
    start_time = adept_event['event_start_time_s']
    end_time = adept_event['event_end_time_s']
    duration = end_time - start_time
    padding = max(duration * 10, 0.001)
    padded_start = max(0, start_time - padding)
    padded_end = min(original_time[-1], end_time + padding)
    time_ranges.append((padded_start, padded_end))
    print(f"ADEPT event: {start_time:.3f}-{end_time:.3f}s (duration: {duration*1000:.2f}ms) -> padded: {padded_start:.3f}-{padded_end:.3f}s")
    
    # Extract data segments
    all_segments_time = []
    all_segments_data = []
    
    for i, (start_t, end_t) in enumerate(time_ranges):
        # Convert time to indices
        start_idx = int(start_t * sample_rate)
        end_idx = int(end_t * sample_rate)
        
        # Extract segment
        segment_time = original_time[start_idx:end_idx]
        segment_data = original_data[start_idx:end_idx]
        
        print(f"Segment {i+1}: {len(segment_data)} points ({(end_t-start_t)*1000:.1f} ms)")
        
        all_segments_time.extend(segment_time)
        all_segments_data.extend(segment_data)
    
    # Convert to numpy arrays
    trimmed_time = np.array(all_segments_time)
    trimmed_data = np.array(all_segments_data)
    
    print(f"\nTrimmed data: {len(trimmed_data)} points ({len(trimmed_data)/sample_rate*1000:.1f} ms total)")
    print(f"Compression ratio: {len(original_data)/len(trimmed_data):.1f}x smaller")
    
    # Save as numpy compressed archive for easy loading (ABF creation is complex)
    np.savez_compressed('tests/data/small_sample.npz', 
                       time=trimmed_time, 
                       data=trimmed_data,
                       sample_rate=sample_rate)
    print(f"Saved trimmed data to tests/data/small_sample.npz")
    
    # Also save metadata about which events are included
    event_info = {
        'original_file': 'tests/data/sample_data.abf',
        'events_included': selected_events + [int(adept_event['event_display_idx'])],
        'time_ranges': time_ranges,
        'sample_rate': sample_rate,
        'total_duration_ms': len(trimmed_data) / sample_rate * 1000,
        'compression_ratio': len(original_data) / len(trimmed_data)
    }
    
    import json
    with open('tests/data/small_sample_info.json', 'w') as f:
        json.dump(event_info, f, indent=2)
    
    print("Saved metadata to tests/data/small_sample_info.json")
    print(f"\nTo load the data: data = np.load('tests/data/small_sample.npz'); time = data['time']; signal = data['data']")

if __name__ == "__main__":
    create_small_sample()