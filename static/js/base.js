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