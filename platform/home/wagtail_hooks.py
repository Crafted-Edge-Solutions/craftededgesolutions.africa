from wagtail import hooks
from django.utils.html import format_html


@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html(
        """<style>
        :root {{
            --w-color-primary: #e89240;
            --w-color-primary-200: #f5c48a;
        }}
        .w-header {{
            background: #0a0a0b !important;
            border-bottom: 1px solid #1e1e20 !important;
        }}
        .sidebar {{
            background: #0d0d0f !important;
        }}
        .sidebar__inner {{
            background: #0d0d0f !important;
        }}
        .sidebar-menu-item__link:hover,
        .sidebar-menu-item--active .sidebar-menu-item__link {{
            background: rgba(232,146,64,0.12) !important;
            color: #e89240 !important;
        }}
        .button.bicolor.button--icon,
        .button-longrunning.bicolor {{
            background-color: #e89240 !important;
        }}
        a {{ color: #e89240; }}
        </style>"""
    )


@hooks.register("insert_global_admin_js")
def global_admin_js():
    return format_html(
        """<script>
        document.addEventListener('DOMContentLoaded', function() {{
            var logo = document.querySelector('.w-header__logo img, .sidebar__logo img');
            if (logo) {{
                logo.alt = 'Crafted Edge Solutions';
                logo.style.height = '28px';
            }}
        }});
        </script>"""
    )
