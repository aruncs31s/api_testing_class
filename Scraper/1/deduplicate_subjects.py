import csv
from collections import defaultdict

data = {}

with open('board_stream_subjects.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        board_id = row['board_id']
        stream_id = row['stream_id']
        subjects = row['subjects']
        
        key = (board_id, row['board_name'], stream_id, row['stream_name'])
        if key not in data:
            data[key] = set()
        
        for subject in subjects.split('|'):
            subject = subject.strip()
            if subject:
                data[key].add(subject)

with open('filtered_board_stream_subject.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['board_id', 'board_name', 'stream_id', 'stream_name', 'subjects'])
    
    for (board_id, board_name, stream_id, stream_name), subjects in sorted(data.items()):
        writer.writerow([board_id, board_name, stream_id, stream_name, ' | '.join(sorted(subjects))])
