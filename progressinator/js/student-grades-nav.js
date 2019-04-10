(function () {
  'use strict';

  const cookieId = `progressinator-${currentCourseSlug}-section`;
  const studentList = document.getElementById('student-controls-list');
  const studentSection = document.querySelector('.student-controls-section');
  const studentPrev = document.getElementById('student-controls-prev');
  const studentNext = document.getElementById('student-controls-next');

  let studentIds = [];
  let currentStudentIndex = false;
  let prevStudentIndex = false;
  let nextStudentIndex = false;

  const setStudentSection = function (section) {
    studentSection.querySelector('[aria-pressed="true"]').setAttribute('aria-pressed', false);

    if (!section || section == 'all') {
      studentIds = allStudentsIds;
      studentSection.querySelector('[data-section="all"]').setAttribute('aria-pressed', true);
    } else {
      studentIds = allStudentsIds.filter((x) => { return x.section == section });
      studentSection.querySelector(`[data-section="${section}"]`).setAttribute('aria-pressed', true);
    }

    currentStudentIndex = studentIds.map((x) => { return x.id }).indexOf(currentStudentId);
    prevStudentIndex = (currentStudentIndex - 1 >= 0) ? currentStudentIndex - 1 : studentIds.length - 1;
    nextStudentIndex = (currentStudentIndex + 1 < studentIds.length) ? currentStudentIndex + 1 : 0;
    studentPrev.href = window.location.href.replace(/\/\d+\/$/i, `/${studentIds[prevStudentIndex].id}/`);
    studentNext.href = window.location.href.replace(/\/\d+\/$/i, `/${studentIds[nextStudentIndex].id}/`);
    studentList.innerHTML = '';

    studentIds.forEach((std, ind) => {
      const opt = document.createElement('option');
      opt.value = ind;
      opt.innerHTML = std.name;
      if (std.id == currentStudentId) opt.selected = true;
      studentList.appendChild(opt);
    });

    if (currentStudentIndex < 0) {
      const opt = document.createElement('option');
      opt.value = '';
      opt.innerHTML = '';
      opt.selected = true;
      studentList.prepend(opt);
    }
  };

  studentList.addEventListener('change', (e) => {
    window.location = window.location.href.replace(/\/\d+\/$/i, `/${studentIds[studentList.value].id}/`);
  });

  studentSection.addEventListener('click', (e) => {
    localStorage.setItem(cookieId, e.target.dataset.section);
    setStudentSection(e.target.dataset.section);
  });

  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === 'ArrowLeft') {
      const btn = document.getElementById('student-controls-prev');
      if (btn) {
        btn.focus();
        btn.click();
      }
    }
    if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === 'ArrowRight') {
      const btn = document.getElementById('student-controls-next');
      if (btn) {
        btn.focus();
        btn.click();
      }
    }
    if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === 'ArrowUp') {
      const btn = document.getElementById('student-controls-list');
      if (btn) btn.focus();
    }
  });

  setStudentSection(localStorage.getItem(cookieId) || 'all');
}());
