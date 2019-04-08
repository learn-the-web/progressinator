(function () {
  'use strict';

  const btnEdit = document.getElementById('grades-edit');
  const btnSave = document.getElementById('grades-save');
  const defaultControls = document.getElementById('grade-actions-default-controls');
  const btnDefaultGo = document.getElementById('grade-actions-default-go');
  const inputDefault = document.getElementById('grade-actions-default');

  btnEdit.addEventListener('click', (e) => {
    e.preventDefault();
    defaultControls.hidden = false;
    [].forEach.call(document.querySelectorAll('.grade-form-wrap'), (gradeForm) => {
      gradeForm.hidden = false;
      btnSave.hidden = btnSave.disabled = false;
      btnEdit.hidden = btnEdit.disabled = true;
    });
  });

  btnDefaultGo.addEventListener('click', (e) => {
    e.preventDefault();
    [].forEach.call(document.querySelectorAll('.grade-form input[name="grade"]'), (gradeInput) => {
      if (gradeInput.value === '') gradeInput.value = inputDefault.value;
    });
  });

  document.getElementById('grades-form').addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.currentTarget.submit();
    }
  });
}());
