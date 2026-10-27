import * as THREE from 'three';
import { gsap } from 'gsap';

const instances = new WeakMap();

export async function renderChart(host, rows, { animate = true } = {}) {
  destroyChart(host);
  if (!rows.length) throw new Error('No hay categorías para graficar.');

  const width = Math.max(300, host.clientWidth || 700);
  const height = 330;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#f7f5f5');
  const camera = new THREE.PerspectiveCamera(34, width / height, 0.1, 100);
  camera.position.set(0, 6.8, 11.5);
  camera.lookAt(0, 1.1, 0);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.6));
  renderer.setSize(width, height);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.domElement.setAttribute('role', 'img');
  renderer.domElement.setAttribute('aria-label', 'Gráfico tridimensional del valor de inventario por categoría');
  host.replaceChildren(renderer.domElement);

  scene.add(new THREE.HemisphereLight(0xffffff, 0xa9b6ca, 2));
  const keyLight = new THREE.DirectionalLight(0xffffff, 2.2);
  keyLight.position.set(-3, 8, 5);
  scene.add(keyLight);

  const floor = new THREE.Mesh(new THREE.PlaneGeometry(12, 7), new THREE.MeshStandardMaterial({ color: '#eeecec', roughness: 0.92 }));
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -0.04;
  scene.add(floor);

  const palette = ['#405d90', '#269dd8', '#ff931e', '#777bbc', '#80b9d4', '#ad8bc7'];
  const maxValue = Math.max(...rows.map((row) => Number(row.valor) || 0), 1);
  const spacing = Math.min(1.75, 9 / Math.max(rows.length, 1));
  const totalWidth = spacing * rows.length;
  const bars = [];

  rows.forEach((row, index) => {
    const value = Math.max(0, Number(row.valor) || 0);
    const finalHeight = Math.max(0.06, (value / maxValue) * 3.4);
    const material = new THREE.MeshStandardMaterial({ color: palette[index % palette.length], roughness: 0.56, metalness: 0.04 });
    const geometry = new THREE.BoxGeometry(Math.min(0.9, spacing * 0.62), finalHeight, 0.72);
    const bar = new THREE.Mesh(geometry, material);
    bar.position.set(index * spacing - totalWidth / 2 + spacing / 2, finalHeight / 2, 0);
    if (animate) { bar.scale.y = 0.015; bar.position.y = 0; }
    scene.add(bar);
    bars.push(bar);

    const label = document.createElement('span');
    label.className = 'chart-3d-label';
    label.textContent = row.nombre;
    label.title = `${row.nombre}: $ ${value.toLocaleString('es-CO')} COP`;
    host.appendChild(label);
  });

  const resizeObserver = new ResizeObserver(() => {
    const nextWidth = Math.max(300, host.clientWidth || 700);
    camera.aspect = nextWidth / height;
    camera.updateProjectionMatrix();
    renderer.setSize(nextWidth, height);
    renderer.render(scene, camera);
  });
  resizeObserver.observe(host);

  let dragging = false;
  let lastX = 0;
  renderer.domElement.addEventListener('pointerdown', (event) => { dragging = true; lastX = event.clientX; renderer.domElement.setPointerCapture(event.pointerId); });
  renderer.domElement.addEventListener('pointermove', (event) => {
    if (!dragging) return;
    scene.rotation.y += (event.clientX - lastX) * 0.006;
    lastX = event.clientX;
    renderer.render(scene, camera);
  });
  renderer.domElement.addEventListener('pointerup', () => { dragging = false; });

  const render = () => renderer.render(scene, camera);
  render();
  if (animate) {
    const entrance = gsap.timeline({ onUpdate: render });
    bars.forEach((bar, index) => {
      const finalHeight = bar.geometry.parameters.height;
      entrance.to(bar.scale, { y: 1, duration: 0.52, ease: 'power2.out' }, index * 0.05);
      entrance.to(bar.position, { y: finalHeight / 2, duration: 0.52, ease: 'power2.out' }, index * 0.05);
    });
  }
  instances.set(host, { renderer, scene, resizeObserver, render });
  host.setAttribute('aria-label', 'Valor estimado por categoría');
}

export function destroyChart(host) {
  const instance = instances.get(host);
  if (!instance) return;
  gsap.ticker.remove(instance.render);
  instance.resizeObserver.disconnect();
  instance.scene.traverse((object) => {
    object.geometry?.dispose();
    if (Array.isArray(object.material)) object.material.forEach((material) => material.dispose());
    else object.material?.dispose();
  });
  instance.renderer.dispose();
  instances.delete(host);
  host.replaceChildren();
}
