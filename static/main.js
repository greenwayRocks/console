// canvas
const myConsole = document.querySelector("#myConsole");

const ctx = document.getElementById("myCanvas").getContext("2d");

const normalTag = document.querySelector("#normal");
const wsTag = document.querySelector("#ws");
const ddosTag = document.querySelector("#ddos");
const dtprobTag = document.querySelector("#dtprob");
const scanTag = document.querySelector("#scan");
const mitmTag = document.querySelector("#mitm");

const canvData = {
  type: "line",
  data: {
    labels: [
      "Normal",
      "Wrong Setup",
      "DDOS",
      "DataType Probing",
      "Scan Attack",
      "MITM"
    ],
    datasets: [
      {
        label: "# of Attacks",
        data: [0, 1, 2, 3, 4, 5],
        backgroundColor: ["crimson"],
        borderWidth: 2
      }
    ]
  },
  options: {}
};

// attack type dictionary - key -> prediction, value -> attack type
attack_type = {
  0: "Normal",
  1: "Wrong Setup",
  2: "DDOS",
  3: "Data Type Probing",
  4: "Scan Attack",
  5: "MITM"
};

(normal = 0), (ws = 0), (ddos = 0), (dtprob = 0), (scan = 0), (mitm = 0);

const myCanvas = new Chart(ctx, canvData);

let socket = new WebSocket("ws://localhost:8000/ws/console/");

socket.onmessage = function(e) {
  // Get backend data

  let djangoData = JSON.parse(e.data);
  let attack = djangoData.attack_type;

  switch (attack) {
    case "Normal":
      normal += 1;
      break;
    case "Wrong Setup":
      ws += 1;
      break;
    case "DDOS":
      ddos += 1;
    case "Data Type Probing":
      dtprob += 1;
    case "Scan Attack":
      scan += 1;
    case "MITM":
      mitm += 1;
    default:
      console.log("!! Unknown Attack !!");
  }

  // sync utc times
  let packettime = djangoData.frame_time.split(" ")[4].split(".")[0]; // eg 01:29:55

  let now = new Date();

  let now_utc = now
    .toUTCString()
    .split(" ")[4]
    .split(".")[0]; // eg 05:36:54

  // console.log(packettime, now_utc);
  if (now_utc.split(":")[1] == packettime.split(":")[1]) {
    diff = now_utc.split(":")[2] - packettime.split(":")[2];
  } else {
    min = now_utc.split(":")[1] - packettime.split(":")[1];
    sec = now_utc.split(":")[2] - packettime.split(":")[2];
    diff = min * 60 + sec;
  }
  // console.log(diff);

  // if (djangoData.attack_type != "Normal") {
  //   console.log("Not Normal");
  //   notNormal += 1;
  // }

  // Canvas thing!
  let tempData = canvData.data.datasets[0].data;
  tempData.shift();
  tempData.push(djangoData.value);

  myCanvas.update();

  // Log Console
  let html = `${djangoData.attack_type} ${djangoData.frame_number} ${djangoData.frame_time} ${djangoData.frame_len} ${djangoData.eth_src} ${djangoData.eth_dst} ${djangoData.ip_src} ${djangoData.ip_dst} ${djangoData.ip_proto} ${djangoData.ip_len} ${djangoData.tcp_len} ${djangoData.tcp_srcport} ${djangoData.tcp_dstport} ${djangoData._ws_col_Info}`;
  //myConsole.appendChild(html);
  myConsole.innerHTML = html;

  // skip to date.now()

  normalTag.innerHTML = `Normal Packets :: ${normal} [- ${diff} -]`;
  wsTag.innerHTML = `Wrong Setup Packets :: ${ws}`;
  ddosTag.innerHTML = `DDOS Packets :: ${ddos}`;
  dtprobTag.innerHTML = `Data Type Probing :: ${dtprob}`;
  scanTag.innerHTML = `Scan Attacks :: ${scan}`;
  mitmTag.innerHTML = `MITM Attacks :: ${mitm}`;
};
