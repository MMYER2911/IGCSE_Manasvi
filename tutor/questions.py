import json
from decimal import Decimal, InvalidOperation

# Original development examples, not official examination-board questions.
SEED = [
 ('Mathematics','Algebra','Foundation','numerical','Solve 3x + 5 = 20. Give x.', '[]','5','Subtract 5, then divide by 3.',1,0,'Original practice example'),
 ('Mathematics','Algebra','Foundation','multiple_choice','Which expression equals 2(x + 3)?',json.dumps(['2x + 3','2x + 6','x + 6']),'2x + 6','Multiply both terms inside the brackets by 2.',1,0,'Original practice example'),
 ('Mathematics','Geometry','Foundation','numerical','A triangle has angles 40° and 65°. What is the third angle in degrees?','[]','75','Angles in a triangle sum to 180°: 180 − 40 − 65 = 75.',1,0,'Original practice example'),
 ('Mathematics','Number','Foundation','numerical','Find 15% of 80.','[]','12','0.15 × 80 = 12.',1,0,'Original practice example'),
 ('Mathematics','Algebra','Higher','numerical','The positive solution of x² = 49 is:','[]','7','Both 7 and −7 square to 49; the positive solution is 7.',1,0,'Original practice example'),
 ('Mathematics','Geometry','Higher','numerical','A circle has radius 3 cm. Find its area in cm² to 2 decimal places (use π = 3.14159).','[]','28.27','Area = πr² = 3.14159 × 9, rounded to 28.27.',1,0.005,'Original practice example'),
 ('Mathematics','Number','Higher','numerical','A price of 120 increases by 20%. What is the new price?','[]','144','120 × 1.20 = 144.',1,0,'Original practice example'),
]


def mark(question, answer):
    if question['kind'] == 'essay':
        return None  # Await human review; never include in automatic scores.
    if question['kind'] == 'numerical':
        try:
            actual = Decimal(answer.strip())
            return question['marks'] if actual.is_finite() and abs(actual - Decimal(question['answer'])) <= Decimal(str(question['tolerance'])) else 0
        except (InvalidOperation, ValueError):
            return 0
    return question['marks'] if answer.strip().casefold() == question['answer'].casefold() else 0
