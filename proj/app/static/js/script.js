// app/static/js/script.js

document.addEventListener('DOMContentLoaded', function () {
    // Находим модальное окно по его ID
    var deleteModal = document.getElementById('deleteAnimalModal');

    // Проверяем, существует ли модальное окно на странице
    if (deleteModal) {
        // Добавляем слушатель события, который сработает перед показом модального окна
        deleteModal.addEventListener('show.bs.modal', function (event) {
            // Получаем кнопку, которая вызвала модальное окно
            var button = event.relatedTarget;
            
            // Извлекаем данные из data-атрибутов кнопки
            var animalName = button.getAttribute('data-animal-name');
            var animalId = button.getAttribute('data-animal-id');
            
            // Формируем URL для отправки запроса на удаление
            var actionUrl = '/animal/' + animalId + '/delete';

            // Находим элементы внутри модального окна для обновления
            var modalTitle = deleteModal.querySelector('.modal-title');
            var modalBody = deleteModal.querySelector('.modal-body');
            var deleteForm = deleteModal.querySelector('#deleteForm');

            // Обновляем содержимое модального окна
            modalTitle.textContent = 'Удаление животного';
            modalBody.textContent = 'Вы уверены, что хотите удалить животное "' + animalName + '"?';
            
            // Устанавливаем атрибут 'action' для формы удаления
            deleteForm.action = actionUrl;
        });
    }
});