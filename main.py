import flet as ft
import sqlite3
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import asyncio

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('eleves.db')
        self.create_tables()
        
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coordinator TEXT,
            teacher_name TEXT,
            teacher_first_name TEXT,
            district TEXT,
            municipality TEXT,
            school TEXT,
            chapter TEXT,
            group_number TEXT,
            level TEXT,
            last_name TEXT,
            first_name TEXT,
            birth_date TEXT,
            birth_place TEXT,
            contract_number TEXT,
            father_name TEXT,
            mother_last_name TEXT,
            mother_first_name TEXT,
            gender TEXT,
            age INTEGER
        )
        ''')
        self.conn.commit()

class EmailPage:
    def __init__(self, page: ft.Page, db, on_back):
        self.page = page
        self.db = db
        self.on_back = on_back
        self.init_fields()
        self.container = self.build()
    
    def init_fields(self):
        self.sender_email = ft.TextField(
            label="البريد الإلكتروني للمرسل (Gmail)",
            text_align="right",
            width=350,
            border_color=ft.Colors.GREEN,
            focused_border_color=ft.Colors.GREEN_900,
            prefix_icon=ft.Icons.EMAIL,
            helper_text="أدخل بريدك الإلكتروني على Gmail"
        )
        self.recipient_email = ft.TextField(
            label="البريد الإلكتروني للمستلم",
            text_align="right",
            width=350,
            border_color=ft.Colors.GREEN,
            focused_border_color=ft.Colors.GREEN_900,
            prefix_icon=ft.Icons.FORWARD_TO_INBOX,
            helper_text="أدخل البريد الإلكتروني الذي تريد إرسال البيانات إليه"
        )
        self.password = ft.TextField(
            label="كلمة المرور",
            password=True,
            text_align="right",
            width=350,
            border_color=ft.Colors.GREEN,
            focused_border_color=ft.Colors.GREEN_900,
            prefix_icon=ft.Icons.LOCK,
            helper_text="أدخل كلمة مرور حساب Gmail الخاص بك"
        )
    
    def send_email(self, e):
        if not self.sender_email.value or not self.recipient_email.value or not self.password.value:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("الرجاء إدخال جميع البيانات المطلوبة"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        try:
            # تصدير البيانات إلى Excel أولاً
            df = pd.read_sql_query("SELECT * FROM students", self.db.conn)
            df.to_excel("bd_students.xlsx", index=False)
            
            # إعداد البريد الإلكتروني
            msg = MIMEMultipart()
            msg['From'] = self.sender_email.value
            msg['To'] = self.recipient_email.value
            msg['Subject'] = "بيانات المتمدرسين"
            
            body = "مرفق ملف بيانات المتمدرسين"
            msg.attach(MIMEText(body, 'plain'))
            
            # إضافة المرفق
            attachment = open("bd_students.xlsx", "rb")
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename= %s' % "bd_students.xlsx")
            msg.attach(part)
            
            # إرسال البريد الإلكتروني
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.sender_email.value, self.password.value)
            text = msg.as_string()
            server.sendmail(self.sender_email.value, self.recipient_email.value, text)
            server.quit()
            
            self.page.snack_bar = ft.SnackBar(content=ft.Text("تم إرسال البيانات بنجاح"))
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(content=ft.Text(f"خطأ في إرسال البريد: {str(ex)}"))
            self.page.snack_bar.open = True
            self.page.update()
    
    def build(self):
        # إنشاء زر الإرسال
        send_button = ft.ElevatedButton(
            "إرسال",
            on_click=self.send_email,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN,
                padding=15,
                shape=ft.RoundedRectangleBorder(radius=10),
                animation_duration=500
            ),
            width=350
        )
        
        # إنشاء زر العودة
        back_button = ft.ElevatedButton(
            "العودة",
            on_click=lambda _: self.on_back(),
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.RED,
                padding=15,
                shape=ft.RoundedRectangleBorder(radius=10),
                animation_duration=500
            ),
            width=350
        )

        # تنظيم العناصر في عمود
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "إرسال البيانات عبر البريد الإلكتروني",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN_900,
                        text_align="right"
                    ),
                    ft.Text(
                        "يرجى استخدام حساب Gmail لإرسال البيانات",
                        size=16,
                        color=ft.Colors.GREY_700,
                        text_align="right"
                    ),
                    self.sender_email,
                    self.recipient_email,
                    self.password,
                    ft.Column([
                        send_button,
                        back_button
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
                ],
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=30,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.BLUE_GREY_100,
                offset=ft.Offset(0, 0)
            )
        )

class StudentManagement:
    def __init__(self, page: ft.Page, db):
        self.page = page
        self.db = db
        self.student_count = 0
        self.init_fields()
        self.container = self.build()
    
    def init_fields(self):
        # القوائم المنسدلة
        self.districts = ["عين جاســر", "عين التوتـة", "آريــس", "بريكـة", "باتنـة", "بوزينـة", "الشمــرة", 
                         "الجـزار", "المعــذر", "إشمـول", "منعـــة", "مروانـة", "نقـاوس", "أولاد سي سليمان", 
                         "رأس العيـون", "سقـانــة", "سريانــة", "تازولــت", "ثنيـة العـابـد", "تيمقــاد", "تكـوت"]
        self.chapters = ["حضري", "شبه حضري", "ريفي"]
        self.groups = ["1", "2"]
        self.levels = ["الأول", "الثاني", "الثالث"]
        self.genders = ["ذكر", "أنثى"]
        
        # حقول الإدخال
        self.coordinator = ft.TextField(label="المنسق", width=300)
        self.teacher_name = ft.TextField(label="لقب المعلم", width=300)
        self.teacher_first_name = ft.TextField(label="اسم المعلم", width=300)
        self.district = ft.Dropdown(label="الدائرة", width=300, options=[ft.dropdown.Option(d) for d in self.districts])
        self.municipality = ft.TextField(label="البلدية", width=300)
        self.school = ft.TextField(label="مؤسسة التدريس", width=300)
        self.chapter = ft.Dropdown(label="الفصل", width=300, options=[ft.dropdown.Option(c) for c in self.chapters])
        self.group = ft.Dropdown(label="الفوج", width=300, options=[ft.dropdown.Option(g) for g in self.groups])
        self.level = ft.Dropdown(label="المستوى", width=300, options=[ft.dropdown.Option(l) for l in self.levels])
        self.last_name = ft.TextField(label="اللقب", width=300)
        self.first_name = ft.TextField(label="الاسم", width=300)
        self.birth_date = ft.TextField(label="تاريخ الميلاد", width=300)
        self.birth_place = ft.TextField(label="مكان الميلاد", width=300)
        self.contract_number = ft.TextField(label="رقم العقد", width=300)
        self.father_name = ft.TextField(label="اسم الأب", width=300)
        self.mother_last_name = ft.TextField(label="لقب الأم", width=300)
        self.mother_first_name = ft.TextField(label="اسم الأم", width=300)
        self.gender = ft.Dropdown(label="الجنس", width=300, options=[ft.dropdown.Option(g) for g in self.genders])
        
        # عداد الطلاب
        self.counter = ft.Text(f"عدد المسجلين: {self.student_count}", size=20)
    
    def calculate_age(self, birth_date):
        try:
            if len(birth_date) == 4:  # سنة فقط
                return datetime.now().year - int(birth_date)
            else:  # تاريخ كامل
                birth = datetime.strptime(birth_date, '%Y-%m-%d')
                return (datetime.now() - birth).days // 365
        except:
            return 0
    
    def save_student(self, e):
        try:
            age = self.calculate_age(self.birth_date.value)
            cursor = self.db.conn.cursor()
            cursor.execute('''
                INSERT INTO students (coordinator, teacher_name, teacher_first_name, district, municipality, school,
                                    chapter, group_number, level, last_name, first_name,
                                    birth_date, birth_place, contract_number, father_name,
                                    mother_last_name, mother_first_name, gender, age)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.coordinator.value, self.teacher_name.value, self.teacher_first_name.value, self.district.value,
                self.municipality.value, self.school.value, self.chapter.value,
                self.group.value, self.level.value, self.last_name.value,
                self.first_name.value, self.birth_date.value, self.birth_place.value,
                self.contract_number.value, self.father_name.value,
                self.mother_last_name.value, self.mother_first_name.value,
                self.gender.value, age
            ))
            self.db.conn.commit()
            self.student_count += 1
            self.counter.value = f"عدد المسجلين: {self.student_count}"
            self.page.snack_bar = ft.SnackBar(content=ft.Text("تم حفظ بيانات المتمدرس(ة) بنجاح"))
            self.page.snack_bar.open = True
            self.clear_fields()
            self.page.update()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(content=ft.Text(f"خطأ في حفظ البيانات: {str(ex)}"))
            self.page.snack_bar.open = True
            self.page.update()
    
    def clear_fields(self):
        for field in [self.coordinator, self.teacher_name, self.teacher_first_name, self.municipality, self.school,
                     self.last_name, self.first_name, self.birth_date, self.birth_place,
                     self.contract_number, self.father_name, self.mother_last_name,
                     self.mother_first_name]:
            field.value = ""
        self.district.value = None
        self.chapter.value = None
        self.group.value = None
        self.level.value = None
        self.gender.value = None
    
    def export_to_excel(self, e):
        try:
            # تعريف أسماء الأعمدة بالعربية
            arabic_columns = {
                'coordinator': 'المنسق',
                'teacher_name': 'لقب المعلم',
                'teacher_first_name': 'اسم المعلم',
                'district': 'الدائرة',
                'municipality': 'البلدية',
                'school': 'مؤسسة التدريس',
                'chapter': 'الفصل',
                'group_number': 'الفوج',
                'level': 'المستوى',
                'last_name': 'اللقب',
                'first_name': 'الاسم',
                'birth_date': 'تاريخ الميلاد',
                'birth_place': 'مكان الميلاد',
                'contract_number': 'رقم العقد',
                'father_name': 'اسم الأب',
                'mother_last_name': 'لقب الأم',
                'mother_first_name': 'اسم الأم',
                'gender': 'الجنس',
                'age': 'العمر'
            }
            
            df = pd.read_sql_query("SELECT * FROM students", self.db.conn)
            # تغيير أسماء الأعمدة إلى العربية
            df = df.rename(columns=arabic_columns)
            
            # تصدير إلى Excel مع تعيين اتجاه الصفحة من اليمين إلى اليسار
            with pd.ExcelWriter('bd_students.xlsx', engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='البيانات')
                # تعيين اتجاه الورقة من اليمين إلى اليسار
                writer.sheets['البيانات'].sheet_view.rightToLeft = True
            
            self.page.snack_bar = ft.SnackBar(content=ft.Text("تم تصدير البيانات إلى ملف Excel بنجاح"))
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(content=ft.Text(f"خطأ في تصدير البيانات: {str(ex)}"))
            self.page.snack_bar.open = True
            self.page.update()
    
    def open_email_page(self, e):
        email_page = EmailPage(self.page, self.db, lambda: self.show_main_page())
        self.page.clean()
        self.page.add(email_page.container)
        self.page.update()

    def show_main_page(self):
        self.page.clean()
        self.page.add(self.container)
        self.page.update()
    
    def build(self):
        # تقسيم الحقول إلى أعمدة
        fields = [
            self.coordinator, self.teacher_name, self.teacher_first_name, 
            self.district, self.municipality, self.school, 
            self.chapter, self.group, self.level, 
            self.last_name, self.first_name, self.birth_date, 
            self.birth_place, self.contract_number, 
            self.father_name, self.mother_last_name, 
            self.mother_first_name, self.gender
        ]
        
        # تطبيق التنسيق على جميع الحقول
        for field in fields:
            if isinstance(field, ft.TextField):
                field.border_color = ft.Colors.GREEN
                field.focused_border_color = ft.Colors.GREEN_900
                field.width = 350
            elif isinstance(field, ft.Dropdown):
                field.border_color = ft.Colors.GREEN
                field.focused_border_color = ft.Colors.GREEN_900
                field.width = 350
        
        # تنظيم الحقول في عمود واحد
        fields_column = ft.Column(
            controls=fields,
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        # عداد الطلاب
        self.counter.color = ft.Colors.GREEN_900
        self.counter.weight = ft.FontWeight.BOLD
        
        # الأزرار
        save_button = ft.ElevatedButton(
            "حفظ",
            on_click=self.save_student,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN,
                padding=15,
                shape=ft.RoundedRectangleBorder(radius=10),
                animation_duration=500
            ),
            width=350
        )
        
        export_button = ft.ElevatedButton(
            "تصدير إلى Excel",
            on_click=self.export_to_excel,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE,
                padding=15,
                shape=ft.RoundedRectangleBorder(radius=10),
                animation_duration=500
            ),
            width=350
        )
        
        email_button = ft.ElevatedButton(
            "إرسال عبر البريد الإلكتروني",
            on_click=self.open_email_page,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.ORANGE,
                padding=15,
                shape=ft.RoundedRectangleBorder(radius=10),
                animation_duration=500
            ),
            width=350
        )
        
        # تنظيم الأزرار في عمود
        buttons_row = ft.Column(
            controls=[save_button, export_button, email_button],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "إدخال معلومات المتمدرسين",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN_900,
                        text_align="right"
                    ),
                    self.counter,
                    fields_column,
                    buttons_row
                ],
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO
            ),
            padding=30,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.BLUE_GREY_100,
                offset=ft.Offset(0, 0)
            )
        )

class LoginPage:
    def __init__(self, page: ft.Page, on_login_success):
        self.page = page
        self.on_login_success = on_login_success
        self.username = ft.TextField(
            label="اسم المستخدم",
            text_align="right",
            width=300,
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_600,
            prefix_icon=ft.Icons.PERSON
        )
        self.password = ft.TextField(
            label="كلمة المرور",
            password=True,
            text_align="right",
            width=300,
            border_color=ft.Colors.BLUE_400,
            focused_border_color=ft.Colors.BLUE_600,
            prefix_icon=ft.Icons.LOCK,
            suffix_icon=ft.IconButton(
                ft.Icons.VISIBILITY_OFF,
                on_click=self.toggle_password_visibility
            )
        )
        self.container = self.build()

    def toggle_password_visibility(self, e):
        self.password.password = not self.password.password
        self.password.suffix_icon.icon = ft.Icons.VISIBILITY if self.password.password else ft.Icons.VISIBILITY_OFF
        self.page.update()

    def build(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "تسجيل الدخول",
                        size=30,
                        text_align="right",
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900
                    ),
                    self.username,
                    self.password,
                    ft.ElevatedButton(
                        "دخول",
                        on_click=self.login_clicked,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.BLUE_400,
                            padding=15,
                            shape=ft.RoundedRectangleBorder(radius=10)
                        ),
                        width=300
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            ),
            padding=30,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.BLUE_GREY_100,
                offset=ft.Offset(0, 0)
            ),
            alignment=ft.alignment.center
        )
    
    def login_clicked(self, e):
        if self.username.value == "admin" and self.password.value == "admin":
            self.on_login_success()
        else:
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text("خطأ في اسم المستخدم أو كلمة المرور")))

class IntroPage:
    def __init__(self, page: ft.Page, on_intro_complete):
        self.page = page
        self.on_intro_complete = on_intro_complete
        self.container = self.build()
    
    def welcome_clicked(self, e):
        self.on_intro_complete()
        self.page.update()
    
    def build(self):
        return ft.Container(
            content=ft.Column([
                # العنوان
                ft.Column([
                    ft.Text(
                        "الجمهورية الجزائرية الديمقراطية الشعبية",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "وزارة التربية الوطنية",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "الديوان الوطني لمحو الأمية و تعليم الكبار",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "ملحقة باتنة",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900,
                        text_align=ft.TextAlign.CENTER
                    ),
                ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                
                # الشعار
                ft.Container(
                    content=ft.Image(
                        src="logo.gif",
                        width=200,
                        height=200,
                        fit=ft.ImageFit.CONTAIN,
                        animate_opacity=300,
                    ),
                    margin=ft.margin.symmetric(vertical=40),
                    alignment=ft.alignment.center
                ),
                
                # زر مرحبا
                ft.ElevatedButton(
                    "مرحبا",
                    on_click=self.welcome_clicked,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE_400,
                        padding=15,
                        shape=ft.RoundedRectangleBorder(radius=10),
                        animation_duration=500
                    ),
                    width=200
                ),
                
                # معلومات التطبيق
                ft.Column([
                    ft.Text(
                        "تطبيق إدخال بيانات المتمدرسين",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "النسخة 1.0",
                        size=16,
                        color=ft.Colors.BLUE_900,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "إعداد و تنفيذ : جبارة عبد الحق",
                        size=16,
                        color=ft.Colors.BLUE_900,
                        text_align=ft.TextAlign.CENTER
                    ),
                ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER
            ),
            padding=30,
            bgcolor=ft.Colors.WHITE,
            alignment=ft.alignment.center,
            animate=ft.animation.Animation(500, ft.AnimationCurve.BOUNCE_OUT)
        )

def main(page: ft.Page):
    page.title = 'الديوان الوطني لمحو الأمية و تعليم الكبار'
    page.scroll = 'auto'
    page.window.top = 1
    page.window.left = 760
    page.window.width = 390
    page.window.height = 800
    page.rtl = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_bgcolor = ft.Colors.WHITE
    page.padding = 10
    
    db = Database()
    
    def on_login_success():
        page.clean()
        student_management = StudentManagement(page, db)
        page.add(student_management.container)
    
    def show_login_page():
        page.clean()
        login_page = LoginPage(page, on_login_success)
        page.add(login_page.container)
    
    # عرض صفحة Intro أولاً
    intro_page = IntroPage(page, show_login_page)
    page.add(intro_page.container)

ft.app(target=main)