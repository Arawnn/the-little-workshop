import * as THREE from 'three'

const canvas = document.querySelector<HTMLCanvasElement>("#scene");
if (!canvas) {
    throw new Error("Canvas not detected in DOM.")
}

const axesHelper = new THREE.AxesHelper(2)
const width = 600;
const height = 400;



const scene = new THREE.Scene();
const geometry = new THREE.BoxGeometry(1, 1, 1)
const material = new THREE.MeshBasicMaterial({ color: 0xff0000 })
const mesh = new THREE.Mesh(geometry, material)
mesh.rotation.x = Math.PI * 0.25
mesh.rotation.y = Math.PI * 0.25



const camera = new THREE.PerspectiveCamera(75, width / height);
camera.position.z = 3
camera.lookAt(mesh.position)


scene.add(axesHelper)
scene.add(mesh)
scene.add(camera)

const renderer = new THREE.WebGLRenderer({ canvas });
renderer.setSize(width,height)
renderer.render(scene, camera)