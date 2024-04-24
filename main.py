# conda activate webservicep2plending webservicep2plending
# uvicorn main:app --reload


from typing import Union # untuk memberikan petunjuk tipe bahwa suatu variabel dapat memiliki beberapa tipe
from fastapi import FastAPI,Response,Request,HTTPException # untuk membuat aplikasi FastAPI, dan HTTP
from fastapi.middleware.cors import CORSMiddleware # untuk menangani permintaan lintas asal dengan menambahkan header yang sesuai ke respons.
import sqlite3 

#inisialisasi aplikasi FastAPI
app = FastAPI() 

# Digunakan untuk Menambahkan middleware CORS untuk mengizinkan permintaan lintas sumber
app.add_middleware( # untuk menambahkan middleware CORS ke aplikasi FastAPI
	CORSMiddleware, 
	allow_origins=["*"], # untuk membuat permintaan lintas sumber ke aplikasi, artinya aplikasi akan menerima permintaan dari domain mana pun
	allow_credentials=True,
	allow_methods=["*"], # menentukan metode HTTP mana yang diizinkan dalam permintaan lintas sumber. seperti GET, POST, PUT, PATCH, DELETE, 
	allow_headers=["*"], # menentukan header mana yang diizinkan dalam permintaan aplikasi akan menerima permintaan dengan header apa pun yang disertakan.
)


@app.get("/") # Route untuk halaman root, merespons dengan pesan sederhana
def read_root(): # untuk merespons dengan pesan JSON yang berisi "Hello: World".
    return {"Hello": "World"}

@app.get("/mahasiswa/{nim}") # Route untuk mengambil data mahasiswa berdasarkan NIM
def ambil_mhs(nim:str): 
    return {"nama": "Budi Martami"}

@app.get("/mahasiswa2/") # Route lain untuk mengambil data mahasiswa
def ambil_mhs2(nim:str):
    return {"nama": "Budi Martami 2"}

@app.get("/daftar_mhs/") # Route untuk menampilkan daftar mahasiswa berdasarkan ID provinsi dan angkatan
def daftar_mhs(id_prov:str,angkatan:str):
    return {"query":" idprov: {}  ; angkatan: {} ".format(id_prov,angkatan),"data":[{"nim":"1234"},{"nim":"1235"}]}

# panggil sekali saja
@app.get("/init/") # Route untuk menginisialisasi database
def init_db(): # untuk menginisialisasi atau membuat database SQLite baru jika belum ada.
  try:
    DB_NAME = "upi.db" # nama database
    con = sqlite3.connect(DB_NAME) # untuk membuat koneksi ke database SQLite yang disimpan dalam variabel con
    cur = con.cursor() # untuk mengeksekusi perintah SQL.

    # Membuat tabel 'mahasiswa' apabila tabel belum ada
    create_table = """ CREATE TABLE mahasiswa( 
            ID      	INTEGER PRIMARY KEY 	AUTOINCREMENT,
            nim     	TEXT            	NOT NULL,
            nama    	TEXT            	NOT NULL,
            id_prov 	TEXT            	NOT NULL,
            angkatan	TEXT            	NOT NULL,
            tinggi_badan  INTEGER
        )  
        """
    cur.execute(create_table) # untuk mengeksekusi perintah SQL yang diberikan (dalam hal ini, perintah pembuatan tabel).
    con.commit 
  except:
           return ({"status":"terjadi error"})  # Jika terjadi kesalahan, kirimkan pesan kesalahan
  finally:
           con.close() # Tutup koneksi setelah selesai
    
  return ({"status":"ok, db dan tabel berhasil dicreate"})

from pydantic import BaseModel # Menggunakan Pydantic untuk mendefinisikan skema model data mahasiswa
from typing import Optional

class Mhs(BaseModel): # untuk mendefinisikan struktur atau skema data untuk entitas "mahasiswa".
   nim: str # unt menunjukkan bahwa NIM akan direpresentasikan sebagai teks
   nama: str # unt menyimpan nama lengkap mahasiswa
   id_prov: str 
   angkatan: str
   tinggi_badan: Optional[int] | None = None  # yang boleh null hanya ini


#status code 201 standard return creation
#return objek yang baru dicreate (response_model tipenya Mhs)
@app.post("/tambah_mhs/", response_model=Mhs,status_code=201) # Route untuk menambahkan mahasiswa baru 
def tambah_mhs(m: Mhs,response: Response, request: Request):
   try:
       DB_NAME = "upi.db" # variabel yang menyimpan nama file database"upi.db".
       con = sqlite3.connect(DB_NAME) # unt membuat koneksi ke database SQLite yang disimpan dalam file "upi.db"
       cur = con.cursor() # digunakan untuk mengeksekusi perintah SQL pada database
       # hanya untuk test, rawal sql injecttion, gunakan spt SQLAlchemy
       cur.execute("""insert into mahasiswa (nim,nama,id_prov,angkatan,tinggi_badan) values ( "{}","{}","{}","{}",{})""".format(m.nim,m.nama,m.id_prov,m.angkatan,m.tinggi_badan)) # Menyisipkan data mahasiswa baru ke dalam database
       con.commit() 
   except:
       print("oioi error") # Jika terjadi kesalahan, kirimkan pesan kesalahan
       return ({"status":"terjadi error"})   # pesan apabila terjadi error
   finally:  	 
       con.close() # Tutup koneksi setelah selesai
   response.headers["Location"] = "/mahasiswa/{}".format(m.nim) # mengatur header respons HTTP.
   print(m.nim) # mencetak NIM mahasiswa yang baru saja ditambahkan, ntuk melihat NIM yang berhasil ditambahkan. 
   print(m.nama)
   print(m.angkatan)
  
   return m # Baris ini mengembalikan objek m yang mewakili data mahasiswa yang baru saja ditambahkan, sebagai respons dari permintaan API.



@app.get("/tampilkan_semua_mhs/") # Route untuk menampilkan semua mahasiswa
def tampil_semua_mhs():
   try:
       DB_NAME = "upi.db"
       con = sqlite3.connect(DB_NAME)
       cur = con.cursor()
       recs = []
       for row in cur.execute("select * from mahasiswa"): # Mengambil semua data mahasiswa dari database
           recs.append(row)
   except:
       return ({"status":"terjadi error"})  # Jika terjadi kesalahan, kirimkan pesan kesalahan 
   finally:  	 
       con.close() # Tutup koneksi setelah selesai
   return {"data":recs} # mengembalikan respons dalam bentuk kamus Python yang berisi data mahasiswa yang telah diambil dari database. 

from fastapi.encoders import jsonable_encoder # Import FastAPI encoders untuk mengkodekan data


@app.put("/update_mhs_put/{nim}",response_model=Mhs) # Route untuk memperbarui data mahasiswa menggunakan metode PUT
def update_mhs_put(response: Response,nim: str, m: Mhs ):
    #update keseluruhan
    #karena key, nim tidak diupdape
    try:
       DB_NAME = "upi.db"
       con = sqlite3.connect(DB_NAME)
       cur = con.cursor()

       # Memeriksa apakah mahasiswa dengan NIM tertentu ada dalam database
       cur.execute("select * from mahasiswa where nim = ?", (nim,) )  #tambah koma untuk menandakan tupple
       existing_item = cur.fetchone() # untuk mengeksekusi query tertentu yang bertujuan untuk mengambil data tertentu dari database.
    except Exception as e: # untuk mencetak pesan kesalahan atau  untuk menangani kesalahan tersebut
        raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))   # Jika terjadi kesalahan, tanggapi dengan status kode 500
    
    if existing_item:  #data ada (data ditemukan, lakukan pembaruan)
            print(m.tinggi_badan)
            cur.execute("update mahasiswa set nama = ?, id_prov = ?, angkatan=?, tinggi_badan=? where nim=?", (m.nama,m.id_prov,m.angkatan,m.tinggi_badan,nim))
            con.commit()            
            response.headers["location"] = "/mahasiswa/{}".format(m.nim)
    else:  # data tidak ada (Jika data tidak ditemukan, kirimkan status kode 404)
            print("item not foud")
            raise HTTPException(status_code=404, detail="Item Not Found")
      
    con.close()
    return m


# khusus untuk patch, jadi boleh tidak ada
# menggunakan "kosong" dan -9999 supaya bisa membedakan apakah tdk diupdate ("kosong") atau mau
# diupdate dengan dengan None atau 0
class MhsPatch(BaseModel): # untuk memperbarui sebagian data mahasiswa, 
   nama: str | None = "kosong"
   id_prov: str | None = "kosong" # menunjukkan bahwa atribut tidak akan diubah. Nilai defaultnya adalah string "kosong", yang akan digunakan jika tidak ada nilai yang diberikan.
   angkatan: str | None = "kosong"
   tinggi_badan: Optional[int] | None = -9999  # yang boleh null hanya ini



@app.patch("/update_mhs_patch/{nim}",response_model = MhsPatch) # Route untuk memperbarui data mahasiswa menggunakan metode PATCH
def update_mhs_patch(response: Response, nim: str, m: MhsPatch ):
    try:
      print(str(m))
      DB_NAME = "upi.db"
      con = sqlite3.connect(DB_NAME)
      cur = con.cursor() 
      cur.execute("select * from mahasiswa where nim = ?", (nim,) )  #tambah koma untuk menandakan tupple
      existing_item = cur.fetchone()
    except Exception as e: # # Tindakan penanganan kesalahan
      raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e))) # misal database down  
    
    if existing_item:  #data ada, lakukan update
        sqlstr = "update mahasiswa set " #asumsi minimal ada satu field update
        # todo: bisa direfaktor dan dirapikan
        if m.nama!="kosong":  # Membangun query update berdasarkan perubahan yang diberikan
            if m.nama!=None: # pengkondisian yang mengecek apakah atribut nama dari objek m tidak sama dengan None
                sqlstr = sqlstr + " nama = '{}' ,".format(m.nama) # untuk menambahkan klausa SQL ke dalam string SQL yang sedang dibentuk.
            else:     
                sqlstr = sqlstr + " nama = null ," #untuk mengatur nilai kolom nama menjadi NULL
        
        if m.angkatan!="kosong": # Ppenjelasannya kurang lebihnya sama yaa
            if m.angkatan!=None:
                sqlstr = sqlstr + " angkatan = '{}' ,".format(m.angkatan)
            else:
                sqlstr = sqlstr + " angkatan = null ,"
        
        if m.id_prov!="kosong":
            if m.id_prov!=None:
                sqlstr = sqlstr + " id_prov = '{}' ,".format(m.id_prov) 
            else:
                sqlstr = sqlstr + " id_prov = null, "     

        if m.tinggi_badan!=-9999: # mengecek apakah nilai atribut tinggi badan telah diisi/diberikan
            if m.tinggi_badan!=None: # untuk memastikan bahwa nilai tinggi badan telah diberikan secara eksplisit
                sqlstr = sqlstr + " tinggi_badan = {} ,".format(m.tinggi_badan) # mengupdate nilai kolom tinggi badan sesuai dengan nilai yang diberikan
            else:    
                sqlstr = sqlstr + " tinggi_badan = null ,"  #apabila pengguna tidak memberikan nilai untuk atribut tinggi badan

        sqlstr = sqlstr[:-1] + " where nim='{}' ".format(nim)  #buang koma yang trakhir  
        print(sqlstr)      
        try:
            cur.execute(sqlstr) # untuk mengeksekusi query SQL yang telah dibentuk sebelumnya dan disimpan dalam variabel sqlstr
            con.commit()         # memastikan bahwa perubahan yang dilakukan pada database dikonfirmasi (commit)
            response.headers["location"] = "/mahasixswa/{}".format(nim)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))   
        

    else:  # data tidak ada 404, item not found
         raise HTTPException(status_code=404, detail="Item Not Found")
   
    con.close()
    return m
  
    
@app.delete("/delete_mhs/{nim}") # Route untuk menghapus data mahasiswa berdasarkan NIM
def delete_mhs(nim: str):
    try:
       DB_NAME = "upi.db" # untuk database SQLite.
       con = sqlite3.connect(DB_NAME) # unt membuat koneksi ke database SQLite dengan menggunakan nama file database yang telah ditentukan sebelumnya
       cur = con.cursor() # untuk mengeksekusi perintah SQL pada database.
       sqlstr = "delete from mahasiswa  where nim='{}'".format(nim)   # Menghapus data mahasiswa dari database berdasarkan NIM          
       print(sqlstr) # debug 
       cur.execute(sqlstr) # unt mengeksekusi query SQL yang telah dibentuk sebelumnya menggunakan objek cursor.
       con.commit() # memastikan bahwa perubahan tersebut dikonfirmasi (commit) untuk menyimpan perubahan secara permanen dalam database
    except:
       return ({"status":"terjadi error"})   # Jika terjadi kesalahan, kirimkan pesan kesalahan
    finally:  	 
       con.close() # Tutup koneksi setelah selesai
    
    return {"status":"ok"}
