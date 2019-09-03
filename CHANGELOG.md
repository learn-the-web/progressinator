# Changelog

This file documents all the notable changes for each version of Progressinator.
Progressinator adheres to [Semantic Versioning](http://semver.org/).

---

## [2.7.5] — 2019-09-03

### Fixed

- Fixed a couple bugs when the user didn’t have a course registered this term.

---

## [2.7.4] — 2019-08-27

### Fixed

- Fixed some spacing around elements on smaller screen sizes.


---

## [2.7.3] — 2019-08-26

### Fixed

- Fixed a bug when trying to load the new course page when the user doesn’t have a profile—in a better, more correct way.

---

## [2.7.2] — 2019-08-26

### Fixed

- Fixed a bug when downloading grades for courses without sections.

---

## [2.7.1] — 2019-08-26

### Fixed

- Fixed a bug when trying to load the new course page when the user doesn’t have a profile.

---

## [2.7.0] — 2019-08-26

### Added

- Added Markbot stats on the student views.
- Added email links when looking directly at a student.
- Added a list of all the courses a student has been registered in previously.

### Changed

- Redesigned the homepage for students to be more obvious & helpful.
- Redesigned the homepage for teachers to be more helpful.

---

## [2.6.2] — 2019-05-07

### Fixed

- Fixed a few bugs for self-directed summer courses when students aren’t assigned to sections, but still have course profiles.

---

## [2.6.1] — 2019-04-30

### Fixed

- Fixed a bug when student names had UTF-8 characters in them instead of basic ASCII.

---

## [2.6.0] — 2019-04-30

### Added

- Added the ability to download a single student’s grades.
- Hover states for the course status tables.

---

## [2.5.0] — 2019-04-30

### Added

- Added the ability to download the course grades as a CSV file.

---

## [2.4.0] — 2019-04-18

### Added

- The ability to press `Esc` to exit grade editing mode.
- Added Markbot stats to the assessment grade page.

### Fixed

- Fixed label & input IDs to work on assessment grading page.
- Fixed a saving bug on the assessment grading page related to user IDs.
- Fixed a saving bug related to mismatch lateness excuse options.
- Fixed the lateness excuses so they show on the assessment grading page.
- Reorganize some code for better reusability.

---

## [2.3.0] — 2019-04-10

### Added

- Add the ability to grade all students for a single assignment at a time.
- Add the ability to edit a single grade at a time.
- Add shortcut keys to the grading navigation.
- Add the ability to clear a grade and have it removed from the system.
- Show letter grades for pass/fail assignments that aren’t 1 or 0.

### Fixed

- Fixed a bug related to user staff & permissions levels.

---

## [2.2.0] — 2019-04-08

### Added

- Next/previous student navigation to the student’s grade pages.

### Changed

- Adjusted the links for each assessment for better findability of the repos & live websites.
- Simplified percentage decimal places if they’re above 100%.

### Fixed

- Prevent the textarea from being horizontally scaled.

---

## [2.1.0] — 2019-01-12

### Added

- Added the ability to email a specific section of students.

---

## [2.0.0] — 2019-01-06

### Changed

- The whole system now revolves around terms, multiple terms with students assigned to specific terms.
  Students can only see their work done for the term they’re assigned to—and they can choose their own section & course once at the start of the term.

---

## [1.10.0] — 2019-01-05

### Added

- Added the new Term model to allow for easier future migrations.

### Changed

- Moved all the course information into the database instead of JSON files—preparing for the transition to allow multiple terms.

### Fixed

- Added a little bit of space beside the email all icon.

---

## [1.9.0] — 2018-12-21

### Added

- Added the ability to email individual students & groupings of students (pass, fail).

---

## [1.8.2] — 2018-12-15

### Fixed

- Made the grade to letter comparisons more accurate by quantizing the decimal places.

---

## [1.8.1] — 2018-12-10

### Fixed

- Added the missing “View on GitHub” link for projects.

---

## [1.8.0] — 2018-12-10

### Added

- Added a “Set ungraded as…” feature to help with finalizing end-of-term grades.

---

## [1.7.5] — 2018-12-06

### Fixed

- Fixed a bug I created earlier where grades were being attributed to the wrong assessments.

---

## [1.7.4] — 2018-12-06

### Changed

- Reorder the assessments in the grade list by due date, also fixes the double “Today” separator better.
- Highlight actual failing grades over a threshold on the grade status page.

---

## [1.7.3] — 2018-12-06

### Fixed

- Removed extra padding at the bottom of the grades list.
- Fixed the doubling of the “Today” separator in the grades list.

---

## [1.7.2] — 2018-12-06

### Fixed

- Fixed a bug where ungraded projects were added as part of the actual grade.

---

## [1.7.1] — 2018-11-22

### Fixed

- Fixed a bug when trying to load a user profile and it doesn’t match the currently viewed course.

---

## [1.7.0] — 2018-11-20

### Added

- Cookies will now be set that record the student’s current Algonquin College section to allow for real due dates on the rest of Learn the Web.

---

## [1.6.3] — 2018-11-19

### Added

- Added a line underneath the currently due assessments in the list to help understand the current location in the course.

### Changed

- Clarified the failures that were close to passing with a slightly different colour.
- Clarified the language for the grade view to help students understand.
- Filtering by section now remembers the section when refreshing, using URL hashes for storage.
- Letter grade assessments show as “Ungraded” by default when submitted with Markbot.

---

## [1.6.2] — 2018-11-03

### Changed

- Changed the Markbot version number to enforce a newer version on all the students.

---

## [1.6.1] — 2018-10-25

### Fixed

- Fixed a typo in one of the headings of the assignment list.

---

## [1.6.0] — 2018-10-25

### Added

- The ability to filter the student list by section on the course status page.

---

## [1.5.3] — 2018-10-22

### Changed

- Added “View on GitHub” links for the lessons.

### Fixed

- Removed the extra spacing at the bottom of the tables.

---

## [1.5.2] — 2018-10-22

### Fixed

- Reset the cookie domains to fix the CSRF token from not working.

---

## [1.5.1] — 2018-10-21

### Changed

- Allow HTML tags within comments but force them to be escaped on output.

---

## [1.5.0] — 2018-10-21

### Added

- Add the ability to edit grades for a single student when the staff user level has the correct permissions.

### Fixed

- Fixed bugs on the courses that aren’t currently running to allow the pages to display.

---

## [1.4.3] — 2018-10-21

### Fixed

- Added the missing timezone filter to the student grades template.

---

## [1.4.2] — 2018-10-19

### Changed

- Changed the stats to use multiplication symbols instead of almost equals symbols for more clarity.
- Changed the domain for the CSRF cookie & the session cookie length.

### Fixed

- Fixed a timezone bug related to due dates & submission lateness.

---

## [1.4.1] — 2018-10-18

### Fixed

- Fixed the `overflow` for the grade tables on larger screen sizes.

---

## [1.4.0] — 2018-10-18

### Added

- The number of students to the stats on the course status page.
- A statistic summary of the grading scheme & student number statics to the grade overview.

### Fixed

- Fixed some responsive bugs on the course status page.

---

## [1.3.0] — 2018-10-18

### Added

- Added a whole teacher section where teachers can see all the grades for Algonquin’s registered students.

### Changed

- Changed the grade checkmarks to black for better colour contrast.

---

## [1.2.2] — 2018-10-15

### Changed

- Removed the secret token from the repository—whoops!

---

## [1.2.1] — 2018-10-09

### Changed

- Moved the API code into its own separate view for better organization.
- Enforce the newest version of Markbot.

### Fixed

- Fixed a bug with Markbot submission after the change to decimal-based grades.

---

## [1.2.0] — 2018-10-08

### Added

- Added proper support for showing letter grades on projects.
- Allow user profiles to be imported & exported in Django Admin.

### Changed

- Restricted to a small set of available sections for user profiles.

### Fixed

- Fixed a bug in the grade weights where certain exercises weren’t categorized properly.

---

## [1.1.1] — 2018-10-02

### Fixed

- Fixed a bug when the user didn’t have a profile, yet it still tried to apply due dates.

---

## [1.1.0] — 2018-10-02

### Added

- Added more details and information to the profile page.
- Added due dates below each assessment & matching coloured icons.
- Added more submission details below each graded assessment.

### Changed

- Change the colour of the assessment icons to match Markbot.
- Adjust the spacing of headings for slightly better alignment.

### Fixed

- Fixed a few of the page titles that had duplicated information.

---

## [1.0.2] — 2018-10-01

### Fixed

- Fixed a bug where the duplicate submission detection ignored the different users.

---

## [1.0.1] — 2018-09-30

### Added

- Force the website to always use HTTPS & adjust the allowed hosts setting.

### Changed

- Make the grade signature field optional.

### Fixed

- Fix a typo in `videos` for all the course API JSON files.

---

## [1.0.0] — 2018-09-30

### Added

- Initial release of the web application.
