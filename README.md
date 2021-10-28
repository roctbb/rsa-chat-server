# rsa-chat-server

### Что это?

Это учебный socket-сервер для обмена текстовыми сообщениями с использованием end-to-end шифрования.

### Шифрование

Используется как шифрование данных между сервером и клиентом, так и шифрованием сообщений, передаваемых клиентами через сервер. Сообщения клиентов сохраняются в базе данных, но ключ расшифровки известен только получателю.

Подразумевается использование "чистого RSA" (без отступов) c 1024 битным ключом.

### Настройка, генерация ключей, запуск

Для работы необходимо переименовать файл **config.py.example** в папке `server` и указать ключи и данные для БД, хост и порт.

**Для генерации ключей:**

```
python3 ./utils/generate-keys.py
```

**Создание таблиц:**

```
cd server
flask db init
flask db migrate
flask db upgrade
cd ..
```

**Запуск:**

```
pip3 install requirements.txt
python3 ./server/rsa-server.py
```

### Протокол

Сервер работает в пасивном режиме, отвечает на запросы клиентов.

* Для отправки незашифрованных сообщений (обмен ключами) сначала передаются 4 байта, содержащие размер данных, а затем сами данные.
* Для отправки зашифрованных сообщений, состоящих из нескольких блоков, сначала передаются 4 байта, содержащие количество блоков, а затем сами блоки, каждый из которых описывается 4мя байтами размера, а затем содержимым блока.

**Последовательность действий:**

- обмен ключами;
- регистрация (при первом подключении);
- отправка команд на получение списка пользователей / отправку / получение сообщений.

### Команды

#### 1. Регистрация

```
{
    "cmd": "register",
    "login": "LOGIN"
}
```

**Ответ:**

```
{
    "state": "ok",
    "data": "welcome"
}
```

**Ошибки:**

```
{
    "state": "error",
    "error": "login exists"
}
```

```
{
    "state": "error",
    "error": "already registered",
    "login": LOGIN
}
```

#### 2. Получение списка пользователей

```
{
    "cmd": "get_users"
}
```

**Ответ:**

```
{
   "state":"ok",
   "data":[
      {
         "login":"roctbb",
         "open_exponent": e,
         "module": N
      }, ...
   ]
}
```

#### 2. Получение сообщений в чате с пользователем

```
{
   "cmd":"get_messages",
   "user":"roctbb"
}
```

**Ответ:**

```
{
   "state":"ok",
   "data":[
      {
         "user":"test",
         "created_at":"2021-10-28T19:37:38.463670",
         "content":"[\"jzsXP9xPkxo0XXVufP95a/2jDNaLNFbQU/RvaQTzNUf5BxideVDJIcIghLzWZhfpGkLxRvTEe0DJ3ho3783sXslm7Llv1avGqYLb+2b9tk6fGZRtdVdxLZJWx4RM6fAFwJpm6HEnKe0tEaUEI0d/E1tog5lv1bZLuCGSXljcoDdvFboEYiWeto8KLx7XKUok2SDDBpERZPk2E/UWovskY/DBlU5uoPlLH396VMYFezMOHtz0WTFq26C+YA0NsVBpwt/M2d51nFWqfuzv8tlZc7vRknCXwX/Cs9pOtKcsKpN5YMymBdh+bAJC5++D0LSXXQvrGyzQIFMsiVpt4jiihg==\"]"
      },
      {
         "user":"test",
         "created_at":"2021-10-28T19:37:42.934702",
         "content":"[\"jzsXP9xPkxo0XXVufP95a/2jDNaLNFbQU/RvaQTzNUf5BxideVDJIcIghLzWZhfpGkLxRvTEe0DJ3ho3783sXslm7Llv1avGqYLb+2b9tk6fGZRtdVdxLZJWx4RM6fAFwJpm6HEnKe0tEaUEI0d/E1tog5lv1bZLuCGSXljcoDdvFboEYiWeto8KLx7XKUok2SDDBpERZPk2E/UWovskY/DBlU5uoPlLH396VMYFezMOHtz0WTFq26C+YA0NsVBpwt/M2d51nFWqfuzv8tlZc7vRknCXwX/Cs9pOtKcsKpN5YMymBdh+bAJC5++D0LSXXQvrGyzQIFMsiVpt4jiihg==\"]"
      }
   ]
}
```

Поле `content` содержит JSON строку, которая в свою очередь кодирует список из base64 строк. Каждая из этих строк кодирует блок данных, зашифрованных публичным ключем пользователя. Их потребуется расшифровать с помощью закрытого ключа и склеить.

#### 3. Отправка сообщения

```
{
   "cmd":"send_message",
   "user":"roctbb",
   "content":"[\"RbOjsi66DlH/fIhTy42tzHOHJA1u7w0mNs3mjbF0vRA/T/p5E/XimalRi5KykH/Vx1mr5kOoif+rnAT8y0ejcdPerwexlJYc/GlT4DfbqCPLB2U83Wxnc73GA/YX76OfRYD6wCmSWuZSjIs8ihp6usMHVg5BtkY1u7Z9zmXcVUkvUhf+A00lsgq4cTMikBaZ6tet4T19zYYMDZKOWJ2Dc9qx6kjMx/R2YwtzLN7bof/ipENLyr8vqV12BtksaNHjdGENexKQp3f7LbqRXI0VP7NFYobCSpvBHtS1nF5OiQaSija1ay6JjMrGTCsPxNwtfl42vyJSGAwJ7SLMx52LDg==\"]"
}
```

Поле `content` содержит JSON строку, которая в свою очередь кодирует список из base64 строк. Каждая из этих строк кодирует блок данных, зашифрованных публичным ключем получателя.

Отправленное таким образом сообщение не может быть расшифровано отправителем, т.к. ключ для дешифровки неизвестен, поэтому в списке сообщений оно возвращено не будет. Чтобы сохранить в истории копию для себя, можно отправить второй запрос.

```
{
   "cmd":"send_message",
   "user":"roctbb",
   "content":"[\"jzsXP9xPkxo0XXVufP95a/2jDNaLNFbQU/RvaQTzNUf5BxideVDJIcIghLzWZhfpGkLxRvTEe0DJ3ho3783sXslm7Llv1avGqYLb+2b9tk6fGZRtdVdxLZJWx4RM6fAFwJpm6HEnKe0tEaUEI0d/E1tog5lv1bZLuCGSXljcoDdvFboEYiWeto8KLx7XKUok2SDDBpERZPk2E/UWovskY/DBlU5uoPlLH396VMYFezMOHtz0WTFq26C+YA0NsVBpwt/M2d51nFWqfuzv8tlZc7vRknCXwX/Cs9pOtKcsKpN5YMymBdh+bAJC5++D0LSXXQvrGyzQIFMsiVpt4jiihg==\"]",
   "self_copy":true
}
```

Здесь данные зашифрованы открытым ключем отправителя и могут быть расшифрованы, поэтому будут отражены в списке сообщений.

**В обоих случаях ответ:**

```
{
   "state":"ok",
   "data":"sent"
}
```

### Пример взаимодействия с сервером

https://github.com/roctbb/rsa-chat-server/tree/master/example_client




