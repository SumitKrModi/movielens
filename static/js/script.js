document.addEventListener("DOMContentLoaded", function () {
    const lazyImages = document.querySelectorAll(".lazy-img");

    if ("IntersectionObserver" in window) {
        const observer = new IntersectionObserver(
            (entries, obs) => {
                entries.forEach(entry => {
                    if (!entry.isIntersecting) return;

                    const img = entry.target;
                    const realSrc = img.dataset.src;
                    if (!realSrc) return;

                    const temp = new Image();
                    temp.src = realSrc;

                    temp.onload = () => {
                        img.src = realSrc;
                        img.classList.add("loaded");
                    };

                    obs.unobserve(img);
                });
            },
            {
                rootMargin: "80px",
                threshold: 0.1
            }
        );

        lazyImages.forEach(img => observer.observe(img));
    } else {
        // Fallback for very old browsers
        lazyImages.forEach(img => {
            const realSrc = img.dataset.src;
            if (!realSrc) return;

            const temp = new Image();
            temp.src = realSrc;

            temp.onload = () => {
                img.src = realSrc;
                img.classList.add("loaded");
            };
        });
    }
});
