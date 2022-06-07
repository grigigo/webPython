array = '~!?@#$%^&*_-+()[]{}></\\|"\'.,:;'


def login_test(text):
    error = ''
    if text:
        if len(text) >= 5:
            for elem in text:
                if not elem.isdigit():
                    if not (65 <= ord(elem) <= 90 or 97 <= ord(elem) <= 122):
                        error = 'Разрешены только цифры и латинские буквы!'
        else:
            error = 'Минимальное кол-во символов - 5!'
        if error:
            return error
        else:
            return False
    else:
        error = 'Поле не может быть пустым!'
        return error


def pass_test(text):
    is_up = False
    is_do = False
    is_dig = False
    is_sym = False
    error = []
    if text:
        if 8 <= len(text) <= 128:
            for elem in text:
                if elem.isdigit():
                    is_dig = True
                else:
                    if 65 <= ord(elem) <= 90 or 1040 <= ord(elem) <= 1071:
                        is_up = True
                    elif 97 <= ord(elem) <= 122 or 1072 <= ord(elem) <= 1103:
                        is_do = True
                    elif elem not in array:
                        if not is_sym:
                            error.append('Введены неверные символы!')
                            is_sym = True
            if not is_up:
                error.append('Необходима минимум одна заглавная буква!')
            if not is_do:
                error.append('Необходима минимум одна строчная буква!')
            if not is_dig:
                error.append('Необходима минимум одна цифра!')
        else:
            error.append('Минимальное кол-во символов - 8!')
        if error:
            return error
        else:
            return False
    else:
        error.append('Поле не может быть пустым!')
        return error
