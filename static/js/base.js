document.addEventListener('DOMContentLoaded', function () {
    const logoutLink = document.getElementById('logout-link');

    if (logoutLink) {
        logoutLink.addEventListener('click', function (event) {
            // 弹出确认框
            const confirmLogout = confirm('确定要登出吗？');

            // 如果用户不确认登出，则阻止默认的点击行为
            if (!confirmLogout) {
                event.preventDefault();
            }
        });
    }
});

function showErrorModal(customMessage) {
    // 设置个性化的错误信息
    document.getElementById('error-message').textContent = customMessage;

    // 显示模态框
    $('#errorModal').modal('show');
}


function showLoadingModal(customMessage) {
    // 设置个性化的错误信息
    document.getElementById('loading-message').textContent = customMessage;

    // 显示模态框
    $('#loadingModal').modal('show');
}

function hideLoadingModal() {
    $('#loadingModal').modal('hide');
}