function retrieveDataAndShowModal() {
    let cropName = document.getElementById("crop-select").value;
    fetchAndUpdate(cropName);
}

// $(document).ready(function() {
//     $('form').submit(function(event) {
//         event.preventDefault();
//         $.ajax({
//             type: $(this).attr('method'),
//             url: $(this).attr('action'),
//             data: $(this).serialize(),
//             success: function(response) {
//                 alert(response.message);
//                 if (response.success) {
//                     window.location.reload(); // 或重定向到其他页面
//                 }
//             }
//         });
//     });
// });

function fetchAndUpdate(cropName) {
    let fetchUrl = document.getElementById('fetch-url').getAttribute('data-url');
    fetch(fetchUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ crop_name: cropName })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("gpt-data").textContent = JSON.stringify(data.gpt_data);
        document.getElementById("neo4j-data").textContent = JSON.stringify(data.neo4j_data);
        document.getElementById("comparison-modal").style.display = 'block';
    });
}

function confirmUpdate() {
    let cropName = document.getElementById("crop-select").value;
    let datadict = document.getElementById("gpt-data").textContent;
    updateNeo4jDatabase(cropName, datadict);
}

function updateNeo4jDatabase(cropName, datadict) {
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
            alert('更新成功');
        } else {
            alert('更新失败');
        }
        closeModal();
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
            if (response.success) {
                alert("作物删除成功");
                location.reload();
            } else {
                alert("错误: " + response.error);
            }
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