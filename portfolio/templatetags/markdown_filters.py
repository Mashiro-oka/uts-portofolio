from django import template
from django.utils.safestring import mark_safe
from markdown_it import MarkdownIt

register = template.Library()

parser = MarkdownIt("js-default", {
    "html": False,
    "breaks": True,
})


@register.filter(name="markdown")
def render_markdown(value):
    return mark_safe(parser.render(str(value or "")))