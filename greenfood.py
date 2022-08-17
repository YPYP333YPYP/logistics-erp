""" pyinstaller 로는 이미지 추가가 안되어서 qrc 파일에 이미지를 저장 후 py 파일로 변환하여 import 함"""
import greenfoodicon
import pymysql
import numpy as np
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from matplotlib.backends.backend_qt5agg import FigureCanvas as FigureCanvas
from matplotlib.figure import Figure
from collections import OrderedDict, defaultdict

font_path = "C:/Windows/Fonts/NGULIM.TTF"
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)
 

con = pymysql.connect(host='127.0.0.1', user='root',password='chfhr0811',charset='utf8')


cur = con.cursor()
# cur.execute("DROP DATABASE testdb1")
cur.execute("CREATE DATABASE IF NOT EXISTS testdb1")
cur.execute("USE testdb1") 


# 메인 화면 창
class main(QMainWindow):

    def __init__(self):
        super().__init__()
        

        with con.cursor() as curs:
              
            sql_buyer ="""
                CREATE TABLE IF NOT EXISTS buyer(
                    buyer_name VARCHAR(20) PRIMARY KEY,
                    buyer_region VARCHAR(10),
                    buyer_sector VARCHAR(10),
                    buyer_etc TEXT
                
                )
            """
                  
            sql_prodcut ="""
                CREATE TABLE IF NOT EXISTS product (
                    prod_name VARCHAR(20) PRIMARY KEY,
                    buy_price INT,
                    prod_vol INT,
                    sell_price INT,
                    buy_where VARCHAR(30) 
                )
                """

            sql_buy = """
                     CREATE TABLE IF NOT EXISTS buy (
                     buyer_name VARCHAR(20) ,  
                     prod_name VARCHAR(20),
                     buy_price INT,
                     prod_vol INT,
                     sell_price INT,
                     buy_where VARCHAR(30),
                     prod_qt INT,
                     total_pur INT,
                     total_sale INT
                   )                 
                     """
           
            sql_total = """
                CREATE TABLE IF NOT EXISTS total AS SELECT 
                buyer.buyer_name, buyer.buyer_region, buy.total_pur, buy.total_sale FROM buyer 
                INNER JOIN buy 
                ON buyer.buyer_name = buy.buyer_name; 
                    """
          
            curs.execute(sql_buyer)
            curs.execute(sql_prodcut)
            curs.execute(sql_buy)   
            curs.execute(sql_total)    
        con.commit()  
    
        self.mainWindow()
        self.setWindowTitle('유통 관리 프로그램')
        self.setWindowIcon(QIcon(':image/cpu.png'))
        self.setGeometry(300,300,700,700)
        self.show()


    def mainWindow(self):
        # 1. exit
        exitAction = QAction(QIcon(':image/exit.png'), 'Exit', self)
        exitAction.setStatusTip('Exit App')
        exitAction.triggered.connect(qApp.quit)

        # 2. clipboard (거래처별 전표)
        clipAction = QAction(QIcon(':image/clipboard.png'), '거래처 전표',self)
        clipAction.setStatusTip('거래처 전표')
        clipAction.triggered.connect(self.ClipboardClicked)

        # 3. Item (식자재 리스트)
        itemAction = QAction(QIcon(':image/food.png'), '물품 목록',self)
        itemAction.setStatusTip('물품 목록')
        itemAction.triggered.connect(self.ItemClicked)

        # 4. check (수량 입력)
        checkAction = QAction(QIcon(':image/checkbox.png'), 'Check',self)
        checkAction.setStatusTip('Check')
        checkAction.triggered.connect(self.CheckClicked)

        # 5. start (시작)
        startAction = QAction(QIcon(':image/power.png'), '시작',self)
        startAction.setStatusTip('Start')
        startAction.triggered.connect(self.StartClicked)
        
        # toolbar show
        self.statusBar()
        self.toolbar = self.addToolBar('ToolBar')
        self.toolbar.addAction(exitAction)
        self.toolbar.addAction(clipAction)
        self.toolbar.addAction(itemAction)
        self.toolbar.addAction(checkAction)
        self.toolbar.addAction(startAction)
      
        
        # Qwidget 생성
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        # 그림을 그리는 영역을 나타내는 객체 FigureCanvas
        canvas = FigureCanvas(Figure(figsize=(4, 3)))
        vbox = QVBoxLayout(self.main_widget)
        vbox.addWidget(canvas)


        with con.cursor() as curs:
            regionlist = []
            totalsale = defaultdict(int)
            sql = """
                SELECT buyer.buyer_region, buy.total_sale FROM buyer INNER JOIN buy ON buyer.buyer_name = buy.buyer_name 
                """
            curs.execute(sql)
            result = curs.fetchall()
            
            for k in result:
                regionlist.append(k[0])
            
            for v in result:
                totalsale[v[0]] += v[1]
            
            x = []
            y = []
            
            for k in totalsale:
                x.append(k)
                y.append(totalsale[k])
            
            total = sum(y)
            self.ax = canvas.figure.subplots(1,1)
            self.ax.bar(x,y,color='g')
            self.ax.set_xlabel('지역')
            self.ax.set_ylabel('합계 매출액')
            self.ax.set_title("지역별 매출액 ( 총 매출액 : " + str(total) + " 원 )")
            
            
    def ClipboardClicked(self):
        self.clipboard = cilpwindow()
        self.clipboard.exec()
    
    def ItemClicked(self):
        self.item = itemwindow()
        self.item.exec()

    def CheckClicked(self):
        self.check = checkwindow()
        self.check.exec()
    
    def StartClicked(self):
        self.start = startwindow()
        self.start.exec()

# 거래처 전표 창    
class cilpwindow(QDialog,QWidget):

    buyer_str = ''
    buyer_arr =[]

    def __init__(self):
        super().__init__()

        self.initUI()
        self.setWindowIcon(QIcon(':image/clipboard.png'))
        self.setWindowTitle('거래처 전표')
        self.setGeometry(300,300,900,600)
        self.show()

    def initUI(self):    

        layout = QVBoxLayout()
        buyer_layout = QHBoxLayout()
        total = QHBoxLayout()

        # 거래처 선택
        self.buy_lbl = QLabel('거래처를 선택해주세요.')
        self.buyer_select = QComboBox(self)

        self.buyer_select.activated[str].connect(self.onActivated)
        buyer_layout.addWidget(self.buy_lbl,2)
        buyer_layout.addWidget(self.buyer_select,8)

        with con.cursor() as curs:
            curs.execute(""" SELECT buyer_name FROM buyer""")
            result = curs.fetchall()

            for v in result:
                self.buyer_select.addItem(v[0])

        con.commit()

        # 총 비용 
        total_cost = QLabel('총 비용 : ')
        self.total_cost_val = QLabel('0')
        total.addWidget(total_cost)
        total.addWidget(self.total_cost_val)
        
        # 총 수익
        total_profit = QLabel('총 수익 : ')
        self.total_profit_val = QLabel('0')
        total.addWidget(total_profit)
        total.addWidget(self.total_profit_val)
       
        # 합계
        total_sum = QLabel('합계 : ')
        self.total_sum_val = QLabel()
        total.addWidget(total_sum)
        total.addWidget(self.total_sum_val)

        layout.addLayout(buyer_layout)
        layout.addLayout(total)
        
        # 조회 버튼
        select_btn = QPushButton('조회')
        select_btn.clicked.connect(self.tableInsert)
        total.addWidget(select_btn)

        # 거래처 추가 버튼
        buyer_add_btn = QPushButton('거래처 추가')
        buyer_add_btn.clicked.connect(self.buyerAddClicked)
        total.addWidget(buyer_add_btn)

        # 거래처 삭제 버튼
        buyer_del_btn = QPushButton('거래처 삭제')
        buyer_del_btn.clicked.connect(self.buyerDelClicekd)
        total.addWidget(buyer_del_btn)

        # table 
        # 열 목록 - 물건 이름(prod_name), 구입 가격(buy_price),
        # 용량(prod_vol), 수량(prod_qt), 판매 가격(sell_price), 구입처(buy_where)
        # 총 매입액(total_pur), 총 매출액(total_sale)
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setColumnCount(8)
        self.tableWidget.setRowCount(20)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
  
        column_headers = ['물품',"구입 가격",'용량',"판매 가격",'구입처','수량',"총 매입액","총 매출액"]
        self.tableWidget.setHorizontalHeaderLabels(column_headers)

        layout.addWidget(self.tableWidget)
        self.setLayout(layout)

       
    def onActivated(self, text):
        self.buy_lbl.setText(text)
        self.buy_lbl.adjustSize()
        self.buyer_str = self.buy_lbl.text()
       

    def tableInsert(self):
        self.tableWidget.clearContents()
        with con.cursor() as curs:
            sql ="""
                SELECT * FROM buy WHERE buyer_name = %s
                """

            curs.execute(sql,self.buyer_str)  
            result = curs.fetchall()
            sparelist = list(result)

            for i in range(8):
                for k,v in enumerate(result):
                    s = list(v)
                    item = QTableWidgetItem(str(s[i+1]))
                    self.tableWidget.setItem(k,i,item)


            self.sum_total_cost = 0
            for i in sparelist:
                self.sum_total_cost += int(i[7])
            self.total_cost_val.setText(str(self.sum_total_cost))   
      

            self.sum_total_profit = 0
            for i in sparelist:
                self.sum_total_profit += int(i[8])
            self.total_profit_val.setText(str(self.sum_total_profit))   
            self.total_sum_val.setText(str(self.sum_total_profit-self.sum_total_cost))        
        con.commit()

    def buyerAddClicked(self):
        self.buyeradd = buyeraddwindow()
        self.buyeradd.exec()
        self.buyer_select.clear()
        
        with con.cursor() as curs:
            sql = """
                SELECT buyer_name FROM buyer
                """
            curs.execute(sql)
            result = curs.fetchall()
         
            for v in result: 
                self.buyer_arr.append(v[0])
                self.buyer_select.addItem(v[0])
        con.commit()

        sparelist = list(dict.fromkeys(self.buyer_arr))
        self.buyer_arr = sparelist


    def buyerDelClicekd(self):
        with con.cursor() as curs:
            sql = """
                 DELETE FROM buyer WHERE buyer_name = %s
                    """
            if self.buyer_str == '':
                 QMessageBox.warning(self,'ERROR','선택된 거래처가 없습니다 !')
            curs.execute(sql,self.buyer_str)
            self.buyer_select.removeItem(self.buyer_arr.index(self.buyer_str))
            self.buy_lbl.setText('거래처를 선택해주세요.')   

        con.commit()
      
# 거래처 전표 - 거래처 추가 창
class buyeraddwindow(QDialog,QWidget):

    Sectordata = '이자카야'
    Regiondata = '강남'

    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle('거래처 추가 입력 창')
        self.setWindowIcon(QIcon(':image/clipboard.png'))
        self.setGeometry(300,300,300,200)
        self.show()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        # 지역 카테고리
        regionlist = ['강남','의정부','노원','건대','홍대']
        self.region_category_lbl = QLabel('지역',self)
        self.region_category = QComboBox(self)
        for i in regionlist:
            self.region_category.addItem(i)
        self.region_category.activated[str].connect(self.onActivatedRegion)

        # 종목 카테고리
        sectorslist = ['이자카야','헌팅포차','룸술집']
        self.sectors_category_lbl = QLabel('업종',self)
        self.sectors_category = QComboBox(self)
        for i in sectorslist:
            self.sectors_category.addItem(i)
        self.sectors_category.activated[str].connect(self.onActivatedSector)

        # 거래처 이름 
        self.line_lbl = QLabel('거래처 이름')
        self.line = QLineEdit(self)
     
        # 기타 특이사항 
        self.unique_edit_lbl = QLabel('기타 특이사항',self)
        self.unique_edit = QTextEdit(self)
      
        # 추가 버튼
        self.enter_btn = QPushButton('추가',self)
        self.enter_btn.clicked.connect(self.buyerDataAdd)
      
        # 레이아웃 배치
        self.layout.addWidget(self.region_category_lbl)
        self.layout.addWidget(self.region_category)
        self.layout.addWidget(self.sectors_category_lbl)
        self.layout.addWidget(self.sectors_category)
        self.layout.addWidget(self.line_lbl)
        self.layout.addWidget(self.line)
        self.layout.addWidget(self.unique_edit_lbl)
        self.layout.addWidget(self.unique_edit)
        self.layout.addWidget(self.enter_btn)
        self.setLayout(self.layout)

    def buyerDataAdd(self):
        self.buyer_line_text = self.line.text()  
        self.unique_edit_text = self.unique_edit.toPlainText()
        
        # 거래처 정보 입력
        try:
            with con.cursor() as curs:
                sql =""" INSERT INTO buyer VALUES (%s,%s,%s,%s)"""
                curs.execute(sql,(self.buyer_line_text,self.Regiondata, self.Sectordata, self.unique_edit_text))
        
            con.commit()
            QMessageBox.information(self,'거래처 추가 완료','거래처가 추가 되었습니다 !')
           
        except:
            QMessageBox.warning(self,'ERROR','입력한 거래처가 이미 있습니다')
       

    def onActivated(self,text):
        self.buyer_line.setText(text)
    
    def onActivatedRegion(self,text):
        self.Regiondata = text

    def onActivatedSector(self,text):
        self.Sectordata = text
         
# 물품 창         
class itemwindow(QDialog,QWidget):

    # DB 삽입용 리스트
    itemlist =["","","","",""," "]

    # 테이블용 리스트
    table_list = []

    # 테이블 용 카운트 변수
    cnt = 0
    delcnt = 0


    def __init__(self):
        super().__init__()
        
        self.initUI()
        self.setWindowTitle('물품 목록')
        self.setWindowIcon(QIcon(':image/food.png'))
        self.setGeometry(300,300,570,600)
        self.show()

    def initUI(self):
        main_layout = QVBoxLayout()

        # 프레임 
        frame = QFrame()
        frame.setFrameShape(QFrame.Panel | QFrame.Panel)
        frame_layout = QVBoxLayout()

        frame.setLayout(frame_layout)
        main_layout.addWidget(frame)

         # 물품 추가
        item_add_btn = QPushButton('물품 추가')
        frame_layout.addWidget(item_add_btn)
        item_add_btn.clicked.connect(self.itemAdd)

        # 물품 수정
        item_rev_btn = QPushButton('물품 수정')
        frame_layout.addWidget(item_rev_btn)
        item_rev_btn.clicked.connect(self.itemRev)

        # 물품 삭제
        item_del_btn = QPushButton('물품 삭제')
        frame_layout.addWidget(item_del_btn)
        item_del_btn.clicked.connect(self.itemDel)

        # 물품 테이블
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setRowCount(20)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        main_layout.addWidget(self.tableWidget)  
        column_headers = ['물품',"구입 가격",'용량',"판매 가격",'구입처']
        self.tableWidget.setHorizontalHeaderLabels(column_headers)

        with con.cursor() as curs:
            sql = """
                SELECT * FROM product
                """
            curs.execute(sql)
            result = curs.fetchall()
            for v in result:
                for i in range(5):
                    item = QTableWidgetItem(str(v[i]))
                    self.tableWidget.setItem(self.cnt,i,item)
                self.cnt +=1
        con.commit()
        self.setLayout(main_layout)

    def itemAdd(self):
        self.itemadd = itemaddwindow()
        self.itemadd.exec()

        rowcnt = self.cnt + self.delcnt
        colcnt = 0

        for k in self.table_list:
            for i in range(5):
                item = QTableWidgetItem(k[i])
                self.tableWidget.setItem(rowcnt,colcnt,item)
                colcnt +=1
            self.cnt +=1
        self.table_list.clear()

    def itemRev(self):
        self.itemrev = itemrevwindow()
        self.itemrev.exec()
        self.tableWidget.clearContents()

        with con.cursor() as curs:
            sql = """
                SELECT * FROM product
                """
            curs.execute(sql)
            result = curs.fetchall()
            for i in range(5):
                for k,v in enumerate(result):
                    s = list(v)
                    item = QTableWidgetItem(str(s[i]))
                    self.tableWidget.setItem(k,i,item)
        con.commit()

    def itemDel(self):
        self.itemdel = itemdelwindow()
        self.itemdel.exec()    
        self.tableWidget.clearContents()

        with con.cursor() as curs:
            sql = """
                SELECT * FROM product
                """
            curs.execute(sql)
            result = curs.fetchall()
            for i in range(5):
                for k,v in enumerate(result):
                    s = list(v)
                    item = QTableWidgetItem(str(s[i]))
                    self.tableWidget.setItem(k,i,item)
        con.commit()
# 물품 - 물품 추가 창
class itemaddwindow(QDialog, QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI()
        self.setWindowTitle('물품 추가 창')
        self.setWindowIcon(QIcon(':image/food.png'))
        self.setGeometry(300,300,300,300)
        self.show()

    def initUI(self):
        grid = QGridLayout()
        
        # 물품 이름 칸
        self.lbl_name = QLabel('물품 이름 ==> ',self)
        self.line_name = QLineEdit(self)
        grid.addWidget(self.lbl_name,1,0)
        grid.addWidget(self.line_name,1,1)

        # 물품 구입 가격 칸
        self.lbl_bp = QLabel('구입 가격 ==> ',self)
        self.line_bp = QLineEdit(self)
        grid.addWidget(self.lbl_bp,2,0)
        grid.addWidget(self.line_bp,2,1)

        # 물품 용량 칸
        self.lbl_vol = QLabel('용량 ==>',self)
        self.line_vol = QLineEdit(self)
        grid.addWidget(self.lbl_vol,3,0)
        grid.addWidget(self.line_vol,3,1)

        # 물품 판매 가격 칸
        self.lbl_sp = QLabel('판매 가격 ==> ',self)
        self.line_sp = QLineEdit(self)
        grid.addWidget(self.lbl_sp,4,0)
        grid.addWidget(self.line_sp,4,1)

        # 물품 구입처 칸
        self.lbl_where = QLabel('구입처 ==>   ',self)
        self.line_where = QLineEdit(self)
        grid.addWidget(self.lbl_where,5,0)
        grid.addWidget(self.line_where,5,1)

        # 추가 버튼
        addbtn = QPushButton('추가')
        addbtn.clicked.connect(self.additem)
        grid.addWidget(addbtn,6,1)
        
    
        self.setLayout(grid)

    def additem(self):
        self.itemlist =["",0,0,0,""]
        if self.line_name.text() == '':
            QMessageBox.warning(self,'ERROR','물품 이름을 적어주세요 !')

        
        with con.cursor() as curs:
            sql = """
                  SELECT prod_name FROM product  
                    """
            curs.execute(sql)
            result = curs.fetchall()

            for v in result:
                if self.line_name.text() == v[0]:
                    QMessageBox.warning(self,'ERROR','이미 같은 이름의 물품이 있습니다 !')  
                    return
                else: 
                    continue
                    
        # itemwindow.itemdict에 값 저장
        self.itemlist[0] = self.line_name.text()
        self.itemlist[1] = self.line_bp.text()
        self.itemlist[2] = self.line_vol.text()
        self.itemlist[3] = self.line_sp.text()
        self.itemlist[4] = self.line_where.text()

        for i in range(3):
            if self.itemlist[i+1] == '':
                self.itemlist[i+1] = 0 

        itemwindow.itemlist = self.itemlist
        itemwindow.table_list.append(self.itemlist)
       
        with con.cursor() as curs:
            sql = """
                INSERT INTO product VALUES(%s,%s,%s,%s,%s)
            """     
            curs.execute(sql,(self.itemlist[0], self.itemlist[1], self.itemlist[2], self.itemlist[3], self.itemlist[4]))

        con.commit()

        QMessageBox.information(self,'물품 추가 완료','물품이 추가 되었습니다 !')   

# 물품 - 물품 수정 창
class itemrevwindow(QDialog, QWidget):

    itemnametext =''
    dictid = 0

    def __init__(self):
        super().__init__()
        
        self.initUI()
        self.setWindowTitle('물품 수정 창')
        self.setWindowIcon(QIcon(':image/food.png'))
        self.setGeometry(300,300,300,300)
        self.show()

    def initUI(self):        
        grid = QGridLayout()

        # 수정할 물품 이름 
        self.itemname = QLabel('수정할 물품 이름 -> : ' ,self)
        
        # 물품 리스트
        self.itemlist = QComboBox(self)
        with con.cursor() as curs:
            sql = """ SELECT * FROM product;"""
            curs.execute(sql)

            result = curs.fetchall()
            for v in result:
                self.itemlist.addItem(v[0])

        con.commit()

        self.itemlist.activated[str].connect(self.onActivated)
        grid.addWidget(self.itemname,0,0)
        grid.addWidget(self.itemlist,0,1)
        
        # 물품 이름 칸
        self.lbl_name = QLabel('물품 이름 ==> ',self)
        self.line_name = QLineEdit(self)
        grid.addWidget(self.lbl_name,1,0)
        grid.addWidget(self.line_name,1,1)

        # 구입 가격 칸
        self.lbl_bp = QLabel('구입 가격 ==> ',self)
        self.line_bp = QLineEdit(self)
        grid.addWidget(self.lbl_bp,2,0)
        grid.addWidget(self.line_bp,2,1)

        # 용량 칸
        self.lbl_vol = QLabel('용량 ==>',self)
        self.line_vol = QLineEdit(self)
        grid.addWidget(self.lbl_vol,3,0)
        grid.addWidget(self.line_vol,3,1)

        # 판매 가격 칸
        self.lbl_sp = QLabel('판매 가격 ==> ',self)
        self.line_sp = QLineEdit(self)
        grid.addWidget(self.lbl_sp,4,0)
        grid.addWidget(self.line_sp,4,1)

        # 구입처 칸
        self.lbl_where = QLabel('구입처 ==>   ',self)
        self.line_where = QLineEdit(self)
        grid.addWidget(self.lbl_where,5,0)
        grid.addWidget(self.line_where,5,1)

        # 수정 버튼
        revbtn = QPushButton('수정')
        revbtn.clicked.connect(self.revitem)
        grid.addWidget(revbtn,6,1)
        
        self.setLayout(grid)
    
    def onActivated(self,text):
        self.itemnametext = text
        QMessageBox.information(self,'물품 선택 완료','물품 선택 완료')
        
    def revitem(self):
        
        with con.cursor() as curs:
            sparelist = []
            sql = """
                  SELECT * FROM product WHERE prod_name = %s  
                    """
            curs.execute(sql, self.itemnametext)
            result = curs.fetchall()

            for v in result:
                sparelist = list(v)
            

            if self.line_name.text() != '':
                sparelist.pop(0)
                sparelist.insert(0,self.line_name.text())
        
            if self.line_bp.text() != '':
                sparelist.pop(1)
                sparelist.insert(1,int(self.line_bp.text()))

            if self.line_vol.text() != '':
                sparelist.pop(2)
                sparelist.insert(2,int(self.line_vol.text())) 

            if self.line_sp.text() != '':
                sparelist.pop(3)
                sparelist.insert(3,int(self.line_sp.text()))

            if self.line_where.text() != '':
                sparelist.pop(4)
                sparelist.insert(4,self.line_where.text())
            
            sql = """
                 UPDATE product SET prod_name = %s , buy_price = %s, prod_vol = %s, sell_price = %s, buy_where = %s WHERE prod_name = %s;  
                    """
            curs.execute(sql,(sparelist[0],sparelist[1],sparelist[2],sparelist[3],sparelist[4], self.itemnametext))
        con.commit()

        QMessageBox.information(self,'물품 수정 완료','물품이 수정 되었습니다 !')

# 물품 - 물품 삭제 창
class itemdelwindow(QDialog, QWidget):

    itemnametext =''

    def __init__(self):
        super().__init__()
        
        self.initUI()
        self.setWindowTitle('물품 삭제 창')
        self.setWindowIcon(QIcon(':image/food.png'))
        self.setGeometry(300,300,100,100)
        self.show()

    def initUI(self):       
        grid = QGridLayout()

        # 아이템 이름
        itemname = QLabel('아이템 선택 -> ') 
        grid.addWidget(itemname,0,0)

        # 아이템 입력 칸
        self.ch_itemname = QLineEdit()   
        grid.addWidget(self.ch_itemname,1,0)

        # 아이템 리스트
        self.itemlist = QComboBox(self)
        with con.cursor() as curs:
            curs.execute("SELECT prod_name FROM product")
            result = curs.fetchall()
            for v in result:
                self.itemlist.addItem(v[0])     
        con.commit()       
        self.itemlist.activated[str].connect(self.onActivated)
        grid.addWidget(self.itemlist,0,1)

        # 아이템 삭제 버튼
        delbtn = QPushButton('삭제')
        delbtn.clicked.connect(self.delitem)
        grid.addWidget(delbtn,1,1)

        self.setLayout(grid)

    def onActivated(self,text):
        self.itemnametext = text
        self.ch_itemname.setText(text)      
        QMessageBox.information(self,'물품 선택 완료','물품 선택 완료')

    def delitem(self):
        if self.itemnametext == '':
            QMessageBox.warning(self,'ERROR','선택된 거래처가 없습니다')
        else:
            with con.cursor() as curs:
                sql = """
                    DELETE FROM product WHERE prod_name = %s   
                        """
                curs.execute(sql, self.itemnametext)
            con.commit()
            itemwindow.delcnt -= 1
            QMessageBox.information(self,'물품 삭제','물품 삭제 완료')
     
# 전표 창
class checkwindow(QDialog,QWidget):

    buyer_name = ''
    item_name = ''

    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowIcon(QIcon(':image/checkbox.png'))
        self.setWindowTitle('전표 생성')
        self.setGeometry(300,300,600,700)
        self.show()
    
    def initUI(self):
        main = QVBoxLayout()
        grid = QGridLayout()

        # 거래처 리스트
        buyer_list = QComboBox()
        buyer_list.setFixedSize(200,20)
        with con.cursor() as curs:
            sql = """
                SELECT buyer.buyer_name FROM buyer """
            
            curs.execute(sql)

            buyer_name = curs.fetchall()
            for v in buyer_name:
                 buyer_list.addItem(v[0])
        con.commit()

        buyer_list.activated[str].connect(self.onActivatedBuyer)
       
        # 전표 생성 버튼
        buyer_btn = QPushButton('전표 생성')
        buyer_btn.clicked.connect(self.chit)

        # 거래처 라벨
        buyer_lbl = QLabel("거래처 : ")
        buyer_lbl.setFixedSize(50,20)
        self.buyer_lbl_sel = QLabel(self)
        self.buyer_lbl_sel.setFixedSize(50,20)

        # 물품 라벨
        item_lbl = QLabel("물품 : ")
        item_lbl.setFixedSize(50,20)
        self.item_lbl_sel = QLabel(self)
        self.item_lbl_sel.setFixedSize(50,20)

        # 수량 라벨
        qt_lbl = QLabel('수량 : ')

        # 수량 입력 라인
        self.item_qt = QLineEdit(self)
        self.item_qt.setFixedSize(30,20)

        # 라벨 레이아웃 배치
        lbl_layout = QHBoxLayout()
        lbl_layout.addWidget(buyer_lbl)
        lbl_layout.addWidget(self.buyer_lbl_sel)
        lbl_layout.addWidget(item_lbl)
        lbl_layout.addWidget(self.item_lbl_sel)
        
        # 물품 리스트
        self.item_list = QComboBox(self)
        self.item_list.activated[str].connect(self.onActivatedItem)
        self.item_list.setFixedSize(200,20)

        # 물품 검색 버튼
        item_btn_sel = QPushButton('물품 검색')
        item_btn_sel.clicked.connect(self.itemSelBtnClicked)

        # 물품 검색 라인
        self.item_find = QLineEdit(self)
        self.item_find.setFixedSize(220,20)

        # 물품 추가 버튼
        item_btn = QPushButton('물품 추가')
        item_btn.clicked.connect(self.itemAddBtnClicked)

        # grid 레이아웃 배치
        grid.addWidget(buyer_list,0,0)
        grid.addLayout(lbl_layout,0,5)
        grid.addWidget(buyer_btn,0,9)

        grid.addWidget(self.item_list,1,0)
        grid.addWidget(self.item_find,1,5)
        grid.addWidget(item_btn_sel,1,6)
        grid.addWidget(qt_lbl,1,7)
        grid.addWidget(self.item_qt,1,8)
        grid.addWidget(item_btn,1,9)

        grid.setColumnStretch(0,5)
        grid.setColumnStretch(5,3)
        grid.setColumnStretch(8,2)
        
        # 테이블 
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setRowCount(20)

        
        column_headers = ['물품',"구입 가격",'용량',"판매 가격",'구입처','수량']
        self.table.setHorizontalHeaderLabels(column_headers)


        main.addLayout(grid)
        main.addWidget(self.table)

        self.setLayout(main)

    def itemSelBtnClicked(self):
        itemname = self.item_find.text()

        self.item_list.clear()
       
        with con.cursor() as curs:
            sql = """ SELECT prod_name FROM product"""
            curs.execute(sql)

            name = curs.fetchall()
            for v in name:
                if v[0].find(itemname) > -1:
                    self.item_list.addItem(v[0])
        con.commit()

    def itemAddBtnClicked(self):
        if self.buyer_name == '':
            QMessageBox.warning(self,'ERROR','거래처를 선택해주세요')
            return
        if self.item_qt.text() == '':
            QMessageBox.warning(self,'ERROR','수량을 입력해주세요')
            return
        
        with con.cursor() as curs:
                sql = """ SELECT * FROM product WHERE prod_name = %s"""
                curs.execute(sql, self.item_name)

                result = curs.fetchone()

                insert = list(result)
                total_pur = int(insert[1]) * int(self.item_qt.text())
                total_sale = int(insert[3]) * int(self.item_qt.text())
                insertsql = """
                        INSERT INTO buy VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                curs.execute(insertsql,(self.buyer_name,insert[0],insert[1],insert[2],insert[3],insert[4],self.item_qt.text(),total_pur,total_sale))
                QMessageBox.information(self,'물건 추가','물건이 추가되었습니다.')
        con.commit()
 
    def chit(self):
        with con.cursor() as curs:
            sql = """SELECT * FROM buy WHERE buyer_name = %s"""
            curs.execute(sql, self.buyer_name)

            result = curs.fetchall()

            for i in range(6):
                for k,v in enumerate(result):
                    s = list(v)
                    item = QTableWidgetItem(str(s[i+1]))
                    self.table.setItem(k,i,item)

        con.commit()
        
    def onActivatedBuyer(self,text):
        self.buyer_name = text
        self.buyer_lbl_sel.setText(text)
        QMessageBox.information(self,'거래처 선택 완료','거래처를 선택하셨습니다.')
        
    def onActivatedItem(self,text):
        self.item_name = text
        self.item_lbl_sel.setText(text)
        QMessageBox.information(self,'물품 선택 완료','물품을 선택하셨습니다.')

# 정보 확인 창
class startwindow(QDialog,QWidget):
    def __init__(self):
        
        super().__init__()
        self.initUI()
        self.setWindowIcon(QIcon(':image/power.png'))
        self.setWindowTitle('정보 확인')
        self.setGeometry(300,300,800,800)
        self.show()
    
    def initUI(self):    
        main = QHBoxLayout()
        btn = QVBoxLayout()

        self.textbox = QTextEdit(self)
        self.textbox.setFixedSize(600,800)

        prod_btn = QPushButton('물품 전체보기')
        prod_btn.clicked.connect(self.prodClicked)
        prod_btn.setFixedSize(200,200)

        buyer_btn = QPushButton('거래처 전체보기')
        buyer_btn.clicked.connect(self.buyerClicked)
        buyer_btn.setFixedSize(200,200)
       
        buy_btn = QPushButton('거래처 별 구매 목록 전체 보기')
        buy_btn.clicked.connect(self.buyClicked)
        buy_btn.setFixedSize(200,200)
        
        sum_btn = QPushButton('합계 매입액, 매출액 보기')
        sum_btn.clicked.connect(self.sumClicked)
        sum_btn.setFixedSize(200,200)

        btn.addWidget(prod_btn)
        btn.addWidget(buyer_btn)
        btn.addWidget(buy_btn)
        btn.addWidget(sum_btn)

        main.addWidget(self.textbox)
        main.addLayout(btn)
        
        self.setLayout(main)
           
    def prodClicked(self):
        self.textbox.clear()
        prodlookup = {0:'물품 : ',1:"구입 가격 : ", 2: '용량 : ', 3:"판매 가격 : ",4:'구입처 : '}
        with con.cursor() as curs:
            sql = "SELECT * FROM product"
            curs.execute(sql)

            result = curs.fetchall()
            for k,v in enumerate(result):
                self.textbox.insertPlainText(str(k) + ' : ' )
                for i in range(5):
                    self.textbox.insertPlainText(str(prodlookup[i]) + str(v[i]) + ' / ')
                self.textbox.insertPlainText('\n')
        con.commit()

    def buyerClicked(self):
        self.textbox.clear()
        buyerlookup = {0:'거래처 : ',1:"지역 : ", 2: '업종 : ', 3:"기타 사항 : "}
        with con.cursor() as curs:
            sql = "SELECT * FROM buyer"
            curs.execute(sql)

            result = curs.fetchall()
            for k,v in enumerate(result):
                self.textbox.insertPlainText(str(k) + ' : ' )
                for i in range(4):
                    self.textbox.insertPlainText(str(buyerlookup[i]) + str(v[i]) + ' / ')
                self.textbox.insertPlainText('\n')
        con.commit()

    def buyClicked(self):
        self.textbox.clear()
        buyerlookup = {0:'거래처 : ',1:"물품 : ", 2: '구입 가격 : ', 3:"용량 : ", 4:'판매가격 : ', 5:'구입처 : ', 6:'수량 : ', 7:'총 매입액 : ', 8:'총 매출액 : '}
        with con.cursor() as curs:
            sql = "SELECT * FROM buy"
            curs.execute(sql)

            result = curs.fetchall()
            for k,v in enumerate(result):
                self.textbox.insertPlainText(str(k) + ' : ' )
                for i in range(9):
                    if i == 6:
                        self.textbox.insertPlainText('\n') 
                    self.textbox.insertPlainText(str(buyerlookup[i]) + str(v[i]) + ' / ')
                self.textbox.insertPlainText('\n')
        con.commit()

    def sumClicked(self):
        self.textbox.clear()
        sumlist = []
        
        pursum = defaultdict(int)
        salesum = defaultdict(int)
        with con.cursor() as curs:
            sql = """SELECT buyer_name, total_pur, total_sale FROM buy"""
            curs.execute(sql)
            result = curs.fetchall()
            print(result)
           
            for k in result:
                sumlist.append(k[0])

            sparelist = set(sumlist)
            sumlist = sparelist
            
            for v in result:    
                 pursum[v[0]] += v[1]
                 salesum[v[0]] += v[2]
         
            for i in sumlist:
                self.textbox.insertPlainText(i +' => '+ '합계 매입액 : ' + str(pursum[i]) + ' , ' + '합계 매출액 : ' + str(salesum[i]) + ' , ' + '총 이익 : ' + str(salesum[i] - pursum[i]) + '\n')
        con.commit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = main()
    sys.exit(app.exec_())
    con.close()
