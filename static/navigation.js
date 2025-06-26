// navigation.js - sticky header for Sparky Messaging
(function() {
    if (document.querySelector('.sparky-header')) return; // Prevent duplicate headers
    const header = document.createElement('header');
    header.className = 'sparky-header';
    header.innerHTML = `
        <div class="sparky-header-left" style="display:flex;align-items:center;padding-left:0;">
            <span>Sparky Messaging</span>
        </div>
        <div class="sparky-header-center"></div>
        <div class="sparky-header-right"></div>
    `;
    // Wait for DOMContentLoaded if body is not ready
    if (document.body) {
        document.body.prepend(header);
    } else {
        document.addEventListener('DOMContentLoaded', function() {
            document.body.prepend(header);
        });
    }
    const style = document.createElement('style');
    style.textContent = `
        .sparky-header {
            position: sticky;
            top: 0;
            width: 100vw;
            background: #fff;
            z-index: 1000;
            box-shadow: 0 2px 8px rgba(42,63,124,0.08);
            display: grid;
            grid-template-columns: max-content 1fr 1fr;
            align-items: center;
            min-height: 64px;
        }
        .sparky-header-left {
            font-size: 2em;
            font-weight: 800;
            color: #1976ff;
            letter-spacing: 1px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
        }
        .sparky-header-center {
            text-align: center;
            background: #e0e0e0;
        }
        .sparky-header-right {
            text-align: right;
            padding-right: 32px;
            display: flex;
            align-items: center;
            gap: 12px;
            justify-content: flex-end;
            background: #cccccc;
        }
    `;
    document.head.appendChild(style);
})();
