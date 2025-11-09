import jwt
import time
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid
import pytz
from datetime import timezone, datetime
from functools import wraps
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'Mkiustafa1765432@#@@'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object(Config)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    first_name = db.Column(db.String(80), nullable=True)
    last_name = db.Column(db.String(80), nullable=True)
    family_name = db.Column(db.String(80), nullable=True)
    image = db.Column(db.String(200), nullable=True)
    user_type = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    position = db.Column(db.String(120), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Candidate {self.name}>'


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), nullable=True)
    published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<News {self.title}>'


class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Subscriber {self.email}>'


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password) and user.user_type == 'admin':
            session['is_admin'] = True
            session['admin_id'] = user.id
            return redirect(url_for('admin_dashboard'))
        else:
            flash('بيانات الدخول غير صحيحة')
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/admin/candidates')
@admin_required
def admin_candidates():
    candidates = Candidate.query.order_by(Candidate.created_at.desc()).all()
    return render_template('admin_candidates.html', candidates=candidates)


@app.route('/admin/candidate/new', methods=['GET', 'POST'])
@admin_required
def admin_candidate_new():
    if request.method == 'POST':
        name = request.form.get('name')
        position = request.form.get('position')
        bio = request.form.get('bio')
        image = request.form.get('image')
        c = Candidate(name=name, position=position, bio=bio, image=image)
        db.session.add(c)
        db.session.commit()
        flash('تم إضافة المرشح')
        return redirect(url_for('admin_candidates'))
    return render_template('admin_candidate_form.html')


@app.route('/admin/candidate/<int:c_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_candidate_edit(c_id):
    c = Candidate.query.get_or_404(c_id)
    if request.method == 'POST':
        c.name = request.form.get('name')
        c.position = request.form.get('position')
        c.bio = request.form.get('bio')
        c.image = request.form.get('image')
        db.session.commit()
        flash('تم تحديث المرشح')
        return redirect(url_for('admin_candidates'))
    return render_template('admin_candidate_form.html', candidate=c)


@app.route('/admin/candidate/<int:c_id>/delete', methods=['POST'])
@admin_required
def admin_candidate_delete(c_id):
    c = Candidate.query.get_or_404(c_id)
    db.session.delete(c)
    db.session.commit()
    flash('تم حذف المرشح')
    return redirect(url_for('admin_candidates'))


@app.route('/admin/news')
@admin_required
def admin_news():
    news = News.query.order_by(News.created_at.desc()).all()
    return render_template('admin_news.html', news_list=news)


@app.route('/admin/news/new', methods=['GET', 'POST'])
@admin_required
def admin_news_new():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        image = request.form.get('image')
        published = True if request.form.get('published') == 'on' else False
        n = News(title=title, content=content, image=image, published=published)
        db.session.add(n)
        db.session.commit()
        flash('تم إنشاء الخبر')
        return redirect(url_for('admin_news'))
    return render_template('admin_news_form.html')


@app.route('/admin/news/<int:n_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_news_edit(n_id):
    n = News.query.get_or_404(n_id)
    if request.method == 'POST':
        n.title = request.form.get('title')
        n.content = request.form.get('content')
        n.image = request.form.get('image')
        n.published = True if request.form.get('published') == 'on' else False
        db.session.commit()
        flash('تم تحديث الخبر')
        return redirect(url_for('admin_news'))
    return render_template('admin_news_form.html', news=n)


@app.route('/admin/news/<int:n_id>/delete', methods=['POST'])
@admin_required
def admin_news_delete(n_id):
    n = News.query.get_or_404(n_id)
    db.session.delete(n)
    db.session.commit()
    flash('تم حذف الخبر')
    return redirect(url_for('admin_news'))


@app.route('/admin/subscribers')
@admin_required
def admin_subscribers():
    subs = Subscriber.query.order_by(Subscriber.created_at.desc()).all()
    return render_template('admin_subscribers.html', subscribers=subs)


def send_news_email(news_item, recipients):
    smtp_host = os.environ.get('SMTP_HOST')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')
    sender = os.environ.get('SENDER_EMAIL', smtp_user)

    subject = news_item.title
    html_body = f"<h2>{news_item.title}</h2><p>{news_item.content}</p>"

    if not recipients:
        return {'sent': 0, 'error': 'no recipients'}

    if not smtp_host or not smtp_user or not smtp_pass:
        print('SMTP not configured. Printing emails to console:')
        for r in recipients:
            print('---')
            print(f'To: {r}')
            print(f'Subject: {subject}')
            print(html_body)
        return {'sent': len(recipients), 'mode': 'console'}

    sent = 0
    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        for r in recipients:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = r
            part = MIMEText(html_body, 'html')
            msg.attach(part)
            server.sendmail(sender, r, msg.as_string())
            sent += 1
        server.quit()
        return {'sent': sent}
    except Exception as e:
        return {'sent': sent, 'error': str(e)}


@app.route('/admin/news/<int:n_id>/send', methods=['POST'])
@admin_required
def admin_news_send(n_id):
    n = News.query.get_or_404(n_id)
    subscribers = [s.email for s in Subscriber.query.all()]
    result = send_news_email(n, subscribers)
    flash(f"أرسلت {result.get('sent',0)} رسالة. {result.get('error','')}")
    return redirect(url_for('admin_news'))


def get_goals():
    return [
        "تعزيز الديمقراطية والمشاركة السياسية",
        "حماية حقوق الإنسان والحريات الأساسية",
        "تطوير الوعي السياسي والاجتماعي",
        "دعم العدالة الاجتماعية والمساواة"
    ]

def get_history():
    return [
        {
            'year': '2020',
            'event': 'تأسيس حركة حقوق'
        },
        {
            'year': '2021',
            'event': 'إطلاق أول حملة توعية وطنية'
        },
        {
            'year': '2022',
            'event': 'تنظيم المؤتمر الوطني الأول للحقوق والحريات'
        },
        {
            'year': '2023',
            'event': 'إطلاق برنامج التدريب والتأهيل السياسي'
        }
    ]

def get_services():
    return [
        {
            'title': 'تطوير المواقع',
            'description': 'تصميم وتطوير مواقع احترافية وتطبيقات ويب متقدمة'
        },
        {
            'title': 'التصميم الجرافيكي',
            'description': 'تصميم هويات بصرية، منشورات، وتصاميم احترافية'
        },
        {
            'title': 'التصوير الفوتوغرافي',
            'description': 'خدمات تصوير احترافية للفعاليات والمناسبات'
        },
        {
            'title': 'إدارة وسائل التواصل الاجتماعي',
            'description': 'إدارة المحتوى وتطوير استراتيجيات التواصل الاجتماعي'
        }
    ]

@app.route('/')
def home():
    return render_template('index.html',
                         goals=get_goals(),
                         history=get_history(),
                         services=get_services())

@app.route('/activities')
def activities():
    activities = [
        {
            'title': 'مهرجان حركة حقوق',
            'date': '2025-10-24',
            'description': 'مهرجان يتحدث عن إنجازات الحركة وخططها المستقبلية',
            'image': '1.jpg'
        },
        {
            'title': 'خطاب عن مرشحات حركة حقوق',
            'date': '2025-11-6',
            'description': 'خطاب عن مرشحات حركة حقوق ودورها في تعزيز المشاركة السياسية',
            'image': '2.jpg'
        }
    ]
    return render_template('activities.html', activities=activities)

@app.route('/programs')
def programs():
    programs = [
        {
            'title': 'برنامج التثقيف السياسي',
            'duration': '3 أشهر',
            'description': 'برنامج شامل للتثقيف السياسي وفهم العملية الديمقراطية'
        },
        {
            'title': 'برنامج تدريب المراقبين',
            'duration': 'شهر واحد',
            'description': 'تدريب متخصص لمراقبة العملية الانتخابية وضمان نزاهتها'
        }
    ]
    return render_template('programs.html', programs=programs)

@app.route('/publications')
def publications():
    publications = [
        {
            'title': 'دليل الناخب العراقي',
            'type': 'كتيب',
            'year': '2025',
            'description': 'دليل شامل يوضح حقوق وواجبات الناخب العراقي'
        },
        {
            'title': 'تقرير الشفافية الانتخابية',
            'type': 'تقرير',
            'year': '2024',
            'description': 'تحليل معمق لشفافية العملية الانتخابية في العراق'
        }
    ]
    return render_template('publications.html', publications=publications)

@app.route('/team')
def team():
    #team_members = [
    #    {
    #        'name': 'الدكتور أحمد العراقي',
    #        'position': 'المدير التنفيذي',
    #        'bio': 'خبير في القانون الدستوري وحقوق الإنسان'
    #    },
    #    {
    #        'name': 'الدكتورة سارة الموسوي',
    #        'position': 'مديرة البرامج',
     #       'bio': 'متخصصة في الديمقراطية والحوكمة'
     #   }
    #]
    #return render_template('team.html', team_members=team_members)
    return render_template('waiting.html')
@app.route('/candidates')
def candidates():
    candidates_list = [
        {
            'name': 'د. علي الحسيني',
            'position': 'مرشح محافظة بغداد',
            'bio': 'دكتوراه في القانون الدستوري، خبرة 15 عاماً في مجال حقوق الإنسان',
            'image': 'candidate1.jpg'
        },
        {
            'name': 'د. زينب الموسوي',
            'position': 'مرشحة محافظة البصرة',
            'bio': 'متخصصة في القانون الدولي، ناشطة في مجال حقوق المرأة',
            'image': 'candidate2.jpg'
        },
        {
            'name': 'م. حسن العبيدي',
            'position': 'مرشح محافظة الموصل',
            'bio': 'مهندس مدني، ناشط في مجال حقوق العمال والتنمية المستدامة',
            'image': 'candidate3.jpg'
        }
    ]
    return render_template('candidates.html', candidates=candidates_list)

@app.route('/services')
def services():
    services_list = [
        {
            'title': 'تطوير المواقع',
            'description': 'تصميم وتطوير مواقع احترافية وتطبيقات ويب متقدمة'
        },
        {
            'title': 'التصميم الجرافيكي',
            'description': 'تصميم هويات بصرية، منشورات، وتصاميم احترافية'
        },
        {
            'title': 'التصوير الفوتوغرافي',
            'description': 'خدمات تصوير احترافية للفعاليات والمناسبات'
        },
        {
            'title': 'إدارة وسائل التواصل الاجتماعي',
            'description': 'إدارة المحتوى وتطوير استراتيجيات التواصل الاجتماعي'
        }
    ]
    return render_template('services.html', services=services_list)

@app.route('/salma')
def salma():
    return render_template('salma.html')

@app.route('/volunteer')
def volunteer():
    opportunities = [
        {
            'title': 'مراقب انتخابات',
            'requirements': 'العمر 18 سنة فما فوق، إتمام التدريب الأساسي'
        },
        {
            'title': 'منسق ميداني',
            'requirements': 'خبرة في العمل التطوعي، مهارات تواصل جيدة'
        }
    ]
    return render_template('volunteer.html', opportunities=opportunities)



if __name__ == '__main__':
    app.run(debug=True)
