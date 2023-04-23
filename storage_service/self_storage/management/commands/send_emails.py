import datetime

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template import Context, Template

from self_storage.models import Box


BOX_RENT_ENDS_SOON_NOTICE_TEMPLATE = """
Уведомление о скором окончании срока аренды:
Срок аренды бокса "{{ box.name }}",
расположенного по адресу: {{ box.warehouse.name }} - {{ box.warehouse.address }},
подходит к концу {{ box.end_date }}
"""

BOX_RENT_ENDED_NOTICE_TEMPLATE = """
Срок аренды бокса {{ box.name }},
расположенного по адресу: {{ box.warehouse.name }} - {{ box.warehouse.address }},
окончен {{ box.end_date }}
Имущество будет храниться не более 6 месяцев с даты окончания срока аренды.
"""

def send_emails():
    current_date = datetime.date.today()

    for box in Box.objects.filter(occupied=True):
        rent_term = (box.end_date - current_date).days

        try:
            if 0 < rent_term <= 30:
                subject = 'Срок аренды подходит к концу!'
                template = Template(BOX_RENT_ENDS_SOON_NOTICE_TEMPLATE)
            elif -180 <= rent_term <= 0:
                subject = 'Срок аренды подошел к концу!'
                template = Template(BOX_RENT_ENDED_NOTICE_TEMPLATE)

            send_mail(
                subject=subject,
                message=template.render(context=Context({"box": box})),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[box.customer.email]
            )
        except:
            continue
        # if 0 < rent_term <= 30:
        #     try:
        #         template = Template(BOX_RENT_ENDS_SOON_NOTICE_TEMPLATE)
        #         send_mail(
        #             subject=subject,
        #             message=template.render(context=Context({"box": box})),
        #             from_email=settings.EMAIL_HOST_USER,
        #             recipient_list=[box.customer.email]
        #         )
        #     except:
        #         continue
        # elif -180 <= rent_term <= 0:
        #     try:
        #         template = Template(BOX_RENT_ENDED_NOTICE_TEMPLATE)
        #         send_mail(
        #             subject=subject,
        #             message=template.render(context=Context({"box": box})),
        #             from_email=settings.EMAIL_HOST_USER,
        #             recipient_list=[box.customer.email]
        #         )
        #     except:
        #         continue


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):

    help = 'Отправляет email по истечении сроков аренды бокса'

    def handle(self, *args, **kwargs):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), 'default')

        scheduler.add_job(
            send_emails,
            # trigger=CronTrigger(day='*/1'),
            trigger=CronTrigger(second="*/10"),
            id="send_emails",
            max_instances=1,
            replace_existing=True
        )

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week='mon', hour='00', minute='00'
            ),
            id='delete_old_job_executions',
            max_instances=1,
            replace_existing=True
        )

        try:
            scheduler.start()
        except KeyboardInterrupt:
            scheduler.shutdown()
