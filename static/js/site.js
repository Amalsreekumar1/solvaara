/* Solvaara: menu drawer and product gallery. Plain JavaScript, no libraries. */
(function () {
    var body = document.body;

    /* ---- Menu drawer ---- */
    var toggle = document.querySelector('[data-drawer-toggle]');
    var drawer = document.getElementById('nav-drawer');
    var backdrop = document.querySelector('[data-drawer-backdrop]');

    if (toggle && drawer) {
        var closeButton = drawer.querySelector('[data-drawer-close]');

        function focusable() {
            return drawer.querySelectorAll('a[href], button:not([disabled])');
        }

        function openDrawer() {
            body.classList.add('drawer-open');
            toggle.setAttribute('aria-expanded', 'true');
            if (closeButton) { closeButton.focus(); }
        }

        function closeDrawer() {
            body.classList.remove('drawer-open');
            toggle.setAttribute('aria-expanded', 'false');
            toggle.focus();
        }

        toggle.addEventListener('click', openDrawer);
        if (closeButton) { closeButton.addEventListener('click', closeDrawer); }
        if (backdrop) { backdrop.addEventListener('click', closeDrawer); }

        document.addEventListener('keydown', function (event) {
            if (!body.classList.contains('drawer-open')) { return; }

            if (event.key === 'Escape') {
                closeDrawer();
                return;
            }

            if (event.key === 'Tab') {
                var items = focusable();
                if (!items.length) { return; }
                var first = items[0];
                var last = items[items.length - 1];
                if (event.shiftKey && document.activeElement === first) {
                    event.preventDefault();
                    last.focus();
                } else if (!event.shiftKey && document.activeElement === last) {
                    event.preventDefault();
                    first.focus();
                }
            }
        });
    }

    /* ---- Product gallery ---- */
    var gallery = document.querySelector('[data-gallery]');
    if (gallery) {
        var main = gallery.querySelector('[data-gallery-main]');
        var thumbs = gallery.querySelectorAll('[data-thumb]');

        thumbs.forEach(function (thumb) {
            thumb.addEventListener('click', function () {
                if (main) {
                    main.src = thumb.getAttribute('data-src');
                    main.alt = thumb.getAttribute('data-alt') || '';
                }
                thumbs.forEach(function (other) {
                    other.classList.remove('is-active');
                    other.removeAttribute('aria-current');
                });
                thumb.classList.add('is-active');
                thumb.setAttribute('aria-current', 'true');
            });
        });
    }
})();