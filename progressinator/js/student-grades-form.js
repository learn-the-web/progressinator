(function () {
  'use strict';

  const gradesForm = document.getElementById('grades-form');
  const btnEdit = document.getElementById('grades-edit');
  const btnSave = document.getElementById('grades-save');
  const btnCancel = document.getElementById('grades-cancel');
  const defaultControls = document.getElementById('grade-actions-default-controls');
  const btnDefaultGo = document.getElementById('grade-actions-default-go');
  const inputDefault = document.getElementById('grade-actions-default');

  const hideGradeForm = function (gradeForm) {
    gradeForm.hidden = true;
    btnSave.hidden = btnSave.disabled = true;
    btnEdit.hidden = btnEdit.disabled = false;
  };

  const showGradeForm = function (gradeForm, hideEditAllBtn=true) {
    gradeForm.hidden = false;
    btnSave.hidden = btnSave.disabled = false;
    if (hideEditAllBtn) btnEdit.hidden = btnEdit.disabled = true;
  };

  const hideDefaultControls = function () {
    btnCancel.hidden = btnCancel.disabled = true;
    defaultControls.hidden = true;
  };

  const showDefaultControls = function () {
    btnCancel.hidden = btnCancel.disabled = false;
    defaultControls.hidden = false;
  };

  const hideAllSingleEditBtns = function () {
    [].forEach.call(document.querySelectorAll('[data-control="edit-single-grade"], [data-control="cancel-single-grade"]'), (elem) => {
      elem.hidden = elem.disabled = true;
    });
  };

  const showAllSingleEditBtns = function () {
    [].forEach.call(document.querySelectorAll('[data-control="edit-single-grade"]'), (elem) => {
      elem.hidden = elem.disabled = false;
    });
    [].forEach.call(document.querySelectorAll('[data-control="cancel-single-grade"]'), (elem) => {
      elem.hidden = elem.disabled = true;
    });
  };

  if (!gradesForm) return;

  btnEdit.addEventListener('click', (e) => {
    e.preventDefault();
    showDefaultControls();
    hideAllSingleEditBtns();
    [].forEach.call(document.querySelectorAll('.grade-form-wrap'), (gradeForm) => {
      showGradeForm(gradeForm);
    });
  });

  btnCancel.addEventListener('click', (e) => {
    e.preventDefault();
    hideDefaultControls();
    showAllSingleEditBtns();
    [].forEach.call(document.querySelectorAll('.grade-form-wrap'), (gradeForm) => {
      hideGradeForm(gradeForm);
    });
  });

  btnDefaultGo.addEventListener('click', (e) => {
    e.preventDefault();
    [].forEach.call(document.querySelectorAll('.grade-form input[name="grade"]'), (gradeInput) => {
      if (gradeInput.value === '') gradeInput.value = inputDefault.value;
    });
  });

  gradesForm.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.currentTarget.submit();
    }
  });

  gradesForm.addEventListener('click', (e) => {
    if (e.target && e.target.dataset.control == 'edit-single-grade') {
      const gradeForm = e.target.parentNode.parentNode.parentNode.querySelector('.grade-form-wrap');
      const cancelBtn = e.target.nextElementSibling;
      if (gradeForm) {
        showDefaultControls();
        showGradeForm(gradeForm, false);
      }
      if (cancelBtn) {
        cancelBtn.hidden = cancelBtn.disabled = false;
        e.target.hidden = e.target.disabled = true;
      }
    }

    if (e.target && e.target.dataset.control == 'cancel-single-grade') {
      const gradeForm = e.target.parentNode.parentNode.parentNode.querySelector('.grade-form-wrap');
      const editBtn = e.target.previousElementSibling;
      if (gradeForm) {
        hideDefaultControls();
        hideGradeForm(gradeForm);
      }
      if (editBtn) {
        editBtn.hidden = editBtn.disabled = false;
        e.target.hidden = e.target.disabled = true;
      }
    }
  });
}());
