import * as THREE from 'three'
import type { RobotState } from './trace'




const canvas = document.querySelector<HTMLCanvasElement>("#scene");
if (!canvas) {
    throw new Error("Canvas not detected in DOM.")
}
const robotColors: Record<RobotState, THREE.Color> = {
    idle: new THREE.Color('pink'),
    moving: new THREE.Color('green'),
    inspecting: new THREE.Color('blue'),
    repairing: new THREE.Color('brown')
}



const axesHelper = new THREE.AxesHelper(2)
const width = 600;
const height = 400;



const scene = new THREE.Scene();


//robot
const robotGeometry = new THREE.BoxGeometry(1, 1, 1)
const robotMaterial = new THREE.MeshStandardMaterial({ color: robotColors.idle })
const robot = new THREE.Mesh(robotGeometry, robotMaterial)
robot.position.x = -1.5
robot.rotation.x = Math.PI * 0.25

export function setRobotState(state: RobotState): void {
    robot.material.color.copy(robotColors[state])
}


//machine
const machineGeometry = new THREE.BoxGeometry(1, 1, 1)
const machineMaterial = new THREE.MeshStandardMaterial({ color: "grey" })
const machine = new THREE.Mesh(machineGeometry, machineMaterial)
machine.position.x = 1.5
machine.rotation.x = Math.PI * 0.25



const camera = new THREE.PerspectiveCamera(75, width / height);
camera.position.z = 4

//lights
const ambientLight = new THREE.AmbientLight("white", 1)

const directionalLight = new THREE.DirectionalLight("white", 0.9)
directionalLight.position.set(1,2,3)

scene.add(axesHelper)
scene.add(robot)
scene.add(machine)
scene.add(directionalLight)
scene.add(ambientLight)


const renderer = new THREE.WebGLRenderer({ canvas });
renderer.setSize(width,height)


const timer = new THREE.Timer()

renderer.setAnimationLoop(() => {
    timer.update()
    const elapsedTime = timer.getElapsed()
    robot.rotation.y = elapsedTime
    renderer.render(scene, camera)
})