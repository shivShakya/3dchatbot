import { ModelLoading } from "../scriptnew.js";
// Select elements from DOM
const loaderOverlay = document.getElementById('loader-overlay');
const loaderFiller = document.getElementById('loader-bar-filler');
const loaderPercentage = document.getElementById('loader-percentage');

function updateLoader(percentage) {
    console.log({percentage});
    loaderFiller.style.width = percentage + '%';
    loaderPercentage.textContent = percentage + '%';
}

const assetsToLoad = [
    { url: '/assets/model/chatbot_female.glb', type: 'model', size: 16048660.8  },
];

const totalSize = assetsToLoad.reduce((acc, asset) => acc + asset.size, 0);
console.log("Total Size of Assets: " + totalSize);
let loadedSize = 0; 
let assetsLoaded = 0;

export function loadAssets() {
    assetsToLoad.forEach(asset => {
        if (asset.type === 'model') {
            const xhr = new XMLHttpRequest();
            xhr.open('GET', asset.url, true);
            xhr.responseType = 'arraybuffer';

            xhr.onprogress = function (event) {
                    const loaded = event.loaded;
                    const currentProgress = (loadedSize + loaded) / totalSize * 100;
                    console.log({currentProgress});
                    updateLoader(Math.round(currentProgress));
            };

            xhr.onload = function () {
                loadedSize += asset.size; 
                assetsLoaded++; 
                console.log({'xhr' : xhr.response});
                ModelLoading(xhr.response, 1, new THREE.Vector3(0, 0, 0), function (success) {
                    console.log('hii')
                    if (success) {
                        console.log({success});
                        checkIfAllAssetsLoaded();
                    } else {
                        console.log('Failed to load model.');
                    }
                });
            };

            xhr.onerror = function () {
                console.error('Failed to load model:', asset.url);
                loadedSize += asset.size;
                assetsLoaded++;
                updateLoader(Math.round((loadedSize / totalSize) * 100));
                checkIfAllAssetsLoaded();
            };

            xhr.send();
        } else if (asset.type === 'image') {
            const img = new Image();
            img.src = asset.url;

            img.onload = function () {
                loadedSize += asset.size;
                assetsLoaded++;
                const percentage = (loadedSize / totalSize) * 100;
                updateLoader(Math.round(percentage));

                checkIfAllAssetsLoaded();
            };

            img.onerror = function () {
                console.error('Failed to load image:', asset.url);
                loadedSize += asset.size;
                assetsLoaded++;
                updateLoader(Math.round((loadedSize / totalSize) * 100));
                checkIfAllAssetsLoaded();
            };
        }
    });
}

// Function to check if all assets are loaded
function checkIfAllAssetsLoaded() {
    if (assetsLoaded === assetsToLoad.length ) {
        console.log('All assets loaded successfully');
        document.getElementById('btn-div').style.display = 'none';
        document.getElementById('canvas-container').style.display = 'block';
        const btns = document.getElementById('btns');
        btns.style.display = 'flex';
        loaderOverlay.style.display = 'none';
    }
}

