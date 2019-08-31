"""__author__ = 叶小永"""
from django.conf import settings
from django.core.mail import send_mail

from celery_tasks.main import app


@app.task(name='send_verity_email')
def send_verity_email(to_email, verity_url):
    subject = '美多商城邮箱验证'
    html_message = '<p>尊敬的用户，您好！</p>'\
                   '<p>感谢您使用美多商城。</p>'\
                   '<p>您的邮箱为：%s。请点击此链接激活您的邮箱：</p>'\
                   '<p><a href="%s">%s<a></p>' % (to_email, verity_url, verity_url)
    # 发送验证邮件
    send_mail(subject, "", settings.EMAIL_FROM, [to_email], html_message=html_message)

