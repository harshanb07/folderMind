from generation import generate_answer

context = """
[Source 1]
File: downtime.txt
Content: Work order WO-7312 recorded a 35-minute
machine stoppage due to a tool-change alarm.
The document does not establish a motor failure.
"""

questions = [
    "What caused the machine stoppage on WO-7312?",
    "Did a motor failure cause the machine stoppage on WO-7312?",
]

for question in questions:
    print("\nQUESTION:", question)
    print("ANSWER:", generate_answer(question, context))