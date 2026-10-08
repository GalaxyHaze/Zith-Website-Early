(() => {
    "use strict";

    const container = document.querySelector(".bubbles");
    if (!container) return;

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const MIN_SPEED = 48;
    const MAX_SPEED = 480;
    const DRIFT = 10;
    const SEPARATION = 0.5;

    const rand = (min, max) => min + Math.random() * (max - min);

    const els = Array.from(container.querySelectorAll(".bubble"));
    if (!els.length) return;

    let width = container.clientWidth;
    let height = container.clientHeight;

    const num = (el, name, fallback) => {
        const raw = parseFloat(el.style.getPropertyValue(name));
        return Number.isFinite(raw) ? raw : fallback;
    };

    const bubbles = els.map((el) => {
        const r = num(el, "--bubble-size", 40) / 2;
        return {
            el,
            r,
            cx: (num(el, "--bubble-left", 50) / 100) * width,
            cy: (num(el, "--bubble-top", 50) / 100) * height,
            vx: rand(-DRIFT, DRIFT),
            vy: -rand(MIN_SPEED, MAX_SPEED),
        };
    });

    function respawn(b, fromBottom) {
        b.r = num(b.el, "--bubble-size", 40) / 2;
        b.cx = rand(b.r, Math.max(b.r, width - b.r));
        b.cy = fromBottom ? height + b.r + rand(0, height * 0.5) : rand(b.r, height - b.r);
        b.vx = rand(-DRIFT, DRIFT);
        b.vy = -rand(MIN_SPEED, MAX_SPEED);
    }

    function step(dt) {
        for (const b of bubbles) {
            b.cx += b.vx * dt;
            b.cy += b.vy * dt;

            if (b.cx - b.r < 0) { b.cx = b.r; b.vx = Math.abs(b.vx); }
            if (b.cx + b.r > width) { b.cx = width - b.r; b.vx = -Math.abs(b.vx); }

            if (b.cy + b.r < 0) respawn(b, true);
        }

        for (let i = 0; i < bubbles.length; i += 1) {
            for (let j = i + 1; j < bubbles.length; j += 1) {
                const a = bubbles[i];
                const c = bubbles[j];
                const dx = c.cx - a.cx;
                const dy = c.cy - a.cy;
                const minDist = a.r + c.r;
                const distSq = dx * dx + dy * dy;
                if (distSq >= minDist * minDist) continue;

                const dist = Math.sqrt(distSq) || 0.001;
                const nx = dx / dist;
                const ny = dy / dist;
                const push = (minDist - dist) * SEPARATION;
                a.cx -= nx * push;
                a.cy -= ny * push;
                c.cx += nx * push;
                c.cy += ny * push;
            }
        }

        for (const b of bubbles) {
            b.el.style.transform = `translate(${b.cx - b.r}px, ${b.cy - b.r}px)`;
        }
    }

    let last = 0;
    function frame(now) {
        const dt = Math.min((now - last) / 1000, 0.05);
        last = now;
        step(dt);
        requestAnimationFrame(frame);
    }

    window.addEventListener("resize", () => {
        width = container.clientWidth;
        height = container.clientHeight;
        for (const b of bubbles) {
            b.r = Math.min(b.r, Math.max(4, width / 2 - 1));
            b.el.style.width = `${b.r * 2}px`;
            b.el.style.height = `${b.r * 2}px`;
            b.cx = Math.min(Math.max(b.cx, b.r), width - b.r);
            b.cy = Math.min(b.cy, height - b.r);
        }
    });

    for (const b of bubbles) {
        b.el.style.transform = `translate(${b.cx - b.r}px, ${b.cy - b.r}px)`;
    }

    document.documentElement.dataset.bubbles = "js";

    requestAnimationFrame((now) => {
        last = now;
        requestAnimationFrame(frame);
    });
})();
