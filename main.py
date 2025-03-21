import os, sys, requests, zipfile, subprocess
from datetime import (
    date
)
from PyQt6.QtCore import (
    QDate, Qt, QSize
)
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, 
    QTableWidget, QTableWidgetItem, QStackedWidget, QLabel, QFrame,
    QScrollArea, QFormLayout, QHBoxLayout, QDialog, QDialogButtonBox, QMessageBox,
    QDateEdit, QComboBox, QSpinBox, QDoubleSpinBox, QHeaderView, QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import (
    QLinearGradient, QBrush, QPalette, QPixmap, QColor, QPainter
)
from db import Database
from config import APP_VERSION

class GradientBackground(QWidget):

    def __init__(self):
        super().__init__()
        self.setObjectName("gradientBackground")

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#1E3A8A"))
        gradient.setColorAt(1, QColor("#C71585"))
        painter.fillRect(self.rect(), QBrush(gradient))


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestionale Clienti e Dipendenti")
        self.setGeometry(100, 100, 1000, 600)
        
        self.stack = QStackedWidget()
        self.db = None
        self.currentAppVersion = APP_VERSION
        
        self.login_screen = LoginScreen(self.stack, self, self.currentAppVersion)
        self.stack.addWidget(self.login_screen)
        
        layout = QVBoxLayout()

        self.stack.setCurrentWidget(self.login_screen)
        
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self.load_styles()
        
    def load_styles(self):
        with open("styles/login_style.qss", "r") as f:
            self.setStyleSheet(f.read())

    def try_login(self, password):
        try:
            self.db = Database(password)

            self.current_user = self.db.get_current_user()
            print(f"Utente attualmente connesso: {self.current_user}")

            self.updatedInformation = self.db.get_updates()
            self.updatedAppVersion = self.updatedInformation[0]
            self.isAppUpdated = self.check_for_updates()

            if(self.isAppUpdated is False):
                QMessageBox.information(
                    self,
                    "Aggiornamento Disponibile",
                    "Il programma deve essere aggiornato alla versione più recente.",
                )
                self.download_update()

            self.menu_screen = MenuScreen(self.stack, self.db, self.current_user)
            self.stack.addWidget(self.menu_screen)
            self.stack.setCurrentWidget(self.menu_screen)

            return True
        except Exception as e:
            print(f"Errore di login: {e}")
            return False
        
    def check_for_updates(self):
        if str(self.currentAppVersion) == str(self.updatedAppVersion):
            return True
        else:
            return False
        
    def download_update(self):
        self.updateURL = str(self.updatedInformation[1])
        self.updateFile = "OMRService.zip"

        print("Scaricando l'aggiornamento...")
        response = requests.get(self.updateURL, stream=True)
        with open(self.updateFile, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print("Download completato!")
        print("Avvio l'aggiornamento...")
        subprocess.Popen(["updater.exe"], creationflags=subprocess.CREATE_NO_WINDOW)
        sys.exit()

    def extract_update(self):
        self.updateFolder = "temp_update"
        print("Estrazione dei file...")
        with zipfile.ZipFile(self.updateFile, "r") as zip_ref:
            zip_ref.extractall(self.updateFolder)
        print("File estratti!")

        for file_name in os.listdir(self.updateFolder):
            src = os.path.join(self.updateFolder, file_name)
            dest = os.path.join(os.getcwd(), file_name)
            os.replace(src, dest)

        print("Aggiornamento completato!")
        

class LoginScreen(GradientBackground):
    def __init__(self, stack, main_app, currentAppVersion):
        super().__init__()

        self.stack = stack
        self.main_app = main_app
        self.setObjectName("loginScreen")
        self.layout = QVBoxLayout()

        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.layout.addItem(spacer)

        self.container = QFrame()
        self.container.setObjectName("loginContainer")
        container_layout = QVBoxLayout()
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.logo_label = QLabel(self)
        pixmap = QPixmap("styles/images/icon.png")
        logo_size = QSize(150, 150)
        pixmap = pixmap.scaled(logo_size, Qt.AspectRatioMode.KeepAspectRatio)
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.login_box = QFrame()
        self.login_box.setObjectName("loginBox")
        self.login_box.setFixedSize(300, 200)
        login_layout = QVBoxLayout()
        login_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title = QLabel("Accedi")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_layout.addWidget(self.title)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_layout.addWidget(self.password_input)

        self.login_button = QPushButton("Accedi")
        self.login_button.setObjectName("loginButton")
        self.login_button.clicked.connect(self.login)
        login_layout.addWidget(self.login_button)

        self.container.setLayout(container_layout)
        self.layout.addWidget(self.container, alignment=Qt.AlignmentFlag.AlignCenter)

        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.layout.addItem(spacer)

        version_frame = QFrame()
        version_frame.setObjectName("versionFrame")
        version_layout = QHBoxLayout(version_frame)
        version_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.version_label = QLabel(f"v {currentAppVersion}")
        self.version_label.setObjectName("versionLabel")
        self.version_label.setStyleSheet("color: black; font-size: 12px; margin-right: 10px;")
        version_layout.addWidget(self.version_label)

        self.login_box.setLayout(login_layout)
        container_layout.addWidget(self.login_box, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.layout.addWidget(version_frame)
        self.setLayout(self.layout)

    def login(self):
        password = self.password_input.text()

        if not password:
            self.show_error("Password obbligatoria")
            return
        
        success = self.main_app.try_login(password)
        if success:
            print("Login effettuato")
        else:
            self.show_error("Password non valida")

    def show_error(self, message):
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Icon.Warning)
        error_box.setWindowTitle("Errore di Login")
        error_box.setText(message)
        error_box.exec()


class MenuScreen(GradientBackground):
    def __init__(self, stack, db, current_user):
        super().__init__()
        self.stack = stack
        self.db = db
        self.current_user = current_user
        if self.current_user == "admin" or self.current_user == "access":
            self.client_screen = ClientScreen(self.stack, self, self.db)
            self.stack.addWidget(self.client_screen)

        self.dipendenti_screen = DipendentiScreen(self.stack, self, self.db)
        self.stack.addWidget(self.dipendenti_screen)

        self.init_ui()

    def init_ui(self):
        with open("styles/menuscreen.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.layout = QVBoxLayout()

        menu_outer_frame = QFrame(self)
        menu_outer_frame.setObjectName("menuContainer")
        menu_outer_layout = QVBoxLayout(menu_outer_frame)
        menu_outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.logo_label = QLabel(self)
        pixmap = QPixmap("styles/images/icon.png")
        logo_size = QSize(150, 150)
        pixmap = pixmap.scaled(logo_size, Qt.AspectRatioMode.KeepAspectRatio)
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        menu_outer_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)

        menu_box_frame = QFrame(self)
        menu_box_frame.setObjectName("menuBox")
        menu_box_layout = QVBoxLayout(menu_box_frame)
        menu_box_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if self.current_user == "admin" or self.current_user == "access":
            self.client_button = QPushButton("Clienti")
            self.client_button.setObjectName("clientButton")
            self.client_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.client_screen))
            menu_box_layout.addWidget(self.client_button)

        self.dipendenti_button = QPushButton("Dipendenti")
        self.dipendenti_button.setObjectName("dipendentiButton")
        self.dipendenti_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.dipendenti_screen))
        menu_box_layout.addWidget(self.dipendenti_button)

        menu_box_frame.setLayout(menu_box_layout)
        menu_outer_layout.addWidget(menu_box_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        menu_outer_frame.setLayout(menu_outer_layout)
        self.layout.addWidget(menu_outer_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.layout)


class ClientScreen(GradientBackground):
    def __init__(self, stack, menu_screen, db):
        super().__init__()
        self.layout = QVBoxLayout()
        
        self.stack = stack
        self.menu_screen = menu_screen
        self.db = db
        self.current_table = None

        with open("styles/visualizationScreen.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.client_container = QFrame(self)
        self.client_container.setObjectName("clientContainer")
        self.client_layout = QVBoxLayout(self.client_container)

        self.title = QLabel("Lista Clienti")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.client_layout.addWidget(self.title)

        self.top_layout = QHBoxLayout()

        self.back_button = QPushButton("←")
        self.back_button.setObjectName("backButton")
        self.back_button.setFixedWidth(40)
        self.back_button.clicked.connect(self.go_back)
        self.top_layout.addWidget(self.back_button)

        self.search_box = QLineEdit()
        self.search_box.setObjectName("searchBox")
        self.search_box.setPlaceholderText("Cerca cliente...")
        self.search_box.textChanged.connect(self.update_clients)
        self.top_layout.addWidget(self.search_box)

        self.client_layout.addLayout(self.top_layout)

        self.filter_layout = QHBoxLayout()

        self.fixed_button = QPushButton("Fissi")
        self.fixed_button.setObjectName("fixedButton")
        self.fixed_button.setCheckable(True)
        self.fixed_button.clicked.connect(lambda: self.change_table("clienti_fissi"))

        self.temporary_button = QPushButton("Occasionali")
        self.temporary_button.setObjectName("temporaryButton")
        self.temporary_button.setCheckable(True)
        self.temporary_button.clicked.connect(lambda: self.change_table("clienti_occasionali"))

        self.filter_layout.addWidget(self.fixed_button)
        self.filter_layout.addWidget(self.temporary_button)

        self.client_layout.addLayout(self.filter_layout)

        self.client_table = QTableWidget()
        self.client_table.setObjectName("clientTable")
        self.client_table.setColumnCount(5)
        self.client_table.setHorizontalHeaderLabels(["ID", "Denominazione", "Codice Fiscale", "Email", "Data Inizio Contratto"])
        self.client_table.horizontalHeader().setStretchLastSection(False)
        self.client_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.client_table.cellClicked.connect(self.show_client_details)
        self.client_layout.addWidget(self.client_table)

        self.button_layout = QHBoxLayout()

        self.add_client_button = QPushButton("Aggiungi Cliente")
        self.add_client_button.setObjectName("addClientButton")
        self.add_client_button.clicked.connect(self.open_add_client_dialog)
        self.button_layout.addWidget(self.add_client_button)

        self.client_layout.addLayout(self.button_layout)

        self.layout.addWidget(self.client_container)
        self.setLayout(self.layout)
        
    
    def go_back(self):
        self.stack.setCurrentWidget(self.menu_screen)

    def change_table(self, table_name):
        self.current_table = table_name
        self.fixed_button.setChecked(table_name == "clienti_fissi")
        self.temporary_button.setChecked(table_name == "clienti_occasionali")
        self.load_clients()
        self.update_clients()

    def load_clients(self):
        self.all_clients = self.db.get_all(self.current_table)

    def update_clients(self):
        if(self.current_table is None):
            return
        query = self.search_box.text().lower()
        self.client_table.setRowCount(0)

        for client in self.all_clients:
            name = f"{client[1]} {client[5]} {client[10]} {client[13]}"

            if not query or query in name.lower():
                self.add_client_to_table(client)


    def add_client_to_table(self, client):
        row_position = self.client_table.rowCount()
        self.client_table.insertRow(row_position)

        self.client_table.setItem(row_position, 0, QTableWidgetItem(str(client[0])))
        self.client_table.setItem(row_position, 1, QTableWidgetItem(client[1]))
        self.client_table.setItem(row_position, 2, QTableWidgetItem(client[5]))
        self.client_table.setItem(row_position, 3, QTableWidgetItem(client[10]))
        self.client_table.setItem(row_position, 4, QTableWidgetItem(str(client[13])))

    def show_client_details(self, row, column):
        client_id = int(self.client_table.item(row, 0).text())
        
        client_data, field_names = self.db.get_record_by_id(self.current_table, "Id_cliente", client_id)
        
        if client_data:
            self.details_window = ClientDetailsWindow(client_data, field_names, self.db, self.current_table, self)
            self.details_window.show()

    def open_add_client_dialog(self):
        if(self.current_table is None):
            return
        self.add_client_window = AddClientDialog(self.db, self.current_table, self)
        self.add_client_window.exec()


class AddClientDialog(QDialog):
    def __init__(self, db, current_table, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aggiungi Cliente")
        self.setGeometry(300, 300, 900, 550)

        self.db = db
        self.parent = parent
        self.current_table = current_table

        with open("styles/add_edit.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.layout = QVBoxLayout()

        self.fields_info = self.db.get_table_fields(self.current_table, "Id_cliente")
        self.input_fields = {}

        main_container = QFrame(self)
        main_container.setObjectName("mainContainer")
        main_layout = QVBoxLayout(main_container)

        form_layout = QFormLayout()
        row_layout = QHBoxLayout()

        for idx, (field_name, field_type, enum_values, max_length) in enumerate(self.fields_info):
            if field_type == "date":  
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setDate(QDate.currentDate())
            elif field_type == "int" or field_type == "smallint":
                widget = QSpinBox()
                widget.setMaximum(99999999)
            elif field_type == "decimal" or field_type == "float":
                widget = QDoubleSpinBox()
                widget.setDecimals(2)
                widget.setMaximum(999999.99)
            elif field_type == "enum" and enum_values:
                widget = QComboBox()
                widget.addItems(enum_values)
            else:
                widget = QLineEdit()
                if max_length:
                    widget.setMaxLength(max_length)
                    if(max_length < 255):
                        widget.setPlaceholderText(f"Massimo {max_length} caratteri")

            label_name = QLabel(f"{field_name}:")
            row_layout.addWidget(label_name)
            row_layout.addWidget(widget)
            row_layout.addItem(QSpacerItem(100, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
            self.input_fields[field_name] = widget

            if (idx + 1) % 2 == 0:
                form_layout.addRow(row_layout)
                row_layout = QHBoxLayout()

        if len(self.fields_info) % 2 != 0:
            form_layout.addRow(row_layout)

        main_layout.addLayout(form_layout)

        self.button_layout = QHBoxLayout()

        self.save_button = QPushButton("Salva")
        self.save_button.setObjectName("saveClientButton")
        self.save_button.clicked.connect(self.save_client)
        self.button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancella")
        self.cancel_button.setObjectName("cancelClientButton")
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(self.button_layout)

        self.layout.addWidget(main_container)

        self.setLayout(self.layout)

    def save_client(self):
        new_client_data = {}
        for field_name, field_type, _, _ in self.fields_info:
            widget = self.input_fields[field_name]
            if isinstance(widget, QDateEdit):
                new_client_data[field_name] = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox) or isinstance(widget, QComboBox):
                new_client_data[field_name] = widget.currentText() if isinstance(widget, QComboBox) else widget.value()
            else:
                new_client_data[field_name] = widget.text()

        self.db.add_record(self.current_table, new_client_data, "Id_cliente")
        self.parent.all_clients = self.db.get_all(self.current_table)
        self.parent.update_clients()
        self.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#1E3A8A"))
        gradient.setColorAt(1, QColor("#C71585"))
        painter.fillRect(self.rect(), QBrush(gradient))


class ClientDetailsWindow(GradientBackground):
    def __init__(self, client_data, field_names, db, current_table, parent):
        super().__init__()
        self.setWindowTitle("Dettagli Cliente")
        self.setGeometry(200, 200, 650, 700)
        
        self.db = db
        self.current_table = current_table
        self.parent = parent
        self.client_id = client_data[0]
        self.client_data = client_data
        self.field_names = field_names

        with open("styles/detailsScreen.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.layout = QVBoxLayout()

        self.details_container = QFrame(self)
        self.details_container.setObjectName("detailsContainer")
        self.details_layout = QVBoxLayout(self.details_container)

        self.title = QLabel("Dettagli Cliente")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details_layout.addWidget(self.title)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("scrollWidget")
        self.scroll_layout = QVBoxLayout(self.scroll_widget)

        self.create_client_details()

        self.scroll_area.setWidget(self.scroll_widget)
        self.details_layout.addWidget(self.scroll_area)
        
        self.button_layout = QHBoxLayout()
        self.edit_button = QPushButton("Modifica")
        self.edit_button.setObjectName("editButton")
        self.edit_button.clicked.connect(self.open_edit_dialog)
        self.button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Elimina")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self.confirm_delete)
        self.button_layout.addWidget(self.delete_button)

        self.details_layout.addLayout(self.button_layout)
        self.layout.addWidget(self.details_container)
        self.setLayout(self.layout)

    def create_client_details(self):
        row_layout = QHBoxLayout()

        for idx, (field, value) in enumerate(zip(self.field_names, self.client_data)):
            if field in ["Ultima_fattura", "Fattura"]:
                continue

            label_name = QLabel(f"<b>{field}:</b>")
            label_name.setObjectName("labelName")
            label_value = QLabel(str(value))
            label_value.setObjectName("labelValue")

            row_layout.addWidget(label_name)
            row_layout.addWidget(label_value)

            if idx % 2 != 0:
                self.scroll_layout.addLayout(row_layout)
                row_layout = QHBoxLayout()

        self.neededclient = "Id_cliente_fisso" if self.current_table == "clienti_fissi" else "Id_cliente_occasionale"
        invoice_label_text = "Ultima Fattura:" if self.current_table == "clienti_fissi" else "Fattura:"

        self.invoice_number = self.db.get_invoices(self.client_id, self.neededclient)
        if self.invoice_number is None:
            self.invoice_number = "Nessuna Fattura Registrata"

        invoice_layout = QHBoxLayout()
        invoice_label = QLabel(f"<b>{invoice_label_text}</b>")
        invoice_label.setObjectName("invoiceLabel")
        self.invoice_value = QLabel(self.invoice_number)
        self.invoice_value.setObjectName("invoiceValue")

        invoice_layout.addWidget(invoice_label)
        invoice_layout.addWidget(self.invoice_value)

        self.add_invoice_button = QPushButton("Aggiungi Fattura")
        self.add_invoice_button.setObjectName("addInvoiceButton")
        self.add_invoice_button.clicked.connect(self.open_add_invoice_dialog)

        self.view_invoices_button = QPushButton("Vedi Fatture")
        self.view_invoices_button.setObjectName("viewInvoicesButton")
        self.view_invoices_button.clicked.connect(self.open_invoice_list)

        invoice_layout.addWidget(self.add_invoice_button)
        invoice_layout.addWidget(self.view_invoices_button)

        self.scroll_layout.addLayout(invoice_layout)


    def open_edit_dialog(self):
        self.edit_window = EditClientDialog(self.db, self.client_id, self.client_data, self.field_names, self.current_table, self.parent)
        self.edit_window.exec()

    def confirm_delete(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText("Sei sicuro di voler eliminare questo cliente?")
        msg.setWindowTitle("Conferma eliminazione")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        response = msg.exec()
        if response == QMessageBox.StandardButton.Yes:
            self.db.delete_record(self.current_table, "Id_cliente", self.client_id)
            self.parent.all_clients = self.db.get_all(self.current_table)
            self.parent.update_clients()
            self.close()

    def open_add_invoice_dialog(self):
        dialog = AddInvoiceDialog(self.db, self.client_id, self.neededclient, self)
        dialog.exec()

    def open_invoice_list(self):
        self.invoice_window = InvoiceListWindow(self.db, self.client_id, self.neededclient)
        self.invoice_window.show()

    def update_invoice_info(self):
        self.invoice_number = self.db.get_invoices(self.client_id, self.neededclient)
        if self.invoice_number is None:
            self.invoice_number = "Nessuna Fattura Registrata"

        self.invoice_value.setText(self.invoice_number)
        
        self.update()


class EditClientDialog(QDialog):
    def __init__(self, db, client_id, client_data, field_names, current_table, parent=None):
        super().__init__()
        self.setWindowTitle("Modifica Cliente")
        self.setGeometry(300, 300, 900, 550)

        self.db = db
        self.client_id = client_id
        self.current_table = current_table
        self.parent = parent
        self.layout = QVBoxLayout()

        with open("styles/add_edit.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.fields_info = self.db.get_table_fields(self.current_table, "Id_cliente")
        self.input_fields = {}

        client_data_dict = dict(zip(field_names, client_data))

        main_container = QFrame(self)
        main_container.setObjectName("mainContainer")
        main_layout = QVBoxLayout(main_container)

        form_layout = QFormLayout()
        row_layout = QHBoxLayout()

        for idx, (field_name, field_type, enum_values, max_length) in enumerate(self.fields_info):
            value = client_data_dict.get(field_name)

            label_name = QLabel(f"{field_name}:")
            label_name.setObjectName("labelName")

            if field_type == "date":
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setObjectName("inputField")
                if value and isinstance(value, date):
                    date_str = value.strftime("%Y-%m-%d")
                    qdate = QDate.fromString(date_str, "yyyy-MM-dd")
                    widget.setDate(qdate)
                else:
                    widget.setDate(QDate.currentDate())

            elif field_type in ["int", "smallint"]:
                widget = QSpinBox()
                widget.setMaximum(99999999)
                widget.setValue(int(value) if value else 0)
                widget.setObjectName("inputField")

            elif field_type in ["decimal", "float"]:
                widget = QDoubleSpinBox()
                widget.setDecimals(2)
                widget.setMaximum(999999.99)
                widget.setValue(float(value) if value else 0.0)
                widget.setObjectName("inputField")

            elif field_type == "enum" and enum_values:
                widget = QComboBox()
                widget.addItems(enum_values)
                widget.setCurrentText(value if value else enum_values[0])
                widget.setObjectName("inputField")

            else:
                widget = QLineEdit(str(value) if value else "")
                widget.setObjectName("inputField")
                if max_length:
                    widget.setMaxLength(max_length)
                    if(max_length < 255):
                        print("ok")
                        widget.setPlaceholderText(f"Massimo {max_length} caratteri")

            row_layout.addWidget(label_name)
            row_layout.addWidget(widget)
            row_layout.addItem(QSpacerItem(100, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
            self.input_fields[field_name] = widget

            if (idx + 1) % 2 == 0:
                form_layout.addRow(row_layout)
                row_layout = QHBoxLayout()

        if len(self.fields_info) % 2 != 0:
            form_layout.addRow(row_layout)

        main_layout.addLayout(form_layout)

        self.button_layout = QHBoxLayout()

        self.save_button = QPushButton("Salva")
        self.save_button.setObjectName("saveClientButton")
        self.save_button.clicked.connect(self.update_client)
        self.button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancella")
        self.cancel_button.setObjectName("cancelClientButton")
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(self.button_layout)

        self.layout.addWidget(main_container)
    
        self.setLayout(self.layout)

    def update_client(self):
        updated_data = {}
        for field_name, field_type, _, _ in self.fields_info:
            widget = self.input_fields[field_name]
            if isinstance(widget, QDateEdit):
                updated_data[field_name] = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox, QComboBox)):
                updated_data[field_name] = widget.currentText() if isinstance(widget, QComboBox) else widget.value()
            else:
                updated_data[field_name] = widget.text()

        self.db.update_record(self.current_table, "Id_cliente", self.client_id, updated_data)
        self.parent.all_clients = self.db.get_all(self.current_table)
        self.parent.update_clients()
        self.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#1E3A8A"))
        gradient.setColorAt(1, QColor("#C71585"))
        painter.fillRect(self.rect(), QBrush(gradient))


class AddInvoiceDialog(QDialog):
    def __init__(self, db, client_id, client_type, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aggiungi Fattura")
        self.setGeometry(300, 300, 400, 400)

        self.db = db
        self.client_id = client_id
        self.client_type = client_type
        self.parent = parent
        self.layout = QVBoxLayout()

        with open("styles/add_edit.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.client_column = self.client_type

        self.fields_info = [
            (name, data_type, enum_values, max_length)
            for name, data_type, enum_values, max_length in self.db.get_table_fields("fatture")
            if name not in [self.client_column]
        ]

        self.input_fields = {}

        main_container = QFrame(self)
        main_container.setObjectName("mainContainer")
        main_layout = QVBoxLayout(main_container)

        form_layout = QFormLayout()
        for field_name, field_type, enum_values, max_length in self.fields_info:
            if(field_name == "Id_cliente_occasionale" or field_name == "Id_cliente_fisso"):
                continue
            if field_type == "date":
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setDate(QDate.currentDate())
            elif field_type in ["int", "smallint"]:
                widget = QSpinBox()
                widget.setMaximum(99999999)
            elif field_type in ["decimal", "float"]:
                widget = QDoubleSpinBox()
                widget.setDecimals(2)
                widget.setMaximum(999999.99)
            elif field_type == "enum" and enum_values:
                widget = QComboBox()
                widget.addItems(enum_values)
            else:
                widget = QLineEdit()
                if max_length:
                    widget.setMaxLength(max_length)
                    if(max_length < 255):
                        widget.setPlaceholderText(f"Massimo {max_length} caratteri")

            label_name = QLabel(f"{field_name}:")
            form_layout.addRow(label_name, widget)
            self.input_fields[field_name] = widget

        main_layout.addLayout(form_layout)

        self.button_layout = QHBoxLayout()

        self.save_button = QPushButton("Salva")
        self.save_button.setObjectName("saveInvoiceButton")
        self.save_button.clicked.connect(self.save_invoice)
        self.button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancella")
        self.cancel_button.setObjectName("cancelInvoiceButton")
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(self.button_layout)

        self.layout.addWidget(main_container)

        self.setLayout(self.layout)

    def save_invoice(self):
        new_invoice_data = {}
        for field_name, field_type, _, _ in self.fields_info:
            if(field_name == "Id_cliente_occasionale" or field_name == "Id_cliente_fisso"):
                new_invoice_data[field_name] = None
                continue
            widget = self.input_fields[field_name]
            if isinstance(widget, QDateEdit):
                new_invoice_data[field_name] = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                new_invoice_data[field_name] = widget.value()
            elif isinstance(widget, QComboBox):
                new_invoice_data[field_name] = widget.currentText()
            else:
                new_invoice_data[field_name] = widget.text()

        new_invoice_data[self.client_column] = self.client_id

        self.db.add_record("fatture", new_invoice_data, "")
        self.accept()
        self.parent.update_invoice_info()

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#1E3A8A"))
        gradient.setColorAt(1, QColor("#C71585"))
        painter.fillRect(self.rect(), QBrush(gradient))


class InvoiceListWindow(GradientBackground):
    def __init__(self, db, client_id, client_type):
        super().__init__()
        self.setWindowTitle("Fatture del Cliente")
        self.setGeometry(300, 200, 500, 400)
        self.db = db
        self.client_id = client_id
        self.client_type = client_type

        with open("styles/invoicesscreen.qss", "r") as f:
            self.setStyleSheet(f.read())

        
        self.layout = QVBoxLayout()

        self.invoices_container = QFrame(self)
        self.invoices_container.setObjectName("invoicesContainer")
        self.invoices_layout = QVBoxLayout(self.invoices_container)

        self.search_box = QLineEdit()
        self.search_box.setObjectName("searchBox")
        self.search_box.setPlaceholderText("Cerca fattura...")
        self.search_box.textChanged.connect(self.update_invoices)
        self.invoices_layout.addWidget(self.search_box)

        self.invoice_table = QTableWidget()
        self.invoice_table.setObjectName("invoicesTable")
        self.invoice_table.setColumnCount(3)
        self.invoice_table.setHorizontalHeaderLabels(["Numero Fattura", "Data", "Importo"])
        self.invoice_table.horizontalHeader().setStretchLastSection(False)
        self.invoice_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.invoice_table.cellClicked.connect(self.show_invoice_details)
        self.invoices_layout.addWidget(self.invoice_table)

        self.all_invoices = self.db.get_invoices_list(self.client_id, self.client_type)
        self.update_invoices()

        self.layout.addWidget(self.invoices_container)
        self.setLayout(self.layout)

    def update_invoices(self):
        query = self.search_box.text().lower()
        self.invoice_table.setRowCount(0)

        for invoice in self.all_invoices:
            invoice_number = str(invoice[0])
            invoice_date = str(invoice[1])
            invoice_amount = f"€{invoice[2]:.2f}"

            if not query or query in invoice_number.lower() or query in invoice_date.lower() or query in invoice_amount.lower():
                self.add_invoice_to_table(invoice)
                

    def add_invoice_to_table(self, invoice):
        row_position = self.invoice_table.rowCount()
        self.invoice_table.insertRow(row_position)
        self.invoice_table.setItem(row_position, 0, QTableWidgetItem(invoice[0]))
        self.invoice_table.setItem(row_position, 1, QTableWidgetItem(str(invoice[1])))
        self.invoice_table.setItem(row_position, 2, QTableWidgetItem(str(invoice[2])))
        

    def show_invoice_details(self, row, column):
        invoice_number = self.invoice_table.item(row, 0).text()
        invoice_data, field_names = self.db.get_record_by_id("fatture", "Numero_fattura", invoice_number)

        if invoice_data:
            self.details_window = InvoiceDetailsWindow(invoice_data, field_names, self.db, self)
            self.details_window.show()


class InvoiceDetailsWindow(GradientBackground):
    def __init__(self, invoice_data, field_names, db, parent):
        super().__init__()
        self.setWindowTitle("Dettagli Fattura")
        self.setGeometry(350, 250, 500, 400)

        self.db = db
        self.parent = parent
        self.invoice_number = invoice_data[0]
        self.field_names = field_names
        self.invoice_data = invoice_data

        with open("styles/detailsScreen.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.layout = QVBoxLayout()

        self.details_container = QFrame(self)
        self.details_container.setObjectName("detailsContainer")
        self.details_layout = QVBoxLayout(self.details_container)

        self.title = QLabel("Dettagli Fattura")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details_layout.addWidget(self.title)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("scrollWidget")
        self.scroll_layout = QVBoxLayout(self.scroll_widget)

        self.create_invoice_details()

        self.scroll_area.setWidget(self.scroll_widget)
        self.details_layout.addWidget(self.scroll_area)

        self.button_layout = QHBoxLayout()
        self.edit_button = QPushButton("Modifica")
        self.edit_button.setObjectName("editButton")
        self.edit_button.clicked.connect(self.edit_invoice)
        self.button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Elimina")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self.delete_invoice)
        self.button_layout.addWidget(self.delete_button)

        self.details_layout.addLayout(self.button_layout)
        self.layout.addWidget(self.details_container)
        self.setLayout(self.layout)

    def create_invoice_details(self):
        column_layout = QVBoxLayout()

        for idx, (field, value) in enumerate(zip(self.field_names, self.invoice_data)):
            if (field == "Id_cliente_fisso") or (field == "Id_cliente_occasionale"):
                continue
            label_name = QLabel(f"<b>{field}:</b>")
            label_name.setObjectName("labelName")
            label_value = QLabel(str(value))
            label_value.setObjectName("labelValue")

            column_layout.addWidget(label_name)
            column_layout.addWidget(label_value)

            self.scroll_layout.addLayout(column_layout)

    def edit_invoice(self):
        self.edit_window = EditInvoiceDialog(self.db, self.invoice_number, self.invoice_data, self.field_names, self.parent.client_id, self.parent.client_type, self.parent)
        self.edit_window.exec()

    def delete_invoice(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText("Sei sicuro di voler eliminare questa fattura?")
        msg.setWindowTitle("Conferma eliminazione")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        response = msg.exec()
        if response == QMessageBox.StandardButton.Yes:
            self.db.delete_record("fatture", "Numero_fattura", self.invoice_number)
            self.parent.all_invoices = self.db.get_invoices_list(self.parent.client_id, self.parent.client_type)
            self.parent.update_invoices()
            self.close()


class EditInvoiceDialog(QDialog):
    def __init__(self, db, invoice_number, invoice_data, field_names, client_id, client_type, parent):
        super().__init__(parent)
        self.setWindowTitle("Modifica Fattura")
        self.setGeometry(300, 300, 400, 300)

        self.db = db
        self.invoice_number = invoice_number
        self.client_id = client_id
        self.client_type = client_type
        self.parent = parent
        self.layout = QVBoxLayout()

        with open("styles/add_edit.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.fields_info = self.db.get_table_fields("fatture")  
        self.input_fields = {}

        invoice_data_dict = dict(zip(field_names, invoice_data))

        main_container = QFrame(self)
        main_container.setObjectName("mainContainer")
        main_layout = QVBoxLayout(main_container)

        form_layout = QFormLayout()
        row_layout = QVBoxLayout()

        for idx, (field_name, field_type, enum_values, max_length) in enumerate(self.fields_info):
            if (field_name == "Id_cliente_fisso") or (field_name == "Id_cliente_occasionale"):
                continue
            value = invoice_data_dict.get(field_name)

            label_name = QLabel(f"{field_name}:")
            label_name.setObjectName("labelName")

            if field_type == "date":
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                if value and isinstance(value, date):
                    date_str = value.strftime("%Y-%m-%d")
                    qdate = QDate.fromString(date_str, "yyyy-MM-dd")
                    widget.setDate(qdate)
                else:
                    widget.setDate(QDate.currentDate())
            elif field_type == "decimal" or field_type == "float":
                widget = QDoubleSpinBox()
                widget.setDecimals(2)
                widget.setMaximum(999999.99)
                widget.setValue(float(value) if value else 0.0)
            else:
                widget = QLineEdit(str(value) if value else "")
                if max_length:
                    widget.setMaxLength(max_length)
                    if(max_length < 255):
                        widget.setPlaceholderText(f"Massimo {max_length} caratteri")

            row_layout.addWidget(label_name)
            row_layout.addWidget(widget)
            row_layout.addItem(QSpacerItem(100, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
            self.input_fields[field_name] = widget

            form_layout.addRow(row_layout)

        main_layout.addLayout(form_layout)

        self.button_layout = QHBoxLayout()

        self.save_button = QPushButton("Salva")
        self.save_button.setObjectName("saveInvoiceButton")
        self.save_button.clicked.connect(self.update_invoice)
        self.button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancella")
        self.cancel_button.setObjectName("cancelInvoiceButton")
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(self.button_layout)

        self.layout.addWidget(main_container)
    
        self.setLayout(self.layout)

    def update_invoice(self):
        updated_data = {}
        for field_name, field_type, _, _ in self.fields_info:
            if(field_name == "Id_cliente_fisso") or (field_name == "Id_cliente_occasionale"):
                continue
            widget = self.input_fields[field_name]
            if isinstance(widget, QDateEdit):
                updated_data[field_name] = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QDoubleSpinBox):
                updated_data[field_name] = widget.value()
            else:
                updated_data[field_name] = widget.text()

        self.db.update_record("fatture", "Numero_fattura", self.invoice_number, updated_data)
        self.parent.all_invoices = self.db.get_invoices_list(self.client_id, self.client_type)
        self.parent.update_invoices()
        self.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#1E3A8A"))
        gradient.setColorAt(1, QColor("#C71585"))
        painter.fillRect(self.rect(), QBrush(gradient))


class DipendentiScreen(GradientBackground):
    def __init__(self, stack, menu_screen, db):
        super().__init__()
        self.layout = QVBoxLayout()

        self.stack = stack
        self.menu_screen = menu_screen
        self.db = db

        self.current_table = "Fisso"

        with open("styles/visualizationScreen.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.dipendenti_container = QFrame(self)
        self.dipendenti_container.setObjectName("dipendentiContainer")
        self.dipendenti_layout = QVBoxLayout(self.dipendenti_container)

        self.title = QLabel("Lista Dipendenti")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dipendenti_layout.addWidget(self.title)

        self.top_layout = QHBoxLayout()

        self.back_button = QPushButton("←")
        self.back_button.setObjectName("backButton")
        self.back_button.setFixedWidth(40)
        self.back_button.clicked.connect(self.go_back)
        self.top_layout.addWidget(self.back_button)

        self.search_box = QLineEdit()
        self.search_box.setObjectName("searchBox")
        self.search_box.setPlaceholderText("Cerca dipendente...")
        self.search_box.textChanged.connect(self.update_dipendenti)
        self.top_layout.addWidget(self.search_box)

        self.dipendenti_layout.addLayout(self.top_layout)

        self.filter_layout = QHBoxLayout()

        self.fixed_button = QPushButton("Fissi")
        self.fixed_button.setObjectName("fixedButton")
        self.fixed_button.setCheckable(True)
        self.fixed_button.clicked.connect(lambda: self.change_table("Fisso"))

        self.temporary_button = QPushButton("Stagionali")
        self.temporary_button.setObjectName("temporaryButton")
        self.temporary_button.setCheckable(True)
        self.temporary_button.clicked.connect(lambda: self.change_table("Stagionale"))

        self.outsourcing_button = QPushButton("Outsourcing")
        self.outsourcing_button.setObjectName("outsourcingButton")
        self.outsourcing_button.setCheckable(True)
        self.outsourcing_button.clicked.connect(lambda: self.change_table("Outsourcing"))

        self.filter_layout.addWidget(self.fixed_button)
        self.filter_layout.addWidget(self.temporary_button)
        self.filter_layout.addWidget(self.outsourcing_button)

        self.dipendenti_layout.addLayout(self.filter_layout)

        # **Tabella dipendenti**
        self.dipendenti_table = QTableWidget()
        self.dipendenti_table.setColumnCount(5)
        self.dipendenti_table.setHorizontalHeaderLabels(["ID", "Nome", "Cognome", "Email", "Data Inizio Contratto"])
        self.dipendenti_table.horizontalHeader().setStretchLastSection(False)
        self.dipendenti_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.dipendenti_table.cellClicked.connect(self.show_dipendente_details)
        self.dipendenti_layout.addWidget(self.dipendenti_table)

        # **Pulsanti Mostra tutti e Aggiungi Dipendente**
        self.button_layout = QHBoxLayout()

        #self.show_all_button = QPushButton("Mostra tutti i dipendenti")
        #self.show_all_button.clicked.connect(self.toggle_all_dipendenti)
        #self.button_layout.addWidget(self.show_all_button)

        self.add_dipendente_button = QPushButton("Aggiungi Dipendente")
        self.add_dipendente_button.setObjectName("addDipendenteButton")
        self.add_dipendente_button.clicked.connect(self.open_add_dipendente_dialog)
        self.button_layout.addWidget(self.add_dipendente_button)

        self.dipendenti_layout.addLayout(self.button_layout)

        self.layout.addWidget(self.dipendenti_container)
        self.setLayout(self.layout)


    def go_back(self):
        self.stack.setCurrentWidget(self.menu_screen)

    def change_table(self, table_name):
        self.current_table = table_name
        self.fixed_button.setChecked(table_name == "Fisso")
        self.temporary_button.setChecked(table_name == "Stagionale")
        self.outsourcing_button.setChecked(table_name == "Outsourcing")
        self.load_dipendenti()
        self.update_dipendenti()

    def load_dipendenti(self):
        self.all_dipendenti = self.db.get_all("dipendenti")
        self.all_dipendenti = [dipendente for dipendente in self.all_dipendenti if dipendente[12] == self.current_table]

    def update_dipendenti(self):
        query = self.search_box.text().lower()
        self.dipendenti_table.setRowCount(0)

        for dipendente in self.all_dipendenti:
            name = f"{dipendente[1]} {dipendente[2]} {dipendente[6]} {dipendente[13]}".lower()

            if query in name:
                self.add_dipendente_to_table(dipendente)

    #def toggle_all_dipendenti(self):
    #    if self.showing_all:
    #        self.dipendenti_table.setRowCount(0)
    #        self.showing_all = False
    #        self.show_all_button.setText("Mostra tutti i dipendenti")
    #    else:
    #        self.dipendenti_table.setRowCount(0)
    #        for dipendente in self.all_dipendenti:
    #            self.add_dipendente_to_table(dipendente)

    #        self.showing_all = True
    #        self.show_all_button.setText("Nascondi tutti i dipendenti")

    def add_dipendente_to_table(self, dipendente):
        row_position = self.dipendenti_table.rowCount()
        self.dipendenti_table.insertRow(row_position)

        self.dipendenti_table.setItem(row_position, 0, QTableWidgetItem(str(dipendente[0])))  # ID
        self.dipendenti_table.setItem(row_position, 1, QTableWidgetItem(dipendente[1]))  # Nome
        self.dipendenti_table.setItem(row_position, 2, QTableWidgetItem(dipendente[2]))  # Cognome
        self.dipendenti_table.setItem(row_position, 3, QTableWidgetItem(dipendente[6]))  # Email
        self.dipendenti_table.setItem(row_position, 4, QTableWidgetItem(str(dipendente[13])))

    def show_dipendente_details(self, row, column):
        dipendente_id = int(self.dipendenti_table.item(row, 0).text())

        dipendente_data, field_names = self.db.get_record_by_id("dipendenti", "Id_dipendente", dipendente_id)

        if dipendente_data:
            self.details_window = DipendenteDetailsWindow(dipendente_data, field_names, self.db, self.current_table, self)
            self.details_window.show()

    def open_add_dipendente_dialog(self):
        self.add_dipendente_window = AddDipendenteDialog(self.db, self.current_table, self)
        self.add_dipendente_window.exec()


class AddDipendenteDialog(QDialog):
    def __init__(self, db, current_table, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aggiungi Dipendente")
        self.setGeometry(300, 300, 400, 400)

        self.db = db
        self.parent = parent
        self.current_table = current_table

        with open("styles/add_edit.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.layout = QVBoxLayout()

        self.fields_info = self.db.get_table_fields("dipendenti", "Id_dipendente")
        self.input_fields = {}

        main_container = QFrame(self)
        main_container.setObjectName("mainContainer")
        main_layout = QVBoxLayout(main_container)

        form_layout = QFormLayout()
        row_layout = QHBoxLayout()

        for idx, (field_name, field_type, enum_values, max_length) in enumerate(self.fields_info):
            if(field_name == "Nome_fornitore") and (self.current_table != "Outsourcing"):
                continue
            elif(field_name == "Tipologia_contratto"):
                widget = QComboBox()
                widget.addItem(self.current_table)
            elif field_type == "date":
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setDate(QDate.currentDate())
            elif field_type in ["int", "smallint"]:
                widget = QSpinBox()
                widget.setMaximum(99999999)
            elif field_type in ["decimal", "float"]:
                widget = QDoubleSpinBox()
                widget.setDecimals(2)
                widget.setMaximum(999999.99)
            elif field_type == "enum" and enum_values:
                widget = QComboBox()
                widget.addItems(enum_values)
            else:
                widget = QLineEdit()
                if max_length:
                    widget.setMaxLength(max_length)
                    if(max_length < 255):
                        widget.setPlaceholderText(f"Massimo {max_length} caratteri")

            label_name = QLabel(f"{field_name}:")
            row_layout.addWidget(label_name)
            row_layout.addWidget(widget)
            row_layout.addItem(QSpacerItem(100, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
            self.input_fields[field_name] = widget

            if (idx + 1) % 2 == 0:
                form_layout.addRow(row_layout)
                row_layout = QHBoxLayout()

        if len(self.fields_info) % 2 != 0:
            form_layout.addRow(row_layout)

        main_layout.addLayout(form_layout)

        self.button_layout = QHBoxLayout()

        self.save_button = QPushButton("Salva")
        self.save_button.setObjectName("saveDipendenteButton")
        self.save_button.clicked.connect(self.save_dipendente)
        self.button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancella")
        self.cancel_button.setObjectName("cancelDipendenteButton")
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(self.button_layout)

        self.layout.addWidget(main_container)

        self.setLayout(self.layout)

    def save_dipendente(self):
        new_dipendente_data = {}
        for field_name, field_type, _, _ in self.fields_info:
            if(field_name == "Nome_fornitore") and (self.current_table != "Outsourcing"):
                new_dipendente_data[field_name] = None
                continue
            widget = self.input_fields[field_name]
            if isinstance(widget, QDateEdit):
                new_dipendente_data[field_name] = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox, QComboBox)):
                new_dipendente_data[field_name] = widget.currentText() if isinstance(widget, QComboBox) else widget.value()
            else:
                new_dipendente_data[field_name] = widget.text()

        self.db.add_record("dipendenti", new_dipendente_data, "Id_dipendente")
        self.parent.load_dipendenti()
        self.parent.update_dipendenti()
        self.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#1E3A8A"))
        gradient.setColorAt(1, QColor("#C71585"))
        painter.fillRect(self.rect(), QBrush(gradient))


class DipendenteDetailsWindow(GradientBackground):
    def __init__(self, dipendente_data, field_names, db, current_table, parent):
        super().__init__()
        self.setWindowTitle("Dettagli Dipendente")
        self.setGeometry(200, 200, 650, 700)
        
        self.db = db
        self.current_table = current_table
        self.parent = parent
        self.dipendente_id = dipendente_data[0]
        self.dipendente_data = dipendente_data
        self.field_names = field_names

        with open("styles/detailsScreen.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.layout = QVBoxLayout()

        self.details_container = QFrame(self)
        self.details_container.setObjectName("detailsContainer")
        self.details_layout = QVBoxLayout(self.details_container)

        self.title = QLabel("Dettagli Dipendente")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details_layout.addWidget(self.title)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("scrollWidget")
        self.scroll_layout = QVBoxLayout(self.scroll_widget)

        self.create_dipendente_details()

        self.scroll_area.setWidget(self.scroll_widget)
        self.details_layout.addWidget(self.scroll_area)

        self.button_layout = QHBoxLayout()
        self.edit_button = QPushButton("Modifica")
        self.edit_button.setObjectName("editButton")
        self.edit_button.clicked.connect(self.open_edit_dialog)
        self.button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Elimina")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self.confirm_delete)
        self.button_layout.addWidget(self.delete_button)

        self.details_layout.addLayout(self.button_layout)
        self.layout.addWidget(self.details_container)
        self.setLayout(self.layout)

        self.dipendente_data = dipendente_data
        self.field_names = field_names

    def create_dipendente_details(self):
        row_layout = QHBoxLayout()

        for idx, (field, value) in enumerate(zip(self.field_names, self.dipendente_data)):
            if (field == "Nome_fornitore") and (self.current_table != "Outsourcing"):
                continue

            label_name = QLabel(f"<b>{field}:</b>")
            label_name.setObjectName("labelName")
            label_value = QLabel(str(value))
            label_value.setObjectName("labelValue")
                
            row_layout.addWidget(label_name)
            row_layout.addWidget(label_value)

            if idx % 2 != 0:
                self.scroll_layout.addLayout(row_layout)
                row_layout = QHBoxLayout()

    def open_edit_dialog(self):
        self.edit_window = EditDipendenteDialog(self.db, self.dipendente_id, self.dipendente_data, self.field_names, self.current_table, self.parent)
        self.edit_window.exec()

    def confirm_delete(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText("Sei sicuro di voler eliminare questo dipendente?")
        msg.setWindowTitle("Conferma eliminazione")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        response = msg.exec()
        if response == QMessageBox.StandardButton.Yes:
            self.db.delete_record("dipendenti", "Id_dipendente", self.dipendente_id)
            self.parent.load_dipendenti()
            self.parent.update_dipendenti()
            self.close()


class EditDipendenteDialog(QDialog):
    def __init__(self, db, dipendente_id, dipendente_data, field_names, current_table, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modifica Dipendente")
        self.setGeometry(300, 300, 400, 400)

        self.db = db
        self.dipendente_id = dipendente_id
        self.current_table = current_table
        self.parent = parent
        self.layout = QVBoxLayout()

        with open("styles/add_edit.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.fields_info = self.db.get_table_fields("dipendenti", "Id_dipendente")
        self.input_fields = {}

        dipendente_data_dict = dict(zip(field_names, dipendente_data))

        main_container = QFrame(self)
        main_container.setObjectName("mainContainer")
        main_layout = QVBoxLayout(main_container)

        form_layout = QFormLayout()
        row_layout = QHBoxLayout()

        for idx, (field_name, field_type, enum_values, max_length) in enumerate(self.fields_info):
            value = dipendente_data_dict.get(field_name)

            if(field_name == "Nome_fornitore") and (self.current_table != "Outsourcing"):
                continue

            label_name = QLabel(f"{field_name}:")
            label_name.setObjectName("labelName")

            if field_type == "date":
                widget = QDateEdit()  
                widget.setCalendarPopup(True)
                if value and isinstance(value, date):
                    date_str = value.strftime("%Y-%m-%d")
                    qdate = QDate.fromString(date_str, "yyyy-MM-dd")
                    widget.setDate(qdate)
                else:
                    widget.setDate(QDate.currentDate())
            elif field_type == "int" or field_type == "smallint":
                widget = QSpinBox()  
                widget.setMaximum(99999999)
                widget.setValue(int(value) if value else 0)
            elif field_type == "decimal" or field_type == "float":
                widget = QDoubleSpinBox()  
                widget.setDecimals(2)
                widget.setMaximum(999999.99)
                widget.setValue(float(value) if value else 0.0)
            elif field_type == "enum" and enum_values:
                widget = QComboBox()  
                widget.addItems(enum_values)
                widget.setCurrentText(value if value else enum_values[0])
            else:
                widget = QLineEdit(str(value) if value else "")
                if max_length:
                    widget.setMaxLength(max_length)
                    if(max_length < 255):
                        widget.setPlaceholderText(f"Massimo {max_length} caratteri")

            row_layout.addWidget(label_name)
            row_layout.addWidget(widget)
            row_layout.addItem(QSpacerItem(100, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
            self.input_fields[field_name] = widget

            if (idx + 1) % 2 == 0:
                form_layout.addRow(row_layout)
                row_layout = QHBoxLayout()

        if len(self.fields_info) % 2 != 0:
            form_layout.addRow(row_layout)

        main_layout.addLayout(form_layout)

        self.button_layout = QHBoxLayout()

        self.save_button = QPushButton("Salva")
        self.save_button.setObjectName("saveDipendenteButton")
        self.save_button.clicked.connect(self.update_dipendente)
        self.button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancella")
        self.cancel_button.setObjectName("cancelDipendenteButton")
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(self.button_layout)

        self.layout.addWidget(main_container)

        self.setLayout(self.layout)

    def update_dipendente(self):
        updated_data = {}
        for field_name, field_type, _, _ in self.fields_info:
            if(field_name == "Nome_fornitore") and (self.current_table != "Outsourcing"):
                continue
            widget = self.input_fields[field_name]
            if isinstance(widget, QDateEdit):
                updated_data[field_name] = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox) or isinstance(widget, QComboBox):
                updated_data[field_name] = widget.currentText() if isinstance(widget, QComboBox) else widget.value()
            else:
                updated_data[field_name] = widget.text()

        self.db.update_record("dipendenti", "Id_dipendente", self.dipendente_id, updated_data)
        self.parent.load_dipendenti()
        self.parent.update_dipendenti()
        self.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#1E3A8A"))
        gradient.setColorAt(1, QColor("#C71585"))
        painter.fillRect(self.rect(), QBrush(gradient))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
