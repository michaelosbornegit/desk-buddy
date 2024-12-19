import os
import glob

from app.db import db

def update_firmware():
    folder_path = os.path.join(os.path.dirname(__file__), '../../../micropython')
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if 'apps/' not in file_path:
                if file_name.endswith('.py') or file_name.endswith('.pf') and file_name != 'main.py' and file_name != 'main_.py':
                    relative_path = f'./{os.path.relpath(file_path, folder_path)}'
                    file_name = file_name.split('.')[0]
                    
                    with open(file_path, 'rb') as file:
                        file_contents = file.read()

                    existing_entry = db.software_versions.find_one({'relative_path': relative_path, 'file_name': file_name})

                    if existing_entry:
                        if existing_entry['contents'] != file_contents:
                            db.software_versions.update_one(
                                {'_id': existing_entry['_id']},
                                {'$set': {'contents': file_contents}, '$inc': {'version': 1}}
                            )
                    else:
                        db.software_versions.insert_one({
                            'relative_path': relative_path,
                            'file_name': file_name,
                            'contents': file_contents,
                            'type': 'firmware',
                            'version': 1
                        })