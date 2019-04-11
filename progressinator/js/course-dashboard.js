(function () {
  'use strict';

  const cookieId = `progressinator-${currentCourseSlug}-section`;
  const courseSectionBtnList = document.querySelector('.class-desc .course-section-list');
  const savedSection = localStorage.getItem(cookieId) || 'all';
  let hash = (window.location.hash) ? window.location.hash : '#';

  if (!courseSectionBtnList) return;

  courseSectionBtnList.addEventListener('click', (e) => {
    if (e.target.dataset.courseSection) {
      document.querySelector('.course-section-btn[aria-pressed="true"]').setAttribute('aria-pressed', false);
      e.target.setAttribute('aria-pressed', true);
      localStorage.setItem(cookieId, e.target.dataset.courseSection);

      [].forEach.call(document.querySelectorAll('[data-filter-course-section]'), (elem) => {
        elem.hidden = false;
        elem.removeAttribute('aria-hidden');
      });

      if (e.target.dataset.courseSection !== 'all') {
        [].forEach.call(document.querySelectorAll(`[data-filter-course-section]:not([data-filter-course-section="${e.target.dataset.courseSection}"])`), (elem) => {
          elem.hidden = true;
          elem.setAttribute('aria-hidden', true);
        });
      }
    }
  });

  if (savedSection && savedSection != 'all') hash = `#${savedSection}`;

  if (hash) {
    const btn = courseSectionBtnList.querySelector(`a[href="${hash}"]`);
    if (btn) btn.click();
  }
}());
