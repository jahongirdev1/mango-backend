from bson import ObjectId
from pymongo import ReturnDocument

from core.datetimes import DatetimeUtils
from core.db import mongo, db
from core.firebase import Firebase
from core.handlers import BaseAPIView
from utils.strs import StrUtils


class OrderView(BaseAPIView):
    STATUS_TEXT = {
        'CREATED': {
            'title': 'Заказ создан',
            'body': 'Мы приняли ваш заказ и скоро начнём готовить к отправке.'
        },
        'CANCELED': {
            'title': 'Заказ отменён',
            'body': 'К сожалению, ваш заказ был отменён. Если это ошибка, свяжитесь с нами.'
        },
        'IN_PROGRESS': {
            'title': 'Заказ в обработке',
            'body': 'Мы готовим ваш заказ к отправке.'
        },
        'ON_ROAD': {
            'title': 'Заказ в пути',
            'body': 'Курьер уже в дороге. Скоро доставим!'
        },
        'READY': {
            'title': 'Заказ готов',
            'body': 'Ваш заказ готов и ждёт вас! Приезжайте забирать.'
        },
        'FINISH': {
            'title': 'Заказ доставлен',
            'body': 'Спасибо, что выбрали нас! Приятного аппетита.'
        }
    }

    async def get(self, request, user, order_id):
        order_id = StrUtils.to_str(order_id)
        if not order_id or not ObjectId.is_valid(order_id):
            return self.error(message='Отсуствует обязательный параметры "Номер заказа"')

        item = await mongo.orders.find_one({
            '_id': ObjectId(order_id)
        })

        return self.success(request=request, user=user, data={
            'order': item
        })

    async def post(self, request, user, order_id):
        order_id = StrUtils.to_str(order_id)
        if not order_id or not ObjectId.is_valid(order_id):
            return self.error(message='Отсуствует обязательный параметры "Номер заказа"')

        action = StrUtils.to_str(request.json.get('action'))
        if action == 'change_status':
            status = StrUtils.to_str(request.json.get('status'))
            if not status:
                return self.error(message='Отсуствует обязательный параметры "Статус"')

            order = await mongo.orders.find_one_and_update({'_id': ObjectId(order_id)}, {'$set': {
                'status': status,
                'temporary_text': None
            }}, return_document=ReturnDocument.AFTER)

            if not order:
                return self.error(message='Операция не выполнена')

            token = await db.fetchval(
                '''
                SELECT firebase_token
                FROM control.clients
                WHERE id = $1
                ''',
                order['client_id']
            )

            if token:
                Firebase.send_message(
                    token=token,
                    notification=status in self.STATUS_TEXT and self.STATUS_TEXT[status] or None,
                    data={
                        'action': 'change_status',
                        'order_id': order_id,
                    })

            return self.success()

        if action == 'change_delivery_time':
            delivery_time = DatetimeUtils.to_datetime(request.json.get('delivery_time'))
            if not delivery_time:
                return self.error(message='Отсуствует обязательный параметры "delivery_time"')

            await mongo.orders.update_one({'_id': ObjectId(order_id)}, {'$set': {
                'delivery_time': delivery_time,
            }})
            return self.success()

        if action == 'change_temporary_text':
            temporary_text = DatetimeUtils.to_datetime(request.json.get('temporary_text'))
            if not temporary_text:
                return self.error(message='Отсуствует обязательный параметры "temporary_text"')

            await mongo.orders.update_one({'_id': ObjectId(order_id)}, {'$set': {
                'temporary_text': temporary_text,
            }})
            return self.success()

        return self.error(message='Операция не выполнена')
