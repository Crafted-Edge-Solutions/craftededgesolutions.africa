from wagtail import hooks
from django.utils.html import format_html


@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html("""<style>
/* CES brand colours in Wagtail admin */
:root {{
    --w-color-primary: #e89240 !important;
    --w-color-primary-200: rgba(232,146,64,0.2) !important;
    --w-color-secondary: #e89240 !important;
}}
.w-header {{ background: #0a0a0b !important; border-bottom: 1px solid #1e1e20 !important; }}
.sidebar, .sidebar__inner {{ background: #0d0d0f !important; }}
.sidebar-menu-item__link:hover {{ background: rgba(232,146,64,0.1) !important; color: #e89240 !important; }}
.sidebar-menu-item--active > .sidebar-menu-item__link {{ color: #e89240 !important; }}
.button--primary, .button.yes, input[type=submit] {{ background-color: #e89240 !important; border-color: #e89240 !important; }}
.button--primary:hover {{ background-color: #d4832e !important; }}
a:not(.button) {{ color: #e89240; }}
a:not(.button):hover {{ color: #f5a35c; }}
.w-breadcrumb__item--current {{ color: #e89240 !important; }}
</style>""")
