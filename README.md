## NX5JSL Szkript nyelvek beadandó

Hallgató: Szabó Ádám (NX5JSL)

Feladat leírása: 

A program egy személyfelismerő (person detection) rendszer, amely:

- Tkinter GUI-t biztosít a beállítások megadásához (YOLOv3 modell elérési út, opcionális e-mail adatok).
- Folyamatosan figyeli a detection_images/ mappát, és az újonnan megjelenő képeken objektumdetektálást futtat (ImageAI YOLOv3).
- Az eredményképet elmenti a detected_images/ mappába.
- Ha a detektálások között van "person" azaz személy, akkor azt naplózza (GUI log + logs.txt),
- és ha az e-mail adatok meg vannak adva, e-mail értesítést küld a feldolgozott (annotált) képpel csatolmányként.
- Nyilvántartja a már feldolgozott képeket a processed_images.txt fájlban, hogy ne dolgozza fel őket újra.

-------

Modulok és modulokban használt függvények:

Beépített / standard modulok

os
- os.getcwd() – aktuális futási könyvtár meghatározása
- os.path.join() – fájlútvonalak összerakása
- os.path.exists() – modell/fájl létezésének ellenőrzése
- os.path.basename() – csatolmány fájlnév kinyerése
- os.listdir() – képfájlok listázása a mappából
- os.makedirs(..., exist_ok=True) – szükséges mappák létrehozása

time
- time.sleep(5) – várakozás két mappaszkennelés között

smtplib
- smtplib.SMTP(host, port) – SMTP kapcsolat
- server.starttls() – TLS titkosítás indítása
- server.login() – bejelentkezés
- server.sendmail() – e-mail elküldése
- server.quit() – kapcsolat lezárása

datetime
- datetime.datetime.now() – aktuális idő
- .strftime() – idő formázása (logokhoz, e-mail szöveghez)

threading
- threading.Thread(target=..., args=..., daemon=True) – detektálás külön szálon

email.mime.text
- MIMEText(body, "plain") – szöveges e-mail törzs

email.mime.multipart
- MIMEMultipart() – több részből álló e-mail (szöveg + csatolmány)

email.mime.image
- MIMEImage(image_data) – kép csatolmányként

-------

Külső (telepítendő) modul

imageai.Detection
- ObjectDetection() – detektor példány
- setModelTypeAsYOLOv3() – modell típus beállítása
- setModelPath(path) – modell fájl elérési út
- loadModel() – modell betöltése
- detectObjectsFromImage(input_image=..., output_image_path=..., minimum_percentage_probability=30) – detektálás és kimeneti (annotált) kép generálása

GUI modulok

tkinter (tk)
- tk.Tk() – főablak
- root.after(ms, callback) – GUI szálon történő biztonságos üzenetdoboz / leállítás ütemezés

tkinter.ttk
- ttk.Frame, ttk.LabelFrame, ttk.Label, ttk.Entry, ttk.Button – modern widgetek

tkinter.scrolledtext
- scrolledtext.ScrolledText – görgethető log mező

tkinter.messagebox
- messagebox.showerror(title, msg) – hibaüzenetek megjelenítése

------

Osztály(ok)
SZA_PersonDetectionApp

Feladata: a teljes alkalmazás GUI-ja és a detektálási folyamat vezérlése.

Fontos attribútumok:
- self.root – Tkinter főablak
- self.is_running – fut-e a detektálás (bool)
- self.detection_thread – a háttérszál referenciája
- self.detector – ImageAI ObjectDetection példány (betöltött modellel)
- UI elemek: model_path_entry, sender_email_entry, receiver_email_entry, password_entry, start_button, stop_button, status_label, log_text

Metódusok:

- __init__(self, root) – alap állapot beállítása, UI felépítése
- setup_ui(self) – GUI elemek létrehozása és elrendezése
- log_message(self, message) – időbélyeges log a GUI scrolled text mezőbe
- start_detection(self) – inputok ellenőrzése, állapotváltás, szál indítása
- stop_detection(self) – futás leállítása, gombok/státusz visszaállítása
- detection_loop(self, model_path, sender_email, receiver_email, password, email_enabled)
	- modell betöltése
	- mappák és logfájlok kezelése
	- képek feldolgozása és “person” esetén értesítés

-------

Egyéb függvény (nem osztály része)
SZA_send_email(subject, body, sender_email, receiver_email, password, image_path, log_callback=None)

Feladata: e-mail küldése SMTP-n keresztül, a feldolgozott képpel csatolmányként.

- Multipart üzenetet épít: kép csatolmány + szöveges body
- Hibakezelést végez, és opcionálisan naplóz a log_callback-en át (pl. GUI logba)