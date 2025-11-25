import re
from collections import defaultdict

# Read the test output file
with open("test_full_output.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Extract summary line
summary_match = re.search(r"=+ (.*?) in ([\d.]+s|[\d]+:[\d]+ min) =+", content)
if summary_match:
    summary = summary_match.group(1)
    duration = summary_match.group(2)
    print(f"SUMMARY: {summary}")
    print(f"DURATION: {duration}\n")

# Parse summary counts
summary_parts = summary.split(", ")
results = {
    "passed": 0,
    "failed": 0,
    "errors": 0,
    "skipped": 0,
    "warnings": 0
}

for part in summary_parts:
    if "passed" in part:
        results["passed"] = int(re.search(r"(\d+)", part).group(1))
    elif "failed" in part:
        results["failed"] = int(re.search(r"(\d+)", part).group(1))
    elif "error" in part:
        results["errors"] = int(re.search(r"(\d+)", part).group(1))
    elif "skipped" in part:
        results["skipped"] = int(re.search(r"(\d+)", part).group(1))
    elif "warning" in part:
        results["warnings"] = int(re.search(r"(\d+)", part).group(1))

print("TEST RESULTS:")
for key, value in results.items():
    print(f"  {key.upper()}: {value}")
print()

# Extract FAILED tests
failed_pattern = r"FAILED (tests/.*?)::(.*?) - (.*?)(?=\nFAILED|\nERROR|\nPASSED|\n=+|$)"
failed_tests = re.findall(failed_pattern, content, re.DOTALL)

if failed_tests:
    print(f"\n{'='*80}")
    print(f"FAILED TESTS ({len(failed_tests)} tests)")
    print(f"{'='*80}\n")
    for file, test, error in failed_tests:
        print(f"FILE: {file}")
        print(f"TEST: {test}")
        print(f"ERROR: {error[:200].strip()}...")
        print("-" * 80)

# Extract ERROR tests  
error_pattern = r"ERROR (tests/.*?)::(.*?) - (.*?)(?=\nFAILED|\nERROR|\nPASSED|\n=+|$)"
error_tests = re.findall(error_pattern, content, re.DOTALL)

if error_tests:
    print(f"\n{'='*80}")
    print(f"ERROR TESTS ({len(error_tests)} tests)")
    print(f"{'='*80}\n")
    for file, test, error in error_tests:
        print(f"FILE: {file}")
        print(f"TEST: {test}")
        print(f"ERROR: {error[:200].strip()}...")
        print("-" * 80)

# Extract SKIPPED tests
skipped_pattern = r"SKIPPED.*?\[(.*?)\] (tests/.*?)::(.*?): (.*?)(?=\nSKIPPED|\nFAILED|\nERROR|\nPASSED|\n=+|$)"
skipped_tests = re.findall(skipped_pattern, content, re.DOTALL)

if skipped_tests:
    print(f"\n{'='*80}")
    print(f"SKIPPED TESTS ({len(skipped_tests)} tests)")
    print(f"{'='*80}\n")
    for skip_type, file, test, reason in skipped_tests:
        print(f"FILE: {file}")
        print(f"TEST: {test}")
        print(f"REASON: {reason[:200].strip()}")
        print("-" * 80)

print(f"\n\nANALYSIS COMPLETE")
print(f"Total tests analyzed: {results['passed'] + results['failed'] + results['errors'] + results['skipped']}")
