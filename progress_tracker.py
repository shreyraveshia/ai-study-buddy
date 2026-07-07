import json
import os

PROGRESS_FILE = "student_progress.json"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"topics": {}}  # empty starting structure

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)

def record_attempt(topic, correct):
    progress = load_progress()
    
    if topic not in progress["topics"]:
        progress["topics"][topic] = {"correct": 0, "incorrect": 0}
    
    if correct:
        progress["topics"][topic]["correct"] += 1
    else:
        progress["topics"][topic]["incorrect"] += 1
    
    save_progress(progress)

def get_weak_topics(threshold=0.5):
    """Returns topics where the student got less than `threshold` fraction correct."""
    progress = load_progress()
    weak = []
    
    for topic, stats in progress["topics"].items():
        total = stats["correct"] + stats["incorrect"]
        if total == 0:
            continue
        accuracy = stats["correct"] / total
        if accuracy < threshold:
            weak.append(topic)
    
    return weak

# --- Test it ---
if __name__ == "__main__":
    record_attempt("DNS", correct=True)
    record_attempt("DNS", correct=False)
    record_attempt("DNS", correct=False)
    record_attempt("HTTP/HTTPS", correct=True)
    record_attempt("HTTP/HTTPS", correct=True)
    
    print("Current progress:", load_progress())
    print("Weak topics:", get_weak_topics())