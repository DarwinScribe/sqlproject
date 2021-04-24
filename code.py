import sys
from PyQt5 import uic, QtWidgets  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow,  QTableWidgetItem, QMessageBox
import sqlite3
from PyQt5.QtGui import QIcon

connect = sqlite3.connect('plan_db')
cursor = connect.cursor()
result = ''
class MenuApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('loginForm.ui', self)
        self.setWindowIcon(QIcon('image/logic.png'))
        self.enter_btn.clicked.connect(self.OnSignup)
        self.reg_btn.clicked.connect(self.regNew)

    def regNew(self):
        dialog = Reg(self)
        dialog.show()

    def OnSignup(self):
        global result
        log = self.log_txb.text()
        pas = self.pass_txb.text()
        cursor.execute("SELECT * FROM user WHERE login = ? and pass = ?", (log, pas))
        result = cursor.fetchall()
        if result:
            print(result[0][1], result[0][0])
            dialog = MA(self, log=result[0][1], id_u=result[0][0])
            dialog.show()
        else:
            QMessageBox.about(self, 'Ошибка входа', "Неверный логин или пароль")
            
    
class MA(QMainWindow):
    def __init__(self, window2 = None, log=None, id_u=None):
        self.log = log
        self.id_u = id_u 
        super().__init__(parent=window2)

        uic.loadUi('menu.ui', self)
        self.setFixedSize(self.size())
        self.setWindowIcon(QIcon('image/logic.png'))
        self.pushButton.clicked.connect(self.inbd)
        self.label.setText(log)
        self.calendarWidget.clicked.connect(self.sebd)
        self.dlbtn.clicked.connect(self.del_task)
        result = cursor.execute('''SELECT *
                          FROM Categories''').fetchall()
        
        self.modified = {}
        for item in result:
            st = list(item)
            self.comboBox.addItem(str(st[0]) +' ' + st[1])

    def del_task(self):
        task = self.tableWidget.selectedItems()
        sp = []
        for el in task:
            sp.append(el.text())
        cursor.execute('''DELETE FROM Tasks
                          WHERE name_task = ? and
                          date = ? and
                          day_week = ?
                          ''', (sp[0], sp[1], sp[2]))
        cursor.fetchall()
        connect.commit()
        self.sebd()

    def inbd(self):
        id_us = str(self.id_u)
        tas = self.lineEdit.text()
        dat = self.calendarWidget.selectedDate().toString()
        wek = dat[0]+dat[1]
        cat = str(self.comboBox.currentText()[0])
        cursor.execute('''INSERT INTO Tasks 
                        (
                         name_task,
                         date,
                         day_week,
                         id_user,
                         id_cat)
                         values
                         (
                          ?,
                          ?,
                          ?,
                          ?,
                          ?
                         )
                        ''',(tas, dat, wek, id_us, cat)).fetchall()
        QMessageBox.about(self, 'Успех!', "Задача успечно добавлена!")
        connect.commit()
        self.sebd()

    def sebd(self):
        da = self.calendarWidget.selectedDate().toString()
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["Навзание задачи", 
                                         "дата", 
                                         "день недели",
                                         "категория"])
        cursor.execute('''SELECT name_task, date, day_week, name_cat
                          FROM Tasks, Categories
                          WHERE Tasks.id_cat = Categories.id_category 
                          and id_user = ?
                          and date = ?''',(str(self.id_u), da))
        result = cursor.fetchall()
        self.tableWidget.setRowCount(len(result))
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.tableWidget.resizeColumnsToContents()
        self.modified = {}
 
class Reg(QMainWindow):
    def __init__(self, window2 = None):
        super().__init__(parent=window2)
        uic.loadUi('creatu.ui', self)
        self.setFixedSize(self.size())
        self.setWindowIcon(QIcon('image/logic.png'))    
        self.cnbtn.clicked.connect(self.cancel)
        self.acbtn.clicked.connect(self.accept)

    def cancel(self):
        self.close()
 
    def accept(self):
        log = self.loglb.text()
        pas = self.paslb.text()
        if not log or not pas:
            QMessageBox.about(self, 'Ошибка создания', "Невозможно создать пользователя без логина или пароля")
        else:
            cursor.execute('''INSERT INTO user
                            (login,
                             pass)
                             VALUES
                             (
                             ?,
                             ?
                             )
                ''',(log, pas))
            cursor.fetchall()
            connect.commit()
            QMessageBox.about(self, 'Успех', "Пользователь успешно создан")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MenuApp()
    ex.show()
    sys.exit(app.exec_())