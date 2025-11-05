import prompt

def show_help():
    """
    Функция отображения справочной информации
    """
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")
    

def welcome():
    print('Первая попытка запустить проект!\n')
    print('*' * 3)
    print('<command> exit - выйти из программы')
    print('<command> help - справочная информация')
    while True:
        command = prompt.string('Введите команду: ')
        if command == 'help':
            show_help()
        if command == 'exit':
            break



