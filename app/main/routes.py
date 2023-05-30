from base64 import b64encode
from io import BytesIO

import cv2
import numpy as np
from PIL import Image
from flask import render_template, abort, send_file, Response, request, redirect, url_for, flash, session
from werkzeug.security import safe_join
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.exceptions import abort
from app import db, bcrypt, login_manager
from app.main import main_bp
from app.main.camera import Camera
from app.form import RegistrationForm, LoginForm, TambahRoleForm, EditRoleForm, TambahUserForm, EditUserForm, UbahProfilForm, PhotoMaskForm
from app.models import Users, Roles

from source.test_new_images import detect_mask_in_image
from source.video_detector import detect_mask_in_frame
from source.video_detector import print_notif

import json
import time
import os
import stat
import datetime as dt
from datetime import date
from datetime import timedelta
from time import gmtime, strftime
from pathlib import Path

counter = 100
statusNotif = "nothing"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

### session route ###

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        encrypted_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Users(
            username    = form.username.data, 
            email       = form.email.data, 
            password    = encrypted_password,
            nama        = form.nama.data,
            alamat      = form.alamat.data,
            notelp      = form.notelp.data,
            gender      = form.gender.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration success!", category='success')
        return redirect(url_for("main.login"))
    return render_template('auth/register.html', form=form, title='Register')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password', category='danger')
    return render_template('auth/login.html', form=form, title='Login')

@main_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

### end of session route ###

@main_bp.route("/")
@login_required
def index():
    # flash("Not So OK", 'error')
    # gg = show_notif()
    # print(gg)
    return render_template("home/index.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    # Get today's date
    today = date.today()
    print("Today is: ", today)
        
    # Yesterday date
    # yesterday = today - timedelta(days = 1)
    # print("Yesterday was: ", yesterday)

    pathDefault = "app/static/gambar_wajah/"

    checkFolderToday = os.path.isdir(pathDefault + str(today))
    print(checkFolderToday)
    if checkFolderToday == True:
        countWithMaskToday = len(os.listdir(pathDefault + str(today) + "/withMask"))
        countNoMaskToday = len(os.listdir(pathDefault + str(today) + "/noMask"))
    else:
        countWithMaskToday = 0
        countNoMaskToday = 0
    print(countWithMaskToday)
    print(countNoMaskToday)

    my_list = os.listdir(pathDefault)
    countListDir = len(my_list)
    print(my_list)
    print(countListDir)
    countWithMaskAll = []
    countNoMaskAll = []
    if countListDir > 0:
        for FolderX in my_list:
            countWithMaskAll.append(int(len(os.listdir(pathDefault + str(FolderX) + "/withMask"))))
            countNoMaskAll.append(int(len(os.listdir(pathDefault + str(FolderX) + "/noMask"))))
    else:
        countWithMaskAll = []
        countNoMaskAll = []
    
    print(countWithMaskAll)
    print(countNoMaskAll)
    legend = 'All Day'
    labels = ["With Mask", "No Mask"]
    labels2 = my_list

    values = countWithMaskToday
    valuesNoMask = countNoMaskToday
    values2 = countWithMaskAll
    values3 = countNoMaskAll  
    return render_template('home/dashboard.html', values=values, valuesNoMask=valuesNoMask, values2=values2, values3=values3, labels=labels, labels2=labels2, legend=legend, title='Dashboard')

def gen(camera):

    while True:
        frame = camera.get_frame()
        frame_processed = detect_mask_in_frame(frame)
        frame_processed = cv2.imencode('.jpg', frame_processed)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_processed + b'\r\n')

@main_bp.route("/users")
@login_required
def users_list():
    if not current_user.id_role == 1:
        flash("Anda tidak memiliki akses ke halaman ini!", category='danger')
        return redirect(url_for('main.dashboard'))
    users = Users.query.all()
    return render_template("home/user-list.html", users=users, title='Users')

### CRUD USER ###

@main_bp.route('/tambah-user', methods=['GET', 'POST'])
@login_required
def tambah_user():
    form = TambahUserForm()
    if not current_user.id_role == 1:
        flash("Anda tidak memiliki akses ke halaman ini!", category='danger')
        return redirect(url_for("main.dashboard"))
    if request.method == 'GET':
        return render_template('home/tambah-user.html', form=form, title='Tambah User')
    else:
        if form.validate_on_submit():
            encrypted_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = Users(
                username    = form.username.data, 
                email       = form.email.data, 
                password    = encrypted_password,
                nama        = form.nama.data,
                alamat      = form.alamat.data,
                notelp      = form.notelp.data,
                gender      = form.gender.data)
            db.session.add(user)
            db.session.commit()
            flash("User berhasil ditambahkan!", category='success')
            return redirect(url_for("main.users_list"))
    return render_template('home/tambah-user.html', form=form, title='Tambah User')

@main_bp.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    form = EditUserForm()
    userUpdate = Users.query.get_or_404(id)
    if not current_user.id_role == 1:
        flash("Anda tidak memiliki akses ke halaman ini!", category='danger')
        return redirect(url_for("main.dashboard"))
    if request.method == 'POST':
        userUpdate.username = form.username.data
        userUpdate.email = form.email.data
        userUpdate.nama = form.nama.data
        userUpdate.alamat = form.alamat.data
        userUpdate.notelp = form.notelp.data
        userUpdate.gender = form.gender.data
        try:
            db.session.commit()
            flash(f"User berhasil diupdate!", category='success')
            return redirect(url_for("main.users_list"))
        except:
            flash(f"Gagal, sepertinya terdapat masalah.", category='danger')
            return render_template('home/edit-user.html', form=form, userUpdate=userUpdate, title='Edit User')
    else:
        return render_template('home/edit-user.html', form=form, userUpdate=userUpdate, title='Edit User')
    
@main_bp.route('/hapus-user/<int:id>', methods=['GET', 'POST'])
@login_required
def hapus_user(id):
    if not current_user.id_role == 1:
        flash("Anda tidak memiliki akses ke halaman ini!", category='danger')
        return redirect(url_for("main.dashboard"))
    user = Users.query.get(id)
    db.session.delete(user)
    db.session.commit()
    flash("User berhasil dihapus!", category='success')
    return redirect(url_for("main.users_list"))

### END OF CRUD USER ###

@main_bp.route('/roles')
@login_required
def role_list():
    if not current_user.id_role == 1:
        flash("Anda tidak memiliki akses ke halaman ini!", category='danger')
        return redirect(url_for("main.dashboard"))
    roles = Roles.query.all()
    return render_template('home/role-list.html', roles=roles, title='Role List')

#### CRUD ROLE #####

@main_bp.route('/tambah-role', methods=['GET', 'POST'])
@login_required
def tambah_role():
    form = TambahRoleForm()
    if not current_user.id_role == 1:
        flash("Anda tidak memiliki akses ke halaman ini!", category='danger')
        return redirect(url_for("main.dashboard"))
    if request.method == 'GET':
        return render_template('home/tambah-role.html', form=form, title='Tambah User')
    else:
        if form.validate_on_submit():
            role = Roles(role = form.role.data)
            db.session.add(role)
            db.session.commit()
            flash("Role berhasil ditambahkan!", category='success')
            return redirect(url_for("main.role_list"))
    return render_template('home/tambah-role.html', form=form, title='Tambah Role')

@main_bp.route('/edit_role/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_role(id):
    form = EditRoleForm()
    roles = Roles.query.get_or_404(id)
    if not current_user.id_role == 1:
        flash("Anda tidak memiliki akses ke halaman ini!", category='danger')
        return redirect(url_for("main.dashboard"))
    if request.method == 'POST':
        roles.role = form.role.data
        try:
            db.session.commit()
            flash(f"Role berhasil diupdate!", category='success')
            return redirect(url_for("main.role_list"))
        except:
            flash(f"Gagal, sepertinya terdapat masalah.", category='danger')
            return render_template('home/edit-role.html', roles=roles, form=form, title='Edit Role')
    else:
        return render_template('home/edit-role.html', roles=roles, form=form, title='Edit Role')

@main_bp.route('/hapus-role/<int:id>', methods=['GET', 'POST'])
@login_required
def hapus_role(id):
    if not current_user.id_role == 1:
        flash("Anda tidak memiliki akses ke halaman ini!", category='danger')
        return redirect(url_for("main.dashboard"))
    role = Roles.query.get(id)
    db.session.delete(role)
    db.session.commit()
    flash("Role berhasil dihapus!", category='success')
    return redirect(url_for("main.role_list"))

### END OF CRUD ROLE ###

@main_bp.route('/profile')
@login_required
def profile():
    user = Users.query.get(current_user.id)
    return render_template('home/profile.html', user=user, title='Profile')

@main_bp.route('/ubah_profil', methods=['GET', 'POST'])
@login_required
def ubah_profil():
    form = UbahProfilForm()
    user = Users.query.get(current_user.id)
    if not current_user.id_role == 1:
        flash("Anda tidak memiliki akses ke halaman ini!", category='danger')
        return redirect(url_for("main.dashboard"))
    if request.method == 'POST':
        user.username = form.username.data
        user.email = form.email.data
        user.nama = form.nama.data
        user.alamat = form.alamat.data
        user.notelp = form.notelp.data
        user.gender = form.gender.data
        try:
            db.session.commit()
            flash(f"Profil berhasil diupdate!", category='success')
            return redirect(url_for("main.profile", id=current_user.id))
        except:
            flash(f"Gagal, sepertinya terdapat masalah.", category='danger')
            return render_template('home/ubah-profil.html', form=form, title='Ubah Profil')
    return render_template('home/ubah-profil.html', form=form, title='Ubah Profil')

@main_bp.route('/datatraining')
@login_required
def data_training():
    if not current_user.id_role == 1:
        flash("Anda tidak memiliki akses ke halaman ini!", category='danger')
        return redirect(url_for("main.dashboard"))
    return ('ini data training')

@main_bp.route("/scanning")
@login_required
def scanning():
    return render_template("home/scanning.html", title='Scanning')

@main_bp.route("/scanning2")
@login_required
def scanning2():
    # flash("Not So OK", 'error')
    # gg = show_notif()
    # print(gg)
    return render_template("home_page.html")

@main_bp.route("/datareview")
@login_required
def chart():
    # Get today's date
  today = date.today()
  print("Today is: ", today)
    
  # Yesterday date
  # yesterday = today - timedelta(days = 1)
  # print("Yesterday was: ", yesterday)

  pathDefault = "app/static/gambar_wajah/"

  checkFolderToday = os.path.isdir(pathDefault + str(today))
  print(checkFolderToday)
  if checkFolderToday == True:
    countWithMaskToday = len(os.listdir(pathDefault + str(today) + "/withMask"))
    countNoMaskToday = len(os.listdir(pathDefault + str(today) + "/noMask"))
  else:
    countWithMaskToday = 0
    countNoMaskToday = 0
  print(countWithMaskToday)
  print(countNoMaskToday)

  my_list = os.listdir(pathDefault)
  countListDir = len(my_list)
  print(my_list)
  print(countListDir)
  countWithMaskAll = []
  countNoMaskAll = []
  if countListDir > 0:
    for FolderX in my_list:
      countWithMaskAll.append(int(len(os.listdir(pathDefault + str(FolderX) + "/withMask"))))
      countNoMaskAll.append(int(len(os.listdir(pathDefault + str(FolderX) + "/noMask"))))
  else:
    countWithMaskAll = []
    countNoMaskAll = []
  
  print(countWithMaskAll)
  print(countNoMaskAll)
  legend = 'All Day'
  labels = ["With Mask", "No Mask"]
  labels2 = my_list

  values = countWithMaskToday
  valuesNoMask = countNoMaskToday
  values2 = countWithMaskAll
  values3 = countNoMaskAll  
  return render_template('datareview.html', values=values, valuesNoMask=valuesNoMask, values2=values2, values3=values3, labels=labels, labels2=labels2, legend=legend)

def gen(camera):

    while True:
        frame = camera.get_frame()
        frame_processed = detect_mask_in_frame(frame)
        frame_processed = cv2.imencode('.jpg', frame_processed)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_processed + b'\r\n')


@main_bp.route('/video_feed')
def video_feed():
    return Response(gen(
        Camera()
    ),
        mimetype='multipart/x-mixed-replace; boundary=frame')

@main_bp.route("/listen")
def listen():

  def respond_to_client():
    while True:
      global counter
      global statusNotif
      statusNotif = print_notif()
    #   print(statusNotif)
      color = "white"
    #   with open("color.txt", "r") as f:
    #     color = f.read()
    #     print("******************")
      if(color == "white"):
        # print(counter)
        # counter += 1
        _data = json.dumps({"color":color, "counter":statusNotif})
        yield f"id: 1\ndata: {_data}\nevent: online\n\n"
      time.sleep(0.5)
  return Response(respond_to_client(), mimetype='text/event-stream')

def allowed_file(filename):
    ext = filename.split(".")[-1]
    is_good = ext in ["jpg", "jpeg", "png"]
    return is_good


@main_bp.route("/image-mask-detector", methods=["GET", "POST"])
def image_mask_detection():
    return render_template("image_detector.html",
                           form=PhotoMaskForm())


@main_bp.route("/image-processing", methods=["POST"])
def image_processing():
    form = PhotoMaskForm()

    if not form.validate_on_submit():
        flash("An error occurred", "danger")
        abort(Response("Error", 400))

    pil_image = Image.open(form.image.data)
    image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    array_image = detect_mask_in_image(image)
    rgb_image = cv2.cvtColor(array_image, cv2.COLOR_BGR2RGB)
    image_detected = Image.fromarray(rgb_image, 'RGB')

    with BytesIO() as img_io:
        image_detected.save(img_io, 'PNG')
        img_io.seek(0)
        base64img = "data:image/png;base64," + b64encode(img_io.getvalue()).decode('ascii')
        return base64img


baseMaskPath = r'D:\KULIAH\TA\1. INI FOLDER SKRIPSI\SIPEMAS\app\static\gambar_wajah'
#baseMaskPath = f"app/static/gambar_wajah/"

def getTimeStampString(tSec: float) -> str:
    tObj = dt.datetime.fromtimestamp(tSec)
    tStr = dt.datetime.strftime(tObj, '%Y-%m-%d %H:%M:%S')
    return tStr

def getReadableByteSize(num, suffix='B') -> str:
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)

def getIconClassForFilename(fName):
    fileExt = Path(fName).suffix
    fileExt = fileExt[1:] if fileExt.startswith(".") else fileExt
    fileTypes = ["aac", "ai", "bmp", "cs", "css", "csv", "doc", "docx", "exe", "gif", "heic", "html", "java", "jpg", "js", "json", "jsx", "key", "m4p", "md", "mdx", "mov", "mp3",
                 "mp4", "otf", "pdf", "php", "png", "pptx", "psd", "py", "raw", "rb", "sass", "scss", "sh", "sql", "svg", "tiff", "tsx", "ttf", "txt", "wav", "woff", "xlsx", "xml", "yml"]
    fileIconClass = f"bi bi-filetype-{fileExt}" if fileExt in fileTypes else "bi bi-file-earmark"
    return fileIconClass

@main_bp.route('/captured/', defaults={'reqPath':""})
@main_bp.route('/captured/<path:reqPath>')
def captured(reqPath):
    absPath = safe_join(baseMaskPath, reqPath)

    if not os.path.exists(absPath):
        return abort(404)

    if os.path.isfile(absPath):
        return send_file(absPath)

    def fObjfromScan(x):
        fIcon = 'bi bi-folder-fill' if os.path.isdir(x.path) else getIconClassForFilename(x.name)
        fileStat = x.stat()
        fBytes = getReadableByteSize(fileStat.st_size)
        fTime = getTimeStampString(fileStat.st_mtime)
        return {
            'name': x.name, 
            'size': fBytes, 
            'mTime': fTime,
            'fIcon': fIcon,
            'fLink': os.path.relpath(x.path, baseMaskPath).replace("\\", "/")
            # 'fLink': x.path
            }
    fNames = [fObjfromScan(x) for x in os.scandir(absPath)]
    parentPath = os.path.relpath(Path(absPath).parents[0], baseMaskPath).replace("\\", "/")
    return render_template('home/browse.html.j2', files=fNames, parentPath=parentPath, title='Captured Person')