import pandas as pd
import json
import glob
import os
from datetime import datetime

def safe(value):
    if pd.isna(value):
        return ""
    return str(value).strip()

def calculate_week_number(date_str):
    """Calculate ISO week number from date string"""
    if not date_str or date_str.strip() == "":
        return ""
    
    try:
        # Try parsing different date formats
        for date_format in ["%d/%b/%y", "%d/%m/%y", "%d-%m-%Y", "%Y-%m-%d"]:
            try:
                date_obj = datetime.strptime(date_str.strip(), date_format)
                # Get ISO week number
                week_num = date_obj.isocalendar()[1]
                year = date_obj.year
                return f"W{week_num:02d}-{year}"
            except ValueError:
                continue
        return ""
    except Exception:
        return ""

def load_existing_comments():
    """Load existing comments from cases.json"""
    comments_map = {}
    planned_week_map = {}
    
    try:
        if os.path.exists("cases.json"):
            with open("cases.json", "r", encoding="utf-8") as f:
                existing_cases = json.load(f)
                for case in existing_cases:
                    issue_key = case.get("issue_key", "")
                    if issue_key:
                        # Preserve comments
                        if "comments" in case:
                            comments_map[issue_key] = case["comments"]
                        # Preserve planned_for_week if it exists
                        if "planned_for_week" in case:
                            planned_week_map[issue_key] = case["planned_for_week"]
    except Exception as e:
        print(f"Warning: Could not load existing comments: {e}")
    
    return comments_map, planned_week_map

# Process data.csv only
filepath = "data.csv"
print(f"Processing {filepath}...")

try:
    # Load existing comments and planned weeks before processing
    comments_map, planned_week_map = load_existing_comments()
    print(f"Loaded {len(comments_map)} existing comments and {len(planned_week_map)} planned weeks")
    
    df = pd.read_csv(filepath, low_memory=False)
    cases = []
    
    for _, row in df.iterrows():
        issue_key = safe(row["Issue key"])
        target_start = safe(row["Target start date"])
        
        case = {
            "hierarchy": safe(row["Hierarchy"]),
            "issue_key": issue_key,
            "title": safe(row["Title"]),
            "assignee": safe(row["Assignee"]),
            "target_start": target_start,
            "target_end": safe(row["Target end date"]),
            "components": safe(row["Components"]),
            "status": safe(row["Issue status"]).title(),
            "deliverable_type": safe(row["Deliverable Type"])
        }
        
        # Preserve existing comments for this issue key
        if issue_key in comments_map:
            case["comments"] = comments_map[issue_key]
        else:
            case["comments"] = ""
        
        # Calculate or preserve planned_for_week
        if issue_key in planned_week_map:
            # Preserve existing planned week
            case["planned_for_week"] = planned_week_map[issue_key]
        else:
            # Calculate from target start date
            case["planned_for_week"] = calculate_week_number(target_start)
        
        cases.append(case)

    # Save cases.json
    with open("cases.json", "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=4, ensure_ascii=False)
    print("Generated cases.json with preserved comments and planned weeks")

    # Save data.json (Summary)
    status_counts = df["Issue status"].value_counts().to_dict()
    
    summary = {
        "total_cases": len(cases),
        "status_distribution": {k.title() if isinstance(k, str) else str(k): v for k, v in status_counts.items()}
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print("Generated data.json")

except Exception as e:
    print(f"Error processing {filepath}: {e}")
