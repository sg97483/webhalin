from pywinauto import application
from pywinauto import keyboard

import Colors
import Util


def web_har_in(target,driver):
    pid = target[0]
    park_id = int(Util.all_trim(target[1]))
    ticket_name = target[3]
    ori_car_num = Util.all_trim(target[2])
    trim_car_num = Util.all_trim(ori_car_num)
    search_id = trim_car_num[-4:]

    print("parkId = " + str(park_id) + ", " + "searchId = " + search_id)
    print(Colors.BLUE + ticket_name + Colors.ENDC)

    app = application.Application(backend="win32").start('AplusAssetEXE/DiscountParking.exe')
    Util.sleep(1)
    login_dialog = app.window(title_re='로그인')
    Util.sleep(2)
    login_dialog.Edit.type_keys('1')
    Util.sleep(2)
    # login_dialog.print_control_identifiers()
    login_dialog.Button2.click()
    Util.sleep(2)

    main_dialog = app.window(title_re='원격할인')
    main_dialog.Edit.type_keys(search_id)
    main_dialog.Button2.click()
    Util.sleep(2)

    listCount = main_dialog.ListView.item_count()
    if(listCount>0):
        for i in range(0,listCount):
            carItem = main_dialog.ListView.texts()[i*3+1]
            print(carItem)
            if (trim_car_num == carItem[-7:]):
                main_dialog.ListView.get_item(i).select()
                Util.sleep(1)
                main_dialog.할인처리.click()
                Util.sleep(1)

                final_dialog = app.window(title_re='할인요청')
                final_dialog.요청.click()
                Util.sleep(1)
                keyboard.send_keys('{ENTER}')
                Util.sleep(1)
                main_dialog.close()

                return True
            else:
                continue
        print("미입차")
        return False
    else:
        return False







