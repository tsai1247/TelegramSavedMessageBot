# TelegramSavedMessageBot
A telegram bot for saved photo and message

## 近期更新
### 2021/10/18
* /conch 指令新增候選詢問語法(題目?選項1:選項2:選項3......)

### 2021/10/12
* 新增備份還原指令 /dump /load


## 環境建置參考
### On termux
| Name | Version |
| -------- | -------- |
| git      | 2.33.0   |
| python   | 3.9.7    |
| tmux     | 3.2a     |

### On conda virtual environment (version 4.10.3)
| Name | Version |
| -------- | -------- |
| git      | 2.32.0   |
| python   | 3.8.8    |

### Python library 
| Name                | Version  |
| ------------------- | -------- |
| pyimgur             | 0.6.0    |
| python-dotnet       | 0.19.0   |
| python-telegram-bot | 13.7     |

## 使用說明
### 寫好.env之後 run TelegramSavedMessageBot.py 就可以了

## .env 說明
### 修改.env.example 的內容，並重新命名為.env
* TELEGRAM_TOKEN：跟bot father建立一個 telegram bot，他會給你這個token
* IMGUR_CLIENT_ID：在imgur新增一個api接口，將imgur client id 填入這裡，不填寫的話就只能存文字訊息
* DEVELOPER_ID：用任何符號分隔的userID，可以為空字串，代表所有人皆可使用管理員指令。
    * 預設的管理員指令有 /add /delete /update
* DATABASENAME='Database.db' 基本上不用改

## 指令說明
* /start：bot的開頭。會回應打招呼的文字。
* /help：說明，會回應Config/helpText的內容。
* /add：新增，步驟為設定名稱→新增照片或文字→輸入 /end 完成新增
* /end：用來結束 /add
* /del：刪除完整名稱對應的訊息與照片
* /list：列出所有已新增的訊息名稱，可以點擊產生的按鈕來顯示文字/照片
* /find：以關鍵字尋找已新增的訊息名稱，可以點擊產生的按鈕來顯示文字/照片
* /update：使用sqlite語法修該database(必為管理員限定)
* /conch：詢問問題，會隨機回覆 Yes、No、Ask again 的回答，可以使用三元運算子格式來給予候選答案
* /dump：可以取得備份訊息
* /load：輸入備份訊息之後可以還原database
* /report：可以輸入回報與建議
* /getreport：可以獲得所有已輸入的回報與建議
* /cancel：取消當前要求的指令

## Database.db/Config 說明
* penalty：Dos defense 使用。過多指令的禁用時間(秒)。
* dos_maximum：Dos defense 使用。超過幾個指令算是過多的數值。
* helpText：/help 指令顯示的內容。
* name：bot的名稱，會放在 /start 的回覆內容中。
* askAgainRange：/conch 指令時的'ask again'回覆頻率(0~0.5)。
* isAddDeleteOpen：將 /Add 跟 /Delete 設為公開(也就是可以讓非管理員使用指令)，0為關閉，1為開啟。
