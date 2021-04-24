const qrCode = window.qrcode;

const video = document.createElement("video");
const canvasElement = document.getElementById("qr-canvas");
const canvas = canvasElement.getContext("2d");

const qrResult = document.getElementById("qr-result");
const outputData = document.getElementById("outputData");
const btnScanQR = document.getElementById("btn-scan-qr");

let scanning = false;
let data;
let resp;

//Callback que obtiene los datos del QR
qrCode.callback = res => {
  if (res) {
    //Convertimos el contenido del QR a JSON y luego enseñamos los datos importantes
    data = JSON.parse(res);
    resp = JSON.stringify('Nombre: ' + data.nombre + ' ' + data.apellido + ', ' +  'Matricula: ' + data.uuid);
    
    outputData.innerText = resp;
    scanning = false;

    video.srcObject.getTracks().forEach(track => {
      track.stop();
    });
    
    qrResult.hidden = false;
    canvasElement.hidden = true;
    btnScanQR.hidden = false;
    
    fetch('/datosQR', {
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
      scanning = true;
      qrResult.hidden = true;
      btnScanQR.hidden = true;
      canvasElement.hidden = false;
      video.setAttribute("playsinline", true);
      video.srcObject = stream;
      video.play();
      tick();
      scan();
    });
};

//Parametros de la ventana de la camara
function tick() {
  canvasElement.height = video.videoHeight;
  canvasElement.width = video.videoWidth;
  canvas.drawImage(video, 0, 0, canvasElement.width, canvasElement.height);

  scanning && requestAnimationFrame(tick);
}

//Funcion para decodificar el QR
function scan() {
  try {
    qrCode.decode();
  } catch (e) {
    setTimeout(scan, 300);
  }
}