import re

content = """
File: /app/Secrets/ChecklyHQ_secrets.txt
File: Secrets\\MailBoxLayer_secrets.txt
"""

file_result_pattern = r"File:\s*(?:.*?/|Secrets\\)([\w\d]+)_secrets\.txt"
file_result = re.findall(file_result_pattern, content)

print("File results trovati:", file_result)
