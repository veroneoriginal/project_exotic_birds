Проект "Экзотические птицы" - небольшой блог, где пользователь может:
1) зарегистрироваться и у него будет свой личный кабинет
2) создать пост и все его посты будут отображаться в личном кабинете
3) задать посту хештеги 
4) редактировать свои посты, удалять их или делать публичными
5) смотреть общую ленту
6) добавлять комментарии к чужим постам 
7) фильтровать посты в общей ленте по хештегам, по пользователям
8) пользователь может выйти из личного кабинета и тогда он не сможет добавлять коменты к чужим постам


Как запустить проект. 
1. Проверяем активно ли виртуальное окружение.
Если нет, то устанавливаем его и активируем.
**python3 -m venv venv**
**source venv/bin/activate**

2. Устанавливаем все пакеты из requirements.txt
**pip install -r requirements.txt**

3. Запускаем базу и gunicorn командой
**docker-compose up**
или
4. Для того, чтобы запустить проект и посмотреть его локально:
**docker compose up -d pg**  - поднимаем базу данных в Docker
**docker compose up gunicorn-backend**

