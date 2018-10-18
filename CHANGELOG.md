# Changelog

This file documents all the notable changes for each version of Progressinator.
Progressinator adheres to [Semantic Versioning](http://semver.org/).

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
