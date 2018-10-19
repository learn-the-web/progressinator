import decimal, math
import pendulum


def grade_as_letter(grade):
    """Change a percent into an Algonquin letter grade"""
    if grade >= .90:
        return "A+"
    elif grade >= .85 and grade < .90:
        return "A"
    elif grade >= .80 and grade < .85:
        return "A-"
    elif grade >= .77 and grade < .80:
        return "B+"
    elif grade >= .73 and grade < .77:
        return "B"
    elif grade >= .70 and grade < .73:
        return "B-"
    elif grade >= .67 and grade < .70:
        return "C+"
    elif grade >= .63 and grade < .67:
        return "C"
    elif grade >= .60 and grade < .63:
        return "C-"
    elif grade >= .57 and grade < .60:
        return "D+"
    elif grade >= .53 and grade < .57:
        return "D"
    elif grade >= .50 and grade < .53:
        return "D-"
    else:
        return "F"


def grade_as_status(grade):
    """Change a percent into an Algonquin mid-term status grade"""
    if grade >= .80:
        return "Excellent"
    elif grade >= .60 and grade < .80:
        return "Satisfactory"
    elif grade >= .50 and grade < .60:
        return "Weak"
    else:
        return "Failing"


def calc_grade(grade, assessment_index, assessments):
    if grade.assessment_uri in assessment_index:
        return grade.grade * decimal.Decimal(assessments[assessment_index[grade.assessment_uri]]['assessment_each_algonquin'])
    return 0


def max_assessments_per_section(assessments):
    max_per_section = {}
    for assessment in assessments:
        for (due_date_section, due_date) in assessment['due_dates_algonquin'].items():
            due_date_datetime = pendulum.parse(due_date, tz='America/Toronto')
            if due_date_datetime <= pendulum.now('America/Toronto'):
                if due_date_section not in max_per_section: max_per_section[due_date_section] = 0
                max_per_section[due_date_section] += decimal.Decimal(assessment['assessment_each_algonquin'])
    return max_per_section
