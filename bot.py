from vk_api.longpoll import VkLongPoll, VkEventType
import datetime
import vk_api
from config import user_token, group_token
from random import randrange
from pprint import pprint
from db import *


class Bot:
    def __init__(self):
        print('Бот создан')
        self.vk_user = vk_api.VkApi(
            token=user_token)  # Создаем переменную сессии, авторизованную личным токеном пользователя.
        self.vk_user_got_api = self.vk_user.get_api()  # # переменную сессии vk_user подключаем к api списку методов.
        self.vk_group = vk_api.VkApi(token=group_token)  # Создаем переменную сесии, авторизованную токеном сообщества.
        self.vk_group_got_api = self.vk_group.get_api()  # переменную сессии vk_group подключаем к api списку методов.
        self.longpoll = VkLongPoll(
            self.vk_group)  # переменную сессии vk_group_got_api подключаем к Long Poll API,
        # позволяет работать с событиями из вашего сообщества в реальном времени.

    def send_msg(self, user_id, message):
        """method for sending messages"""
        self.vk_group_got_api.messages.send(
            user_id=user_id,
            message=message,
            random_id=randrange(10 ** 7)
        )

    def name(self, user_id):
        """getting the name of the user who written to the bot"""
        user_info = self.vk_group_got_api.users.get(user_id=user_id)
        if user_info:
            try:
                name = user_info[0]['first_name']
                return name
            except KeyError:
                self.send_msg(user_id, "Ошибка")

    def naming_of_years(self, years, till=True):
        """addition to years"""
        if till is True:
            name_years = [1, 21, 31, 41, 51, 61, 71, 81, 91, 101]
            if years in name_years:
                return f'{years} года'
            else:
                return f'{years} лет'
        else:
            name_years = [2, 3, 4, 22, 23, 24, 32, 33, 34, 42, 43, 44, 52, 53, 54, 62, 63, 64]
            if years == 1 or years == 21 or years == 31 or years == 41 or years == 51 or years == 61:
                return f'{years} год'
            elif years in name_years:
                return f'{years} года'
            else:
                return f'{years} лет'

    def input_looking_age(self, user_id, age):
        a = age.split("-")
        try:
            age_from = int(a[0])
            age_to = int(a[1])
            if age_from == age_to:
                self.send_msg(user_id, f' Ищем возраст {self.naming_of_years(age_to, False)}')
                return age_from, age_to
            self.send_msg(user_id, f' Ищем возраст в пределах от {age_from} и до {self.naming_of_years(age_to, True)}')
            return age_from, age_to
        except IndexError:
            age_to = int(age)
            self.send_msg(user_id, f' Ищем возраст {self.naming_of_years(age_to, False)}')
            return age_to, age_to
        except (NameError, ValueError):
            self.send_msg(user_id, f' Ошибка! Введен не правильный числовой формат! Game over!')
            return None, None

    def get_years_of_person(self, bdate: str) -> object:
        """determining the number of years"""
        bdate_splited = bdate.split(".")
        month = ""
        try:
            reverse_bdate = datetime.date(int(bdate_splited[2]), int(bdate_splited[1]), int(bdate_splited[0]))
            today = datetime.date.today()
            years = (today.year - reverse_bdate.year)
            if reverse_bdate.month >= today.month and reverse_bdate.day > today.day or reverse_bdate.month > today.month:
                years -= 1
            return self.naming_of_years(years, False)
        except IndexError:
            if bdate_splited[1] == "1":
                month = "января"
            elif bdate_splited[1] == "2":
                month = "февраля"
            elif bdate_splited[1] == "3":
                month = "марта"
            elif bdate_splited[1] == "4":
                month = "апреля"
            elif bdate_splited[1] == "5":
                month = "мая"
            elif bdate_splited[1] == "6":
                month = "июня"
            elif bdate_splited[1] == "7":
                month = "июля"
            elif bdate_splited[1] == "8":
                month = "августа"
            elif bdate_splited[1] == "9":
                month = "сентября"
            elif bdate_splited[1] == "10":
                month = "октября"
            elif bdate_splited[1] == "11":
                month = "ноября"
            elif bdate_splited[1] == "12":
                month = "декабря"
            return f'День рождения {int(bdate_splited[0])} {month}.'

    def get_age_of_user(self, user_id):
        """determine the user's age"""
        try:
            info = self.vk_user_got_api.users.get(
                user_ids=user_id,
                fields="bdate",
            )[0]['bdate']
            num_age = self.get_years_of_person(info).split()[0]
            age_from = num_age
            age_to = num_age
            if num_age == "День":
                print(f'Ваш {self.get_years_of_person(info)}')
                self.send_msg(user_id,
                              f'   Бот ищет людей вашего возраста, но в ваших настройках профиля установлен пункт "Показывать только месяц и день рождения"! \n'
                              f'   Поэтому, введите возраст поиска, на пример от 21 года и до 35 лет, в формате : 21-35 (или 21 конкретный возраст 21 год).'
                              )
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        age = event.text
                        age_from, age_to = self.input_looking_age(user_id, age)
                        if age_from is not None and age_to is not None:
                            break
            return age_from, age_to
        except KeyError:
            print(f'День рождения скрыт настройками приватности!')
            self.send_msg(user_id,
                          f' Бот ищет людей вашего возраста, но в ваших в настройках профиля установлен пункт "Не показывать дату рождения". '
                          f'\n Поэтому, введите возраст поиска, на пример от 21 года и до 35 лет, в формате : 21-35 (или 21 конкретный возраст 21 год).'
                          )
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    age = event.text
                    age_from, age_to = self.input_looking_age(user_id, age)
                    if age_from is not None and age_to is not None:
                        break
            return age_from, age_to

    def get_target_city(self, user_id):
        """define city to search"""
        self.send_msg(user_id,
                      f' Введите "Да" - поиск будет произведен в городе указанный в профиле.'
                      f' Или введите название города, например: Москва'
                      )
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                answer = event.text.lower()
                if answer == "да" or answer == "y":
                    info = self.vk_user_got_api.users.get(
                        user_id=user_id,
                        fields="city"
                    )
                    city_id = info[0]['city']["id"]
                    city_title = info[0]['city']["title"]
                    return city_id, city_title
                else:
                    cities = self.vk_user_got_api.database.getCities(
                        country_id=1,
                        q=answer.capitalize(),
                        need_all=1,
                        count=1000
                    )['items']
                    for i in cities:
                        if i["title"] == answer.capitalize():
                            city_id = i["id"]
                            city_title = answer.capitalize()
                            return city_id, city_title

    def looking_for_gender(self, user_id):
        """looking for the opposite gender to the user"""
        info = self.vk_user_got_api.users.get(
            user_id=user_id,
            fields="sex"
        )
        if info:
            if info[0]['sex'] == 1:  # 1 — женщина, 2 — мужчина,
                print(f'Ваш пол женский, ищем мужчину.')
                return 2
            elif info[0]['sex'] == 2:
                print(f'Ваш пол мужской, ищем женщину.')
                return 1
        print("ERROR!!!")
        return None

    def looking_for_persons(self, user_id):
        """Search for a person based on the data received."""
        global list_found_persons
        list_found_persons = []
        age_from, age_to = self.get_age_of_user(user_id)
        if age_from is not None and age_to is not None:
            city_id, city_title = self.get_target_city(user_id)
            if city_id is not None and city_title is not None:
                gender = self.looking_for_gender(user_id)
                if gender is not None:
                    offset = 0
                    while True:
                        res = self.vk_user_got_api.users.search(
                            sort=0,
                            city=city_id,
                            hometown=city_title,
                            sex=gender,
                            status=1,
                            age_from=age_from,
                            age_to=age_to,
                            has_photo=1,
                            count=100,
                            fields="can_write_private_message,city,domain,home_town",
                            offset=offset
                        )
                        if not res["items"]:
                            break

                        for person in res["items"]:
                            if not person["is_closed"]:
                                if "city" in person and person["city"]["id"] == city_id and person["city"]["title"] == city_title:
                                    list_found_persons.append(person["id"])

                        offset += 100

                    print(f'Bot found {len(list_found_persons)} opened profiles for viewing from {res["count"]}')

    def photo_of_found_person(self, user_id):
        """getting a photo of a found person"""
        res = self.vk_user_got_api.photos.get(
            owner_id=user_id,
            album_id="profile",  # wall — фотографии со стены, profile — фотографии профиля.
            extended=1,  # 1 — будут возвращены дополнительные поля likes, comments, tags, can_comment, reposts. По
            # умолчанию: 0.
            count=30
        )
        dict_photos = dict()
        for i in res['items']:
            photo_id = str(i["id"])
            i_likes = i["likes"]
            # i_comments = i["comments"]
            if i_likes["count"]:
                likes = i_likes["count"]
                dict_photos[likes] = photo_id
        list_of_ids = sorted(dict_photos.items(), reverse=True)
        attachments = []
        photo_ids = []
        for i in list_of_ids:
            photo_ids.append(i[1])
        try:
            attachments.append('photo{}_{}'.format(user_id, photo_ids[0]))
            attachments.append('photo{}_{}'.format(user_id, photo_ids[1]))
            attachments.append('photo{}_{}'.format(user_id, photo_ids[2]))
            return attachments
        except IndexError:
            try:
                attachments.append('photo{}_{}'.format(user_id, photo_ids[0]))
                return attachments
            except IndexError:
                return print(f'Нет фото')

    def get_found_person_id(self):
        global list_found_persons
        seen_person = []
        for i in check():  # Выбираем из БД просмотренные анкеты.
            seen_person.append(int(i[0]))
        if not seen_person:
            if not list_found_persons:
                self.looking_for_persons(user_id)
            try:
                unique_person_id = list_found_persons[0]
                return unique_person_id
            except IndexError:
                return None
        else:
            try:
                for ifp in list_found_persons:
                    if ifp in seen_person:
                        pass
                    else:
                        unique_person_id = ifp
                        return unique_person_id
            except NameError:
                return None

    def get_user_info(self, user_id, fields):
        """Getting user info using the 'users.get' method with specified fields."""
        user_info = self.vk_group_got_api.users.get(
            user_id=user_id,
            fields=fields
        )
        return user_info[0]

    def found_person_info(self, show_person_id):
        """Information about the found person."""
        fields_to_get = "about,activities,bdate,status,can_write_private_message,city,common_count," \
                        "contacts,domain,home_town,interests,movies,music,occupation"
        person_info = self.get_user_info(show_person_id, fields_to_get)

        first_name = person_info["first_name"]
        last_name = person_info["last_name"]
        age = self.get_years_of_person(person_info.get("bdate", ""))
        vk_link = 'vk.com/' + person_info["domain"]
        city = ''

        try:
            if "city" in person_info and person_info["city"]["title"] is not None:
                city = f'Город {person_info["city"]["title"]}'
            else:
                city = f'Город {person_info["home_town"]}'
        except KeyError:
            pass

        print(f'{first_name} {last_name}, {age}, {city}. {vk_link}')
        return f'{first_name} {last_name}, {age}, {city}. {vk_link}'

    def send_photo(self, user_id, message, attachments):
        """method for sending photos"""
        try:
            self.vk_group_got_api.messages.send(
                user_id=user_id,
                message=message,
                random_id=randrange(10 ** 7),
                attachment=",".join(attachments)
            )
        except TypeError:
            pass

    def show_found_person(self, user_id):
        """Show person from database."""
        if len(list_found_persons) == 0:
            self.send_msg(user_id,
                          f'Все анкеты ранее были просмотрены. Будет выполнен новый поиск. '
                          f'Измените критерии поиска (возраст, город). '
                          f'Введите возраст поиска, например, от 21 года до 35 лет, '
                          f'в формате: 21-35 (или 21, если нужен конкретный возраст).'
                          )
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    age = event.text
                    age_from, age_to = self.input_looking_age(user_id, age)
                    if age_from is not None and age_to is not None:
                        city_id, city_title = self.get_target_city(user_id)
                        if city_id is not None and city_title is not None:
                            gender = self.looking_for_gender(user_id)
                            if gender is not None:
                                self.looking_for_persons(user_id)
                                break
        else:
            show_person_id = list_found_persons.pop(0)
            self.send_msg(user_id, self.found_person_info(show_person_id))
            self.send_photo(user_id, 'Фото с максимальными лайками', self.photo_of_found_person(show_person_id))
            insert_data_seen_person(show_person_id)


bot = Bot()
