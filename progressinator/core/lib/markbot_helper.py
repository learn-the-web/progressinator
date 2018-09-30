import json
import hashlib
from django.conf import settings
import semantic_version as semver


class MarkbotHelper:

    @classmethod
    def confirm_version(cls, ver):
        try:
            markbot_version = semver.Version(ver.replace('Markbot/', '').replace('Markbot Online/', ''))
        except:
            return False

        if 'Markbot Online' in ver:
            expected_version = semver.Version(settings.MARKBOT['ONLINE_VERSION'])
        else:
            expected_version = semver.Version(settings.MARKBOT['DESKTOP_VERSION'])

        return markbot_version >= expected_version

    @classmethod
    def generate_signature(cls, ghUsername, data):
        if 'submitted_by' not in data: return False
        if 'assessment_uri' not in data: return False
        if 'grade' not in data: return False
        if 'cheated' not in data: return False

        return hashlib.sha512(json.dumps([
            ghUsername,
            data['submitted_by'],
            data['assessment_uri'],
            data['grade'],
            data['cheated'],
            settings.MARKBOT['PASSCODE_HASH'],
            ], separators=(',', ':')).encode('ascii')).hexdigest()

    @classmethod
    def confirm_signature(cls, ghUsername, data):
        sig = cls.generate_signature(ghUsername, data)
        return sig == data['signature']
