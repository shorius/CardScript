# -*- coding: utf-8 -*-
import json
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from random import shuffle
import itertools
import pyperclip
from collections import Counter
import TestScriptUpload


def get_hostconfig():
    dir = os.getcwd()
    with open(os.path.join(dir, "host_cfg.json"), "r") as fp:
        host_cfg = json.loads(fp.read())
    return host_cfg


class PlayerView(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(PlayerView, self).__init__(parent)

        # self.m_model = QtGui.QStandardItemModel(self)
        # self.setModel(self.m_model)
        self.setMinimumSize(520, 170)
        self.setAcceptDrops(False)
        self.setViewMode(QtWidgets.QListView.IconMode)  # 用Icon模式呈現
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setIconSize(QtCore.QSize(50, 50))
        self.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)  # 可以多選
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)  # 設置拖曳模式.DragOnly/.DropOnly/.DragDrop
        self.setSpacing(7)  # 物件的間隔
        self.setUniformItemSizes(True)
        self.setStyleSheet(
            """
            QListWidget
            {
                border:4px solid rgb(244, 172, 110);
                font-size: 9pt;
            }
            """
        )

        # self.setMinimumWidth(self.sizeHintForColumn(0))

        all_cards_dict = PorkerValue.pokerDict()

        for key in all_cards_dict.keys():
            item = QtWidgets.QListWidgetItem(key)
            item.setSizeHint(QtCore.QSize(30, 30))
            if '♦' in key:
                item.setForeground(QtCore.Qt.red)
            elif '♥' in key:
                item.setForeground(QtCore.Qt.red)
            item.setText(key)
            self.addItem(item)
        # self.item(0).setForeground(QtCore.Qt.red)

    def startDrag(self, event):
        indexes = self.getSelectedDraggableIndexes()
        if not indexes:
            return
        # 拖曳數據
        mimeData = self.model().mimeData(indexes)
        if not mimeData:
            return

        drag = QtGui.QDrag(self)
        # 將MIME型別資料放到剪貼簿中
        drag.setMimeData(mimeData)

        # 移動事件結束後將元素進行標記，不刪除
        if drag.exec(QtCore.Qt.MoveAction) == QtCore.Qt.MoveAction:
            self.highlightSelected()

    def highlightSelected(self):
        listItems = self.selectedItems()
        if not listItems:
            return
        for item in listItems:
            # 拖動之後反灰+禁用
            # item.setBackground(QtCore.Qt.lightGray)
            item.setForeground(QtCore.Qt.lightGray)
            # item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

    def getSelectedDraggableIndexes(self):
        # 練立一個清單來記錄所有被選取items對應的index
        indexes = []
        for index in self.selectedIndexes():
            item = self.itemFromIndex(index)
            indexes.append(index)
        return indexes


class EmptyView(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(EmptyView, self).__init__(parent)

        self.setAcceptDrops(False)
        self.setViewMode(QtWidgets.QListView.IconMode)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setIconSize(QtCore.QSize(50, 50))
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)  # 設置拖曳模式.DragOnly/.DropOnly/.DragDrop
        self.setSpacing(10)
        self.setUniformItemSizes(True)
        self.setMinimumWidth(200)

    def startDrag(self, event):
        indexes = self.getSelectedDraggableIndexes()
        if not indexes:
            return
        # 拖曳數據
        mimeData = self.model().mimeData(indexes)
        if not mimeData:
            return
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)  # 寫入拖曳數據(不加就會是空值)

        # 設置dropAction若成立就將item從原本的list移除
        dropAction = self.defaultDropAction()
        self.setDefaultDropAction(dropAction)
        dragResult = drag.exec_(event, dropAction)

        if dragResult == QtCore.Qt.MoveAction:
            self.removeSel()

        # if drag.exec(QtCore.Qt.MoveAction) == QtCore.Qt.MoveAction:
        #     pass
        #     self.removeSel()

    def removeSel(self):
        listItems = self.selectedItems()
        if not listItems:
            return
        for item in listItems:
            self.takeItem(self.row(item))

    def getSelectedDraggableIndexes(self):
        """ Get a list of indexes for selected items that are drag-enabled. """
        indexes = []
        for index in self.selectedIndexes():
            item = self.itemFromIndex(index)
            indexes.append(index)
        return indexes

    def dragEnterEvent(self, event):
        # 回傳每位玩家最多手牌張數
        player_cards_max = PorkerValue.PlayerCardsMax()

        # drag之前的計數器
        last_row_count = self.model().rowCount()
        # drag之前的所有items
        # itemsTextList0 = [str(self.item(i).text()) for i in range(self.count())]
        # print('drag before items {}'.format(itemsTextList0))
        # print("目前張數 {} 上限 {}".format(last_row_count, player_cards_max))
        # 判斷玩家目前手牌張數與上限，若超過手牌上限，不接受此次拖動事件
        if last_row_count < player_cards_max:
            tmp_data = event.mimeData()
            if tmp_data.hasFormat('application/x-qabstractitemmodeldatalist'):
                if event.source() != self:
                    event.setDropAction(QtCore.Qt.MoveAction)
                    # print("移動事件")
                    event.accept()
                else:
                    event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        dropAction = self.defaultDropAction()
        super(EmptyView, self).dropEvent(event)

        if event.source() != self:
            event.setDropAction(QtCore.Qt.MoveAction)

        if dropAction == QtCore.Qt.MoveAction:
            print("dropAction == QtCore.Qt.MoveAction")
            self.setDefaultDropAction(dropAction)
            self.removeSel()

        # itemsTextList = [str(self.item(i).text()) for i in range(self.count())]
        # print("drop 物件:", itemsTextList)


class HostCombo(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super(HostCombo, self).__init__(parent)

        self.host_name = get_hostconfig()
        self.addItem("-- 請選擇伺服器 -")
        for key in self.host_name.keys():
            self.addItem(key)
        # 部分選項禁用
        # self.model().item(1).setEnabled(False)
        # self.model().item(2).setEnabled(False)
        # self.model().item(6).setEnabled(False)
        # self.model().item(5).setEnabled(False)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)

        self.setWindowTitle("Card Script")
        self.resize(670, 600)
        # self.resize(670, 650)
        # self.setFixedSize(self.width(), self.height())

        # Radio buttons單選按鈕，設定幾人玩法
        self.group = QtWidgets.QButtonGroup()
        self.group.setExclusive(False)  # Radio buttons are not exclusive
        self.radioButton2 = QtWidgets.QRadioButton("2人", self)
        self.radioButton3 = QtWidgets.QRadioButton("3人", self)
        self.radioButton4 = QtWidgets.QRadioButton("4人", self)
        self.radioButton4.setChecked(True)
        self.group.addButton(self.radioButton2)
        self.group.addButton(self.radioButton3)
        self.group.addButton(self.radioButton4)

        self.textLabel_each_max = QtWidgets.QLabel("玩家數量:", self)
        self.textLabel = QtWidgets.QLabel(self)
        self.textLabel.setVisible(False)
        # self.textLabel_deck = QtWidgets.QLabel('牌庫:', self)

        # 各玩家手牌Widgets
        self.all_cards_view = PlayerView()
        self.player_seat_0 = EmptyView()
        self.player_seat_1 = EmptyView()
        self.player_seat_2 = EmptyView()
        self.player_seat_3 = EmptyView()
        self.player_gold = EmptyView()
        self.player_deck = EmptyView()
        self.combobox = HostCombo()

        self.all_cards_view.setMaximumSize(530, 170)
        self.all_cards_view.setMinimumSize(530, 170)
        self.player_gold.setMinimumSize(70, 70)
        # self.player_gold.setMaximumSize(80, 70)
        self.player_deck.setMinimumWidth(380)
        self.player_deck.setMaximumHeight(70)

        self.player_gold.setStyleSheet(
            """
            QListWidget
            {
                background-color:rgb(249, 237, 169);
            }
            """
        )

        self.pushButton = QtWidgets.QPushButton("產生腳本", self)
        self.pushButtonSend = QtWidgets.QPushButton("上傳測試腳本", self)
        # self.pushButtonSend.setEnabled(False)
        self.pushButtonClear = QtWidgets.QPushButton("清除", self)
        self.spinboxPort = QtWidgets.QSpinBox(self)
        self.spinboxPort.setRange(0, 9999)
        self.spinboxPort.setValue(9400)

        # 設置layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QGridLayout(central_widget)

        layout.addWidget(self.textLabel_each_max, 0, 0, 1, 1)
        layout.addWidget(self.radioButton2, 0, 1, 1, 1)
        layout.addWidget(self.radioButton3, 0, 2, 1, 1)
        layout.addWidget(self.radioButton4, 0, 3, 1, 1)

        layout.addWidget(self.all_cards_view, 4, 0, 4, 4)
        layout.addWidget(self.player_seat_0, 2, 0, 1, 2)
        layout.addWidget(self.player_seat_1, 1, 0, 1, 2)
        layout.addWidget(self.player_seat_2, 1, 2, 1, 2)
        layout.addWidget(self.player_seat_3, 2, 2, 1, 2)
        layout.addWidget(self.player_gold, 3, 0, 1, 1)
        layout.addWidget(self.player_deck, 3, 1, 1, 3)
        layout.addWidget(self.combobox, 4, 4, 1, 1)
        layout.addWidget(self.pushButton, 3, 4, 1, 3)
        layout.addWidget(self.pushButtonSend, 5, 4, 1, 3)
        layout.addWidget(self.pushButtonClear, 7, 4, 1, 3)
        layout.addWidget(self.spinboxPort, 4, 5, 1, 2)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.player_gold.sizePolicy().hasHeightForWidth())
        self.player_gold.setSizePolicy(sizePolicy)
        layout.setSpacing(20)

        # 每個元件觸發的函式
        # self.player_seat_0.model().dataChanged.connect(self.current_list_item)
        # self.player_seat_1.itemChanged.connect(self.current_list_item)
        self.pushButton.clicked.connect(self.buttonOkClicked)
        self.pushButtonSend.clicked.connect(self.buttonUpload)
        self.pushButtonClear.clicked.connect(self.buttonRestart)
        # 單選按鈕 2/3/4人
        self.group.buttonClicked.connect(self.check_buttons)

    def btnState(self, radioButton):
        if radioButton.isChecked() == True:
            pass

    def check_buttons(self, radioButton):
        for button in self.group.buttons():
            # 單選，將剩餘選的項目取消勾選
            if button is not radioButton:
                button.setChecked(False)
            # 被選中的選項
            else:
                current_player_text = button.text()
                self.textLabel.setText(current_player_text)
                # self.playerInfo()
                b = PorkerValue()
                count_text = b.playerCount(self.textLabel, self.player_seat_2, self.player_seat_3)
                self.textLabel_each_max.setText('手牌上限數: ' + str(count_text))
                self.textLabel_each_max.setStyleSheet('font: bold')

    def current_list_item(self):
        # 列出主視窗中所有QListWidget的物件
        player_list = self.findChildren(QtWidgets.QListWidget)
        for i in range(len(player_list)):
            # 第0個object為牌庫，故忽略之，取剩餘所有玩家列表
            if i != 0:
                current_list = player_list[i]
                itemsTextList = [str(current_list.item(i).text()) for i in range(current_list.count())]
                print('玩家 {}手牌 {}'.format(i, itemsTextList))

    def buttonOkClicked(self):
        # 列出主視窗中所有QListWidget的物件
        player_list = self.findChildren(QtWidgets.QListWidget)
        player_cards = []
        for i in range(len(player_list)):
            # 第0個為牌庫，故忽略之，取剩餘所有玩家列表
            if i != 0:
                current_list = player_list[i]
                itemsTextList = [str(current_list.item(i).text()) for i in range(current_list.count())]
                if i < 5:
                    print('玩家 {} 手牌 {}'.format(i, itemsTextList))
                elif i == 5:
                    print('Gold {}'.format(itemsTextList))
                elif i == 6:
                    print('牌庫 {}'.format(itemsTextList))
                player_cards.append(itemsTextList)

        # 取得所有QListWidget的元素，轉換為牌值
        poker_value = PorkerValue()
        final_result = poker_value.poker2Index(player_cards)  # tuple(list,testfile)
        print(final_result[0])
        # 如果腳本正確字串長度必定是209
        if len(final_result[-1]) == 209:
            try:
                # 如果資料夾不存在就建立
                if not os.path.isdir('.\Testfile'):
                    os.mkdir('.\Testfile')
                #
                fp = open('.\Testfile\TestScript.json', 'w', encoding="utf-8")
                # with open('TestScript.json', 'r') as fp:
                fp.write(str(final_result[-1]))
                fp.close()
            except Exception as e:
                print(e)
            self.msg = QtWidgets.QMessageBox.about(self, "⚠ 提示", '已複製至剪貼簿 ' + str(final_result[-1]))
            self.pushButtonSend.setEnabled(True)
        else:
            self.msg = QtWidgets.QMessageBox.about(self, "⚠ 提示", '失敗' + str(final_result[-1]))

    def buttonUpload(self):

        self.host_cfg = get_hostconfig()
        host_text = self.combobox.currentText()
        host_port = self.spinboxPort.value()
        print(f'port:{host_port}')

        if self.combobox.currentIndex() > 0:
            self.host = self.host_cfg[host_text]['host']
            print(self.host)
            try:
                upload_stat = TestScriptUpload.upLoadTestFile(self.host)
                if upload_stat == True:
                    self.msg = QtWidgets.QMessageBox.about(self, "", '上傳成功')
                else:
                    self.msg = QtWidgets.QMessageBox.about(self, "", '失敗')
            except Exception as e:
                print(e)
        else:
            self.msg = QtWidgets.QMessageBox.about(self, "⚠ 提示", '未選擇SERVER')

    def buttonRestart(self):
        self.player_seat_0.clear()
        self.player_seat_1.clear()
        self.player_seat_2.clear()
        self.player_seat_3.clear()
        self.player_gold.clear()
        self.player_deck.clear()

        for i in range(self.all_cards_view.count()):
            current_poker = self.all_cards_view.item(i)
            # current_poker.setFlags(QtCore.Qt.ItemIsSelectable)
            if '♦' in current_poker.text():
                current_poker.setForeground(QtCore.Qt.red)
            elif '♥' in current_poker.text():
                current_poker.setForeground(QtCore.Qt.red)
            else:
                current_poker.setForeground(QtCore.Qt.black)


class PorkerValue(object):
    player_count = 4  # 預設玩家人數
    player_cards = 7  # 預設玩家手牌張數

    def __init__(self):
        self.card_index = None

    @classmethod
    def pokerDict(cls):
        card_suit = ['♣', '♦', '♥', '♠']
        card_point = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        all_pokers = tuple([c + n for c in card_suit for n in card_point])
        card_index = [i for i in range(1, 62) if i % 16 > 0 and i % 16 <= 13]
        cls.card_dict = dict(zip(all_pokers, card_index))
        return cls.card_dict

    def repeatCheck(self, card_script):
        n = dict(Counter(card_script))
        max_key = max(n, key=lambda key: n[key])
        if n[max_key] > 1:
            print('重複:\n', [key for key, value in n.items() if value > 1])
            print('統計:\n', {key: value for key, value in n.items() if value > 1})
            return False
        return True

    def fillCards(self, all_player_card_list):
        self.player_cards_max = self.PlayerCardsMax()
        self.player_max = self.PlayerCount()
        # all_player_card_list:[[p0], [p1], [p2], [p3], [海底金], [牌庫]]
        print('傳入陣列:', all_player_card_list)
        self.all_select = all_player_card_list[0:self.player_max]  # 按玩家人數決定取到陣列第幾個位置
        self.sea_gold = all_player_card_list[-2]  # 海底金牌位置
        self.sea_deck = all_player_card_list[-1]  # 指定牌庫位置
        self.all_cards_id = [i for i in range(1, 62) if i % 16 > 0 and i % 16 <= 13]

        # 所有玩家手牌合併為一個列表，從完整牌庫移除
        first_zip = list(itertools.chain.from_iterable(self.all_select))
        for card in first_zip:
            self.all_cards_id.remove(card)

        shuffle(self.all_cards_id)  # randomized shuffling ->  random deck
        # 檢查海底金是否為空，給予洗牌後的第一張，給完就從random deck移除
        if len(self.sea_gold) == 0:
            self.sea_gold.append(self.all_cards_id[0])
            self.all_cards_id.remove(self.all_cards_id[0])
        elif len(self.sea_gold) == 1:
            self.all_cards_id.remove(self.sea_gold[0])
        else:
            return None

        # 檢查是否有指定牌庫
        if len(self.sea_deck) > 0:
            for d in self.sea_deck:
                self.all_cards_id.remove(d)

        # 剩下開始處理所有玩家手牌
        self.all_player_cards = []
        for i in range(len(self.all_select)):
            current_player_cards = self.all_select[i]  # 檢查第N個玩家手牌
            for card in self.all_cards_id:
                # 該玩家手牌數 < 手牌上限
                if len(current_player_cards) < self.player_cards_max:
                    current_player_cards.append(card)  # 從random deck取一張牌到第N個玩家手牌裡面
                    self.all_cards_id.remove(card)  # remove from the random deck of cards
            self.all_player_cards.append(current_player_cards)

        # 建立一個list，按座位依序將每個玩家手牌放入
        zip_all = [x for y in zip(*self.all_player_cards) for x in y]

        if self.repeatCheck(zip_all):
            # 全部加總
            total_cards = zip_all + self.sea_gold + self.sea_deck + self.all_cards_id
            if len(total_cards) == 52:
                script_format = {"crds": [i for i in total_cards]}
                try:
                    testScript = json.dumps(script_format)
                    pyperclip.copy(testScript)
                    return testScript
                except Exception as e:
                    print(e)
                    return None
            else:
                return len(total_cards)
        else:
            return None

    # 牌值轉換
    def poker2Index(self, player_items):
        self.player_card_list = player_items
        self.player_card_final = []
        for each_player_cards in self.player_card_list:
            each_player_new_cards = [self.card_dict[i] for i in each_player_cards]
            self.player_card_final.append(each_player_new_cards)

        # 回傳最後的手牌陣列
        self.testFile = self.fillCards(self.player_card_final)
        return self.player_card_final, self.testFile

    @classmethod
    def playerCount(cls, labelText, seat2, seat3):
        # 預設玩家數量及手牌張數
        current_label_text = labelText.text()
        cls.player_count = 4
        cls.player_cards = 7
        if current_label_text == "2人":
            cls.player_count = 2
            cls.player_cards = 11
            seat2.setEnabled(False)
            seat3.setEnabled(False)
        elif current_label_text == "3人":
            cls.player_count = 3
            cls.player_cards = 9
            seat2.setEnabled(True)
            seat3.setEnabled(False)
        elif current_label_text == "4人":
            seat2.setEnabled(True)
            seat3.setEnabled(True)
        return cls.player_cards

    @classmethod
    def PlayerCardsMax(self):
        return self.player_cards

    @classmethod
    def PlayerCount(self):
        return self.player_count
