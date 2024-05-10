import os
from os.path import join, dirname
from dotenv import load_dotenv

from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, make_response, send_file
from werkzeug.utils import secure_filename
from bson import ObjectId
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter
import io
from io import BytesIO
import logging
from flask import send_from_directory


app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = "./static/profile_pics"

SECRET_KEY = "MERZY"
app.secret_key = "triowonders"

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

MONGODB_URI = 'mongodb://rkhawariz:merzy@ac-ds5pieh-shard-00-00.hweccjp.mongodb.net:27017,ac-ds5pieh-shard-00-01.hweccjp.mongodb.net:27017,ac-ds5pieh-shard-00-02.hweccjp.mongodb.net:27017/?ssl=true&replicaSet=atlas-h8931u-shard-0&authSource=admin&retryWrites=true&w=majority'
DB_NAME = 'tripwonders'

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

TOKEN_KEY = "mytoken"


@app.route("/", methods=["GET"])
def home():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        is_admin = user_info.get("role") == "admin"
        logged_in = True
        return render_template(
            "index.html", user_info=user_info, logged_in=logged_in, is_admin=is_admin
        )
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging you in"
    return render_template("index.html", msg=msg)


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login_user", methods=["POST"])
def login_user():
    if request.method == "POST":
        data = request.json
        email = data.get("email")
        password = data.get("password")
        pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

        result = db.user.find_one({"email": email, "password": pw_hash})
        if result:
            payload = {
                "id": email,
                "exp": datetime.now() + timedelta(seconds=60 * 60 * 48),
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return jsonify(
            {"success": True, "message": "Login successful!", "token": token}
        )
    else:
        return jsonify({"success": False, "message": "Invalid email or password"}), 401


@app.route("/sign-up", methods=["GET"])
def get_register():
    return render_template("register.html")


@app.route("/sign-up", methods=["POST"])
def register():
    if request.method == "POST":
        try:
            # Mengambil data dari permintaan POST
            data = request.json
            nama = data["nama"]
            email = data["email"]
            password = data["password"]
            confirm_password = data["confirm_password"]
            password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

            # Memastikan password dan konfirmasi password sesuai
            if password == confirm_password:
                user_count = db.user.count_documents({})
                user_id = user_count + 1

                user_data = {
                    "id": user_id,
                    "nama": nama,
                    "username": "",
                    "email": email,
                    "password": password_hash,
                    "role": "user",
                    "status": "active",
                    "file_foto_profile": "",
                    "foto_profile": "static/profile/profile_placeholder.png",
                    "tanggal_register": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

                # Insert user_data ke koleksi 'user'
                db.user.insert_one(user_data)

                return jsonify(
                    {"status": "Success", "message": "Account created successfully"}
                )
            else:
                return jsonify(
                    {
                        "status": "Error",
                        "message": "Password and confirm password do not match",
                    }
                )
        except Exception as e:
            return jsonify({"status": "Error", "message": str(e)})
    return render_template("register.html")


@app.route("/destinasi", methods=["GET"])
def destinations():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        is_admin = user_info.get("role") == "admin"
        logged_in = True
        return render_template(
            "destinations.html",
            user_info=user_info,
            logged_in=logged_in,
            is_admin=is_admin,
        )
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging you in"
    return render_template("destinations.html", msg=msg)


@app.route("/add_destinasi", methods=["POST"])
def add_destinasi():
    data = request.form

    nama_destinasi = data["namaDestinasi"]
    nama_destinasi_noSpace = nama_destinasi.replace(" ", "")
    card_destinasi = request.files["gambarCardDestinasi"]
    extension_card = card_destinasi.filename.split(".")[-1]
    file_name_card = f"static/card/gambarCard-{nama_destinasi_noSpace}.{extension_card}"
    card_destinasi.save(file_name_card)

    judul_attraction1 = data["judulAttraction1"]
    judul_attraction1_noSpace = judul_attraction1.replace(" ", "")
    subtitle_attraction1 = data["subtitleAttraction1"]
    harga_attraction1 = int(data["hargaAttraction1"])
    gambar_attraction1 = request.files["gambarAttraction1"]
    deskripsi_attraction1 = data["deskripsiAttraction1"]
    extension_attr1 = gambar_attraction1.filename.split(".")[-1]
    file_name_attr1 = (
        f"static/attraction/gambar-{judul_attraction1_noSpace}.{extension_attr1}"
    )
    gambar_attraction1.save(file_name_attr1)

    judul_attraction2 = data["judulAttraction2"]
    judul_attraction2_noSpace = judul_attraction2.replace(" ", "")
    subtitle_attraction2 = data["subtitleAttraction2"]
    harga_attraction2 = int(data["hargaAttraction2"])
    gambar_attraction2 = request.files["gambarAttraction2"]
    deskripsi_attraction2 = data["deskripsiAttraction2"]
    extension_attr2 = gambar_attraction2.filename.split(".")[-1]
    file_name_attr2 = (
        f"static/attraction/gambar-{judul_attraction2_noSpace}.{extension_attr2}"
    )
    gambar_attraction2.save(file_name_attr2)

    judul_attraction3 = data["judulAttraction3"]
    judul_attraction3_noSpace = judul_attraction3.replace(" ", "")
    subtitle_attraction3 = data["subtitleAttraction3"]
    harga_attraction3 = int(data["hargaAttraction3"])
    gambar_attraction3 = request.files["gambarAttraction3"]
    deskripsi_attraction3 = data["deskripsiAttraction3"]
    extension_attr3 = gambar_attraction3.filename.split(".")[-1]
    file_name_attr3 = (
        f"static/attraction/gambar-{judul_attraction3_noSpace}.{extension_attr3}"
    )
    gambar_attraction3.save(file_name_attr3)

    quotes = data["quotes"]

    gambar_artikel = request.files["gambarArtikel"]
    extension_artikel = gambar_artikel.filename.split(".")[-1]
    file_name_artikel = (
        f"static/artikel/gambar-{nama_destinasi_noSpace}.{extension_artikel}"
    )
    gambar_artikel.save(file_name_artikel)
    deskripsi_artikel = data["deskripsiArtikel"]

    destinasi_data = {
        "nama_destinasi": nama_destinasi,
        "card_destinasi": file_name_card,
        "attractions": {
            "attraction1": {
                "judul": judul_attraction1,
                "subtitle": subtitle_attraction1,
                "harga": harga_attraction1,
                "gambar": file_name_attr1,
                "deskripsi_attraction1": deskripsi_attraction1,
            },
            "attraction2": {
                "judul": judul_attraction2,
                "subtitle": subtitle_attraction2,
                "harga": harga_attraction2,
                "gambar": file_name_attr2,
                "deskripsi_attraction2": deskripsi_attraction2,
            },
            "attraction3": {
                "judul": judul_attraction3,
                "subtitle": subtitle_attraction3,
                "harga": harga_attraction3,
                "gambar": file_name_attr3,
                "deskripsi_attraction3": deskripsi_attraction3,
            },
        },
        "quotes": quotes,
        "gambar_artikel": file_name_artikel,
        "deskripsi_artikel": deskripsi_artikel,
        "tanggal_tambah": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    db.destinasi.insert_one(destinasi_data)
    return jsonify({"status": "success", "msg": "Berhasil Menambahkan Destinasi Baru!"})


@app.route("/manajemen_destinasi")
def manajemen_destinasi():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        is_admin = user_info.get("role") == "admin"
        logged_in = True
        if is_admin:
            destinasi_list = db.destinasi.find()

            return render_template(
                "manajemen_destinasi.html",
                user_info=user_info,
                logged_in=logged_in,
                is_admin=is_admin,
                destinasi=destinasi_list,
            )
        else:
            return render_template("login.html")
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging you in"
    return render_template("login.html", msg=msg)

@app.route('/edit_destinasi/<id>', methods=['POST'])
def edit_destinasi(id):
        destinasi = db.destinasi.find_one({'_id': ObjectId(id)})

        data = request.form

        hargaTiketAttraction1Baru = data['attraction1_harga']
        hargaTiketAttraction2Baru = data['attraction2_harga']
        hargaTiketAttraction3Baru = data['attraction3_harga']

        destinasi['attractions']['attraction1']['harga'] = int(hargaTiketAttraction1Baru)
        destinasi['attractions']['attraction2']['harga'] = int(hargaTiketAttraction2Baru)
        destinasi['attractions']['attraction3']['harga'] = int(hargaTiketAttraction3Baru)

        try:
            db.destinasi.update_one({'_id': ObjectId(id)}, {'$set': destinasi})
            flash('Berhasil memperbaharui data!', 'success')
        except Exception as e:
            flash(f'Gagal. Error: {str(e)}', 'danger')
        return redirect(url_for('manajemen_destinasi'))

@app.route('/delete_destinasi/<id>', methods=['DELETE'])
def delete_destinasi(id):
    try:
        db.destinasi.delete_one({"_id": ObjectId(id)})
        return jsonify({"message": "berhasil"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/listdestinasi", methods=["GET"])
def get_destinasi():
    destinasi = db.destinasi.find()
    destinasi_list = []
    for destinasi_info in destinasi:
        destinasi_list.append(
            {
                "id": str(destinasi_info["_id"]),
                "nama_destinasi": destinasi_info["nama_destinasi"],
                "card_destinasi": destinasi_info["card_destinasi"],
            }
        )
    return jsonify(destinasi_list), 200


@app.route("/detail_destinasi/<destinasi_id>", methods=["GET"])
def detail_destinasi(destinasi_id):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        is_admin = user_info.get("role") == "admin"
        logged_in = True
        destinasi_info = db.destinasi.find_one({"_id": ObjectId(destinasi_id)})
        return render_template(
            "detail_destinasi.html",
            destinasi_info=destinasi_info,
            user_info=user_info,
            logged_in=logged_in,
            is_admin=is_admin,
        )
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging you in"
    return render_template("login.html", msg=msg)


@app.route("/getulasan", methods=["GET"])
def get_ulasan():
    try:
        ulasan_data = db.ulasan.find({}, {"_id": 0})  # Ambil semua data ulasan, hilangkan field _id
        ulasan_list = list(ulasan_data)
        return jsonify({"ulasan": ulasan_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/pesantiket", methods=["POST"])
def pesantiket():
    namaAttraction = request.form["attractionGive"]
    namaPemesan = request.form["namaPemesan"]
    emailPemesan = request.form["emailPemesan"]
    hargaTiket = int(request.form["hargaTiket"])
    jumlahTiket = request.form["jumlahTiket"]
    totalHargaTiket = int(request.form["totalHargaTiket"])
    tanggal = request.form["tanggal"]
    doc = {
        "namaAttraction": namaAttraction,
        "namaPemesan": namaPemesan,
        "emailPemesan": emailPemesan,
        "hargaTiket": hargaTiket,
        "jumlahTiket": jumlahTiket,
        "totalHargaTiket": totalHargaTiket,
        "tanggal": tanggal,
        "status": "pending",
        "buktiPembayaran": "",
        "e-ticket": "",
        "waktuPemesanan": datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    db.tiket.insert_one(doc)
    return redirect(url_for("home"))
  
@app.route("/about", methods=["GET"])
def about():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        is_admin = user_info.get("role") == "admin"
        logged_in = True
        print(user_info)
        return render_template(
            "about.html", user_info=user_info, logged_in=logged_in, is_admin=is_admin
        )
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging you in"
    return render_template("about.html", msg=msg)


@app.route("/cek_pesanan/<nama>")
def cek_pesanan(nama):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        is_admin = user_info.get("role") == "admin"
        logged_in = True

        tiket_list = []
        tiket_pdf = list(db.tiket.find())
        tiket_info = db.tiket.find({"namaPemesan": nama})

        for ticket in tiket_info:
            tiket_data = {
                "_id": str(ticket['_id']),
                "namaAttraction": ticket["namaAttraction"],
                "namaPemesan": ticket["namaPemesan"],
                "jumlahTiket": ticket["jumlahTiket"],
                "hargaTiket": ticket["hargaTiket"],
                "totalHargaTiket": ticket["totalHargaTiket"],
                "buktiPembayaran": ticket["buktiPembayaran"],
                "status": ticket["status"],
                "e-ticket": ticket["e-ticket"],
            }
            tiket_list.append(tiket_data)

        return render_template(
            "cek_pesanan.html",
            user_info=user_info,
            logged_in=logged_in,
            is_admin=is_admin,
            tiket_list=tiket_list, 
            tiket_pdf=tiket_pdf,
        )
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging you in"
    return render_template("login.html", msg=msg)

@app.route('/upload_bukti/<ticket_id>', methods=['POST'])
def upload_bukti(ticket_id):
    try:
        buktiUpload = request.files['buktiUpload']
        token_receive = request.cookies.get(TOKEN_KEY)
        
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"email": payload["id"]})
        
        file_extension = os.path.splitext(buktiUpload.filename)[1]
        namaBuktiUpload = f'static/booking/bukti_pembayaran-{ticket_id}{file_extension}'

        buktiUpload.save(namaBuktiUpload)
        
        db.tiket.update_one(
            {'_id': ObjectId(ticket_id)},
            {'$set': {
                'buktiPembayaran': namaBuktiUpload,
                'status': 'uploaded'
            }}
        )
        return jsonify({'message': 'Proof updated successfully', 'status': 'uploaded'}), 200
    
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Your token has expired'}), 401
    except jwt.exceptions.DecodeError:
        return jsonify({'message': 'There was a problem logging you in'}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route("/beranda_admin", methods=["GET"])
def beranda_admin():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        is_admin = user_info.get("role") == "admin"
        logged_in = True
        if is_admin:
            return render_template(
                "beranda_admin.html",
                user_info=user_info,
                logged_in=logged_in,
                is_admin=is_admin,
            )
        else:
            return redirect(url_for('home'))
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging you in"
    return render_template("login.html", msg=msg)

@app.route('/get_statistik_pemesanan', methods=['GET'])
def get_statistik_pemesanan():
    semua_data = db.tiket.find()

    jumlah_pemesanan_per_bulan = {
        '01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0,
        '07': 0, '08': 0, '09': 0, '10': 0, '11': 0, '12': 0
    }

    for data in semua_data:
        bulan = datetime.strptime(data['waktuPemesanan'], '%Y-%m-%d %H:%M').strftime('%m')
        jumlah_pemesanan_per_bulan[bulan] += 1

    data_pemesanan = {
        'labels': [datetime.strptime(str(k), '%m').strftime('%B') for k in jumlah_pemesanan_per_bulan.keys()],
        'data': list(jumlah_pemesanan_per_bulan.values())
    }

    return jsonify(data_pemesanan=data_pemesanan)

@app.route('/get_statistik_pendapatan', methods=['GET'])
def get_statistik_pendapatan():
    data = db.tiket.aggregate([
                {
            '$match': {'status': 'confirmed'}
        },
        {
            '$group': {
                '_id': {'$substr': ['$waktuPemesanan', 0, 7]},
                'totalHarga': {'$sum': '$totalHargaTiket'}
            }
        },
        {
            '$sort': {'_id': 1}
        }
    ])

    result = list(data)
    return jsonify(data=result)

@app.route("/manajemen_tiket", methods=["GET"])
def manajemen_tiket():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        logged_in = True

        if user_info:
            is_admin = (
                user_info.get("role") == "admin" if "role" in user_info else False
            )

            if is_admin:
                tikets = db.tiket.find()
                tiket_list = []

                for tiket in tikets:
                    tiket_info = {
                        "id": str(tiket["_id"]),
                        "namaAttraction": tiket["namaAttraction"],
                        "namaPemesan": tiket["namaPemesan"],
                        "buktiPembayaran": tiket["buktiPembayaran"],
                        "hargaTiket": tiket["hargaTiket"],
                        "jumlahTiket": tiket["jumlahTiket"],
                        "totalHargaTiket": tiket["totalHargaTiket"],
                        "tanggal": tiket["tanggal"],
                        "status": tiket["status"],
                    }
                    tiket_list.append(tiket_info)
                return render_template(
                    "manajemen_tiket.html",
                    user_info=user_info,
                    logged_in=logged_in,
                    is_admin=is_admin,
                    data_tiket=tiket_list,
                )
            else:
                return render_template("manajemen_tiket.html", user_info=user_info, is_admin=is_admin)
        else:
            return render_template("manajemen_tiket.html", msg="User not found", user_info=user_info)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging you in"

    return render_template("manajemen_tiket.html", msg=msg, user_info=user_info)



@app.route("/manajemen_tiket/konfirmasi_pembayaran/<ticket_id>", methods=["GET"])
def konfirmasi_pembayaran(ticket_id):
    try:
        tiket_info = db.tiket.find_one({"_id": ObjectId(ticket_id)})

        if tiket_info and tiket_info["status"] in ["pending", "uploaded"]:

            db.tiket.update_one({"_id": ObjectId(ticket_id)}, {"$set": {"status": "confirmed"}})
            flash('Konfirmasi pembayaran berhasil!', 'success')
        else:
            flash('Tiket tidak ditemukan atau sudah dikonfirmasi', 'danger')

    except Exception as e:
        flash(f'Gagal. Error: {str(e)}', 'danger')

    return redirect(url_for('manajemen_tiket'))



@app.route("/manajemen_tiket/lihat_bukti_pembayaran/<ticket_id>", methods=["GET"])
def lihat_bukti_pembayaran(ticket_id):
    try:
        tiket_info = db.tiket.find_one({"_id": ObjectId(ticket_id)})
        
        if tiket_info and tiket_info["status"] == "uploaded":
            file_path = os.path.join('booking', tiket_info['buktiPembayaran'])
            print("File Path:", file_path)
            return send_from_directory('booking', os.path.basename(file_path))
        # if tiket_info and tiket_info["status"] == "confirmed":
        #     return send_from_directory('booking', tiket_info['buktiPembayaran'])
        else:
            flash('Bukti pembayaran tidak ditemukan atau tiket belum dikonfirmasi', 'danger')

    except Exception as e:
        flash(f'Gagal. Error: {str(e)}', 'danger')

    return redirect(url_for('manajemen_tiket'))


@app.route("/delete_ticket/<ticket_id>", methods=["DELETE"])
def delete_ticket(ticket_id):
    try:
        # Implement logic to delete the ticket from the database using ticket_id
        db.tiket.delete_one({"_id": ObjectId(ticket_id)})
        return jsonify({"message": "Ticket deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/ulasan_rekomendasi", methods=["GET"])
def list_ulasan_rekomendasi():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        is_admin = user_info.get("role") == "admin"
        logged_in = True
        if is_admin:
            data_ulasan = db.ulasan.find({},{'_id': False})
            
            list_ulasan = list(data_ulasan)
            
            return render_template(
                "ulasan_dan_rekom.html",
                list_ulasan=list_ulasan,
                user_info=user_info,
                logged_in=logged_in,
                is_admin=is_admin,
            )
        else:
            return render_template("login.html")
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging you in"
    return render_template("login.html", msg=msg)
  

@app.route("/manajemen_user", methods=["GET"])
def manajemen_user():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        is_admin = user_info.get("role") == "admin"
        logged_in = True
        if is_admin:
            users = db.user.find()
            user_list = []

            for user in users:
                user_lists = {
                    "id": str(user["_id"]),
                    "nama": user["nama"],
                    "email": user["email"],
                    "password": user["password"],
                    "role": user["role"],
                    # 'status': user['status'],
                }
                user_list.append(user_lists)

            return render_template(
                "manajemen_user.html",
                user_info=user_info,
                logged_in=logged_in,
                is_admin=is_admin,
                users=user_list,
            )
        else:
            return render_template("login.html")
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging you in"
    return render_template("login.html", msg=msg)


@app.route('/edit_user/<string:user_id>', methods=['POST'])
def edit_user(user_id):
    try:
        # Convert user_id to ObjectId
        user_id_object = ObjectId(user_id)

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        status = request.form['status']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        doc = {
            'nama': username,
            'email': email,
            'password': hashed_password,
            'role': role,
            'status': status
        }

        db.user.update_one({'_id': user_id_object}, {'$set': doc})

        return jsonify({'message': 'Data updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/delete_user/<string:user_id>', methods=['POST'])
def delete_user(user_id):
    try:
        user_id_object = ObjectId(user_id)

        result = db.user.delete_one({'_id': user_id_object})

        if result.deleted_count == 1:
            return jsonify({'message': 'User deleted successfully'})
        else:
            return jsonify({'error': 'User not found'})

    except Exception as e:
        return jsonify({'error': str(e)})  


@app.route("/profile_admin/<nama>", methods=["GET"])
def profile_admin(nama):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        is_admin = user_info.get("role") == "admin"
        logged_in = True
        return render_template(
            "profile_Admin.html",
            user_info=user_info,
            logged_in=logged_in,
            is_admin=is_admin,
        )
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging you in"
    return render_template("login.html", msg=msg)


@app.route("/profile_User/<nama>", methods=["GET"])
def get_profil_user(nama):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"email": payload["id"]})
        is_admin = user_info.get("role") == "admin"
        logged_in = True
        return render_template(
            "profile_User.html",
            user_info=user_info,
            logged_in=logged_in,
            is_admin=is_admin,
        )
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging you in"
    return render_template("login.html", msg=msg)


@app.route("/profile_User", methods=["POST"])
def profil_User():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        emailBefore = payload.get("id")

        nama = request.form["nama"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

        # Menggunakan request.files untuk mendapatkan file gambar yang diunggah
        if "profileImage" in request.files:
            profile_image = request.files["profileImage"]
            # Simpan gambar ke direktori /static/img/profile_user/
            if profile_image.filename != '':
                image_path = f'static/img/profile_user/{profile_image.filename}'
                profile_image.save(image_path)
                foto_profile = image_path

        data_baru = {
            "nama": nama,
            "username": username,
            "email": email,
            "password": password_hash,
            "foto_profile": foto_profile if 'foto_profile' in locals() else '/static/profile/profile_placeholder.png'
        }

        db.user.update_one({"email": emailBefore}, {"$set": data_baru})

        return redirect(url_for("home"))  # Redirect ke halaman yang sesuai setelah update
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging you in"
    return render_template("login.html", msg=msg)


@app.route('/simpan-ulasan', methods=['POST'])
def simpan_ulasan():
    try:
        namaAttraction = request.form['namaAttraction']
        rating = request.form['rating']
        review = request.form['review']
        pemberiUlasan = request.form['pemberiUlasan']  

        doc = {
            "namaAttraction" : namaAttraction,
            "rating": rating,
            "review": review,
            "pemberiUlasan": pemberiUlasan,
            "waktu": datetime.now().strftime("%B %Y")
        }
        
        db.ulasan.insert_one(doc)

        return jsonify({"status": "success", "message": "Ulasan berhasil disimpan!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f'Gagal menyimpan ulasan: {str(e)}'})
    
@app.route('/generate_pdf/<booking_id>')
def generate_pdf(booking_id):
    specific_card = db.tiket.find_one({'_id': ObjectId(booking_id)})
    
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    y_coordinate = 750
    line_spacing = 20
    
    pdf.setFillColorRGB(0, 0, 0.8)  # Set Title Color
    pdf.setFont("Helvetica-Bold", 16)
    
    pdf.setFillColorRGB(0, 0, 0)
    
    pdf.setFont("Helvetica", 12)
    pdf.line(50, 780, 550, 780)
    pdf.line(50, 50, 550, 50)
    
    pdf.drawString(100, y_coordinate, "Trip Wonders | Tiket Anda")
    y_coordinate -= line_spacing
    pdf.drawString(100, y_coordinate, f"Nama Pemesan: {specific_card['namaPemesan']}")
    y_coordinate -= line_spacing

    pdf.drawString(100, y_coordinate, f"Email Pemesan: {specific_card['emailPemesan']}")
    y_coordinate -= line_spacing

    pdf.drawString(100, y_coordinate, f"Nama Attraction: {specific_card['namaAttraction']}")
    y_coordinate -= line_spacing

    pdf.drawString(100, y_coordinate, f"Jumlah Tiket: {specific_card['jumlahTiket']}")
    y_coordinate -= line_spacing

    pdf.drawString(100, y_coordinate, f"Harga Tiket: {specific_card['hargaTiket']}")
    y_coordinate -= line_spacing

    pdf.drawString(100, y_coordinate, f"Total Harga: {specific_card['totalHargaTiket']}")
    y_coordinate -= line_spacing

    pdf.drawString(100, y_coordinate, f"Tanggal Keberangkatan: {specific_card['tanggal']}")
    y_coordinate -= line_spacing

    pdf.save()

    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Tiket_{specific_card["namaAttraction"]}.pdf'
    return response

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
