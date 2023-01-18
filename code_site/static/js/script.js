let ready = (callback) => {
    if (document.readyState !== "loading") callback();
    else document.addEventListener("DOMContentLoaded", callback);
}

ready(() => {

    function getXmlHttp(){
        let xmlhttp;
        try {
            xmlhttp = new ActiveXObject('Msxml2.XMLHTTP');
        } catch (e) {
            try {
                xmlhttp = new ActiveXObject('Microsoft.XMLHTTP');
            } catch (e) {
                xmlhttp = false;
            }
        }
        if (!xmlhttp && typeof XMLHttpRequest !== 'undefined') {
            xmlhttp = new XMLHttpRequest();
        }
        return xmlhttp;
    }

    let loginFormPassInput = document.getElementById('id_password');
    if (loginFormPassInput) {
        let changePassView = document.getElementById('password-control');
        changePassView.addEventListener('click', function (e) {
            if (loginFormPassInput.getAttribute('type') === 'password') {
                changePassView.classList.add('view');
                loginFormPassInput.setAttribute('type', 'text');
            } else {
                changePassView.classList.remove('view');
                loginFormPassInput.setAttribute('type', 'password');
            }
        });
    }

    let loginForm = document.getElementById('login_form');
    if (loginForm) {
        loginForm.addEventListener("submit", function (e) {
            e.preventDefault();
            let thisForm = e.target;
            let method = thisForm.getAttribute('method');
            let endpoint = thisForm.getAttribute('action');
            let errorInput = document.getElementById('login_form-errors');
            let data = thisForm.elements;
            let resultForm = '';
            for (let i = 0; i < data.length; i++) {
                let item = data.item(i);
                let value = item.value;
                resultForm = resultForm + '&' + item.name + '=' + encodeURIComponent(value);
            }
            let myxmlhttp = getXmlHttp();
            myxmlhttp.open(method, endpoint, true);
            myxmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            myxmlhttp.setRequestHeader("X-CSRFToken", data.csrfmiddlewaretoken.value);
            myxmlhttp.send(resultForm);
            myxmlhttp.onload = function() {
                if (myxmlhttp.status === 401) {
                    errorInput.innerHTML = JSON.parse(myxmlhttp.response).answer;
                } else if (myxmlhttp.status === 403) {
                    errorInput.innerHTML = JSON.parse(myxmlhttp.response).answer;
                } else if (myxmlhttp.status === 200) {
                    document.location.href = "/";
                }
            };
            myxmlhttp.onerror = function() {
                console.log(myxmlhttp.responseText)
            };
        });
    }

    let mobileBurger = document.querySelector('.nav_icon-mobile');
    let mobileBody = document.querySelector('.menu_block-mobile');
    if (mobileBurger) {
        mobileBurger.addEventListener('click', function (e) {
            mobileBurger.classList.toggle('open');
            mobileBody.classList.toggle('visible_body');
        });
    }

    let deleteArchVideosBtns = document.querySelectorAll('.arch_cam_video_block-btn_delete');
    if (deleteArchVideosBtns.length > 0) {
        let modalAus = document.getElementById('del_video_aus');
        let modalAusYes = document.getElementById('del_video_aus_yes');
        let modalAusNo = document.getElementById('del_video_aus_no');
        let modalAusClose = document.getElementById('del_video_aus_close');
        let deleteForm = document.getElementById('delete_archive_video_form');
        deleteForm.addEventListener("submit", function (e) {
            e.preventDefault();
            let thisForm = e.target;
            let method = thisForm.getAttribute('method');
            let endpoint = thisForm.getAttribute('action');
            let data = thisForm.elements;
            let resultForm = '';
            for (let i = 0; i < data.length; i++) {
                let item = data.item(i);
                let value = item.value;
                resultForm = resultForm + '&' + item.name + '=' + encodeURIComponent(value);
            }
            let myxmlhttp = getXmlHttp();
            myxmlhttp.open(method, endpoint, true);
            myxmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            myxmlhttp.setRequestHeader("X-CSRFToken", data.csrfmiddlewaretoken.value);
            myxmlhttp.send(resultForm);
            myxmlhttp.onload = function() {
                if (myxmlhttp.status === 200) {
                    let answer = JSON.parse(myxmlhttp.response).answer;
                    let blockToDelete = document.getElementById(answer).parentElement.parentElement;
                    blockToDelete.remove();
                    modalAus.style.display = "none";
                }
            };
            myxmlhttp.onerror = function() {
                console.log(myxmlhttp.responseText)
            };
        });
        for (let i = 0; i < deleteArchVideosBtns.length; i ++) {
            deleteArchVideosBtns[i].addEventListener('click', function () {
                modalAus.style.display = "flex";
                window.onclick = function(event) {
                    if (event.target === modalAus || event.target === modalAusClose || event.target === modalAusNo) {
                        modalAus.style.display = "none";
                    }
                    if (event.target === modalAusYes) {
                        modalAusYes.value = deleteArchVideosBtns[i].id;
                    }
                }
            });
        }
    }

    let videoCamEntrance = document.getElementById('cam_entrance_video');
    if (videoCamEntrance) {
        console.log(window.location.origin + '/media/stream/cam_entrance/streaming.m3u8');
        let pathToStream = window.location.origin + '/media/stream/cam_entrance/streaming.m3u8';
        if(Hls.isSupported()) {
            let hls = new Hls();
            hls.on(Hls.Events.Error, function (event, data) {
                console.log("HLS error: ", event, data);
            });
            hls.attachMedia(videoCamEntrance);
            hls.on(Hls.Events.MEDIA_ATTACHED, function() {
                hls.loadSource(pathToStream);
                hls.on(Hls.Events.MANIFEST_PARSED,function() {
                    videoCamEntrance.play();
                });
            });
        }
        else if (videoCamEntrance.canPlayType('application/vnd.apple.mpegurl')) {
            videoCamEntrance.src = pathToStream;
            videoCamEntrance.addEventListener('loadedmetadata',function() {
                videoCamEntrance.play();
            });
        }
    }


});
