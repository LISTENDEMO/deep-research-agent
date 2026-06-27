import { useEffect, useRef } from "react";

type TrailPoint = {
  x: number;
  y: number;
  age: number;
  hue: number;
};

const maxAge = 72;
const maxPoints = 56;

export function MouseWake() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const pointsRef = useRef<TrailPoint[]>([]);
  const hueRef = useRef(170);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const context = canvas.getContext("2d");
    if (!context) return;
    const targetCanvas = canvas;
    const ctx = context;

    let animationFrame = 0;
    let width = 0;
    let height = 0;

    function resize() {
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      width = window.innerWidth;
      height = window.innerHeight;
      targetCanvas.width = Math.floor(width * ratio);
      targetCanvas.height = Math.floor(height * ratio);
      targetCanvas.style.width = `${width}px`;
      targetCanvas.style.height = `${height}px`;
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    }

    function addPoint(x: number, y: number) {
      hueRef.current = (hueRef.current + 7) % 360;
      pointsRef.current.push({ x, y, age: 0, hue: hueRef.current });
      if (pointsRef.current.length > maxPoints) {
        pointsRef.current.splice(0, pointsRef.current.length - maxPoints);
      }
    }

    function drawRibbon(points: TrailPoint[], offset: number, lineWidth: number, alpha: number) {
      if (points.length < 3) return;
      ctx.beginPath();
      const first = points[0];
      ctx.moveTo(first.x, first.y + offset);
      for (let index = 1; index < points.length - 1; index += 1) {
        const current = points[index];
        const next = points[index + 1];
        const midX = (current.x + next.x) / 2;
        const midY = (current.y + next.y) / 2 + Math.sin(index * 0.82 + offset) * 9;
        ctx.quadraticCurveTo(current.x, current.y + offset, midX, midY);
      }
      const last = points[points.length - 1];
      ctx.strokeStyle = `hsla(${last.hue}, 95%, 68%, ${alpha})`;
      ctx.lineWidth = lineWidth;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      ctx.stroke();
    }

    function draw() {
      ctx.clearRect(0, 0, width, height);
      for (const point of pointsRef.current) {
        point.age += 1;
      }
      pointsRef.current = pointsRef.current.filter((point) => point.age < maxAge);

      const points = pointsRef.current;
      if (points.length > 2) {
        ctx.save();
        ctx.globalCompositeOperation = "lighter";
        ctx.shadowBlur = 28;
        ctx.shadowColor = "rgba(126, 249, 212, 0.55)";

        const drifting = points.map((point, index) => {
          const life = 1 - point.age / maxAge;
          return {
            ...point,
            x: point.x + Math.sin(index * 1.7 + point.age * 0.05) * (1 - life) * 18,
            y: point.y + Math.cos(index * 1.3 + point.age * 0.04) * (1 - life) * 14,
          };
        });

        drawRibbon(drifting, -10, 2.2, 0.2);
        drawRibbon(drifting, 0, 1.25, 0.55);
        drawRibbon(drifting, 12, 1.6, 0.18);

        for (const point of drifting) {
          const life = 1 - point.age / maxAge;
          const radius = 18 * life;
          const gradient = ctx.createRadialGradient(point.x, point.y, 0, point.x, point.y, radius);
          gradient.addColorStop(0, `hsla(${point.hue}, 100%, 72%, ${0.16 * life})`);
          gradient.addColorStop(0.55, `hsla(${(point.hue + 60) % 360}, 100%, 78%, ${0.05 * life})`);
          gradient.addColorStop(1, "rgba(255,255,255,0)");
          ctx.fillStyle = gradient;
          ctx.beginPath();
          ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
          ctx.fill();
        }
        ctx.restore();
      }

      animationFrame = window.requestAnimationFrame(draw);
    }

    function handlePointerMove(event: PointerEvent) {
      addPoint(event.clientX, event.clientY);
    }

    resize();
    window.addEventListener("resize", resize);
    window.addEventListener("pointermove", handlePointerMove, { passive: true });
    animationFrame = window.requestAnimationFrame(draw);

    return () => {
      window.removeEventListener("resize", resize);
      window.removeEventListener("pointermove", handlePointerMove);
      window.cancelAnimationFrame(animationFrame);
    };
  }, []);

  return <canvas className="mouse-wake" ref={canvasRef} aria-hidden="true" />;
}
