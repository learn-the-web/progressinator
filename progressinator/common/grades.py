import decimal, math
import pendulum


TWO_DECIMALS = decimal.Decimal('0.000')


def grade_as_letter(grade):
    """Change a percent into an Algonquin letter grade"""
    if grade >= decimal.Decimal(.90).quantize(TWO_DECIMALS):
        return "A+"
    elif grade >= decimal.Decimal(.85).quantize(TWO_DECIMALS) and grade < decimal.Decimal(.90).quantize(TWO_DECIMALS):
        return "A"
    elif grade >= decimal.Decimal(.80).quantize(TWO_DECIMALS) and grade < decimal.Decimal(.85).quantize(TWO_DECIMALS):
        return "A-"
    elif grade >= decimal.Decimal(.77).quantize(TWO_DECIMALS) and grade < decimal.Decimal(.80).quantize(TWO_DECIMALS):
        return "B+"
    elif grade >= decimal.Decimal(.73).quantize(TWO_DECIMALS) and grade < decimal.Decimal(.77).quantize(TWO_DECIMALS):
        return "B"
    elif grade >= decimal.Decimal(.70).quantize(TWO_DECIMALS) and grade < decimal.Decimal(.73).quantize(TWO_DECIMALS):
        return "B-"
    elif grade >= decimal.Decimal(.67).quantize(TWO_DECIMALS) and grade < decimal.Decimal(.70).quantize(TWO_DECIMALS):
        return "C+"
    elif grade >= decimal.Decimal(.63).quantize(TWO_DECIMALS) and grade < decimal.Decimal(.67).quantize(TWO_DECIMALS):
        return "C"
    elif grade >= decimal.Decimal(.60).quantize(TWO_DECIMALS) and grade < decimal.Decimal(.63).quantize(TWO_DECIMALS):
        return "C-"
    elif grade >= decimal.Decimal(.57).quantize(TWO_DECIMALS) and grade < decimal.Decimal(.60).quantize(TWO_DECIMALS):
        return "D+"
    elif grade >= decimal.Decimal(.53).quantize(TWO_DECIMALS) and grade < decimal.Decimal(.57).quantize(TWO_DECIMALS):
        return "D"
    elif grade >= decimal.Decimal(.50).quantize(TWO_DECIMALS) and grade < decimal.Decimal(.53).quantize(TWO_DECIMALS):
        return "D-"
    else:
        return "F"


def grade_as_status(grade):
    """Change a percent into an Algonquin mid-term status grade"""
    if grade >= decimal.Decimal(.80).quantize(TWO_DECIMALS):
        return "Excellent"
    elif grade >= decimal.Decimal(.60).quantize(TWO_DECIMALS) and grade < decimal.Decimal(.80).quantize(TWO_DECIMALS):
        return "Satisfactory"
    elif grade >= decimal.Decimal(.50).quantize(TWO_DECIMALS) and grade < decimal.Decimal(.60).quantize(TWO_DECIMALS):
        return "Weak"
    else:
        return "Failing"

def grade_as_status_fine_grained(grade):
    """Change a percent into an Algonquin mid-term status grade"""
    if grade >= decimal.Decimal(.80).quantize(TWO_DECIMALS):
        return "Excellent"
    elif grade >= decimal.Decimal(.60).quantize(TWO_DECIMALS) and grade < decimal.Decimal(.80).quantize(TWO_DECIMALS):
        return "Satisfactory"
    elif grade >= decimal.Decimal(.50).quantize(TWO_DECIMALS) and grade < decimal.Decimal(.60).quantize(TWO_DECIMALS):
        return "Weak"
    elif grade >= decimal.Decimal(.40).quantize(TWO_DECIMALS) and grade < decimal.Decimal(.50).quantize(TWO_DECIMALS):
        return "Failing, close"
    else:
        return "Failing"


def calc_grade(grade, assessment_index, assessments):
    if grade.assessment_uri in assessment_index:
        if assessments[assessment_index[grade.assessment_uri]]['grading_type'] == 'letter_grade' and 'Markbot' in grade.submitted_by:
            return 0
        return grade.grade * decimal.Decimal(assessments[assessment_index[grade.assessment_uri]]['assessment_each_algonquin'])
    return 0


def max_assessments_per_section(assessments):
    max_per_section = {}
    for assessment in assessments:
        if len(assessment['due_dates_algonquin']) > 0:
            for (due_date_section, due_date) in assessment['due_dates_algonquin'].items():
                due_date_datetime = pendulum.parse(due_date, tz='America/Toronto')
                if due_date_datetime <= pendulum.now('America/Toronto'):
                    if due_date_section not in max_per_section: max_per_section[due_date_section] = 0
                    max_per_section[due_date_section] += decimal.Decimal(assessment['assessment_each_algonquin'])
    return max_per_section
