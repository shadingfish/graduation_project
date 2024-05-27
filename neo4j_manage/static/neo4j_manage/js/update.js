document.addEventListener('DOMContentLoaded', function() {
    
    document.getElementById('uploadFile').addEventListener('submit', function(e) {
        e.preventDefault();

        const fileInput = document.getElementById('customFile');
        if (!fileInput.files.length) {
            alert('请先选择一个文件再上传。');
            return; // 如果没有文件被选择，提醒用户并中断提交
        }
        
        showLoadingModal("正在导入名录...")
        const formData = new FormData(this);
        fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            credentials: 'same-origin'  // 确保 cookies 与请求一同发送
        })
        .then(response => {
            if (!response.ok) {
                alert('服务器错误, 状态码: ' + response.status);
                throw new Error('服务器错误, 状态码: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                hideLoadingModal();
                alert('上传成功！');
                window.location.reload(); // 刷新页面
            } else {
                hideLoadingModal();
                alert('上传失败: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorModal('上传异常，请稍后再试。');
        });
    });
    
    // const form = document.getElementById('addNewCrop');
    // if (form) {
    //     form.addEventListener('submit', function(event) {
    //         event.preventDefault(); // 阻止表单默认提交行为
    //
    //         // 使用 FormData 接口收集表单数据
    //         const formData = new FormData(this);
    //
    //         // 发送 fetch 请求
    //         fetch(this.action, {
    //             method: 'POST',
    //             body: formData,
    //             headers: {
    //                 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    //             },
    //             credentials: 'same-origin'  // 确保 cookies 与请求一同发送
    //         })
    //         .then(response => {
    //             if (!response.ok) {
    //                 throw new Error('Network response was not ok.');
    //             }
    //             return response.json();
    //         })
    //         .then(data => {
    //             alert(data.message);  // 根据后端返回的消息进行提示
    //             if (data.success) {
    //                 window.location.reload(); // 或重定向到其他页面
    //             }
    //         })
    //         .catch(error => {
    //             console.error('Error:', error);
    //             alert('上传异常，请稍后再试。');
    //         });
    //     });
    // }
});

function retrieveDataAndShowModal() {
    let cropName = document.getElementById("crop-select").value;
    fetchAndUpdate(cropName);
}

function fetchAndUpdate(cropName) {
    showLoadingModal("正在获取数据...");
    let fetchUrl = document.getElementById('fetch-url').getAttribute('data-url');
    fetch(fetchUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        body: cropName
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("gpt-data").textContent = JSON.stringify(data.gpt_data);
        document.getElementById("neo4j-data").textContent = JSON.stringify(data.neo4j_data);
        hideLoadingModal();
        document.getElementById("comparison-modal").style.display = 'block';
    })
    .catch(error => {
        showErrorModal(error);
    });
}

function confirmUpdate() {
    let cropName = JSON.parse(document.getElementById("crop-select").value).latin_name;
    let datadict = document.getElementById("gpt-data").textContent;
    updateNeo4jDatabase(cropName, datadict);
}

function updateNeo4jDatabase(cropName, datadict) {
    showLoadingModal("正在更新知识图谱...");
    let updateUrl = document.getElementById('update-url').getAttribute('data-url');
    fetch(updateUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ crop_name: cropName, datadict: datadict })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            hideLoadingModal();
            alert('更新成功');
            location.reload();
        } else {
            hideLoadingModal();
            alert('更新失败');
        }
        closeModal();
    })
    .catch(error => {
        showErrorModal(error);
    });
}

function confirmDelete(latinName, url) {
    if (confirm('确定要删除作物 ' + latinName + ' 吗？')) {
        deleteCrop(latinName, url);
    }
}

function deleteCrop(latinName, url) {
    $.ajax({
        type: 'POST',
        url: url,
        data: {
            'latin_name': latinName,
            'csrfmiddlewaretoken': getCSRFToken() // 获取 CSRF 令牌
        },
        success: function(response) {
            alert("作物删除成功");
            location.reload();  // 成功后刷新页面
        },
        error: function(response) {
            // 从响应中解析错误信息并显示
            let errorMsg = response.responseJSON && response.responseJSON.error ? response.responseJSON.error : "未知错误";
            alert("删除失败: " + errorMsg);
        }
    });
}


function closeModal() {
    document.getElementById("comparison-modal").style.display = 'none';
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getCSRFToken() {
        // 从 cookie 中获取 CSRF 令牌
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            let cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = cookies[i].trim();
                if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken' + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }