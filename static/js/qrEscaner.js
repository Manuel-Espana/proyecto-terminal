const codigo_qr = window.qrcode;
const video = document.createElement("video");
const qr_canvas = document.getElementById("qr-canvas");
const canvas = qr_canvas.getContext("2d");
const qr_res = document.getElementById("qr-res");
const respuesta = document.getElementById("respuesta");
const btnScanQR = document.getElementById("btn-scan-qr");

let escanear = false;
let data;
let resp;

//Callback que obtiene los datos del QR
codigo_qr.callback = res => {
  if (res) {
    //Convertimos el contenido del QR a JSON y luego enseñamos los datos importantes
    data = JSON.parse(res);
    resp = JSON.stringify('Nombre: ' + data.nombre + ' ' + data.apellido + ', ' +  'Matricula: ' + data.uuid);
    
    respuesta.innerText = resp;
    escanear = false;

    video.srcObject.getTracks().forEach(track => {
      track.stop();
    });
    
    qr_res.hidden = false;
    qr_canvas.hidden = true;
    btnScanQR.hidden = false;
    
    fetch('/datos_qr', {
      // Declaramos los datos que se envian
      headers: {
        'Content-Type': 'application/json'
      },
      method: 'POST',
      // El cuerpo es un JSON
      body: JSON.stringify(res)
    }).then(function (response) {
      return response.text();
    }).then(function (text) {
      console.log('POST response: ');
      // Mensaje de verificacion que todo salio bien
      console.log(text);
    });
  }
};

//Evento para activar la carmara
btnScanQR.onclick = () => {
  navigator.mediaDevices
    .getUserMedia({ video: { facingMode: "environment" } })
    .then(function(stream) {
      escanear = true;
      qr_res.hidden = true;
      btnScanQR.hidden = true;
      qr_canvas.hidden = false;
      video.setAttribute("playsinline", true);
      video.srcObject = stream;
      video.play();
      tick();
      scan();
    });
};

//Parametros de la ventana de la camara
function tick() {
  qr_canvas.height = video.videoHeight;
  qr_canvas.width = video.videoWidth;
  canvas.drawImage(video, 0, 0, qr_canvas.width, qr_canvas.height);

  escanear && requestAnimationFrame(tick);
}

//Funcion para decodificar el QR
function scan() {
  try {
    codigo_qr.decode();
  } catch (e) {
    setTimeout(scan, 300);
  }
}