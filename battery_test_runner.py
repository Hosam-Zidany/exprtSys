from battery_fuzzy_system import BatteryFuzzySystem


def print_header(text):
    print(f"\n{'='*80}")
    print(f"{text}")
    print(f"{'='*80}")


def print_test(number, name, battery, temp, health, load, result):
    print(f"\n[Test {number}] {name}")
    print(f"  Input:  Battery={battery:>3}%  Temp={temp:>3}°C  Health={health:>3}  Load={load:>3}")
    print(f"  Output: Charging={result['charging_speed']:>6} (raw:{result['charging_speed_raw']:>5.1f})  " +
          f"Cooling={result['cooling_level']:>6} (raw:{result['cooling_level_raw']:>5.1f})  " +
          f"Warning={result['warning_status']:>8} (raw:{result['warning_status_raw']:>5.1f})  " +
          f"Discharge={result['discharge_limit']:>10} (raw:{result['discharge_limit_raw']:>5.1f})")


def run_tests():
    
    print_header("BATTERY FUZZY SYSTEM - TEST SUITE")
    print("\nInitializing system...")
    system = BatteryFuzzySystem()
    print("✓ System initialized successfully!\n")
    
    # Test cases
    tests = [
        # Basic Functionality Tests
        (1, "Full Battery - Optimal Conditions", 100, 30, 100, 30),
        (2, "Low Battery - Cool Temperature", 15, 22, 75, 20),
        (3, "Medium Battery - Normal Conditions", 50, 40, 70, 50),
        
        # Temperature Stress Tests
        (4, "Low Battery - Hot Temperature", 20, 65, 40, 60),
        (5, "Extreme Heat - Emergency", 10, 90, 20, 80),
        (6, "Cold Start - Safe Charging", 20, 10, 85, 10),
        
        # Health Impact Tests
        (7, "Poor Health - Low Battery", 30, 50, 20, 70),
        (8, "Degraded Battery - Heat Stress", 40, 75, 30, 75),
        (9, "Excellent Health - New Battery", 15, 25, 95, 15),
        
        # Boundary Conditions
        (10, "Battery at 0% - Critical Low", 0, 35, 50, 50),
        (11, "Temperature at 99°C - Extreme Heat", 50, 99, 60, 85),
        (12, "Battery at 50% - Medium Center", 50, 50, 50, 50),
        
        # Extreme Combinations
        (13, "Worst Case - All Critical", 5, 95, 15, 90),
        (14, "Best Case - All Optimal", 100, 25, 100, 20),
        (15, "Conflicting Priorities - Heat vs Full", 90, 80, 40, 70),
        
        # Real-World Scenarios
        (16, "Gaming Session - Heat & Power Draw", 45, 70, 65, 85),
        (17, "Outdoor Summer - Extreme Heat", 25, 85, 50, 70),
        (18, "Overnight Charging - Final Top-up", 95, 40, 85, 10),
        
        # New Discharge Limit Tests
        (19, "Slow Charge - Low Load", 50, 50, 50, 20),
        (20, "Fast Charge - High Load", 50, 50, 50, 80),
        (21, "Moderate Charge - Medium Load", 50, 50, 50, 50),
    ]
    
    results = []
    failed = 0
    
    for test_num, name, battery, temp, health, load in tests:
        try:
            result = system.get_recommendations(battery, temp, health, load)
            print_test(test_num, name, battery, temp, health, load, result)
            results.append((test_num, name, "PASS", result))
        except Exception as e:
            print(f"\n[Test {test_num}] {name}")
            print(f"  Input:  Battery={battery:>3}%  Temp={temp:>3}°C  Health={health:>3}  Load={load:>3}")
            print(f"  ✗ FAILED: {str(e)}")
            results.append((test_num, name, "FAIL", str(e)))
            failed += 1
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = len(results) - failed
    print(f"\nTotal Tests:  {len(results)}")
    print(f"Passed:       {passed}")
    print(f"Failed:       {failed}")
    print(f"Pass Rate:    {(passed/len(results)*100):.1f}%")
    
    if failed == 0:
        print("\n✓ ALL TESTS PASSED!")
    else:
        print(f"\n✗ {failed} test(s) failed")
        print("\nFailed Tests:")
        for num, name, status, error in results:
            if status == "FAIL":
                print(f"  [{num}] {name}: {error}")
    
    # Detailed Results Table
    print("\n" + "="*80)
    print("DETAILED RESULTS TABLE")
    print("="*80)
    print(f"\n{'#':<3} {'Test Name':<40} {'Status':<6}")
    print("-" * 80)
    for num, name, status, _ in results:
        status_mark = "✓ PASS" if status == "PASS" else "✗ FAIL"
        print(f"{num:<3} {name:<40} {status_mark:<6}")
    
    print("\n" + "="*80)
    print("Test run completed")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_tests()
