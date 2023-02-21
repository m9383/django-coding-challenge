from typing import List, Any

from django.core.mail import send_mail
from django.template import Template
from django.template.loader import get_template


DEFAULT_FROM_EMAIL = "noreply@email.com"


class EmailNotification:
    """A convenience class to send email notifications"""

    subject = "License expiry info"  # type: str
    from_email = DEFAULT_FROM_EMAIL  # type: str
    html_template_path = "license_expiry_email.html"  # type: str
    text_template_path = "license_expiry_email.txt"  # type: str

    @classmethod
    def render_templates(cls, context: Any) -> (str, str):
        html_template = get_template(cls.html_template_path)
        txt_template = get_template(cls.text_template_path)
        message_body_html = html_template.render(context=context)
        message_body_txt = txt_template.render(context=context)
        return message_body_txt, message_body_html

    @classmethod
    def send_notification(
        cls, recipients: List[str], message_body_text: str, message_body_html: str
    ):
        """Send the notification using the given context"""
        send_mail(
            cls.subject,
            message_body_text,
            cls.from_email,
            recipients,
            fail_silently=False,
            html_message=message_body_html,
        )
