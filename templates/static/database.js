// const url = window.location.href;
// const url = 'http://127.0.0.1:8765/';
$("#export").on('click', function () {
    fetch(url + '?method=export', {
        method: 'get'
    }).then(res => res.blob().then(blob => {
        let a = document.createElement('a');
        let url = window.URL.createObjectURL(blob);
        // let filename = res.headers.get('Content-Disposition');
        a.href = url;
        a.download = 'output.txt';
        a.click();
        window.URL.revokeObjectURL(url);
    }));
});
$("#clear").on('click', function () {
    document.getElementById('text').value = ''
})
$("#execute").on('click', function () {
    let sql = window.prompt("Please Enter Sql Statement!")
    if (sql === null) return
    if (sql === '') {
        window.alert("Statement Can't Be Null!")
        return;
    }
    console.log(sql)
    let select = false;
    let u = url;
    if (sql.includes('select')) {
        select = true;
        u = url + '?method=select'
    } else u = url + '?method=sql'
    fetch(u, {
        method: 'post',
        headers: {
            'content-length': sql.length
        },
        body: sql
    }).then(response => {
        if (response.status === 200) {
            if (select) {
                let rows = response.headers.get('rows')
                window.alert('Select Succeed!\nSelected ' + rows + ' Row(s)')
                response.text().then(text => {
                    console.log(text)
                    document.getElementById('text').value += text + '\n';
                })
            } else window.alert("Succeed!")
        } else {
            response.text().then(text => {
                window.alert("Error!\nMessage: " + text)
            })
        }
    })
})
$("#confirm").on('click', function () {
    if (method !== '') {
        if (methods_1.includes(method)) {
            fetch(url + '?method=' + method, {
                method: 'post'
            }).then(response => response.text()).then(text => {
                console.log(text)
                document.getElementById('text').value += text + '\n'
                $('#text').scrollTop($('#text')[0].scrollHeight);
            })
        } else {
            if (document.getElementById('form1').value.length > 0) {
                console.log(document.getElementById('form1').value.length)
                fetch(url + '?method=' + method, {
                    method: 'post',
                    headers: {'content-length': document.getElementById('form1').value.length},
                    body: document.getElementById('form1').value
                }).then(response => response.text()).then(text => {
                    console.log(text)
                    document.getElementById('text').value += text + '\n'
                    $('#text').scrollTop($('#text')[0].scrollHeight);
                })
            }
        }
    }
})