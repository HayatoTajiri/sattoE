# ライブラリ
from selenium import webdriver
import time
import random
import threading
import tkinter as tk
import requests
import json
import base64
from PIL import Image
from selenium.webdriver.common.alert import Alert

# APIキー
API_KEY = "API_KEY"#Google cloud visionの自身のAPIキーを入れてください

###############################################################################################
###############################################################################################
# イベント関数一覧
###############################################################################################
###############################################################################################

###############################################################################################
# 終了ボタンが押されたら
###############################################################################################
def quit_task(event):
    quit()
###############################################################################################


################################################################################################
#スタートボタンが押されたら
################################################################################################
def start(event):
    ## スレッド処理
    task = threading.Thread(target=answer_questions, args=(event,))
    task.start()
################################################################################################


################################################################################################
# 問題を解く
################################################################################################
def answer_questions(event):

    global start_button
    global var_class
    global var_ver
    global var_task
    global student_number
    global password_number
    global task_number
    global student_id
    global all_acount

    while True:
        try:
            #### クラスの取得
            if var_class.get() == 0:
                TOPPAGE = "https://yaruzo.gyuto-e.jp/iwate-pu/?class=basic"
            elif var_class.get() == 1:
                TOPPAGE = "https://yaruzo.gyuto-e.jp/iwate-pu/?class=intermediate"
            elif var_class.get() == 2:
                TOPPAGE = "https://yaruzo.gyuto-e.jp/iwate-pu/?class=advanced"

            #### ログインページに移動
            driver = webdriver.Chrome("driver/chromedriver" + str(var_ver.get()) + ".exe")
            driver.set_page_load_timeout(1000)
            driver.get(TOPPAGE)
            driver.implicitly_wait(5)

            #### ID/PASSを入力
            id = driver.find_element_by_name("userName")
            id.send_keys(student_number.get())
            password = driver.find_element_by_id("passWord")
            password.send_keys(password_number.get())

            #### ログインボタンをクリック
            login_button = driver.find_element_by_id("loginBtn")
            login_button.click()

            #### レッスンページに移動
            lesson_start = driver.find_element_by_class_name('btn-primary')
            lesson_start.click()

            if var_task.get() == 0:
                reading(int(task_number.get()), driver)
            elif var_task.get() == 1:
                vocabulary(int(task_number.get()), driver)
            elif var_task.get() == 2:
                listening(int(task_number.get()), driver)
            elif var_task.get() == 3:
                grammer(int(task_number.get()), driver)

            close_window(driver)
            break
        except Exception:
            driver.close()
            break
#######################################################################################


#######################################################################################
# ウィンドウを閉じる
#######################################################################################
def close_window(driver):
    ## 終了する
    finish_button = driver.find_element_by_class_name("btn-success")
    finish_button.click()
    ## ホームページに移動
    driver.get("https://yaruzo.gyuto-e.jp/iwate-pu/home")
    ## ログアウトする
    driver.execute_script("jump('logout/')")
    ## ウィンドウを閉じる
    driver.close()
######################################################################################




#######################################################################################
#######################################################################################
# 通常の関数一覧
#######################################################################################
#######################################################################################

#######################################################################################
# 文字入力認証を自動で入力する
#######################################################################################
def check_input_text_in_image(driver):

    ## ファイルパス
    img_path = 'screen.png'

    ## スクリーンショットの保存
    w = driver.execute_script('return document.body.scrollWidth')
    h = driver.execute_script('return document.body.scrollHeight')
    driver.set_window_size(w, h)
    driver.save_screenshot(img_path)

    ## 画像の切り抜き
    im = Image.open(img_path)
    im.crop((15, 165, 415, 565)).save(img_path, quality=95)

    ## 文字認識する
    res_json = text_detection(img_path)
    res_text = res_json["responses"][0]["textAnnotations"][0]["description"]
    print(res_text)
    answer = driver.find_element_by_id("answer")
    answer.send_keys(res_text)

    ## Alert クリック
    time.sleep(1)
    Alert(driver).accept()
    time.sleep(1)
########################################################################################


########################################################################################
# Google Cloud Vision OCRで文字認識する
#######################################################################################
def text_detection(image_path):

    ## API KEY
    api_url = 'https://vision.googleapis.com/v1/images:annotate?key={}'.format(API_KEY)

    with open(image_path, "rb") as img:
        image_content = base64.b64encode(img.read())
        req_body = json.dumps({
            'requests': [{
                'image': {
                    'content': image_content.decode('utf-8')  # base64でエンコードしたものjsonにするためdecodeする
                },
                'features': [{
                    'type': 'TEXT_DETECTION'
                }]
            }]
        })
        res = requests.post(api_url, data=req_body)
        return res.json()
##########################################################################################


##########################################################################################
# グラマーを処理する
##########################################################################################
def grammer(Number, driver):

    global val_optim

    ### グラマーページに移動
    driver.execute_script("jump('webapi/lesson/grammar/start')")

    ##回答を始める
    while True:# do while
        time.sleep(0.25)

        ### 私はロボットではありません
        if driver.page_source.__contains__("写真の単語を正確にタイプできたら先に進めるよ。"):
            check_input_text_in_image(driver)

        retry_counter = '0'
        questions_number = driver.find_element_by_xpath("/html/body/div/div/div[3]/div").text

        ### 再挑戦が表示されているか判定する
        if '再挑戦' in questions_number:
            retry_counter = questions_number[10:]
            questions_number = questions_number[:11]
        questions_number = int(questions_number.strip('"課題 No.問題解答チェック再挑戦回目'))
        retry_counter = int(retry_counter.strip('"課題 No.問題解答チェック再挑戦回目'))

        ### 終了判定
        if questions_number > Number:
            break

        ###選択する
        driver.execute_script("document.getElementsByClassName('k_answer')[" + str(retry_counter % 4) + "].click();")

        ### 高速化する
        time_submit = random.randint(5, 15)
        if val_optim.get() == False:
            time.sleep(time_submit)

        ### 提出する
        submit_button = driver.find_element_by_class_name("btn-danger")
        submit_button.click()
        time.sleep(1)

        ###提出時間を偽造する
        driver.execute_script("lastTime = lastTime - " + str(random.randint(3000, 5000))+";")
        #driver.execute_script("const vue.commentTime = " + str(random.randint(3000, 10000)) + ";")

        ### 次の問題に進む
        next_button = driver.find_element_by_class_name("k_btn_move")
        next_button.click()
        time.sleep(0.25)
##########################################################################################


##########################################################################################
# リスニングを処理する
##########################################################################################
def listening(Number, driver):

    global val_optim

    ## リスニングページに移動
    driver.execute_script("jump('webapi/lesson/listening/start')")

    ##回答を始める
    while True:  # do while
        time.sleep(0.25)

        ### 私はロボットではありません
        if driver.page_source.__contains__("写真の単語を正確にタイプできたら先に進めるよ。"):
            check_input_text_in_image(driver)

        retry_counter = '0'
        questions_number = driver.find_element_by_xpath("/html/body/div/div/div[3]/div").text

        ### 再挑戦が表示されているか判定する
        if '再挑戦' in questions_number:
            retry_counter = questions_number[10:]
            questions_number = questions_number[:11]
        questions_number = int(questions_number.strip('"課題 No.問題解答チェック再挑戦回目'))
        retry_counter = int(retry_counter.strip('"課題 No.問題解答チェック再挑戦回目'))

        ### 終了判定
        if questions_number > Number:
            break

        ###選択する
        ###4つの場合
        if driver.page_source.__contains__('value="3"') == True:
            driver.execute_script("document.getElementsByClassName('k_answer')[" + str(retry_counter % 4) + "].click();")
        ###3つの場合
        else:
            driver.execute_script("document.getElementsByClassName('k_answer')[" + str(retry_counter % 3) + "].click();")

        ### 高速化する
        time_submit = random.randint(10, 25)
        if val_optim.get() == False:
            time.sleep(time_submit)

        ### 提出する
        submit_button = driver.find_element_by_class_name("btn-danger")
        submit_button.click()
        time.sleep(1)

        ###提出時間を偽造する
        driver.execute_script("lastTime = lastTime - " + str(random.randint(3000, 5000))+";")

        ### 次の問題に進む
        next_button = driver.find_element_by_class_name("k_btn_move")
        next_button.click()
        time.sleep(1)
######################################################################################


#######################################################################################
# リーディングを処理する
######################################################################################
def reading(Number, driver):

    global val_optim

    # リーディングページに移動
    driver.execute_script("jump('webapi/lesson/reading/start')")

    ##回答開始
    while True:

        time.sleep(0.25)

        ### 私はロボットではありません
        if driver.page_source.__contains__("写真の単語を正確にタイプできたら先に進めるよ。"):
            check_input_text_in_image(driver)
            time.sleep(1)

        ### 再挑戦が表示されているか判定する
        questions_number = driver.find_element_by_xpath("/html/body/div/div/div[3]/div").text
        if '再挑戦' in questions_number:
            questions_number = questions_number[:11]
        questions_number = int(questions_number.strip('"課題 No.問題解答チェック再挑戦回目'))

        ### 終了判定
        if questions_number > Number:
            break

        ### 回答用リストを用意
        Answer1 = ['F'] * 40
        Answer2 = ['F'] * 40

        ### 区切りを見つける
        Term = questions_number
        if questions_number % 2 == 1:
            Term = Term + 1

        ### 回答する
        for i in range(4):
            #### 終了可能であれば終了する
            questions_number = driver.find_element_by_xpath("/html/body/div/div/div[3]/div").text
            if '再挑戦' in questions_number:
                questions_number = questions_number[:11]
            questions_number = int(questions_number.strip('"課題 No.問題解答チェック再挑戦回目'))
            if questions_number > Term:
                break

            #### 読み始める
            start_button = driver.find_element_by_class_name("btn-warning")
            start_button.click()
            time.sleep(1)

            #### 高速回答
            time_submit = random.randint(240, 360)
            if val_optim.get() == False:
                time.sleep(time_submit)

            #### 読み終わる
            finish_button = driver.find_element_by_class_name("btn-warning")
            finish_button.click()
            time.sleep(1)

            #### 時間を偽造する
            driver.execute_script(
                "vue.readingTime = " + str(time_submit) + ";vue.readingSpeed=Math.round(" + str(200*60/time_submit) + ");")

            #### 問題開始
            start_button = driver.find_element_by_class_name("btn-warning")
            start_button.click()
            time.sleep(1)

            #### 選択1
            #### 問題数を取得する
            Question_number = 0
            for j in range(40):
                Question_number = driver.page_source.__contains__("option_" + str(j + 1))
                if Question_number != True:
                    Question_number = j
                    break

            #### 回答1
            for j in range(Question_number):
                if (Answer1[j] == 'F'):
                    driver.execute_script("document.getElementsByName('option_" + str(j + 1) + "')[" + str(i) + "].click();")
                else:
                    driver.execute_script("document.getElementsByName('option_" + str(j + 1) + "')[" + str(Answer1[j]) + "].click();")

            #### 高速回答
            time_submit = random.randint(100, 180)
            if val_optim.get() == False:
                time.sleep(time_submit)

            #### 採点
            finish_button = driver.find_element_by_class_name("btn-danger")
            finish_button.click()
            time.sleep(1)

            #### Answer1の保存
            for num in range(Question_number):
                if Answer1[num] == 'F':
                    if "k_maru_icon" in driver.find_elements_by_class_name("k_answer_icon")[num*4+i].get_attribute("class"):
                        Answer1[num] = i
                    else:
                        Answer1[num] = 'F'

            #### 次の問題へ
            time.sleep(0.5)
            start_button = driver.find_element_by_class_name("k_btn_move")
            start_button.click()
            time.sleep(1)

    #######################################################################################

            #### 私はロボットではありません
            if driver.page_source.__contains__("写真の単語を正確にタイプできたら先に進めるよ。"):
                check_input_text_in_image(driver)
                time.sleep(1)

            #### 終了可能であれば終了する
            questions_number = driver.find_element_by_xpath("/html/body/div/div/div[3]/div").text
            if '再挑戦' in questions_number:
                questions_number = questions_number[:11]
            questions_number = int(questions_number.strip('"課題 No.問題解答チェック再挑戦回目'))
            if questions_number > Term:
                break

            #### 読み始める
            start_button = driver.find_element_by_class_name("btn-warning")
            start_button.click()
            time.sleep(1)

            #### 高速回答
            time_submit = random.randint(240, 360)
            if val_optim.get() == False:
                time.sleep(time_submit)

            #### 読み終わる
            finish_button = driver.find_element_by_class_name("btn-warning")
            finish_button.click()
            time.sleep(1)

            #### 時間を偽造する
            driver.execute_script(
                "vue.readingTime = " + str(time_submit) + ";vue.readingSpeed=Math.round(" + str(
                    200 * 60 / time_submit) + ");")

            #### 問題開始
            start_button = driver.find_element_by_class_name("btn-warning")
            start_button.click()
            time.sleep(1)

            #### 問題数を取得する
            Question_number = 0
            for j in range(40):
                Question_number = driver.page_source.__contains__("option_" + str(j + 1))
                if Question_number != True:
                    Question_number = j
                    break

            #### 回答2
            for j in range(Question_number):
                if (Answer2[j] == 'F'):
                    driver.execute_script("document.getElementsByName('option_" + str(j + 1) + "')[" + str(i) + "].click();")
                else:
                    driver.execute_script("document.getElementsByName('option_" + str(j + 1) + "')[" + str(Answer2[j]) + "].click();")

            #### 高速回答
            time_submit = random.randint(100, 180)
            if val_optim.get() == False:
                time.sleep(time_submit)

            #### 採点
            finish_button = driver.find_element_by_class_name("btn-danger")
            finish_button.click()
            time.sleep(1)

            #### Answer2の保存
            for num in range(Question_number):
                if Answer2[num] == 'F':
                    if "k_maru_icon" in driver.find_elements_by_class_name("k_answer_icon")[num*4+i].get_attribute("class"):
                        Answer2[num] = i
                    else:
                        Answer2[num] = 'F'

            #### 次の問題へ
            time.sleep(0.5)
            start_button = driver.find_element_by_class_name("k_btn_move")
            start_button.click()
            time.sleep(1)

###########################################################################################


###########################################################################################
# ボキャブラリを処理する
###########################################################################################
def vocabulary(Number, driver):

    global val_optim

    ## ボキャブラリページに移動
    driver.execute_script("jump('webapi/lesson/vocabulary/start')")

    while True:
        time.sleep(0.25)

        ### 私はロボットではありません
        if driver.page_source.__contains__("写真の単語を正確にタイプできたら先に進めるよ。"):
            check_input_text_in_image(driver)

        ###課題NOを取得
        questions_number = driver.find_element_by_xpath("/html/body/div/div/div[3]/div").text
        questions_number = int(questions_number.strip('"課題 No.問題解答チェック再挑戦回目'))

        ### 終了判定
        if questions_number > Number:
            break

        ### 問題数を取得する
        for i in range(40):
            Question_number = driver.page_source.__contains__("["+str(i).zfill(2)+"]")
            if Question_number != True:
                Question_number = i
                break

        ### 英語を格納する
        Word = [0] * Question_number
        for i in range(Question_number):
            Word[i] = driver.find_element_by_xpath(
                "/html/body/div/div[2]/form/div[2]/table/tbody/tr["+str(i + 2)+"]/td[3]").text

        ### 日本語を格納する
        Japanese = [0] * Question_number
        for i in range(Question_number):
            Japanese[i] = driver.find_element_by_xpath(
                "/html/body/div/div[2]/form/div[2]/table/tbody/tr["+str(i + 2)+"]/td[4]/span").text

        ### 音声を格納する
        Sound = [0] * Question_number
        for i in range(Question_number):
            Sound[i] = driver.find_element_by_id("playBtn-" + str(i)).get_attribute("id")

        ### 取得した単語の表示
        #print(Word)
        #print(Japanese)
        #print(Sound)

        ### テストを開始する
        start_button = driver.find_element_by_class_name("k_btn_move")
        start_button.click()

        ### 単語を見つける
        for i in range(Question_number):
            #### 単語(英語)を検索する
            for j in range(Question_number):
                #### j番目に格納した単語を見つけたとき
                if driver.find_element_by_xpath(
                        "/html/body/div/div[2]/form/div[2]/table/tbody/tr["+str(i+2)+"]/td[3]").text == Word[j]:
                    ##### 回答を検索する
                    for k in range(Question_number):
                        ###### k番目に格納した単語が回答だった時
                        if driver.find_element_by_xpath(
                        "/html/body/div/div[2]/form/div[2]/table/tbody/tr[2]/td[6]/div["+str(k+1)+"]/input").get_attribute("value") == Japanese[j]:
                            ####### クリックする
                            driver.execute_script("document.getElementsByClassName('k_choice_area')[" + str(k) + "].click();")
                            break
                    break

        ### 高速回答
        time_submit = random.randint(30, 120)
        if val_optim.get() == False:
            time.sleep(time_submit)

        ### 英単語→日本語の採点する
        driver.execute_script(
            "if( submitDone ) return;document.getElementsByName('FORWARD')[0].value = 'COMMENT_E_J';submitDone = true;document.getElementsByName('duration')[0].value = " + str(
               time_submit) + ";document.forms[0].submit();")
        ### 次の問題に進む
        driver.execute_script("mySubmit('QUIZ_S_J')")

        ### 単語を見つける
        for i in range(Question_number):
            #### 単語(音声)を検索する
            for j in range(Question_number):
                ##### j番目に格納した単語を見つけたとき
                Sound_question = driver.find_element_by_id("playBtn-" + str(i)).get_attribute("onclick")
                if Sound_question.rstrip("radioButtonCheck( " + str(i) + " );") in Sound[j]:
                    ###### 回答を検索する
                    for k in range(Question_number):
                        ####### k番目に格納した単語が回答だった時
                        if driver.find_element_by_id("japaneses-" + str(k)).get_attribute("value") == Japanese[j]:
                            ######## クリックする
                            driver.execute_script("japaneseClick(" + str(k) + ");playBtnFocus();")
                            break
                    break

        ### 高速回答
        time_submit = random.randint(40, 180)
        if val_optim.get() == False:
            time.sleep(time_submit)
        ### 音声→日本語の採点する
        driver.execute_script(
            "if( submitDone ) return;document.getElementsByName('FORWARD')[0].value = 'COMMENT_S_J';submitDone = true;document.getElementsByName('duration')[0].value = " + str(
                time_submit) + ";document.forms[0].submit();")
        ### 次の問題に進む
        driver.execute_script("mySubmit('QUIZ_J_E')")

        ### 単語を見つける
        for i in range(Question_number):
            #### 単語(日本語)を検索する
            for j in range(Question_number):
                ##### j番目に格納した単語を見つけたとき
                if driver.find_element_by_xpath(
                        "/html/body/form/table/tbody/tr[2]/td[2]/div/table/tbody/tr[" + str(i + 2) + "]/td[3]").text == \
                        Japanese[j]:
                    ###### 回答を入力する
                    driver.find_element_by_id("userAnswer-" + str(i)).send_keys(Word[j])
                    break

        ### 高速回答
        time_submit = random.randint(60, 120)
        if val_optim.get() == False:
            time.sleep(time_submit)

        ### 日本語→英語語の採点する
        driver.execute_script(
            "if( submitDone ) return;document.getElementsByName('FORWARD')[0].value = 'COMMENT_J_E';submitDone = true;document.getElementsByName('duration')[0].value = " + str(
                time_submit) + ";document.forms[0].submit();")
        ### レポート確認へ
        driver.execute_script("mySubmit('REPORT')")
        if int(driver.find_element_by_xpath("/html/body/div[2]/table/tbody/tr/td").text.strip('課題 No.　練習（英 -> 日）音テストレポート')) != Number:
            driver.execute_script("mySubmitReport('START')")
        else:
            driver.execute_script("mySubmitReport('LESSON_MENU')")
            break
#######################################################################################################




#######################################################################################################
# GUIウィンドウを作成#
#######################################################################################################
window = tk.Tk()
window.title("さっとe  -ぎゅ〇とeを自動で終わらせるソフトfor某東北の大学用-")
window.geometry("1100x200")
# ラベル
label1 = tk.Label(text=u'クラスを選択してください。')
label1.place(x=60, y=10)

label2 = tk.Label(text=u'課題を選んでください。')
label2.place(x=210, y=10)

label3 = tk.Label(text=u'課題を何番まで終了させるか入力してください。')
label3.place(x=360, y=10)

label4 = tk.Label(text=u'課題番号(半角数字)')
label4.place(x=360, y=40)

label6 = tk.Label(text=u'学籍番号とパスワードを入力してください。')
label6.place(x=660, y=10)

label7 = tk.Label(text=u'学籍番号(半角数字)')
label7.place(x=660, y=40)

label8 = tk.Label(text=u'パスワード(半角数字)')
label8.place(x=660, y=70)

label9 = tk.Label(text=u'Google Chorome バージョン')
label9.place(x=900, y=10)

label10 = tk.Label(text=u'※不適切学習になる可能性があります。')
label10.place(x=460, y=70)
#####################################################################################


#####################################################################################
# ラジオボタン作成
#####################################################################################
# クラス選択ボタン
var_class = tk.IntVar()
var_class.set(1)

rd_class1 = tk.Radiobutton(window, value=0, variable=var_class, text='Basic')
rd_class1.place(x=70, y=40)

rd_class2 = tk.Radiobutton(window, value=1, variable=var_class, text='Intermediate')
rd_class2.place(x=70, y=70)

rd_class3 = tk.Radiobutton(window, value=2, variable=var_class, text='Advanced')
rd_class3.place(x=70, y=100)

# 課題選択ボタン
var_task = tk.IntVar()
var_task.set(3)

rd_task1 = tk.Radiobutton(window, value=0, variable=var_task, text='リーディング')
rd_task1.place(x=220, y=40)

rd_task2 = tk.Radiobutton(window, value=1, variable=var_task, text='ボキャブラリ')
rd_task2.place(x=220, y=70)

rd_task3 = tk.Radiobutton(window, value=2, variable=var_task, text='リスニング')
rd_task3.place(x=220, y=100)

rd_task4 = tk.Radiobutton(window, value=3, variable=var_task, text='グラマー')
rd_task4.place(x=220, y=130)

# グーグルクロームバージョン選択

var_ver = tk.IntVar()
var_ver.set(8)

rd_ver1 = tk.Radiobutton(window, value=3, variable=var_ver, text='76.x')
rd_ver1.place(x=920, y=40)

rd_ver2 = tk.Radiobutton(window, value=4, variable=var_ver, text='77.x')
rd_ver2.place(x=920, y=60)

rd_ver3 = tk.Radiobutton(window, value=5, variable=var_ver, text='78.x')
rd_ver3.place(x=920, y=80)

rd_ver4 = tk.Radiobutton(window, value=6, variable=var_ver, text='79.x')
rd_ver4.place(x=920, y=100)

rd_ver5 = tk.Radiobutton(window, value=7, variable=var_ver, text='80.x')
rd_ver5.place(x=920, y=120)

rd_ver6 = tk.Radiobutton(window, value=8, variable=var_ver, text='81.x(デフォルト)')
rd_ver6.place(x=920, y=140)

rd_ver7 = tk.Radiobutton(window, value=9, variable=var_ver, text='83.x')
rd_ver7.place(x=920, y=160)
################################################################################


#################################################################################
# チェックボックス作成
#################################################################################
# 高速回答するかしないか
val_optim = tk.BooleanVar()
val_optim.set(False)
optimize_check = tk.Checkbutton(text=u"高速回答する",variable = val_optim)
optimize_check.place(x=360, y=68)
#################################################################################


##################################################################################
# エントリーボックス作成
##################################################################################
## 学籍番号入力
student_number = tk.Entry(width=12)
student_number.place(x=770, y=40)

## パスワード入力
password_number = tk.Entry(width=6)
password_number.place(x=770, y=70)

## 課題番号入力
task_number = tk.Entry(width=5)
task_number.place(x=470, y=40)
###################################################################################


###################################################################################
# ボタン
###################################################################################
# スタート
start_flag = 0
start_button = tk.Button(text=u'スタート')
start_button.bind("<Button-1>", start)
start_button.place(x=570, y=150)

# 終了
quit_button = tk.Button(text=u'終了')
quit_button.bind("<Button-1>", quit_task)
quit_button.place(x=670, y=150)

window.mainloop()
####################################################################################